from __future__ import annotations

from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.role_competency import RoleCompetency
from src.schemas.role_competency import RoleCompetencyCreate


# PUBLIC_INTERFACE
async def get_role_competency(session: AsyncSession, role_id: str, competency_id: str) -> Optional[RoleCompetency]:
    """Return a RoleCompetency mapping for the given role and competency, or None if not found."""
    stmt = select(RoleCompetency).where(
        and_(RoleCompetency.role_id == role_id, RoleCompetency.competency_id == competency_id)
    )
    result = await session.execute(stmt)
    return result.scalars().first()


# PUBLIC_INTERFACE
async def list_role_competencies_for_role(session: AsyncSession, role_id: str) -> List[RoleCompetency]:
    """List RoleCompetency mappings for a given role."""
    result = await session.execute(select(RoleCompetency).where(RoleCompetency.role_id == role_id))
    return list(result.scalars().all())


# PUBLIC_INTERFACE
async def create_role_competency(session: AsyncSession, payload: RoleCompetencyCreate) -> RoleCompetency:
    """
    Create and persist a RoleCompetency mapping.

    Raises:
        ValueError: if a mapping for (role_id, competency_id) already exists.
    """
    existing = await get_role_competency(session, payload.role_id, payload.competency_id)
    if existing:
        raise ValueError("Mapping for this role and competency already exists")

    entity = RoleCompetency(
        id=payload.id,  # may be None -> default generator will run
        role_id=payload.role_id,
        competency_id=payload.competency_id,
        required_level=payload.required_level,
        weight=payload.weight,
        notes=payload.notes,
        metadata_=payload.metadata,
    )
    session.add(entity)
    await session.commit()
    await session.refresh(entity)
    return entity
