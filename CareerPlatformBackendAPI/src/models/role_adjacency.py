from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, JSON, Float, ForeignKey, UniqueConstraint

from src.db.base import Base


def _gen_uuid() -> str:
    """Generate a UUID4 string."""
    return str(uuid.uuid4())


class RoleAdjacency(Base):
    """
    Role adjacency expresses that a transition from source_role to target_role
    is viable, with optional strength and rationale.

    Notes:
    - Unique constraint on (source_role_id, target_role_id) to avoid duplicates.
    """
    __tablename__ = "role_adjacency"
    __table_args__ = (
        UniqueConstraint("source_role_id", "target_role_id", name="uq_role_adjacency_pair"),
    )

    id = Column(String(64), primary_key=True, index=True, default=_gen_uuid)
    source_role_id = Column(String(64), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    target_role_id = Column(String(64), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)

    strength = Column(Float, nullable=True)  # 0..1 or relative weight
    rationale = Column(String, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:  # pragma: no cover
        return f"RoleAdjacency({self.source_role_id!r} -> {self.target_role_id!r}, strength={self.strength!r})"
