from fastapi import APIRouter

from app.schemas.mercury_source_profile import (
    MercurySourceProfileRequest,
    MercurySourceProfileResponse,
)
from app.services.mercury_source_profile import build_mercury_source_profile

router = APIRouter(prefix="/mercury-source-profile", tags=["mercury-source-profile"])


@router.post("", response_model=MercurySourceProfileResponse)
def create_mercury_source_profile(
    payload: MercurySourceProfileRequest,
) -> MercurySourceProfileResponse:
    return build_mercury_source_profile(payload)
