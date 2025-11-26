from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, JSON

from src.db.base import Base


def _gen_uuid() -> str:
    """Generate a UUID4 string."""
    return str(uuid.uuid4())


class User(Base):
    """
    User model for basic CRUD validation against SQLite.

    Notes on SQLite compatibility:
    - UUID stored as String primary key (app generates uuid4)
    - JSON type is supported by SQLAlchemy and stored as TEXT in SQLite
    """
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True, default=_gen_uuid)
    email = Column(String(320), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    roles = Column(JSON, nullable=False, default=list)

    # New: store salted password hash (PBKDF2), never store plaintext
    password_hash = Column(String(512), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:  # pragma: no cover - simple debug helper
        return f"User(id={self.id!r}, email={self.email!r})"
