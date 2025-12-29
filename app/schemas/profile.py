from datetime import date
from pydantic import BaseModel, Field

class ProfileRequest(BaseModel):
    birth_date: date = Field(..., description="Date of birthday")
    favorite_stack: str  | None = Field(
        default=None,
        description="Favorite stack(ex. Python, JS, DevOps",
        examples=["Python"],

    )

class ProfileResponse(BaseModel):
    title: str
    sun_sign: str
    it_archetype: str
    notes: str