from fastapi import APIRouter, HTTPException

from app.schemas.mars_source_profile import (
    MarsSourceProfileRequest,
    MarsSourceProfileResponse,
)
from app.services.mars_profile_synthesis import serialize_mars_source_profile
from app.services.mars_source_profile import build_mars_source_profile

router = APIRouter(prefix="/mars-source-profile", tags=["mars-source-profile"])


@router.post("", response_model=MarsSourceProfileResponse)
def create_mars_source_profile(
    payload: MarsSourceProfileRequest,
) -> MarsSourceProfileResponse:
    try:
        profile = build_mars_source_profile(
            birth_date=payload.birth_date,
            birth_place=payload.birth_place,
            birth_time=payload.birth_time,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return serialize_mars_source_profile(profile)
