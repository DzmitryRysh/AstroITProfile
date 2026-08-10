from datetime import date, time
from datetime import date as dt_date
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class CandidateInput(BaseModel):
    candidate_id: str = Field(..., min_length=1)
    display_name: str = Field(..., min_length=1)
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


class CandidateCompareRequest(BaseModel):
    target_role: str = Field(..., min_length=1)
    candidates: list[CandidateInput] = Field(..., min_length=2, max_length=8)

    @model_validator(mode="after")
    def validate_unique_candidate_ids(self) -> "CandidateCompareRequest":
        ids = [item.candidate_id for item in self.candidates]
        if len(ids) != len(set(ids)):
            raise ValueError("candidate_id must be unique within the request")
        return self


class CandidateCompareItem(BaseModel):
    candidate_id: str
    display_name: str
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


class FunctionDistributionItem(BaseModel):
    team_function: str
    candidate_ids: list[str]


class CandidateCompareResponse(BaseModel):
    target_role: str
    candidate_count: int
    candidates: list[CandidateCompareItem]
    function_distribution: list[FunctionDistributionItem]
    comparison_notes: list[str]
