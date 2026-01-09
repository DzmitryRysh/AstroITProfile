from datetime import date, time
from datetime import date as dt_date
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ProfileRequest(BaseModel):
    birth_date: date = Field(..., description="Date of birth YYYY-MM-DD")
    birth_time: time = Field(..., description="Time of birth (HH:MM)")
    birth_place: str = Field(..., min_length=2, description="Place of birth(e.g., 'Miami, FL, USA')")


    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls,v: date) -> date:
        if v > dt_date.today():
            raise ValueError("Date can't be from future")
        if v < dt_date(1900,1,1):
            raise ValueError("Too old date (min 1900-01-01)")
        return v



class ProfileResponse(BaseModel):
    title: str
    sun_sign: str
    it_fit_score: int
    personality_style_archetype: str
    it_archetype: str
    career_axis: dict[str, Any]

    strengths: list[str]
    risks: list[str]
    notes: str

    chart_type: str
    mercury_sign: str
    uranus_house: int
    house_6_sign: str
    house_10_sign: str


