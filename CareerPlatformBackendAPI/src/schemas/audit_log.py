from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AuditLogBase(BaseModel):
    """Shared properties for an audit log entry."""
    user_id: Optional[str] = Field(None, description="User identifier responsible for action (if known)")
    action: str = Field(..., description="Action performed")
    entity_type: Optional[str] = Field(None, description="Entity type affected")
    entity_id: Optional[str] = Field(None, description="Entity identifier affected")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional structured details/context")


class AuditLogCreate(AuditLogBase):
    """Schema for creating a new audit log entry."""
    timestamp: Optional[datetime] = Field(None, description="Optional timestamp override; otherwise server uses current time")
    id: Optional[str] = Field(None, description="Optional client-supplied identifier (UUID or text). If omitted, server generates.")


class AuditLogRead(AuditLogBase):
    """Schema for reading an audit log entry."""
    id: str = Field(..., description="Identifier of the audit log entry")
    timestamp: datetime = Field(..., description="Timestamp of the event")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")

    model_config = {"from_attributes": True}
