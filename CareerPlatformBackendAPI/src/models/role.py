from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String, JSON

from src.db.base import Base


def _gen_uuid() -> str:
    """Generate a UUID4 string."""
    return str(uuid.uuid4())


class Role(Base):
    """
    Role model persisted in the database.

    Notes:
    - `id` stored as String primary key (app generates uuid4 when not provided).
    - `metadata` is a reserved name in SQLAlchemy declarative base. To avoid conflicts,
      the ORM attribute is named `metadata_` while the underlying column name is "metadata".
    - JSON type is used for portability (maps to TEXT in SQLite and JSON in PostgreSQL).
    """
    __tablename__ = "roles"

    id = Column(String(64), primary_key=True, index=True, default=_gen_uuid)
    name = Column(String(255), nullable=False, index=True)
    description = Column(String, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)  # Column name 'metadata', ORM attr 'metadata_'
    version = Column(String(64), nullable=True)
    source = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:  # pragma: no cover
        return f"Role(id={self.id!r}, name={self.name!r})"
