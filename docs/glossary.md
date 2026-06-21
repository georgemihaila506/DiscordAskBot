# Glossary

Vocabulary for DiscordAskBot — the Discord and Anthropic terms the code leans on.

- **Slash command / application command** — a `/`-prefixed command registered with
  Discord; what users invoke. Here there's exactly one: `/ask`.
- **Interaction** — the event Discord sends when a user runs a command. Must be
  acknowledged within ~3 seconds or Discord shows "the application did not respond."
- **Defer** — acknowledging an interaction with a "thinking…" placeholder, which
  extends the window to respond to ~15 minutes. We defer because Claude takes longer
  than 3s.
- **Follow-up message** — a message sent (or edited) after a deferral. The streamed
  answer lives in one or more follow-up messages.
- **Ephemeral** — a reply only the invoking user can see ("only you can see this").
  Used here for guard/error notices (in-progress, budget spent), never for answers.
- **Intents** — Discord gateway permission flags declaring which events the bot
  receives. Kept minimal (`Intents.none()`); slash commands need no message-content intent.
- **Command sync** — registering the command tree with Discord. To a dev guild it's
  instant; global sync can take up to ~an hour to propagate. See `DEV_GUILD_ID`.
- **Gateway** — Discord's persistent WebSocket connection the bot logs into.
- **Streaming (Anthropic)** — receiving the answer as incremental token events
  (`text_stream`) rather than one final blob. Enables the typewriter effect.
- **`max_tokens`** — hard ceiling on a single answer's length (and so its cost).
- **Daily token budget** — running per-day token counter (`budget.py`); the bot stops
  answering once it's exceeded. Resets at UTC midnight.
- **In-flight guard** — the set of users with an active `/ask` (`inflight.py`); blocks
  a second concurrent request from the same user.
- **Chunking** — splitting an answer into ≤2000-char Discord messages on safe
  boundaries (`chunking.py`). Discord hard-caps a message at 2000 characters.
- **System prompt** — the persona/instructions sent to Claude on every call
  (`SYSTEM_PROMPT`).
- **Message Content Intent** — a *privileged* gateway intent that lets the bot
  read the text of messages. Required for reply-to-continue; toggle it on in Dev
  Portal → Bot → Privileged Gateway Intents.
- **Reply-to-continue** — replying to one of the bot's answers to ask a follow-up
  that carries the prior conversation as context (`on_message` + `memory.py`).
- **Conversation memory** — the in-memory map of answer message id → the
  conversation that produced it, bounded by a turn window, an idle TTL, and a
  size cap (`memory.py`).
- **Allowlist** — the set of server (guild) ids permitted to use the bot
  (`ALLOWED_GUILD_IDS`; empty = all). See `access.py`.
- **Cooldown** — a minimum gap enforced between one user's requests
  (`USER_COOLDOWN_SECONDS`; 0 = off). See `access.py`.
