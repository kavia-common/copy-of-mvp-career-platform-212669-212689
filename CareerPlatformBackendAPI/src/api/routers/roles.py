from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import get_settings
from src.core.security import get_current_user
from src.db.session import get_session
from src.models.role import Role
from src.repositories.roles import create_role as repo_create_role
from src.repositories.roles import list_roles as repo_list_roles
from src.repositories.roles import get_role_by_id
from src.schemas.role import RoleCreate, RoleRead

router = APIRouter(prefix="/api/v1/roles", tags=["Roles"])


def _to_role_read(entity: Role) -> RoleRead:
    """
    Helper to convert ORM Role (with metadata_ attribute) to RoleRead schema.
    """
    return RoleRead(
        id=entity.id,
        name=entity.name,
        description=entity.description,
        metadata=entity.metadata_,
        version=entity.version,
        source=entity.source,
        created_at=entity.created_at,
    )


class RoleSelection(BaseModel):
    """Payload to select current and target roles."""
    currentRoleId: str = Field(..., description="Current role identifier")
    targetRoleId: str = Field(..., description="Target role identifier")


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=RoleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a role",
    description="Create a new role record in the database.",
    responses={
        201: {"description": "Role created successfully"},
        409: {"description": "A role with this id already exists"},
    },
)
async def create_role(
    payload: RoleCreate,
    session: AsyncSession = Depends(get_session),
) -> RoleRead:
    """
    Create a role.

    Args:
        payload: RoleCreate schema including required name and optional id/description/metadata/version/source.
        session: Async SQLAlchemy session.

    Returns:
        The created role.

    Raises:
        HTTPException 409: if a role with the provided id already exists.
    """
    try:
        role = await repo_create_role(session, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return _to_role_read(role)


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[RoleRead],
    summary="List roles",
    description="Retrieve all roles, with optional case-insensitive filtering on name/description.",
    responses={200: {"description": "List of roles"}},
)
async def list_roles(
    q: Optional[str] = Query(default=None, description="Optional case-insensitive search on name or description"),
    session: AsyncSession = Depends(get_session),
) -> List[RoleRead]:
    """
    List roles with optional filtering.

    Args:
        q: Optional case-insensitive filter substring.
        session: Async SQLAlchemy session.

    Returns:
        List of roles.
    """
    items = await repo_list_roles(session, q)
    return [_to_role_read(it) for it in items]


# PUBLIC_INTERFACE
@router.post(
    "/seed",
    response_model=RoleRead,
    summary="Seed a sample role",
    description="Insert a sample role for verification. Guarded by ALLOW_SEED_ENDPOINT=true.",
    responses={
        200: {"description": "Seeded (or existing) role returned"},
        403: {"description": "Seeding is disabled"},
    },
)
async def seed_role(
    session: AsyncSession = Depends(get_session),
    settings=Depends(get_settings),
) -> RoleRead:
    """
    Seed a sample role for simple verification of persistence.

    Requires environment variable ALLOW_SEED_ENDPOINT=true (or 1/yes/on).
    Returns the existing role if already present.
    """
    if not settings.ALLOW_SEED_ENDPOINT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Seeding is disabled")

    sample_id = "sample-cto-role"
    existing = await get_role_by_id(session, sample_id)
    if existing:
        return _to_role_read(existing)

    role = await repo_create_role(
        session,
        RoleCreate(
            id=sample_id,
            name="Chief Technology Officer",
            description="Executive role responsible for overall technology strategy and execution.",
            metadata={"seed": True, "area": "Executive"},
            version="v1",
            source="seed",
        ),
    )
    return _to_role_read(role)


# PUBLIC_INTERFACE
@router.post(
    "/select",
    summary="Select current and target roles",
    description="Validate and record role selection (MVP does not persist; audits only).",
)
async def select_roles(
    payload: RoleSelection,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
) -> dict:
    """
    Validate that both roles exist and return a simple confirmation.
    """
    src = await get_role_by_id(session, payload.currentRoleId)
    dst = await get_role_by_id(session, payload.targetRoleId)
    if not src or not dst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    # No persistence for MVP; the frontend should pass the selection to subsequent calls.
    return {"status": "ok", "currentRoleId": payload.currentRoleId, "targetRoleId": payload.targetRoleId}
