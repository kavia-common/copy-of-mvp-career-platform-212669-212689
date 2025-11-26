from __future__ import annotations

from typing import List, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.competency import Competency
from src.schemas.competency import CompetencyCreate


# PUBLIC_INTERFACE
async def get_competency_by_id(session: AsyncSession, competency_id: str) -> Optional[Competency]:
    """Return a competency by its identifier or None if not found."""
    result = await session.execute(select(Competency).where(Competency.id == competency_id))
    return result.scalars().first()


# PUBLIC_INTERFACE
async def list_competencies(session: AsyncSession, q: Optional[str] = None) -> List[Competency]:
    """List competencies, optionally filtered by case-insensitive substring of name or definition."""
    stmt = select(Competency)
    if q:
        query = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Competency.name).like(query),
                func.lower(Competency.definition).like(query),
            )
        )
    result = await session.execute(stmt)
    return list(result.scalars().all())


# PUBLIC_INTERFACE
async def create_competency(session: AsyncSession, payload: CompetencyCreate) -> Competency:
    """
    Create and persist a new competency.

    Raises:
        ValueError: if a competency with the provided id already exists.
    """
    if payload.id:
        existing = await get_competency_by_id(session, payload.id)
        if existing:
            raise ValueError("Competency with this id already exists")

    entity = Competency(
        id=payload.id,  # may be None -> default generator will run
        name=payload.name,
        definition=payload.definition,
        category=payload.category,
        metadata_=payload.metadata,
    )
    session.add(entity)
    await session.commit()
    await session.refresh(entity)
    return entity
