from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_current_user
from src.db.session import get_session
from src.schemas.gap_analysis import GapAnalysisRequest, GapAnalysisResult
from src.services.audit import log_action
from src.services.gap_analysis import analyze_gaps

router = APIRouter(prefix="/api/v1", tags=["Gap Analysis"])


# PUBLIC_INTERFACE
@router.post(
    "/gap-analysis",
    response_model=GapAnalysisResult,
    summary="Perform gap analysis",
    description="Compute competency gaps against a target role.",
)
async def gap_analysis(
    payload: GapAnalysisRequest,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
) -> GapAnalysisResult:
    """
    Compare current competencies with the target role's required competencies and return gaps.
    """
    result = await analyze_gaps(session, payload)
    await log_action(
        session=session,
        user_id=user.id,
        action="gap-analysis",
        entity_type="Role",
        entity_id=payload.targetRoleId,
        details={"gaps": len(result.gaps)},
    )
    return result
