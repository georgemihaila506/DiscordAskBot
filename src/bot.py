"""DiscordAskBot entrypoint.

- ``/ask`` — ask a question; the streamed answer is posted in the channel.
- ``/usage`` — show today's token usage vs the daily budget.
- Reply to one of the bot's answers to ask a follow-up that carries context
  (reply-to-continue; requires the Message Content privileged intent).
"""

import time
from collections.abc import Awaitable, Callable

import discord
from discord import app_commands

from src import access, budget, chunking, claude, config, inflight, memory

# Discord hard-caps a single message at 2000 characters (from chunking).
DISCORD_CHAR_LIMIT = chunking.DISCORD_CHAR_LIMIT
# Minimum seconds between message edits, to stay clear of Discord rate limits.
EDIT_INTERVAL = 1.0

# A coroutine that posts a message and returns it (e.g. followup.send / channel.send).
Sender = Callable[[str], Awaitable[discord.Message]]


class StreamingReply:
    """Renders a growing answer across one or more Discord messages.

    Posts via the given ``send`` coroutine, so it works for both slash-command
    follow-ups and plain channel messages. Edits the active (last) message at
    most once per ``EDIT_INTERVAL``; when it would exceed the char limit, it's
    sealed at a clean boundary and a new message opens for the overflow — so
    nothing is ever truncated.
    """

    def __init__(self, send: Sender) -> None:
        self._send = send
        self._messages: list[discord.Message] = []
        self._buffer = ""       # full text received so far
        self._committed = 0     # chars sealed into messages[:-1]
        self._shown = ""        # content last pushed to the active message
        self._last_edit = 0.0   # monotonic time of last edit (0 -> paint fast)

    @property
    def text(self) -> str:
        return self._buffer

    @property
    def message_ids(self) -> list[int]:
        return [m.id for m in self._messages]

    async def start(self) -> None:
        self._messages.append(await self._send("…"))

    async def feed(self, delta: str) -> None:
        self._buffer += delta
        # Seal overflow into fresh messages as needed (may be several at once).
        while len(self._buffer) - self._committed > DISCORD_CHAR_LIMIT:
            active = self._buffer[self._committed:]
            cut = chunking.split_index(active, DISCORD_CHAR_LIMIT)
            await self._messages[-1].edit(content=active[:cut])
            self._committed += cut
            self._shown = ""
            self._messages.append(await self._send("…"))
        # Throttled repaint of the active message.
        now = time.monotonic()
        if now - self._last_edit >= EDIT_INTERVAL:
            await self._paint(now)

    async def _paint(self, now: float | None = None) -> None:
        content = self._buffer[self._committed:] or "…"
        if content != self._shown:
            await self._messages[-1].edit(content=content)
            self._shown = content
            self._last_edit = now if now is not None else time.monotonic()

    async def finish(self) -> None:
        if not self._buffer:
            await self._messages[-1].edit(content="(no answer)")
            return
        await self._paint()

    async def fail(self, exc: Exception) -> None:
        if self._messages:
            await self._messages[-1].edit(content=f"⚠️ Something went wrong: {exc}")


def precheck(guild_id: int | None, user_id: int) -> str | None:
    """Run access + inflight + budget gates. Return a rejection message or None."""
    denied = access.check(guild_id, user_id)
    if denied:
        return denied
    if inflight.is_active(user_id):
        return "⏳ You already have a question in progress — let it finish first."
    if budget.is_over_budget():
        return "🪫 The bot's daily budget is used up. Try again tomorrow."
    return None


async def _answer(send: Sender, question: str, prior_history: list[dict]) -> None:
    """Stream an answer, account for tokens, and store it for follow-ups."""
    reply = StreamingReply(send)
    await reply.start()
    try:
        usage: dict[str, int] = {}
        async for delta in claude.stream(question, history=prior_history, usage=usage):
            await reply.feed(delta)
        await reply.finish()
    except Exception as exc:  # surface failures instead of leaving a dangling "…"
        await reply.fail(exc)
        raise
    budget.add_usage(usage.get("input_tokens", 0), usage.get("output_tokens", 0))
    conversation = [
        *prior_history,
        {"role": "user", "content": question},
        {"role": "assistant", "content": reply.text},
    ]
    memory.put(reply.message_ids, conversation)


class AskBot(discord.Client):
    def __init__(self) -> None:
        # Reply-to-continue needs to read message content, so enable that
        # privileged intent (toggle it on in the Dev Portal too). Everything
        # else stays minimal.
        intents = discord.Intents.none()
        intents.guilds = True
        intents.guild_messages = True
        intents.dm_messages = True
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        # Sync the command tree. To a dev guild it's instant; global sync can
        # take up to ~an hour to propagate.
        if config.DEV_GUILD_ID is not None:
            guild = discord.Object(id=config.DEV_GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print(f"Synced commands to dev guild {config.DEV_GUILD_ID}")
        else:
            await self.tree.sync()
            print("Synced commands globally (may take up to ~1h to appear)")


client = AskBot()


@client.event
async def on_ready() -> None:
    print(f"Logged in as {client.user} (id: {client.user.id})")


@client.event
async def on_message(message: discord.Message) -> None:
    """Reply-to-continue: a reply to one of our answers is a follow-up question."""
    if message.author.bot:
        return
    ref = message.reference
    if ref is None or ref.message_id is None:
        return

    # Resolve the replied-to message and confirm it's one of our answers.
    replied = ref.resolved
    if not isinstance(replied, discord.Message):
        try:
            replied = await message.channel.fetch_message(ref.message_id)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return
    if replied.author.id != client.user.id:
        return

    question = message.content.strip()
    if not question:
        return

    user_id = message.author.id
    guild_id = message.guild.id if message.guild else None
    denied = precheck(guild_id, user_id)
    if denied:
        await message.reply(denied)
        return

    prior_history = memory.get(ref.message_id)
    inflight.begin(user_id)
    access.record(user_id)
    try:
        await _answer(message.channel.send, question, prior_history)
    finally:
        inflight.end(user_id)


@client.tree.command(name="ask", description="Ask a question.")
@app_commands.describe(question="What do you want to ask?")
async def ask(interaction: discord.Interaction, question: str) -> None:
    user_id = interaction.user.id
    denied = precheck(interaction.guild_id, user_id)
    if denied:
        await interaction.response.send_message(denied, ephemeral=True)
        return

    inflight.begin(user_id)
    access.record(user_id)
    try:
        # Acknowledge within ~3s; gives us ~15 min to answer.
        await interaction.response.defer()
        await _answer(interaction.followup.send, question, [])
    finally:
        # Always release the guard, even on error — or the user is locked out.
        inflight.end(user_id)


@client.tree.command(name="usage", description="Show today's token usage and budget.")
async def usage(interaction: discord.Interaction) -> None:
    used = budget.used()
    total = config.DAILY_TOKEN_BUDGET
    pct = (used / total * 100) if total else 0
    await interaction.response.send_message(
        "📊 **Today's usage**\n"
        f"Used: {used:,} / {total:,} tokens ({pct:.0f}%)\n"
        f"Remaining: {budget.remaining():,}\n"
        "Resets at 00:00 UTC.",
        ephemeral=True,
    )


def main() -> None:
    client.run(config.DISCORD_TOKEN)


if __name__ == "__main__":
    main()
