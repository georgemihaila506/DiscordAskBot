# 0002 — `/ask` slash command is the only interface

- **Status:** Amended by [ADR-0012](0012-reply-to-continue-memory.md) (2026-06-21) —
  the bot now also listens for replies to its answers; slash commands remain the
  primary entry point.
- **Date:** 2026-06-21

## Context

Discord bots can be invoked several ways: a slash command, an @mention, replying
to every message in a channel, or DMs. Each implies different message-handling
code and different "when should I respond?" ambiguity.

## Decision

Expose a single `/ask <question>` slash command. No mention-listening, no
DM handling, no reacting to ordinary channel messages.

## Consequences

- Explicit and discoverable (Discord's command picker shows it); zero ambiguity
  about when the bot fires.
- No need for the privileged message-content intent — keeps the permission
  surface minimal (see ADR-0004's `Intents.none()`).
- Users can't "chat" with it conversationally; every interaction is one command.
  Acceptable given the stateless design (ADR-0003).
