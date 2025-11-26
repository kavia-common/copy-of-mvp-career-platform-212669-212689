from __future__ import annotations

from typing import List, Optional, Sequence, Set

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_current_user
from src.db.session import get_session
from src.models.competency import Competency
from src.models.role_competency import RoleCompetency
from src.schemas.competency import CompetencyRead
from src.schemas.gap_analysis import AssessedCompetency, AssessmentAck
from src.schemas.user import UserRead

router = APIRouter(prefix="/api/v1/competencies", tags=["Competencies"])


def _to_read(entity: Competency) -> CompetencyRead:
    return CompetencyRead(
        id=entity.id,
        name=entity.name,
        definition=entity.definition,
        category=entity.category,
        metadata=entity.metadata_,
        created_at=entity.created_at,
    )


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[CompetencyRead],
    summary="List competencies",
    description="List competencies. Optionally filter by role_id to return only competencies mapped to those roles.",
)
async def list_competencies(
    role_id: Optional[List[str]] = Query(
        default=None,
        description="Optional role id filter. Repeat query param for multiple values."
    ),
    session: AsyncSession = Depends(get_session),
    _user=Depends(get_current_user),
) -> List[CompetencyRead]:
    """
    List competencies, optionally for specific roles using RoleCompetency mappings.
    """
    if not role_id:
        result = await session.execute(select(Competency))
        entities: Sequence[Competency] = result.scalars().all()
        return [_to_read(c) for c in entities]

    # Get competency ids for provided roles
    result = await session.execute(
        select(RoleCompetency.competency_id).where(RoleCompetency.role_id.in_(role_id))
    )
    comp_ids: Set[str] = set([cid for (cid,) in result.all()])

    if not comp_ids:
        return []

    result = await session.execute(select(Competency).where(Competency.id.in_(list(comp_ids))))
    entities: Sequence[Competency] = result.scalars().all()
    return [_to_read(c) for c in entities]


# PUBLIC_INTERFACE
@router.post(
    "/assess",
    response_model=AssessmentAck,
    summary="Submit user competency assessment",
    description="Accepts assessed competencies for the current user. MVP stores no persistent assessment.",
    responses={200: {"description": "Assessment accepted"}},
)
async def assess_competencies(
    payload: List[AssessedCompetency],
    _user: UserRead = Depends(get_current_user),
) -> AssessmentAck:
    """
    MVP endpoint to accept assessed competencies. Returns echo details.
    """
    return AssessmentAck(accepted=len(payload))
