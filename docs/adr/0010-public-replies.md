# 0010 — Public (non-ephemeral) replies

- **Status:** Accepted
- **Date:** 2026-06-21

## Context

A slash-command reply can be public (everyone in the channel sees it) or
ephemeral (only the invoking user sees it). This is a UX choice about whether the
bot is a shared knowledge resource or a private assistant.

## Decision

Answers are posted **publicly** in the channel. Ephemeral replies are reserved
for guard/error notices (in-progress, budget spent, failures).

## Consequences

- The whole channel benefits from each answer; natural for a shared Q&A bot.
- Questions and answers add to channel history (no privacy for the asker).
- Public + streaming is the straightforward combo here; ephemeral + streaming is
  more delicate, and avoiding it keeps the streaming editor simple (ADR-0005).
