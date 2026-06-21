"""One-in-flight-per-user guard.

Tracks which users currently have an ``/ask`` being answered, so a second
concurrent request from the same user can be rejected. In-memory only — a
restart clears it, which is fine (nothing is in flight after a restart).
"""

_active: set[int] = set()


def is_active(user_id: int) -> bool:
    return user_id in _active


def begin(user_id: int) -> None:
    _active.add(user_id)


def end(user_id: int) -> None:
    _active.discard(user_id)
