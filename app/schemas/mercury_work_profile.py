from datetime import date, time
from datetime import date as dt_date
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class MercuryWorkProfileRequest(BaseModel):
    birth_date: date = Field(..., description="Date of birth YYYY-MM-DD")
    birth_place: str = Field(..., min_length=2, description="Place of birth")
    birth_time: Optional[time] = Field(
        default=None,
        description="Time of birth (HH:MM). Omit or null if unknown.",
    )

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: date) -> date:
        if v > dt_date.today():
            raise ValueError("Date can't be from future")
        if v < dt_date(1900, 1, 1):
            raise ValueError("Too old date (min 1900-01-01)")
        return v


class PlanetAspect(BaseModel):
    planet: str
    type: str
    orb_deg: Optional[float] = None


class MercuryAspect(PlanetAspect):
    """Mercury-to-planet aspect. Same geometry shape as PlanetAspect."""


class DispositorCondition(BaseModel):
    harmonious_aspect_count: int
    tense_aspect_count: int
    conjunction_count: int


class MercurySourceFactors(BaseModel):
    birth_time_known: bool
    mercury_sign: Optional[str] = None
    mercury_element: Optional[str] = None
    mercury_longitude: Optional[float] = None
    mercury_motion: Optional[Literal["direct", "retrograde"]] = None
    mercury_house: Optional[int] = None
    house_system_used: Optional[str] = None
    aspects: list[MercuryAspect] = Field(default_factory=list)
    major_dispositor: Optional[str] = None
    minor_dispositor: Optional[str] = None
    major_dispositor_sign: Optional[str] = None
    minor_dispositor_sign: Optional[str] = None
    major_dispositor_house: Optional[int] = None
    minor_dispositor_house: Optional[int] = None
    major_dispositor_aspects: list[PlanetAspect] = Field(default_factory=list)
    minor_dispositor_aspects: list[PlanetAspect] = Field(default_factory=list)
    major_dispositor_condition: Optional[DispositorCondition] = None
    minor_dispositor_condition: Optional[DispositorCondition] = None


class MercuryWorkProfileResponse(BaseModel):
    thinking: str
    learning: str
    communication: str
    strengths: list[str]
    risks: list[str]
    team_value: str
    possible_roles: list[str]
    source_factors: MercurySourceFactors
    limitations: list[str]
