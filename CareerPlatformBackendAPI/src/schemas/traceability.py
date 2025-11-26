from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TraceabilityBase(BaseModel):
    """Shared properties for a traceability mapping."""
    entity_type: str = Field(..., description="Entity type (e.g., Role, Competency, Mapping)")
    entity_id: str = Field(..., description="Entity identifier")
    source_documents: List[str] = Field(default_factory=list, description="List of source document IDs/paths/URLs")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Arbitrary metadata")


class TraceabilityCreate(TraceabilityBase):
    """Schema for creating/updating traceability."""
    id: Optional[str] = Field(None, description="Optional client-supplied identifier (UUID or text). If omitted, server generates.")


class TraceabilityRead(TraceabilityBase):
    """Schema for reading traceability."""
    id: str = Field(..., description="Identifier of the traceability entry")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")

    model_config = {"from_attributes": True}
