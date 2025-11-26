from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

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
    description="Central backend service for the MVP Career Platform. Defaults to SQLite (async via aiosqlite). PostgreSQL configuration is disabled for this migration.",
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

logger = logging.getLogger(__name__)


@app.on_event("startup")
async def on_startup() -> None:
    """
    Initialize application components on startup.

    - Creates DB tables if they do not exist (no Alembic migrations in MVP).
    - Performs a lightweight self-check against SQLite: create+list+cleanup a temp role.
    """
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Lightweight self-check: create and list roles
    try:
        async_session = sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
        async with async_session() as session:
            from src.models.role import Role

            test_id = "__startup_self_check__"
            created = False

            # Create a temporary role if it's not present
            result = await session.execute(select(Role).where(Role.id == test_id))
            existing = result.scalars().first()
            if not existing:
                session.add(
                    Role(
                        id=test_id,
                        name="Startup Self-Check",
                        description="Temporary record to verify DB connectivity.",
                        metadata_={"self_check": True},
                        version="check",
                        source="startup",
                    )
                )
                await session.commit()
                created = True

            # List roles to ensure read path works
            result = await session.execute(select(Role))
            roles_count = len(result.scalars().all())
            logger.info("DB self-check OK: roles_count=%s created=%s", roles_count, created)

            # Cleanup temp record if we created it
            if created:
                result = await session.execute(select(Role).where(Role.id == test_id))
                entity = result.scalars().first()
                if entity:
                    await session.delete(entity)
                    await session.commit()

    except Exception as exc:  # pragma: no cover - startup guard
        logger.warning("DB self-check failed: %s", exc)


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
