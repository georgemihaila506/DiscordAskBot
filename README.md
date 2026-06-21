# DiscordAskBot

A small personal Discord bot that answers questions using Anthropic's Claude,
exposed as a single `/ask` slash command. Ask a question, get a streamed answer
in the channel.

Deliberately minimal and cost-bounded: open general Q&A (no knowledge base),
stateless (no conversation memory), with a per-answer token cap and a daily
spend budget. See `docs/adr/` for the decisions and `docs/glossary.md` for the
vocabulary.

## Setup

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
copy .env.example .env   # then fill in DISCORD_TOKEN and ANTHROPIC_API_KEY
```

## Run

```powershell
.\.venv\Scripts\python.exe -m src.bot
```

## Configuration

All config is via environment variables (see `.env.example`): `DISCORD_TOKEN`,
`ANTHROPIC_API_KEY` (required), and `MODEL`, `MAX_TOKENS`, `DAILY_TOKEN_BUDGET`,
`SYSTEM_PROMPT`, `DEV_GUILD_ID` (optional).

## Documentation

- `docs/glossary.md` — the Discord/Anthropic vocabulary the code uses.
- `docs/adr/` — one Architecture Decision Record per design decision (why, not
  just what). Start at `docs/adr/README.md`.
