# 0005 — Defer, then stream via throttled edits

- **Status:** Accepted
- **Date:** 2026-06-21

## Context

Discord requires an interaction to be acknowledged within ~3 seconds, but a
Claude call takes longer. Two shapes are possible after deferring: edit once with
the full answer, or stream tokens and edit the message repeatedly for a
typewriter feel. Repeated edits risk Discord's rate limit (HTTP 429).

## Decision

`defer()` immediately (buys ~15 minutes), then stream Claude's tokens and edit
the reply as they arrive — but throttled to at most one edit per second, and
skipping edits whose content hasn't changed.

## Consequences

- Responsive, live-feeling answers without tripping rate limits.
- More moving parts than a single final edit: a streaming generator
  (`claude.stream`) and an editor that tracks timing and last-shown content
  (`StreamingReply`).
- Interacts with chunking (ADR-0008): when the streamed message overflows 2000
  chars it must be sealed and continued in a new message mid-stream.
