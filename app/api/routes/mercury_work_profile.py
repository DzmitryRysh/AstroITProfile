from fastapi import APIRouter, HTTPException

from app.schemas.mercury_work_profile import (
    MercuryWorkProfileRequest,
    MercuryWorkProfileResponse,
)
from app.services.mercury_work_profile import build_mercury_work_profile

router = APIRouter(prefix="/mercury-work-profile", tags=["mercury-work-profile"])


@router.post("", response_model=MercuryWorkProfileResponse)
def create_mercury_work_profile(
    payload: MercuryWorkProfileRequest,
) -> MercuryWorkProfileResponse:
    try:
        return build_mercury_work_profile(payload)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
