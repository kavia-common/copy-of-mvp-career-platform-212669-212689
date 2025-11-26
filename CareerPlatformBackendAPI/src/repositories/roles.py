from __future__ import annotations

from typing import List, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.role import Role
from src.schemas.role import RoleCreate


# PUBLIC_INTERFACE
async def get_role_by_id(session: AsyncSession, role_id: str) -> Optional[Role]:
    """Return a role by its identifier or None if not found."""
    result = await session.execute(select(Role).where(Role.id == role_id))
    return result.scalars().first()


# PUBLIC_INTERFACE
async def list_roles(session: AsyncSession, q: Optional[str] = None) -> List[Role]:
    """List roles, optionally filtered by case-insensitive substring of name or description."""
    stmt = select(Role)
    if q:
        query = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Role.name).like(query),
                func.lower(Role.description).like(query),
            )
        )
    result = await session.execute(stmt)
    return list(result.scalars().all())


# PUBLIC_INTERFACE
async def create_role(session: AsyncSession, payload: RoleCreate) -> Role:
    """
    Create and persist a new role.

    Raises:
        ValueError: if a role with the provided id already exists.
    """
    # If client supplied an id, ensure no conflict
    if payload.id:
        existing = await get_role_by_id(session, payload.id)
        if existing:
            raise ValueError("Role with this id already exists")

    role = Role(
        id=payload.id,  # may be None -> default generator will run
        name=payload.name,
        description=payload.description,
        metadata_=payload.metadata,  # Note: ORM attribute is metadata_
        version=payload.version,
        source=payload.source,
    )
    session.add(role)
    await session.commit()
    await session.refresh(role)
    return role
