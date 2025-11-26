from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Shared properties for User."""
    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., description="Full name of the user")
    roles: List[str] = Field(default_factory=list, description="Assigned role identifiers")


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
