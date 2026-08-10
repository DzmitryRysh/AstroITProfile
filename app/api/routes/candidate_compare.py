from fastapi import APIRouter

from app.schemas.candidate_compare import (
    CandidateCompareRequest,
    CandidateCompareResponse,
)
from app.services.candidate_compare import compare_candidates

router = APIRouter(prefix="/candidate-compare", tags=["candidate-compare"])


@router.post("", response_model=CandidateCompareResponse)
def create_candidate_compare(payload: CandidateCompareRequest) -> CandidateCompareResponse:
    return compare_candidates(payload)
