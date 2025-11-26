from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers.users import router as users_router
from src.api.routers.roles import router as roles_router
from src.core.config import get_settings
from src.db.base import Base
from src.db.session import get_engine

# Import models for table registration with Base metadata
# (Create_all requires models imported before metadata operation)
import src.models.user  # noqa: F401
import src.models.role  # noqa: F401

settings = get_settings()

tags_metadata = [
    {"name": "Health", "description": "Health and service status"},
    {"name": "Users", "description": "Simple CRUD endpoints to validate DB data access"},
    {"name": "Roles", "description": "Manage role definitions persisted in the database"},
]

app = FastAPI(
    title=settings.APP_NAME,
    description="Central backend service for the MVP Career Platform. Uses PostgreSQL (async via asyncpg) if configured via env; falls back to SQLite (aiosqlite) otherwise.",
    version=settings.APP_VERSION,
    openapi_tags=tags_metadata,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    """
    Initialize application components on startup.

    - Creates DB tables if they do not exist (no Alembic migrations in MVP).
    """
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Cleanup on shutdown (dispose of DB engine)."""
    engine = get_engine()
    await engine.dispose()


# PUBLIC_INTERFACE
@app.get("/", summary="Health Check", tags=["Health"])
def health_check() -> dict:
    """Simple health check endpoint returning a basic status message."""
    return {"message": "Healthy"}


# Register routers
app.include_router(users_router)
app.include_router(roles_router)
