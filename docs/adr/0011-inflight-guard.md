# 0011 — One-in-flight-per-user guard

- **Status:** Accepted
- **Date:** 2026-06-21

## Context

ADR-0006 deliberately skipped per-user rate limiting, leaving the daily budget as
the only spend wall. But streaming (ADR-0005) holds a connection open longer per
call, so a single user firing `/ask` repeatedly could open many concurrent
streams and burn the budget in a burst.

## Decision

Add a minimal guard: reject a user's new `/ask` (with an ephemeral notice) while
their previous one is still being answered. Tracked as an in-memory set of user
ids (`inflight.py`); the id is added before work starts and removed in a
`finally` so it's always released — even on error.

## Consequences

- Kills the obvious burst/spam vector with ~a handful of lines, while keeping the
  "daily cap is the budget wall" design from ADR-0006 intact.
- Not a general rate limiter: a user can still ask again the instant their prior
  answer finishes. That's the intended, minimal scope.
- In-memory, so a restart clears it — correct, since nothing is in flight after a
  restart.
