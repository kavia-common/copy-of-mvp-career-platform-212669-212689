from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, JSON, Float, ForeignKey, UniqueConstraint

from src.db.base import Base


def _gen_uuid() -> str:
    """Generate a UUID4 string."""
    return str(uuid.uuid4())


class RoleCompetency(Base):
    """
    Mapping between Role and Competency with required proficiency and optional weighting.

    Notes:
    - Uses separate `id` primary key for simplicity and an additional unique constraint
      on (role_id, competency_id) to prevent duplicates.
    - JSON metadata for portability.
    """
    __tablename__ = "role_competencies"
    __table_args__ = (
        UniqueConstraint("role_id", "competency_id", name="uq_role_competency_pair"),
    )

    id = Column(String(64), primary_key=True, index=True, default=_gen_uuid)
    role_id = Column(String(64), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    competency_id = Column(String(64), ForeignKey("competencies.id", ondelete="CASCADE"), nullable=False, index=True)

    required_level = Column(String(64), nullable=True)
    weight = Column(Float, nullable=True)
    notes = Column(String, nullable=True)

    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:  # pragma: no cover
        return f"RoleCompetency(role_id={self.role_id!r}, competency_id={self.competency_id!r})"
