from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Response
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import create_access_token, get_current_user, hash_password, verify_password
from src.db.session import get_session
from src.models.user import User
from src.schemas.user import UserRead

# Primary auth router (versioned under /api/v1/auth)
router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])
# Public/legacy-compatibility router (versioned under /api/v1 without /auth segment)
# This aligns with some frontend clients that call /api/v1/login and /api/v1/register directly.
router_public = APIRouter(prefix="/api/v1", tags=["Auth"])


class RegisterRequest(BaseModel):
    """Registration payload for a new user."""
    email: EmailStr = Field(..., description="Email address")
    name: str = Field(..., description="Full name")
    password: str = Field(..., description="Password (stored as salted hash; never returned)")


class LoginRequest(BaseModel):
    """
    Login payload for authentication.

    Requires email and password.
    """
    # Make fields optional to allow custom 400 handling for missing fields (avoids FastAPI 422).
    email: EmailStr | None = Field(None, description="Email address")
    password: str | None = Field(None, description="Password")


class TokenResponse(BaseModel):
    """JWT response for successful authentication."""
    token: str = Field(..., description="Bearer token (JWT)")


# PUBLIC_INTERFACE
@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Register a new user account with name, email, and password. The password is stored as a salted hash and is never returned.",
)
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_session)) -> UserRead:
    """
    Create a user if it does not exist. Enforces email uniqueness.

    Returns:
        The created user (sans password).
    Raises:
        HTTPException 409 if email already exists.
    """
    exists_stmt = select(User).where(func.lower(User.email) == payload.email.lower())
    result = await session.execute(exists_stmt)
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    pwd_hash = hash_password(payload.password)
    user = User(email=payload.email, name=payload.name, roles=[], password_hash=pwd_hash)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


# PUBLIC_INTERFACE
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Login with email and password, and receive a JWT.",
    responses={
        200: {"description": "JWT token issued"},
        400: {"description": "Invalid request (email or password missing)"},
        401: {"description": "Invalid credentials"},
    },
)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    """
    Issue a JWT for the email if the user exists and password is valid.

    Args:
        payload: LoginRequest with email and password.

    Returns:
        TokenResponse containing a signed JWT.

    Raises:
        HTTPException 400: if email or password is missing.
        HTTPException 401: if credentials are invalid.
    """
    # Validate required fields explicitly to return 400 (not 422)
    if not payload.email or not payload.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email and password are required")

    stmt = select(User).where(func.lower(User.email) == payload.email.lower())
    result = await session.execute(stmt)
    user = result.scalars().first()
    if not user or not verify_password(payload.password, user.password_hash):
        # Do not leak which part failed; use 401 Unauthorized for bad credentials
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=user.id, claims={"email": user.email, "roles": user.roles})
    return TokenResponse(token=token)


# PUBLIC_INTERFACE
@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="User logout",
    description="Stateless logout. Clients should discard the token.",
)
async def logout(_: User = Depends(get_current_user)) -> Response:
    """
    Stateless logout. There is no server-side session in the MVP.

    Clients should simply discard stored tokens.
    """
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ----- Legacy/alias routes to avoid 404 when clients call /api/v1/* directly ----- #

# PUBLIC_INTERFACE
@router_public.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user (alias)",
    description="Alias for /api/v1/auth/register to support clients calling /api/v1/register.",
)
async def register_alias(payload: RegisterRequest, session: AsyncSession = Depends(get_session)) -> UserRead:
    """
    Alias wrapper that delegates to the /api/v1/auth/register handler.
    """
    return await register(payload, session)  # type: ignore[arg-type]


# PUBLIC_INTERFACE
@router_public.post(
    "/login",
    response_model=TokenResponse,
    summary="User login (alias)",
    description="Alias for /api/v1/auth/login to support clients calling /api/v1/login.",
    responses={
        200: {"description": "JWT token issued"},
        400: {"description": "Invalid request (email or password missing)"},
        401: {"description": "Invalid credentials"},
    },
)
async def login_alias(payload: LoginRequest, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    """
    Alias wrapper that delegates to the /api/v1/auth/login handler.
    """
    return await login(payload, session)  # type: ignore[arg-type]


# PUBLIC_INTERFACE
@router_public.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="User logout (alias)",
    description="Alias for /api/v1/auth/logout to support clients calling /api/v1/logout.",
)
async def logout_alias(_: User = Depends(get_current_user)) -> Response:
    """
    Alias wrapper for stateless logout.
    """
    return await logout(_)  # type: ignore[misc]
