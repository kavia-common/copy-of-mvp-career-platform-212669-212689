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
    Build the database URL with the following precedence:
    1) DATABASE_URL (normalized to asyncpg for postgres)
    2) POSTGRES_URL (normalized to asyncpg)
    3) Discrete postgres env vars: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT
    4) Fallback to SQLite (aiosqlite)
    """
    # 1) Explicit DATABASE_URL
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return _normalize_to_asyncpg(env_url)

    # 2) Combined postgres URL
    pg_url = os.getenv("POSTGRES_URL")
    if pg_url:
        return _normalize_to_asyncpg(pg_url)

    # 3) Discrete vars
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    database = os.getenv("POSTGRES_DB")
    host = os.getenv("POSTGRES_HOST", "localhost")
    # Prefer configured container port, fallback to 5432 if not set
    port = os.getenv("POSTGRES_PORT", "5432")

    if user and password and database:
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"

    # 4) Fallback to SQLite
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
