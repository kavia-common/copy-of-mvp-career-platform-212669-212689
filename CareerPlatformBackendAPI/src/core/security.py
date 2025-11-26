from __future__ import annotations

import datetime as dt
from typing import Any, Dict, Optional

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import get_settings
from src.db.session import get_session
from src.models.user import User

http_bearer = HTTPBearer(auto_error=False)


# PUBLIC_INTERFACE
def create_access_token(
    subject: str,
    claims: Optional[Dict[str, Any]] = None,
    expires_minutes: Optional[int] = None,
    settings=None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        subject: Subject identifier (typically the user id).
        claims: Additional claims to include in the token.
        expires_minutes: Override expiration in minutes (defaults to settings).
        settings: Optional settings override, for testability.

    Returns:
        Encoded JWT string.
    """
    settings = settings or get_settings()
    now = dt.datetime.utcnow()
    exp_minutes = expires_minutes if expires_minutes is not None else settings.JWT_EXPIRE_MINUTES
    payload: Dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "nbf": now,
        "exp": now + dt.timedelta(minutes=exp_minutes),
        "iss": settings.JWT_ISSUER,
    }
    if claims:
        payload.update(claims)
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


# PUBLIC_INTERFACE
async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    Dependency that validates a Bearer token and returns the corresponding User.

    This uses HS256 JWT with a shared secret from env. For the MVP, password
    verification is not persisted in the DB; register/login issue a token for
    an existing user by email.

    Raises:
        HTTPException 401: if token is missing/invalid or user not found.
    """
    settings = get_settings()
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM], issuer=settings.JWT_ISSUER)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: missing subject")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidIssuerError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token issuer")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Load user
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
