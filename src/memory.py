"""Conversation memory for reply-to-continue follow-ups.

Maps each answer's Discord message id -> the conversation that produced it (the
list of prior {role, content} turns, including that answer). When a user replies
to any of the bot's answer messages, we look the conversation up and continue it.

In-memory only (cleared on restart, which is fine — there's nothing to continue
after a restart). Bounded three ways: a per-conversation turn window
(HISTORY_MAX_MESSAGES), an idle TTL (MEMORY_TTL_MINUTES), and a cap on the number
of stored conversations (MEMORY_MAX_CONVERSATIONS, oldest evicted first).
"""

import time

from src import config

# message_id -> (conversation: list[{role, content}], last_active_monotonic)
_store: dict[int, tuple[list[dict], float]] = {}


def _ttl_seconds() -> float:
    return config.MEMORY_TTL_MINUTES * 60


def get(message_id: int) -> list[dict]:
    """Return the conversation for a replied-to message id, or [] if none/expired."""
    entry = _store.get(message_id)
    if entry is None:
        return []
    conversation, last_active = entry
    if time.monotonic() - last_active > _ttl_seconds():
        _store.pop(message_id, None)
        return []
    return conversation


def put(message_ids: list[int], conversation: list[dict]) -> None:
    """Store ``conversation`` under every message id the answer spans.

    The conversation is trimmed to the most recent HISTORY_MAX_MESSAGES turns so
    follow-ups stay bounded in tokens.
    """
    trimmed = conversation[-config.HISTORY_MAX_MESSAGES:]
    now = time.monotonic()
    for mid in message_ids:
        _store[mid] = (trimmed, now)
    _evict_expired_and_overflow()


def _evict_expired_and_overflow() -> None:
    now = time.monotonic()
    ttl = _ttl_seconds()
    # Drop expired entries.
    for mid in [m for m, (_, ts) in _store.items() if now - ts > ttl]:
        _store.pop(mid, None)
    # Enforce the size cap, evicting least-recently-active first.
    if len(_store) > config.MEMORY_MAX_CONVERSATIONS:
        for mid, _ in sorted(_store.items(), key=lambda kv: kv[1][1])[
            : len(_store) - config.MEMORY_MAX_CONVERSATIONS
        ]:
            _store.pop(mid, None)
