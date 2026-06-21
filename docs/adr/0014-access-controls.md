# 0014 — Access controls: guild allowlist + per-user cooldown

- **Status:** Accepted
- **Date:** 2026-06-21
- **Closes the accepted risk in:** [ADR-0006](0006-cost-controls.md), [ADR-0011](0011-inflight-guard.md)

## Context

ADR-0006/0011 deliberately shipped with only a daily cap and a one-in-flight
guard, accepting that the bot wasn't safe to expose widely (no way to restrict
servers, no rate limit beyond one concurrent request). Making it shareable
requires closing that gap.

## Decision

Add two opt-in controls (`access.py`), both off by default so v1 behavior is
unchanged:
- **Guild allowlist** (`ALLOWED_GUILD_IDS`, comma-separated; empty = allow all) —
  the bot refuses requests from servers not on the list.
- **Per-user cooldown** (`USER_COOLDOWN_SECONDS`; 0 = off) — a minimum gap between
  one user's requests, tracked in a `last_use` map.

Both run in the shared `precheck()` alongside the existing inflight and budget
gates; the same gate protects `/ask` and reply-to-continue follow-ups.

## Consequences

- The bot can be safely added to a known set of servers and throttled per user,
  closing the ADR-0006/0011 risk.
- Defaults preserve the original "open to anyone who can see it" behavior — these
  are knobs, not a new mandatory policy.
- Allowlist + cooldown state is in-memory; the cooldown map resets on restart
  (harmless), and the allowlist is config, not state.
