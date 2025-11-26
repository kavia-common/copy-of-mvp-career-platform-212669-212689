from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class DevelopmentPlanStep(BaseModel):
    """A single actionable step in the development plan."""
    description: str = Field(..., description="Step description")
    actionType: str = Field(..., description="Type of action (learn, practice, shadow, etc.)")
    resource: Optional[str] = Field(None, description="Helpful link or resource")


class DevelopmentPlan(BaseModel):
    """A generated development plan."""
    steps: List[DevelopmentPlanStep] = Field(default_factory=list, description="Plan steps")


class PlanExportRequest(BaseModel):
    """Request to export a plan as pdf or link."""
    format: Literal["pdf", "link"] = Field(..., description="Export format")


class PlanExportResponse(BaseModel):
    """Response containing a URL to the exported plan."""
    url: str = Field(..., description="URL to exported artifact")
