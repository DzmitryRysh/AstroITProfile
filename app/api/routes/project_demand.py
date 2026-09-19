"""Project Demand API — explicit work-requirement snapshot (stateless).

Project Demand is Contribution-dimension demand for a project.
It is independent of astrology and parallel to Team Gap workflow coverage.
"""

from fastapi import APIRouter

from app.schemas.project_demand import ProjectDemand, ProjectDemandRequest
from app.services.project_demand import build_project_demand

router = APIRouter(prefix="/project-demand", tags=["project-demand"])


@router.post("", response_model=ProjectDemand)
def create_project_demand(payload: ProjectDemandRequest) -> ProjectDemand:
    return build_project_demand(payload)
