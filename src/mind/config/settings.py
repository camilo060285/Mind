"""Global configuration for Mind."""

import os
from pathlib import Path


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


class Settings:
    """Global configuration for Mind."""

    DEBUG = os.getenv("MIND_DEBUG", "0").lower() in {"1", "true", "yes"}
    LOG_LEVEL = os.getenv("MIND_LOG_LEVEL", "INFO").upper()

    HISTORY_DIR = Path(os.getenv("MIND_HISTORY_DIR", str(Path.home() / ".mind")))
    HISTORY_FILE = HISTORY_DIR / "history.json"
    HISTORY_LIMIT = _int_env("MIND_HISTORY_LIMIT", 100)

    ANALYZE_MAX_CHARS = _int_env("MIND_ANALYZE_MAX_CHARS", 50000)
