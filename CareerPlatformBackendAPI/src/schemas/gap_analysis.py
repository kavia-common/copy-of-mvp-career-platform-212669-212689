from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class AssessedCompetency(BaseModel):
    """Client-provided competency level for gap analysis/assessment."""
    id: str = Field(..., description="Competency identifier")
    proficiencyLevel: str = Field(..., description="Current proficiency level (string or number)")


class AssessmentAck(BaseModel):
    """Acknowledgement of assessment submission."""
    accepted: int = Field(..., description="Number of competencies accepted")


class GapItem(BaseModel):
    """One competency gap entry."""
    competencyId: str = Field(..., description="Competency identifier")
    name: Optional[str] = Field(None, description="Competency name, if known")
    currentLevel: str = Field(..., description="Current level")
    requiredLevel: str = Field(..., description="Required level for target role")


class GapAnalysisRequest(BaseModel):
    """Payload for computing a gap analysis."""
    currentCompetencies: List[AssessedCompetency] = Field(..., description="Current user competencies")
    targetRoleId: str = Field(..., description="Target role identifier")


class GapAnalysisResult(BaseModel):
    """Computed gap analysis result."""
    targetRoleId: str = Field(..., description="Target role identifier")
    currentCompetencies: List[AssessedCompetency] = Field(..., description="Echo of input competences")
    gaps: List[GapItem] = Field(default_factory=list, description="List of identified gaps")
