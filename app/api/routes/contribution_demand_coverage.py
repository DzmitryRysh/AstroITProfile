"""Contribution × Project Demand Coverage API — qualitative requirement coverage."""

from fastapi import APIRouter, HTTPException

from app.schemas.contribution_demand_coverage import (
    ContributionDemandCoverageRequest,
    ContributionDemandCoverageResponse,
)
from app.services.contribution_demand_coverage import build_contribution_demand_coverage

router = APIRouter(
    prefix="/contribution-demand-coverage",
    tags=["contribution-demand-coverage"],
)


@router.post("", response_model=ContributionDemandCoverageResponse)
def create_contribution_demand_coverage(
    payload: ContributionDemandCoverageRequest,
) -> ContributionDemandCoverageResponse:
    try:
        return build_contribution_demand_coverage(payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
