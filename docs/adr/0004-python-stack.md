# 0004 — Python + discord.py + anthropic SDK

- **Status:** Accepted
- **Date:** 2026-06-21

## Context

The bot could be built in Python (discord.py) or Node.js (discord.js). Both have
mature Discord libraries and first-class Anthropic SDKs.

## Decision

Build in Python with `discord.py` for the Discord side and the official
`anthropic` SDK (its async client) for Claude.

## Consequences

- Matches the author's existing Python background.
- The async client (`AsyncAnthropic`) integrates with discord.py's event loop —
  network calls never block the gateway.
- Dependencies and metadata live in `pyproject.toml`; the package is `src/`, run
  from the repo root with `python -m src.bot`.
