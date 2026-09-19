"""Schemas for Contribution × Project Demand Coverage v1.

Coverage is the qualitative relationship between Project Demand
(what the work requires) and Contribution Profile (what a person
currently contributes). Not a ranking, score, or hire recommendation.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.contribution_profile import (
    ContributionProfileRequest,
    ContributionState,
)
from app.schemas.project_demand import (
    ProjectDemand,
    ProjectDemandDimensionKey,
    ProjectDemandLevel,
)

CoverageStatus = Literal[
    "covered",
    "partially_covered",
    "conditional_coverage",
    "gap",
    "not_required",
]


class ContributionDemandCoverageRequest(BaseModel):
    """Canonical Project Demand + person natal inputs for coverage."""

    project_demand: ProjectDemand
    person: ContributionProfileRequest


class CoverageDimension(BaseModel):
    dimension: ProjectDemandDimensionKey
    title: str
    demand_level: ProjectDemandLevel
    demand_rationale: str
    contribution_state: Optional[ContributionState] = None
    coverage_status: CoverageStatus
    explanation: str


class ContributionDemandCoverageResponse(BaseModel):
    project_label: str
    person_display_name: Optional[str] = None
    dimensions: list[CoverageDimension] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
