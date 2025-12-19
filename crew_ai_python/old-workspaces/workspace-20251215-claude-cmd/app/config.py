"""Application configuration settings."""

import os
from typing import Optional


class Settings:
    """Application settings loaded from environment variables."""

    SECRET_KEY: str = os.getenv("SECRET_KEY", "pixelpet-secret-key-change-in-production")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./pixelpet.db")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    ALGORITHM: str = "HS256"

    # Pet configuration
    VALID_SPECIES: list[str] = ["otter", "cat", "dragon", "axolotl"]
    INITIAL_STAT_VALUE: int = 50
    MAX_STAT_VALUE: int = 100
    MIN_STAT_VALUE: int = 0

    # Sleep duration in minutes
    SLEEP_DURATION_MINUTES: int = 2

    # Evolution requirements
    EVOLUTION_THRESHOLD: int = 50
    EVOLUTION_TIME_MINUTES: int = 5


settings = Settings()
