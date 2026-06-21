"""DiscordAskBot entrypoint.

Registers an ``/ask`` slash command that streams a Claude answer back into the
channel, editing the reply ~once per second (step 4).
"""

import time

import discord
from discord import app_commands

from src import budget, chunking, claude, config, inflight

# Discord hard-caps a single message at 2000 characters (from chunking).
DISCORD_CHAR_LIMIT = chunking.DISCORD_CHAR_LIMIT
# Minimum seconds between message edits, to stay clear of Discord rate limits.
EDIT_INTERVAL = 1.0


class StreamingReply:
    """Renders a growing answer across one or more Discord messages.

    Edits the active (last) message at most once per ``EDIT_INTERVAL``. When the
    active message would exceed the char limit, it's sealed at a clean boundary
    and a new message opens for the overflow — so nothing is ever truncated.
    """

    def __init__(self, interaction: discord.Interaction) -> None:
        self._interaction = interaction
        self._messages: list[discord.Message] = []
        self._buffer = ""       # full text received so far
        self._committed = 0     # chars sealed into messages[:-1]
        self._shown = ""        # content last pushed to the active message
        self._last_edit = 0.0   # monotonic time of last edit (0 -> paint fast)

    async def start(self) -> None:
        self._messages.append(await self._interaction.followup.send("…"))

    async def feed(self, delta: str) -> None:
        self._buffer += delta
        # Seal overflow into fresh messages as needed (may be several at once).
        while len(self._buffer) - self._committed > DISCORD_CHAR_LIMIT:
            active = self._buffer[self._committed:]
            cut = chunking.split_index(active, DISCORD_CHAR_LIMIT)
            await self._messages[-1].edit(content=active[:cut])
            self._committed += cut
            self._shown = ""
            self._messages.append(await self._interaction.followup.send("…"))
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
        await self._messages[-1].edit(content=f"⚠️ Something went wrong: {exc}")


class AskBot(discord.Client):
    def __init__(self) -> None:
        # Slash commands need no privileged intents; keep the surface minimal.
        super().__init__(intents=discord.Intents.none())
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


@client.tree.command(name="ask", description="Ask a question.")
@app_commands.describe(question="What do you want to ask?")
async def ask(interaction: discord.Interaction, question: str) -> None:
    user_id = interaction.user.id

    # Instant pre-checks (reply within Discord's ~3s window, before deferring).
    if inflight.is_active(user_id):
        await interaction.response.send_message(
            "⏳ You already have a question in progress — let it finish first.",
            ephemeral=True,
        )
        return
    if budget.is_over_budget():
        await interaction.response.send_message(
            "🪫 The bot's daily budget is used up. Try again tomorrow.",
            ephemeral=True,
        )
        return

    inflight.begin(user_id)
    reply: StreamingReply | None = None
    try:
        # Acknowledge within ~3s; gives us ~15 min to answer.
        await interaction.response.defer()
        reply = StreamingReply(interaction)
        await reply.start()
        usage: dict[str, int] = {}
        async for delta in claude.stream(question, usage):
            await reply.feed(delta)
        await reply.finish()
        budget.add_usage(usage.get("input_tokens", 0), usage.get("output_tokens", 0))
    except Exception as exc:  # surface failures instead of leaving a dangling "…"
        if reply is not None:
            await reply.fail(exc)
        raise
    finally:
        # Always release the guard, even on error — or the user is locked out.
        inflight.end(user_id)


def main() -> None:
    client.run(config.DISCORD_TOKEN)


if __name__ == "__main__":
    main()
