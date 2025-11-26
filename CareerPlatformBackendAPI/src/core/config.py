import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

# Load .env if present
load_dotenv()


def _normalize_to_asyncpg(url: str) -> str:
    """
    Normalize a PostgreSQL URL to use the asyncpg driver for SQLAlchemy async engine.
    Accepts postgres:// or postgresql:// and converts to postgresql+asyncpg://
    """
    if not url:
        return url
    if url.startswith("postgres://"):
        return "postgresql+asyncpg://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url[len("postgresql://") :]
    # leave other schemes (e.g., sqlite+aiosqlite) unchanged
    return url


def _build_database_url() -> str:
    """
    Build the database URL with the following precedence (SQLite-first migration):
    1) DATABASE_URL if provided and using SQLite; normalizes "sqlite://" to "sqlite+aiosqlite://"
    2) Fallback to bundled SQLite file (aiosqlite) at ./data/app.db

    NOTE: PostgreSQL-specific environment variables (POSTGRES_URL, POSTGRES_*) are intentionally ignored
    in this migration to avoid accidental connections to unavailable Postgres instances.
    """
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        # Normalize sqlite scheme for async usage
        if env_url.startswith("sqlite+aiosqlite://"):
            return env_url
        if env_url.startswith("sqlite://"):
            return "sqlite+aiosqlite://" + env_url[len("sqlite://") :]
        # Non-sqlite URLs are ignored in this SQLite-first deployment
        # to ensure the app always starts without external DB dependencies.

    # Default to local SQLite file inside data/
    return "sqlite+aiosqlite:///./data/app.db"


def _env_flag(name: str, default: bool = False) -> bool:
    """Parse a boolean environment variable."""
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on", "y"}


@dataclass
class Settings:
    """Application settings loaded from environment variables."""
    DATABASE_URL: str = _build_database_url()
    APP_NAME: str = os.getenv("APP_NAME", "MVP Career Platform Backend")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    ALLOW_SEED_ENDPOINT: bool = _env_flag("ALLOW_SEED_ENDPOINT", False)


# PUBLIC_INTERFACE
@lru_cache
def get_settings() -> Settings:
    """Return the application settings as a cached singleton instance."""
    return Settings()
