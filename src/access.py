"""Access controls: guild allowlist + per-user cooldown.

Both are configured via env (see config). The allowlist restricts which servers
may use the bot (empty = all). The cooldown enforces a minimum gap between one
user's requests (0 = off), complementing the one-in-flight guard (inflight.py).
"""

import time

from src import config

_last_use: dict[int, float] = {}


def check(guild_id: int | None, user_id: int) -> str | None:
    """Return a user-facing rejection message, or None if the request may proceed."""
    if config.ALLOWED_GUILD_IDS and guild_id not in config.ALLOWED_GUILD_IDS:
        return "🚫 This bot isn't enabled here."
    if config.USER_COOLDOWN_SECONDS > 0:
        last = _last_use.get(user_id)
        if last is not None:
            wait = config.USER_COOLDOWN_SECONDS - (time.monotonic() - last)
            if wait > 0:
                return f"⏱️ Slow down — try again in {wait:.0f}s."
    return None


def record(user_id: int) -> None:
    """Mark that a user just made a request (starts their cooldown)."""
    _last_use[user_id] = time.monotonic()
