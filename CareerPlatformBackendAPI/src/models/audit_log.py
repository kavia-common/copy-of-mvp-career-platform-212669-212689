from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, JSON

from src.db.base import Base


def _gen_uuid() -> str:
    """Generate a UUID4 string."""
    return str(uuid.uuid4())


class AuditLog(Base):
    """
    Audit log entry capturing user actions and context for compliance/traceability.

    SQLite compatibility:
    - JSON details stored as TEXT under SQLite via SQLAlchemy JSON type.
    """
    __tablename__ = "audit_logs"

    id = Column(String(64), primary_key=True, index=True, default=_gen_uuid)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    user_id = Column(String(64), nullable=True, index=True)
    action = Column(String(255), nullable=False)
    entity_type = Column(String(128), nullable=True, index=True)
    entity_id = Column(String(128), nullable=True, index=True)

    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:  # pragma: no cover
        return f"AuditLog(id={self.id!r}, action={self.action!r}, entity={self.entity_type!r}:{self.entity_id!r})"
