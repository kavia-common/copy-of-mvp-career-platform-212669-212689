from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, field_validator

from src.core.config import get_settings


class UserBase(BaseModel):
    """Shared properties for User."""
    email: str = Field(..., description="User email string (relaxed; requires '@' unless STRICT_EMAIL_VALIDATION=true)")
    name: str = Field(..., description="Full name of the user")
    roles: List[str] = Field(default_factory=list, description="Assigned role identifiers")

    @field_validator("email")
    @classmethod
    def _validate_email(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("email must be a non-empty string")
        s = v.strip()
        settings = get_settings()
        if settings.STRICT_EMAIL_VALIDATION:
            try:
                from email_validator import validate_email  # type: ignore
                validate_email(s, check_deliverability=False)
            except Exception as e:
                raise ValueError("invalid email format") from e
        else:
            if "@" not in s:
                raise ValueError("email must contain '@' (relaxed validation)")
        return s


class UserCreate(UserBase):
    """Schema for creating a new user."""
    pass


class UserRead(UserBase):
    """Schema for reading back a stored user."""
    id: str = Field(..., description="UUID4 string identifier")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")

    model_config = {
        "from_attributes": True
    }
