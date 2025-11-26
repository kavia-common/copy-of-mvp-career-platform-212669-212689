from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class CompetencyBase(BaseModel):
    """Shared properties for Competency."""
    name: str = Field(..., description="Display name of the competency")
    definition: Optional[str] = Field(None, description="Optional description/definition")
    category: Optional[str] = Field(None, description="Optional category name")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Arbitrary metadata for the competency")


class CompetencyCreate(CompetencyBase):
    """Schema for creating a new competency."""
    id: Optional[str] = Field(None, description="Optional client-supplied identifier (UUID or text). If omitted, server generates.")


class CompetencyRead(CompetencyBase):
    """Schema for reading a competency."""
    id: str = Field(..., description="Identifier of the competency (UUID or text)")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")

    model_config = {"from_attributes": True}
