from fastapi import APIRouter

from app.schemas.candidate_team_impact import (
    CandidateTeamImpactRequest,
    CandidateTeamImpactResponse,
)
from app.services.candidate_team_impact import analyze_candidate_team_impact

router = APIRouter(prefix="/candidate-team-impact", tags=["candidate-team-impact"])


@router.post("", response_model=CandidateTeamImpactResponse)
def create_candidate_team_impact(
    payload: CandidateTeamImpactRequest,
) -> CandidateTeamImpactResponse:
    return analyze_candidate_team_impact(payload)
