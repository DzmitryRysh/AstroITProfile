"""Schemas for Contribution Profile v1.

Descriptive work-contribution states derived from Mercury, Mars, and
Thinking → Execution evidence. Not a ranking, score, or hire recommendation.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.mercury_work_profile import MercuryWorkProfileRequest

ContributionState = Literal["primary", "strong", "supporting", "conditional"]


class ContributionProfileRequest(MercuryWorkProfileRequest):
    display_name: Optional[str] = None
    sex: Optional[str] = None


class ContributionDimension(BaseModel):
    key: str
    title: str
    state: ContributionState
    description: str
    mercury_support: list[str] = Field(default_factory=list)
    mars_support: list[str] = Field(default_factory=list)
    root_fact_ids: list[str] = Field(default_factory=list)
    thinking_to_execution_support: list[str] = Field(default_factory=list)
    mercury_provenance: list[str] = Field(default_factory=list)
    mars_provenance: list[str] = Field(default_factory=list)
    why_this_appears: str
    limitations: list[str] = Field(default_factory=list)
    presentation_ready: bool = True


class ContributionTraceability(BaseModel):
    dimension_count: int
    primary_count: int
    strong_count: int
    supporting_count: int
    conditional_count: int
    mercury_support_count: int
    mars_support_count: int
    root_fact_count: int
    bridge_support_count: int


class ContributionProfileResponse(BaseModel):
    dimensions: list[ContributionDimension] = Field(default_factory=list)
    strongest: list[str] = Field(default_factory=list)
    supporting: list[str] = Field(default_factory=list)
    conditional: list[str] = Field(default_factory=list)
    traceability: ContributionTraceability
    limitations: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
