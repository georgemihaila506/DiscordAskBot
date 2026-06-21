# 0006 — Cost controls: max_tokens cap + daily token budget

- **Status:** Accepted
- **Date:** 2026-06-21

## Context

Every `/ask` spends real Anthropic API money, and a Discord command can be run by
anyone who can see it. Possible controls: per-answer token cap, per-user
cooldown/rate limit, a server/user allowlist, and a global daily spend cap.

## Decision

Adopt two hard cost controls from day one:
- **`max_tokens` per answer** (`config.MAX_TOKENS`) — bounds the worst-case cost
  of any single response.
- **Daily global token budget** (`budget.py`) — a running per-day counter; the
  bot stops answering once `DAILY_TOKEN_BUDGET` is reached, resetting at UTC
  midnight.

Deliberately **not** adopted: per-user cooldown/rate limiting and a server
allowlist. (A lightweight one-in-flight-per-user guard is added separately —
ADR-0011.)

## Consequences

- Per-answer and per-day spend are both bounded.
- **Accepted risk:** the daily cap is the only hard spend wall. A burst of
  requests could exhaust the day's budget quickly, and usage is counted *after*
  each answer completes. Acceptable for a small, trusted private server; revisit
  (add per-user rate limiting / an allowlist) before exposing the bot widely.
- The budget counter is in-memory, so a restart resets it — see ADR-0007's
  local-first stance; swap in a JSON/sqlite store if durable accounting matters.
