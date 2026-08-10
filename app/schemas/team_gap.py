from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.team_map import TeamMemberInput

CoverageProfileKey = Literal["ai_ml_product_delivery"]
FunctionCoverageStatus = Literal["represented", "single_coverage", "missing"]


class TeamGapRequest(BaseModel):
    team_name: str = Field(..., min_length=1)
    coverage_profile: CoverageProfileKey
    members: list[TeamMemberInput] = Field(..., min_length=1, max_length=30)

    @model_validator(mode="after")
    def validate_unique_member_ids(self) -> "TeamGapRequest":
        ids = [item.member_id for item in self.members]
        if len(ids) != len(set(ids)):
            raise ValueError("member_id must be unique within the request")
        return self


class RequiredFunctionStatus(BaseModel):
    team_function: str
    workflow_stage: str
    why_it_matters: str
    status: FunctionCoverageStatus
    member_ids: list[str]
    count: int


class TeamGapMember(BaseModel):
    member_id: str
    display_name: str
    current_role: Optional[str] = None
    profile_available: bool
    team_function: Optional[str] = None
    limitations: list[str] = Field(default_factory=list)
    error: Optional[str] = None


class TeamGapResponse(BaseModel):
    team_name: str
    coverage_profile: str
    coverage_profile_name: str
    member_count: int
    profiled_member_count: int
    unavailable_member_count: int
    required_functions: list[RequiredFunctionStatus]
    represented_required_functions: list[str]
    missing_required_functions: list[str]
    single_coverage_functions: list[str]
    uncovered_workflow_stages: list[str]
    additional_represented_functions: list[str]
    members: list[TeamGapMember]
    gap_notes: list[str]
