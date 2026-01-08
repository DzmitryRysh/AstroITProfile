from fastapi import APIRouter, HTTPException

from app.schemas.profile import ProfileRequest, ProfileResponse
from app.services.astro_service import AstroService

from app.services.places import list_places


router = APIRouter(prefix="/profile", tags=["profile"])
astro_service = AstroService()


@router.post("", response_model=ProfileResponse)
def build_profile(payload: ProfileRequest) -> ProfileResponse:
    try:
        return astro_service.build_profile(payload)
    except ValueError as e:
        # place not found, timezone not found, etc.
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/places")
def available_places():
    places = list_places()
    return {
        "count": len(places),
        "places": places,
    }