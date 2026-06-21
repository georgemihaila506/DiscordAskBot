"""Splitting answers to fit Discord's 2000-char message limit.

Pure, Discord-free helpers so the boundary logic can be unit-tested on plain
strings. The streaming orchestration that *uses* these lives in bot.py.
"""

DISCORD_CHAR_LIMIT = 2000


def split_index(text: str, limit: int = DISCORD_CHAR_LIMIT) -> int:
    """Return how many chars of ``text`` belong in the first chunk (<= limit).

    Prefer a natural boundary inside the limit, in order of niceness:
    paragraph break, then line break, then a space. Only accept a boundary in
    the second half of the window, so we never emit a tiny chunk; otherwise hard
    cut at the limit.
    """
    if len(text) <= limit:
        return len(text)
    window = text[:limit]
    for sep in ("\n\n", "\n", " "):
        idx = window.rfind(sep)
        if idx >= limit // 2:
            return idx + len(sep)
    return limit


def split_all(text: str, limit: int = DISCORD_CHAR_LIMIT) -> list[str]:
    """Split ``text`` into a list of chunks, each <= limit, on good boundaries."""
    chunks: list[str] = []
    remaining = text
    while len(remaining) > limit:
        cut = split_index(remaining, limit)
        chunks.append(remaining[:cut])
        remaining = remaining[cut:]
    if remaining:
        chunks.append(remaining)
    return chunks
