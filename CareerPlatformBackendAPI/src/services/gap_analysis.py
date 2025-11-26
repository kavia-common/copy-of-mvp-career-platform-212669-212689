from __future__ import annotations

from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.competency import Competency
from src.repositories.role_competencies import list_role_competencies_for_role
from src.schemas.gap_analysis import (
    GapAnalysisRequest,
    GapAnalysisResult,
    GapItem,
)


_LEVEL_MAP = {
    "none": 0,
    "novice": 1,
    "beginner": 1,
    "intermediate": 2,
    "competent": 2,
    "advanced": 3,
    "proficient": 3,
    "expert": 4,
    "master": 5,
}


def _score(level: str | int | None) -> int:
    if level is None:
        return 0
    if isinstance(level, int):
        return level
    s = str(level).strip().lower()
    if s.isdigit():
        try:
            return int(s)
        except Exception:
            return 0
    return _LEVEL_MAP.get(s, 0)


async def _get_competency_lookup(session: AsyncSession, ids: List[str]) -> Dict[str, Competency]:
    if not ids:
        return {}
    result = await session.execute(select(Competency).where(Competency.id.in_(ids)))
    rows = result.scalars().all()
    return {c.id: c for c in rows}


# PUBLIC_INTERFACE
async def analyze_gaps(session: AsyncSession, payload: GapAnalysisRequest) -> GapAnalysisResult:
    """
    Analyze gaps between current user competencies and target role requirements.

    Rules:
    - Required level comes from RoleCompetency.required_level (string or numeric).
    - Current level comes from client provided AssessedCompetency.proficiencyLevel.
    - A gap exists when current score < required score.

    Returns:
        GapAnalysisResult with lists of gaps (id, name, current, required).
    """
    # Collect target role requirements
    mappings = await list_role_competencies_for_role(session, payload.targetRoleId)
    required: Dict[str, str | int | None] = {
        m.competency_id: m.required_level for m in mappings
    }
    names = await _get_competency_lookup(session, list(required.keys()))

    # Index current assessments
    current_map: Dict[str, str | int | None] = {a.id: a.proficiencyLevel for a in payload.currentCompetencies}

    gaps: List[GapItem] = []
    for comp_id, req_level in required.items():
        curr_level = current_map.get(comp_id)
        if _score(curr_level) < _score(req_level):
            comp = names.get(comp_id)
            gaps.append(
                GapItem(
                    competencyId=comp_id,
                    name=(comp.name if comp else comp_id),
                    currentLevel=str(curr_level) if curr_level is not None else "none",
                    requiredLevel=str(req_level) if req_level is not None else "0",
                )
            )

    return GapAnalysisResult(
        targetRoleId=payload.targetRoleId,
        currentCompetencies=payload.currentCompetencies,
        gaps=gaps,
    )
