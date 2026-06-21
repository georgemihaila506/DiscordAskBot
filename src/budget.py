"""Daily global token budget, persisted across restarts.

A per-day token counter that resets at UTC midnight. Once the day's used tokens
reach ``config.DAILY_TOKEN_BUDGET`` the bot stops answering until the next day.
State is saved to ``config.BUDGET_FILE`` (JSON) so a restart doesn't wipe the
day's accounting. Writes are atomic (tmp file + rename).
"""

import json
import os
from datetime import datetime, timezone

from src import config

_day: str | None = None   # UTC date, ISO string e.g. "2026-06-21"
_used = 0
_loaded = False


def _today_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _load() -> None:
    global _day, _used, _loaded
    _loaded = True
    try:
        with open(config.BUDGET_FILE, encoding="utf-8") as f:
            data = json.load(f)
        _day = data.get("date")
        _used = int(data.get("used", 0))
    except (FileNotFoundError, ValueError, OSError):
        _day, _used = None, 0


def _save() -> None:
    path = config.BUDGET_FILE
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"date": _day, "used": _used}, f)
    os.replace(tmp, path)


def _roll_if_new_day() -> None:
    """Load on first use, then reset (and persist) when the UTC date changes."""
    global _day, _used
    if not _loaded:
        _load()
    today = _today_iso()
    if _day != today:
        _day, _used = today, 0
        _save()


def is_over_budget() -> bool:
    _roll_if_new_day()
    return _used >= config.DAILY_TOKEN_BUDGET


def add_usage(input_tokens: int, output_tokens: int) -> None:
    global _used
    _roll_if_new_day()
    _used += input_tokens + output_tokens
    _save()


def used() -> int:
    _roll_if_new_day()
    return _used


def remaining() -> int:
    _roll_if_new_day()
    return max(0, config.DAILY_TOKEN_BUDGET - _used)
