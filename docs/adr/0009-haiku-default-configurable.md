# 0009 — Haiku 4.5 default, model read from env

- **Status:** Accepted
- **Date:** 2026-06-21

## Context

The model choice is the single biggest driver of both cost (against the daily
budget, ADR-0006) and answer quality. Options spanned Haiku (cheapest/fastest),
Sonnet (balanced), and Opus (most capable, priciest).

## Decision

Default to **Haiku 4.5** (`claude-haiku-4-5`) for cheap, fast casual Q&A, but read
the model id from the `MODEL` environment variable so it can be swapped without
editing code.

## Consequences

- Maximizes answers-per-dollar; the daily budget stretches furthest.
- Slightly less depth on hard/nuanced questions than Sonnet/Opus — acceptable for
  a casual Q&A bot, and a one-line `.env` change upgrades it.
- No code path depends on a specific model.
