from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.candidate_compare import CandidateInput
from app.schemas.team_gap import CoverageProfileKey, RequiredFunctionStatus
from app.schemas.team_map import TeamMemberInput


class CandidateTeamImpactRequest(BaseModel):
    team_name: str = Field(..., min_length=1)
    coverage_profile: CoverageProfileKey
    target_role: Optional[str] = None
    members: list[TeamMemberInput] = Field(..., min_length=1, max_length=29)
    candidate: CandidateInput

    @model_validator(mode="after")
    def validate_unique_ids(self) -> "CandidateTeamImpactRequest":
        member_ids = [item.member_id for item in self.members]
        if len(member_ids) != len(set(member_ids)):
            raise ValueError("member_id must be unique within the request")
        if self.candidate.candidate_id in set(member_ids):
            raise ValueError("candidate_id must not collide with an existing member_id")
        return self


class CandidateImpactProfile(BaseModel):
    candidate_id: str
    display_name: str
    profile_available: bool
    team_function: Optional[str] = None
    limitations: list[str] = Field(default_factory=list)
    error: Optional[str] = None


class TeamCoverageSnapshot(BaseModel):
    member_count: int
    profiled_member_count: int
    unavailable_member_count: int
    required_functions: list[RequiredFunctionStatus]
    represented_required_functions: list[str]
    missing_required_functions: list[str]
    single_coverage_functions: list[str]
    uncovered_workflow_stages: list[str]
    additional_represented_functions: list[str]


class CandidateImpactSummary(BaseModel):
    impact_available: bool
    closed_missing_functions: list[str]
    closed_workflow_stages: list[str]
    strengthened_single_coverage_functions: list[str]
    reinforced_represented_functions: list[str]
    added_additional_functions: list[str]
    reinforced_additional_functions: list[str]
    remaining_missing_functions: list[str]
    remaining_uncovered_workflow_stages: list[str]
    required_coverage_changed: bool


class CandidateTeamImpactResponse(BaseModel):
    team_name: str
    coverage_profile: str
    coverage_profile_name: str
    target_role: Optional[str] = None
    candidate: CandidateImpactProfile
    before: TeamCoverageSnapshot
    after: TeamCoverageSnapshot
    impact: CandidateImpactSummary
    impact_notes: list[str]
