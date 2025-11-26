from __future__ import annotations

from typing import List, Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.role_adjacency import RoleAdjacency
from src.schemas.role_adjacency import RoleAdjacencyCreate


# PUBLIC_INTERFACE
async def get_role_adjacency(session: AsyncSession, source_role_id: str, target_role_id: str) -> Optional[RoleAdjacency]:
    """Return a RoleAdjacency mapping from source to target, or None if not found."""
    stmt = select(RoleAdjacency).where(
        and_(RoleAdjacency.source_role_id == source_role_id, RoleAdjacency.target_role_id == target_role_id)
    )
    result = await session.execute(stmt)
    return result.scalars().first()


# PUBLIC_INTERFACE
async def list_outgoing_role_adjacencies(session: AsyncSession, role_id: str) -> List[RoleAdjacency]:
    """List all adjacencies outgoing from the given role."""
    result = await session.execute(select(RoleAdjacency).where(RoleAdjacency.source_role_id == role_id))
    return list(result.scalars().all())


# PUBLIC_INTERFACE
async def list_incoming_role_adjacencies(session: AsyncSession, role_id: str) -> List[RoleAdjacency]:
    """List all adjacencies incoming to the given role."""
    result = await session.execute(select(RoleAdjacency).where(RoleAdjacency.target_role_id == role_id))
    return list(result.scalars().all())


# PUBLIC_INTERFACE
async def list_role_adjacencies_bidirectional(session: AsyncSession, role_id: str) -> List[RoleAdjacency]:
    """List all adjacencies that involve the given role in either direction."""
    stmt = select(RoleAdjacency).where(
        or_(RoleAdjacency.source_role_id == role_id, RoleAdjacency.target_role_id == role_id)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


# PUBLIC_INTERFACE
async def create_role_adjacency(session: AsyncSession, payload: RoleAdjacencyCreate) -> RoleAdjacency:
    """
    Create and persist a RoleAdjacency mapping.

    Raises:
        ValueError: if an adjacency for (source_role_id, target_role_id) already exists.
    """
    existing = await get_role_adjacency(session, payload.source_role_id, payload.target_role_id)
    if existing:
        raise ValueError("Adjacency for this source/target already exists")

    entity = RoleAdjacency(
        id=payload.id,  # may be None -> default generator will run
        source_role_id=payload.source_role_id,
        target_role_id=payload.target_role_id,
        strength=payload.strength,
        rationale=payload.rationale,
        metadata_=payload.metadata,
    )
    session.add(entity)
    await session.commit()
    await session.refresh(entity)
    return entity
