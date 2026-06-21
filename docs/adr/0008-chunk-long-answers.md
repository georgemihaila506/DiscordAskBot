# 0008 — Auto-split long answers at ~2000-char boundaries

- **Status:** Accepted
- **Date:** 2026-06-21

## Context

A Discord message is hard-capped at 2000 characters, but Claude can answer
longer. Options when an answer is too long: split into multiple messages, cap the
length so it always fits, or upload the answer as a file attachment.

## Decision

Auto-split: chunk the answer into ≤2000-char pieces on natural boundaries
(paragraph break, then line break, then space; hard cut only if no boundary is
found in the second half of the window) and post follow-up messages. Nothing is
truncated.

## Consequences

- The user always gets the full answer, split readably.
- The boundary logic is a pure, unit-tested function (`chunking.split_index` /
  `split_all`); the Discord orchestration lives in `StreamingReply`.
- Combined with streaming (ADR-0005), an active message is sealed at a boundary
  the moment it would exceed 2000 chars and a new message continues — handled
  incrementally so earlier messages never get re-edited.
- Code fences that span a split aren't reopened (a fenced block broken across two
  messages loses its formatting at the seam). Acceptable for now; a future
  refinement could make splitting fence-aware.
