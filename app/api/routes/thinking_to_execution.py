from fastapi import APIRouter, HTTPException

from app.schemas.mercury_source_profile import MercurySourceProfileRequest
from app.schemas.thinking_to_execution import (
    ThinkingToExecutionRequest,
    ThinkingToExecutionSynthesis,
)
from app.services.mars_source_profile import build_mars_source_profile
from app.services.mercury_source_profile import build_mercury_source_profile
from app.services.person_perspective import build_person_perspective
from app.services.thinking_to_execution import build_thinking_to_execution

router = APIRouter(prefix="/thinking-to-execution", tags=["thinking-to-execution"])


@router.post("", response_model=ThinkingToExecutionSynthesis)
def create_thinking_to_execution(
    payload: ThinkingToExecutionRequest,
) -> ThinkingToExecutionSynthesis:
    mercury_request = MercurySourceProfileRequest(
        birth_date=payload.birth_date,
        birth_place=payload.birth_place,
        birth_time=payload.birth_time,
    )
    try:
        mercury = build_mercury_source_profile(mercury_request)
        mars = build_mars_source_profile(
            birth_date=payload.birth_date,
            birth_place=payload.birth_place,
            birth_time=payload.birth_time,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    person = build_person_perspective(
        name=payload.display_name or "",
        sex=payload.sex,
    )
    return build_thinking_to_execution(mercury, mars, person)
