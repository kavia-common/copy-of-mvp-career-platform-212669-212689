from __future__ import annotations

from typing import List

from src.schemas.development_plan import DevelopmentPlan, DevelopmentPlanStep
from src.schemas.gap_analysis import GapAnalysisResult


# PUBLIC_INTERFACE
def generate_plan_from_gaps(gaps: GapAnalysisResult) -> DevelopmentPlan:
    """
    Generate a basic, actionable development plan based on competency gaps.

    Each gap becomes one or more steps directing the user to bridge the gap.
    """
    steps: List[DevelopmentPlanStep] = []
    for g in gaps.gaps:
        query = g.name.replace(" ", "+")
        steps.append(
            DevelopmentPlanStep(
                description=f"Raise '{g.name}' from {g.currentLevel} to {g.requiredLevel}.",
                actionType="learn",
                resource=f"https://www.google.com/search?q={query}+course",
            )
        )
        steps.append(
            DevelopmentPlanStep(
                description=f"Apply '{g.name}' in a small project or PoC.",
                actionType="practice",
                resource="https://www.notion.so/templates/project-plan",
            )
        )
    return DevelopmentPlan(steps=steps)
