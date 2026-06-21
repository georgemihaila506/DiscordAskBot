# 0013 — Persist the daily budget across restarts

- **Status:** Accepted
- **Date:** 2026-06-21
- **Strengthens:** [ADR-0006](0006-cost-controls.md)

## Context

v1's daily token budget (ADR-0006) was in-memory, so restarting the bot reset the
day's count to zero — a restart loop could blow well past the intended daily
spend. Making it safe to run unattended means the count must survive restarts.

## Decision

Back the counter with a small JSON file (`BUDGET_FILE`, default
`data/budget.json`) holding `{"date", "used"}`. Load on first use; reset (and
persist) when the UTC date changes; write after each `add_usage` using an atomic
tmp-file + rename. `data/` is gitignored. Added a `used()` accessor for the new
`/usage` command.

## Consequences

- The daily cap now holds across restarts; the bot can run unattended without
  losing its accounting.
- Single-file JSON is enough for one process on one host; if the bot is ever
  sharded or multi-process, this needs a shared store (SQLite/Redis).
- Accounting is still post-hoc (counted after each answer completes), consistent
  with ADR-0006's accepted risk.
