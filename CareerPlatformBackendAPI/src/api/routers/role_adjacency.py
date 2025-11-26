from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.core.security import get_current_user
from src.services.role_mapper_client import suggest_role_adjacency


class RoleSuggestion(BaseModel):
    """One suggested target role with weight and rationale."""
    targetRoleId: str = Field(..., description="Suggested target role identifier")
    weight: float = Field(..., description="Relative score or probability (0..1)")
    rationale: Optional[str] = Field(None, description="Reason for adjacency")

    model_config = {"json_schema_extra": {"example": {"targetRoleId": "cto", "weight": 0.92, "rationale": "Leadership adjacency"}}}


class RoleAdjacencyResponse(BaseModel):
    """Response payload for role adjacency suggestions."""
    currentRoleId: str = Field(..., description="Current role identifier")
    suggestions: List[RoleSuggestion] = Field(default_factory=list, description="Top-N suggestions")

    model_config = {"json_schema_extra": {"example": {"currentRoleId": "chief-architect", "suggestions": [{"targetRoleId": "cto", "weight": 0.92, "rationale": "Leadership adjacency"}]}}}


router = APIRouter(prefix="/api/v1", tags=["Roles"])


# PUBLIC_INTERFACE
@router.get(
    "/role-adjacency",
    response_model=RoleAdjacencyResponse,
    summary="Get alternative role suggestions",
    description="Return top-N adjacent roles for the given currentRoleId, powered by the internal Node Role Mapping Service.",
    responses={
        200: {"description": "Suggestions returned"},
        401: {"description": "Unauthorized"},
        502: {"description": "Upstream role mapper failure"},
    },
)
async def get_role_adjacency(
    currentRoleId: str = Query(..., description="Current role identifier"),
    topN: Optional[int] = Query(None, description="Number of suggestions to return"),
    _user=Depends(get_current_user),
) -> RoleAdjacencyResponse:
    """
    Proxy to the internal Role Mapping Service to fetch adjacency suggestions.

    - Requires user authentication via Bearer JWT.
    - Uses internal header X-Internal-Token when calling the Node service.
    """
    try:
        raw = await suggest_role_adjacency(currentRoleId, topN)
    except Exception as exc:
        # Hide internal details; report as upstream failure
        raise HTTPException(status_code=502, detail=f"Role mapping service error: {exc}")

    # Normalize and validate basic shape
    suggestions: List[RoleSuggestion] = []
    for s in raw:
        try:
            weight_val = float(s.get("weight", 0))
        except Exception:
            weight_val = 0.0
        target_id = s.get("targetRoleId")
        if not isinstance(target_id, str) or not target_id:
            # Skip invalid entries
            continue
        suggestions.append(RoleSuggestion(targetRoleId=target_id, weight=weight_val, rationale=s.get("rationale")))

    return RoleAdjacencyResponse(currentRoleId=currentRoleId, suggestions=suggestions)
