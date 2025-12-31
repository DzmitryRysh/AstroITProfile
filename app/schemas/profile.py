from datetime import date

from pydantic import BaseModel, Field, field_validator


class ProfileRequest(BaseModel):
    birth_date: date = Field(..., description="Date of birthday YYYY-MM-DD")
    favorite_stack: str  | None = Field(
        default=None,
        description="Favorite stack(ex. Python, JS, DevOps",
        # examples=["Python"],

    )

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls,v: date) -> date:
        if v > date.today():
            raise ValueError("Date can't be from future")
        if v < date(1900,1,1):
            raise ValueError("Too old date (min 1900-01-01)")
        return v



class ProfileResponse(BaseModel):
    title: str
    sun_sign: str
    it_archetype: str
    notes: str