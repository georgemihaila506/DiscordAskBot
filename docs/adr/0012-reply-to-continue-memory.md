# 0012 — Multi-turn follow-ups via reply-to-continue

- **Status:** Accepted
- **Date:** 2026-06-21
- **Supersedes:** [ADR-0003](0003-stateless.md); **amends** [ADR-0002](0002-slash-command-only.md)

## Context

Users want follow-up questions ("which is fastest?") to carry the prior
conversation. v1 was deliberately stateless (ADR-0003). Three mechanisms were
considered: an implicit per-(channel,user) rolling window, Discord threads, and
reply-to-continue. Reply-to-continue is the most intuitive UX, but a
slash-command answer isn't a Discord "reply", so context can't be reconstructed
by walking reply references.

## Decision

Support **reply-to-continue**: replying to one of the bot's answer messages asks
a follow-up that carries context. Implemented by mapping **each answer message id
→ the conversation that produced it** (`memory.py`), rather than walking Discord
reply chains. An `on_message` listener detects a reply whose target is one of the
bot's messages, looks up the stored conversation, and continues it. This requires
enabling the **Message Content** privileged intent.

Memory is in-memory and bounded three ways: a per-conversation turn window
(`HISTORY_MAX_MESSAGES`), an idle TTL (`MEMORY_TTL_MINUTES`), and a cap on stored
conversations (`MEMORY_MAX_CONVERSATIONS`, oldest evicted first). Each answer maps
all of its (possibly several, due to chunking) message ids to the same
conversation, so replying to any chunk works.

## Consequences

- Natural follow-ups without threads or implicit/ambiguous continuation; `/ask`
  always starts fresh, a reply continues.
- Requires the Message Content privileged intent (Dev Portal toggle) and an
  `on_message` listener — a real expansion of the v1 slash-command-only surface
  (hence the ADR-0002 amendment).
- Memory resets on restart (acceptable — nothing is mid-conversation after a
  restart) and expires by TTL, so very old replies are answered as fresh.
- Follow-ups send prior turns as input tokens, increasing per-call cost; the turn
  window bounds this and it's still counted by the daily budget (ADR-0006/0013).
