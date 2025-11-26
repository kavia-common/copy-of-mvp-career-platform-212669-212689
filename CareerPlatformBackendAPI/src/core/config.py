import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

# Load .env if present
load_dotenv()


@dataclass
class Settings:
    """Application settings loaded from environment variables."""
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/app.db")
    APP_NAME: str = os.getenv("APP_NAME", "MVP Career Platform Backend")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")


# PUBLIC_INTERFACE
@lru_cache
def get_settings() -> Settings:
    """Return the application settings as a cached singleton instance."""
    return Settings()
