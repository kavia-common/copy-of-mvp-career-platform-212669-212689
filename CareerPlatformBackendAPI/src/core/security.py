from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import secrets
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

# Password hashing defaults (PBKDF2-HMAC-SHA256)
_PBKDF2_ALG = "sha256"
_PBKDF2_ITERATIONS = 260_000
_SALT_BYTES = 16


# PUBLIC_INTERFACE
def hash_password(password: str, iterations: int = _PBKDF2_ITERATIONS) -> str:
    """Return a salted PBKDF2-HMAC-SHA256 hash for the given password.

    Stored format:
        pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>
    """
    if not isinstance(password, str) or password == "":
        raise ValueError("Password must be a non-empty string")

    salt = secrets.token_bytes(_SALT_BYTES)
    dk = hashlib.pbkdf2_hmac(_PBKDF2_ALG, password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${dk.hex()}"


# PUBLIC_INTERFACE
def verify_password(password: str, password_hash: Optional[str]) -> bool:
    """Verify a plaintext password against a stored PBKDF2 salted hash."""
    if not password_hash or not isinstance(password_hash, str):
        return False

    try:
        scheme, iter_str, salt_hex, hash_hex = password_hash.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        iterations = int(iter_str)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
    except Exception:
        return False

    candidate = hashlib.pbkdf2_hmac(_PBKDF2_ALG, password.encode("utf-8"), salt, iterations)
    # Constant-time comparison
    return hmac.compare_digest(candidate, expected)


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

    This uses HS256 JWT with a shared secret from env. Passwords are stored as
    salted PBKDF2 hashes on the User model.
    Raises:
        HTTPException 401: if token is missing/invalid or user not found.
    """
    settings = get_settings()
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM], issuer=settings.JWT_ISSUER
        )
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
