from fastapi import APIRouter

from app.api.routes.candidate_compare import router as candidate_compare_router
from app.api.routes.candidate_team_impact import router as candidate_team_impact_router
from app.api.routes.health import router as health_router
from app.api.routes.mercury_work_profile import router as mercury_work_profile_router
from app.api.routes.profile import router as profile_router
from app.api.routes.team_gap import router as team_gap_router
from app.api.routes.team_map import router as team_map_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(profile_router)
api_router.include_router(mercury_work_profile_router)
api_router.include_router(candidate_compare_router)
api_router.include_router(team_map_router)
api_router.include_router(team_gap_router)
api_router.include_router(candidate_team_impact_router)







