# 0003 — Stateless / one-shot (no conversation memory)

- **Status:** Superseded by [ADR-0012](0012-reply-to-continue-memory.md) (2026-06-21)
- **Date:** 2026-06-21

## Context

A Q&A bot can either remember the recent conversation (so follow-ups like "and
the second one?" work) or treat every question independently. Memory means
assembling and replaying message history into each API call, plus deciding scope
(per-thread? per-channel?) and trimming for token limits.

## Decision

Every `/ask` is answered cold — no history is sent. Each call contains only the
system prompt and the single question.

## Consequences

- Dead simple, cheap, and predictable; no state to store or evict.
- Follow-up questions that depend on prior context won't work — the user must
  ask self-contained questions.
- Adding multi-turn memory later is a separate increment (collect recent turns,
  prepend them to the `messages` list).
