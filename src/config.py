"""Configuration loaded from environment variables (and a local .env file).

Import this module to read settings as constants, e.g. ``config.MODEL``.
Required values are validated at import time so the bot fails fast with a clear
message instead of crashing later on a ``None``.
"""

import os

from dotenv import load_dotenv

# Populate os.environ from a local .env file if present (no-op in production
# where the host injects real env vars).
load_dotenv()


def _required(name: str) -> str:
    """Return a required env var, or raise a clear error if it's missing/empty."""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


# --- Required ---
DISCORD_TOKEN: str = _required("DISCORD_TOKEN")
ANTHROPIC_API_KEY: str = _required("ANTHROPIC_API_KEY")

# --- Optional (with defaults) ---
MODEL: str = os.environ.get("MODEL", "claude-haiku-4-5")
MAX_TOKENS: int = int(os.environ.get("MAX_TOKENS", "1024"))
DAILY_TOKEN_BUDGET: int = int(os.environ.get("DAILY_TOKEN_BUDGET", "200000"))
SYSTEM_PROMPT: str = os.environ.get(
    "SYSTEM_PROMPT",
    "You are a concise, helpful assistant answering questions in a Discord "
    "server. Prefer clear, direct answers.",
)

# Optional dev-guild for instant slash-command sync; None means sync globally.
_dev_guild_raw = os.environ.get("DEV_GUILD_ID", "").strip()
DEV_GUILD_ID: int | None = int(_dev_guild_raw) if _dev_guild_raw else None


def _int_set(name: str) -> set[int]:
    """Parse a comma-separated list of ints from an env var (empty -> empty set)."""
    raw = os.environ.get(name, "").strip()
    return {int(part) for part in raw.split(",") if part.strip()}


# --- Access controls (v2) ---
# Empty set = allow all servers. Otherwise only these guild ids may use the bot.
ALLOWED_GUILD_IDS: set[int] = _int_set("ALLOWED_GUILD_IDS")
# Minimum seconds between a single user's requests (0 = no cooldown).
USER_COOLDOWN_SECONDS: int = int(os.environ.get("USER_COOLDOWN_SECONDS", "0"))

# --- Conversation memory (v2) ---
# Max turns (user+assistant messages) kept as context per conversation.
HISTORY_MAX_MESSAGES: int = int(os.environ.get("HISTORY_MAX_MESSAGES", "8"))
# Drop a conversation after this many minutes of inactivity.
MEMORY_TTL_MINUTES: int = int(os.environ.get("MEMORY_TTL_MINUTES", "60"))
# Cap on stored conversations; oldest are evicted past this.
MEMORY_MAX_CONVERSATIONS: int = int(os.environ.get("MEMORY_MAX_CONVERSATIONS", "500"))

# --- Persistence (v2) ---
# Where the daily token budget is persisted so it survives restarts.
BUDGET_FILE: str = os.environ.get("BUDGET_FILE", "data/budget.json")
