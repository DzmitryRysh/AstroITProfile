from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.candidate_compare import CandidateInput
from app.schemas.team_gap import CoverageProfileKey
from app.schemas.team_map import TeamMemberInput


class WorkspaceData(BaseModel):
    team_name: str = Field(..., min_length=1)
    coverage_profile: CoverageProfileKey
    target_role: Optional[str] = None
    members: list[TeamMemberInput] = Field(..., min_length=1, max_length=30)
    candidates: list[CandidateInput] = Field(default_factory=list, max_length=8)

    @model_validator(mode="after")
    def validate_unique_ids(self) -> "WorkspaceData":
        member_ids = [item.member_id for item in self.members]
        if len(member_ids) != len(set(member_ids)):
            raise ValueError("member_id must be unique within the workspace")

        candidate_ids = [item.candidate_id for item in self.candidates]
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("candidate_id must be unique within the workspace")

        collisions = set(member_ids) & set(candidate_ids)
        if collisions:
            raise ValueError(
                "candidate_id must not collide with member_id within the workspace"
            )
        return self


class WorkspaceRecord(BaseModel):
    workspace_id: str
    team_name: str
    coverage_profile: str
    target_role: Optional[str] = None
    members: list[TeamMemberInput]
    candidates: list[CandidateInput]
    created_at: datetime
    updated_at: datetime

    @field_validator("workspace_id")
    @classmethod
    def validate_workspace_id(cls, value: str) -> str:
        UUID(value)
        return value


class WorkspaceSummary(BaseModel):
    workspace_id: str
    team_name: str
    coverage_profile: str
    target_role: Optional[str] = None
    member_count: int
    candidate_count: int
    created_at: datetime
    updated_at: datetime


class WorkspaceListResponse(BaseModel):
    workspaces: list[WorkspaceSummary]
