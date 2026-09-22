from fastapi import APIRouter, HTTPException

from app.schemas.mercury_source_profile import (
    MercurySourceProfileRequest,
    MercurySourceProfileResponse,
)
from app.services.mercury_profile_synthesis import attach_mercury_profile_synthesis
from app.services.mercury_source_profile import build_mercury_source_profile

router = APIRouter(prefix="/mercury-source-profile", tags=["mercury-source-profile"])


@router.post("", response_model=MercurySourceProfileResponse)
def create_mercury_source_profile(
    payload: MercurySourceProfileRequest,
) -> MercurySourceProfileResponse:
    try:
        profile = build_mercury_source_profile(payload)
    except ValueError as exc:
        # Unknown place / timezone failures — same contract as Mars and THINK→DO.
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return attach_mercury_profile_synthesis(profile)
