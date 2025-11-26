from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session
from src.models.user import User
from src.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user",
    responses={
        201: {"description": "User created successfully"},
        409: {"description": "A user with this email already exists"},
    },
)
async def create_user(payload: UserCreate, session: AsyncSession = Depends(get_session)) -> UserRead:
    """
    Create a new user.

    This endpoint demonstrates write operations on SQLite via SQLAlchemy (async).
    Application-side uniqueness is enforced to avoid relying on ON CONFLICT specifics.

    Args:
        payload: UserCreate schema containing email, name, and roles.
        session: Async database session.

    Returns:
        The created User.
    """
    # SQLite-safe uniqueness check (avoid ON CONFLICT usage)
    exists_stmt = select(User).where(func.lower(User.email) == payload.email.lower())
    result = await session.execute(exists_stmt)
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(email=payload.email, name=payload.name, roles=payload.roles or [])
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[UserRead],
    summary="List users",
    responses={200: {"description": "List of users"}},
)
async def list_users(
    q: Optional[str] = Query(default=None, description="Optional case-insensitive search on email or name"),
    session: AsyncSession = Depends(get_session),
) -> List[UserRead]:
    """
    Retrieve users, optionally filtering by a case-insensitive query string.

    Uses lower() LIKE instead of ILIKE for portability to SQLite.

    Args:
        q: Optional case-insensitive search term.
        session: Async database session.

    Returns:
        A list of User objects.
    """
    stmt = select(User)
    if q:
        query = f"%{q.lower()}%"
        stmt = stmt.where(or_(func.lower(User.email).like(query), func.lower(User.name).like(query)))

    result = await session.execute(stmt)
    return list(result.scalars().all())


# PUBLIC_INTERFACE
@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Get user by ID",
    responses={200: {"description": "User found"}, 404: {"description": "User not found"}},
)
async def get_user(user_id: str, session: AsyncSession = Depends(get_session)) -> UserRead:
    """
    Retrieve a user by ID.

    Args:
        user_id: UUID string identifier for the user.
        session: Async database session.

    Returns:
        The matching User.

    Raises:
        HTTPException 404 if not found.
    """
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
