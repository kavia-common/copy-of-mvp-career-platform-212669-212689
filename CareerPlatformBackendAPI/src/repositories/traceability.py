from __future__ import annotations

from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.traceability import Traceability
from src.schemas.traceability import TraceabilityCreate


# PUBLIC_INTERFACE
async def get_traceability(session: AsyncSession, entity_type: str, entity_id: str) -> Optional[Traceability]:
    """Return a traceability entry for the given entity, or None if not found."""
    stmt = select(Traceability).where(
        and_(Traceability.entity_type == entity_type, Traceability.entity_id == entity_id)
    )
    result = await session.execute(stmt)
    return result.scalars().first()


# PUBLIC_INTERFACE
async def upsert_traceability(session: AsyncSession, payload: TraceabilityCreate) -> Traceability:
    """
    Create or update a traceability entry using application-side upsert (SQLite-safe).

    If an entry for (entity_type, entity_id) exists, it will be updated. Otherwise, a new one is created.
    """
    existing = await get_traceability(session, payload.entity_type, payload.entity_id)
    if existing:
        existing.source_documents = list(payload.source_documents or [])
        existing.metadata_ = payload.metadata
        await session.commit()
        await session.refresh(existing)
        return existing

    entity = Traceability(
        id=payload.id,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        source_documents=list(payload.source_documents or []),
        metadata_=payload.metadata,
    )
    session.add(entity)
    await session.commit()
    await session.refresh(entity)
    return entity
