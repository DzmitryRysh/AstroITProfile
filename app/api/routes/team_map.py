from fastapi import APIRouter

from app.schemas.team_map import TeamMapRequest, TeamMapResponse
from app.services.team_map import build_team_map

router = APIRouter(prefix="/team-map", tags=["team-map"])


@router.post("", response_model=TeamMapResponse)
def create_team_map(payload: TeamMapRequest) -> TeamMapResponse:
    return build_team_map(payload)
