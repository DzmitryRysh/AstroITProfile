from fastapi import APIRouter

from app.schemas.team_gap import TeamGapRequest, TeamGapResponse
from app.services.team_gap import analyze_team_gap

router = APIRouter(prefix="/team-gap", tags=["team-gap"])


@router.post("", response_model=TeamGapResponse)
def create_team_gap(payload: TeamGapRequest) -> TeamGapResponse:
    return analyze_team_gap(payload)
