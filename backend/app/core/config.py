"""
Application Configuration

Centralized configuration management using Pydantic's BaseSettings.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings."""

    APP_NAME: str = "Feedback Management System P2"
    APP_VERSION: str = "2.0.0"
    APP_DESCRIPTION: str = (
        "Feedback Management System with a Pandas-based ETL pipeline, "
        "analytics tables, and downloadable reports. Built with FastAPI, "
        "SQLAlchemy and SQLite."
    )
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///./feedback.db"
    SQL_ECHO: bool = False

    CORS_ALLOW_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance (singleton pattern)."""
    return Settings()


settings = get_settings()
