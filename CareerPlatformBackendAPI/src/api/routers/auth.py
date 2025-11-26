from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import create_access_token, get_current_user
from src.db.session import get_session
from src.models.user import User
from src.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    """Login payload for MVP authentication (password not persisted/validated)."""
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password (ignored for MVP)")


class TokenResponse(BaseModel):
    """JWT response for successful authentication."""
    token: str = Field(..., description="Bearer token (JWT)")


# PUBLIC_INTERFACE
@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Register a new user account. Password handling is not persisted in the MVP; only email/name/roles.",
)
async def register(payload: UserCreate, session: AsyncSession = Depends(get_session)) -> UserRead:
    """
    Create a user if it does not exist. Enforces email uniqueness.
    """
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
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Login by email and receive a JWT. Password is accepted but not validated in MVP.",
)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    """
    Issue a JWT for the given email if the user exists.
    """
    result = await session.execute(
        select(User).where(func.lower(User.email) == payload.email.lower())
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=user.id, claims={"email": user.email, "roles": user.roles})
    return TokenResponse(token=token)


# PUBLIC_INTERFACE
@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="User logout",
    description="Stateless logout. Clients should discard the token.",
)
async def logout(_: User = Depends(get_current_user)) -> None:
    """
    No server-side session to invalidate in MVP. Clients should discard tokens.
    """
    return None
