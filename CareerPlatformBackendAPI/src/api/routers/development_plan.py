from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_current_user
from src.db.session import get_session
from src.schemas.development_plan import DevelopmentPlan, PlanExportRequest, PlanExportResponse
from src.schemas.gap_analysis import GapAnalysisRequest, GapAnalysisResult
from src.services.audit import log_action
from src.services.gap_analysis import analyze_gaps
from src.services.plan_generator import generate_plan_from_gaps

router = APIRouter(prefix="/api/v1", tags=["Development Plan"])


# PUBLIC_INTERFACE
@router.post(
    "/development-plan",
    response_model=DevelopmentPlan,
    summary="Generate development plan",
    description="Generate a personalized development plan from a gap analysis input.",
)
async def generate_plan(
    payload: GapAnalysisRequest,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
) -> DevelopmentPlan:
    """
    Generate a plan directly from current competencies and a target role id.
    """
    gaps: GapAnalysisResult = await analyze_gaps(session, payload)
    plan = generate_plan_from_gaps(gaps)
    await log_action(
        session=session,
        user_id=user.id,
        action="development-plan-generate",
        entity_type="Role",
        entity_id=payload.targetRoleId,
        details={"steps": len(plan.steps)},
    )
    return plan


# PUBLIC_INTERFACE
@router.get(
    "/development-plan",
    response_model=DevelopmentPlan,
    summary="Retrieve development plan (MVP placeholder)",
    description="Returns a placeholder plan. Use POST /development-plan with gap analysis for a tailored plan.",
)
async def get_plan_placeholder(_: AsyncSession = Depends(get_session), user=Depends(get_current_user)) -> DevelopmentPlan:
    """
    MVP placeholder for GET plan. Returns an empty plan (no persistence in MVP).
    """
    return DevelopmentPlan(steps=[])


# PUBLIC_INTERFACE
@router.post(
    "/development-plan/export",
    response_model=PlanExportResponse,
    summary="Export development plan",
    description="Export a plan to a shareable link (MVP returns a placeholder URL).",
)
async def export_plan(
    payload: PlanExportRequest,
    user=Depends(get_current_user),
) -> PlanExportResponse:
    """
    MVP export returns a static link indicating successful export.
    """
    url = "https://example.com/plan/export/placeholder"
    return PlanExportResponse(url=url)
