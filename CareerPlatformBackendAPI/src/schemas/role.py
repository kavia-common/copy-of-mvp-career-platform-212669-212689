from __future__ import annotations

from typing import Any, Dict, Optional
from datetime import datetime

from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    """Shared properties for Role."""
    name: str = Field(..., description="Unique display name of the role")
    description: Optional[str] = Field(None, description="Optional description of the role")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Arbitrary metadata for the role (JSONB/JSON)")
    version: Optional[str] = Field(None, description="Optional version identifier for the role definition")
    source: Optional[str] = Field(None, description="Optional source or origin of this role")


class RoleCreate(RoleBase):
    """Schema for creating a new role."""
    id: Optional[str] = Field(None, description="Optional client-supplied identifier (UUID or text). If omitted, server generates.")


class RoleRead(RoleBase):
    """Schema for reading back a stored role."""
    id: str = Field(..., description="Identifier of the role (UUID or text)")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")

    model_config = {
        "from_attributes": True
    }
