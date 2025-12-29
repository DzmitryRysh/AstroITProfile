from fastapi import APIRouter
from app.schemas.profile import ProfileRequest, ProfileResponse

router = APIRouter(prefix="/profile", tags=["profile"])


def _fake_sun_sign(birth_date) -> str:
    month = birth_date.month
    if month in (3,4):
        return "Aries-ish"
    if month in (5,6):
        return "Gemini-ish"
    if month in (7,8):
        return "Leo-ish"
    return "Mystery Sign"


@router.post("",response_model=ProfileResponse)
def build_profile(payload: ProfileRequest) -> ProfileResponse:
    sun_sign = _fake_sun_sign(payload.birth_date)

    it_archetype = "Backend Astronaut"
    if payload.favorite_stack:
        it_archetype = f"{payload.favorite_stack} Astronaut"

    return ProfileResponse(
        title="Astro IT Profile (draft)",
        sun_sign=sun_sign,
        it_archetype=it_archetype,
        notes="draft answer. later we will add real logic",
    )







