from __future__ import annotations

import uuid
from datetime import datetime


from sqlalchemy import Column, DateTime, String, JSON

from src.db.base import Base


def _gen_uuid() -> str:
    """Generate a UUID4 string."""
    return str(uuid.uuid4())


class Competency(Base):
    """
    Competency model represents standardized skills/competencies that can be
    mapped to roles and assessments.

    SQLite compatibility:
    - UUID stored as String primary key (app generates uuid4)
    - JSON for metadata is stored as TEXT under SQLite
    """
    __tablename__ = "competencies"

    id = Column(String(64), primary_key=True, index=True, default=_gen_uuid)
    name = Column(String(255), nullable=False, index=True)
    definition = Column(String, nullable=True)
    category = Column(String(128), nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:  # pragma: no cover
        return f"Competency(id={self.id!r}, name={self.name!r})"
