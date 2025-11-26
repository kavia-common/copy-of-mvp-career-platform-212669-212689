from __future__ import annotations

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import make_url

from src.core.config import get_settings

_settings = get_settings()

# Ensure the data directory exists if using a SQLite URL
try:
    url = make_url(_settings.DATABASE_URL)
    if url.drivername.startswith("sqlite") and url.database:
        db_dir = os.path.dirname(url.database)
        if db_dir:  # may be empty for in-memory DBs
            os.makedirs(db_dir, exist_ok=True)
except Exception:
    # Fail open: if parsing fails, we won't try to create directories
    pass

# Create an async engine for SQLite (aiosqlite driver)
_async_engine: AsyncEngine = create_async_engine(
    _settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    future=True,
)


# PUBLIC_INTERFACE
def get_engine() -> AsyncEngine:
    """Return the configured Async SQLAlchemy engine instance."""
    return _async_engine


# Configure AsyncSession factory
_async_session_factory = sessionmaker(
    bind=_async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# PUBLIC_INTERFACE
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an AsyncSession bound to the configured engine.

    Yields:
        AsyncSession: an async SQLAlchemy session.
    """
    async with _async_session_factory() as session:
        try:
            yield session
        finally:
            # Session context manager will handle close
            ...
