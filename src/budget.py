"""Daily global token budget.

A simple in-memory counter that resets at UTC midnight. Once the day's used
tokens reach ``config.DAILY_TOKEN_BUDGET`` the bot stops answering until the
next day. In-memory means a restart resets the count — acceptable for a small
personal bot; swap in a JSON/sqlite file if durable accounting is ever needed.
"""

from datetime import date, datetime, timezone

from src import config

_day: date | None = None
_used = 0


def _roll_if_new_day() -> None:
    """Reset the counter when the UTC date changes."""
    global _day, _used
    today = datetime.now(timezone.utc).date()
    if _day != today:
        _day = today
        _used = 0


def is_over_budget() -> bool:
    _roll_if_new_day()
    return _used >= config.DAILY_TOKEN_BUDGET


def add_usage(input_tokens: int, output_tokens: int) -> None:
    global _used
    _roll_if_new_day()
    _used += input_tokens + output_tokens


def remaining() -> int:
    _roll_if_new_day()
    return max(0, config.DAILY_TOKEN_BUDGET - _used)
