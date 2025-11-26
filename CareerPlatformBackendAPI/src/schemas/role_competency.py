from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class RoleCompetencyBase(BaseModel):
    """Shared properties for RoleCompetency mapping."""
    role_id: str = Field(..., description="Role identifier")
    competency_id: str = Field(..., description="Competency identifier")
    required_level: Optional[str] = Field(None, description="Required proficiency level")
    weight: Optional[float] = Field(None, description="Optional weight or importance factor")
    notes: Optional[str] = Field(None, description="Optional notes/rationale")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Arbitrary metadata for the mapping")


class RoleCompetencyCreate(RoleCompetencyBase):
    """Schema for creating a role->competency mapping."""
    id: Optional[str] = Field(None, description="Optional client-supplied identifier (UUID or text). If omitted, server generates.")


class RoleCompetencyRead(RoleCompetencyBase):
    """Schema for reading back a mapping."""
    id: str = Field(..., description="Identifier of the mapping")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")

    model_config = {"from_attributes": True}
