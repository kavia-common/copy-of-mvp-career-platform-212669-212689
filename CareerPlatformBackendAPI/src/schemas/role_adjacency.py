from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class RoleAdjacencyBase(BaseModel):
    """Shared properties for RoleAdjacency."""
    source_role_id: str = Field(..., description="Source role identifier")
    target_role_id: str = Field(..., description="Target role identifier")
    strength: Optional[float] = Field(None, description="Normalized strength/likelihood (0..1)")
    rationale: Optional[str] = Field(None, description="Optional explanation")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Arbitrary metadata for the adjacency")


class RoleAdjacencyCreate(RoleAdjacencyBase):
    """Schema for creating a role adjacency."""
    id: Optional[str] = Field(None, description="Optional client-supplied identifier (UUID or text). If omitted, server generates.")


class RoleAdjacencyRead(RoleAdjacencyBase):
    """Schema for reading a role adjacency."""
    id: str = Field(..., description="Identifier of the adjacency")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")

    model_config = {"from_attributes": True}
