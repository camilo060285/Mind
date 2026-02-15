"""Global configuration for Mind."""

import os


class Settings:
    """Global configuration for Mind."""

    DEBUG = os.getenv("MIND_DEBUG", "0").lower() in {"1", "true", "yes"}
    LOG_LEVEL = os.getenv("MIND_LOG_LEVEL", "INFO").upper()
