# DiscordAskBot

A small personal Discord bot that answers questions using Anthropic's Claude.
Ask a question, get a streamed answer in the channel.

- **`/ask <question>`** — streamed answer, split across messages if long.
- **Reply to an answer** — asks a follow-up that carries the conversation
  context (reply-to-continue).
- **`/usage`** — today's token usage vs the daily budget.

Cost-bounded: open general Q&A (no knowledge base), a per-answer token cap, and a
daily spend budget that survives restarts. Optional access controls (server
allowlist + per-user cooldown). See `docs/adr/` for the decisions and
`docs/glossary.md` for the vocabulary.

## Setup

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
copy .env.example .env   # then fill in DISCORD_TOKEN and ANTHROPIC_API_KEY
```

**Enable the Message Content Intent** (required for reply-to-continue): in the
[Developer Portal](https://discord.com/developers/applications) → your app →
**Bot** → **Privileged Gateway Intents** → turn on **Message Content Intent**.
Without it, the bot raises a `PrivilegedIntentsRequired` error on startup.

## Run

```powershell
.\.venv\Scripts\python.exe -m src.bot
```

## Configuration

All config is via environment variables (see `.env.example`):

- **Required:** `DISCORD_TOKEN`, `ANTHROPIC_API_KEY`.
- **Answer:** `MODEL`, `MAX_TOKENS`, `SYSTEM_PROMPT`, `DEV_GUILD_ID`.
- **Cost:** `DAILY_TOKEN_BUDGET`, `BUDGET_FILE` (persisted daily spend).
- **Access:** `ALLOWED_GUILD_IDS` (empty = all), `USER_COOLDOWN_SECONDS` (0 = off).
- **Memory:** `HISTORY_MAX_MESSAGES`, `MEMORY_TTL_MINUTES`, `MEMORY_MAX_CONVERSATIONS`.

## Documentation

- `docs/glossary.md` — the Discord/Anthropic vocabulary the code uses.
- `docs/adr/` — one Architecture Decision Record per design decision (why, not
  just what). Start at `docs/adr/README.md`.
