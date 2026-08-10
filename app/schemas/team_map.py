from datetime import date, time
from datetime import date as dt_date
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class TeamMemberInput(BaseModel):
    member_id: str = Field(..., min_length=1)
    display_name: str = Field(..., min_length=1)
    current_role: Optional[str] = None
    birth_date: date
    birth_time: Optional[time] = None
    birth_place: str = Field(..., min_length=2)

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: date) -> date:
        if v > dt_date.today():
            raise ValueError("Date can't be from future")
        if v < dt_date(1900, 1, 1):
            raise ValueError("Too old date (min 1900-01-01)")
        return v


class TeamMapRequest(BaseModel):
    team_name: str = Field(..., min_length=1)
    members: list[TeamMemberInput] = Field(..., min_length=1, max_length=30)

    @model_validator(mode="after")
    def validate_unique_member_ids(self) -> "TeamMapRequest":
        ids = [item.member_id for item in self.members]
        if len(ids) != len(set(ids)):
            raise ValueError("member_id must be unique within the request")
        return self


class TeamMapMember(BaseModel):
    member_id: str
    display_name: str
    current_role: Optional[str] = None
    profile_available: bool
    team_function: Optional[str] = None
    thinking_style: Optional[str] = None
    top_skills: list[str] = Field(default_factory=list)
    key_risks: list[str] = Field(default_factory=list)
    team_contribution: Optional[str] = None
    communication_style: Optional[str] = None
    onboarding_guidance: list[str] = Field(default_factory=list)
    role_directions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    error: Optional[str] = None


class TeamFunctionGroup(BaseModel):
    team_function: str
    member_ids: list[str]
    count: int


class RepeatedFunction(BaseModel):
    team_function: str
    member_ids: list[str]
    count: int


class TeamMapResponse(BaseModel):
    team_name: str
    member_count: int
    profiled_member_count: int
    unavailable_member_count: int
    members: list[TeamMapMember]
    function_distribution: list[TeamFunctionGroup]
    represented_functions: list[str]
    repeated_functions: list[RepeatedFunction]
    team_notes: list[str]
