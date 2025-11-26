from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, JSON, UniqueConstraint

from src.db.base import Base


def _gen_uuid() -> str:
    """Generate a UUID4 string."""
    return str(uuid.uuid4())


class Traceability(Base):
    """
    Traceability mapping for any entity to its source documents or artifacts.
    """
    __tablename__ = "traceability"
    __table_args__ = (
        UniqueConstraint("entity_type", "entity_id", name="uq_traceability_entity"),
    )

    id = Column(String(64), primary_key=True, index=True, default=_gen_uuid)
    entity_type = Column(String(128), nullable=False, index=True)
    entity_id = Column(String(128), nullable=False, index=True)

    # Array of source document identifiers/paths/URLs stored as JSON
    source_documents = Column(JSON, nullable=False, default=list)
    metadata_ = Column("metadata", JSON, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:  # pragma: no cover
        return f"Traceability({self.entity_type!r}:{self.entity_id!r})"
