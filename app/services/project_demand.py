"""Project Demand v1 — deterministic work-requirement normalizer.

Answers: what contribution patterns does THIS WORK require?

Does not:
  - derive demand from astrology / Mercury / Mars / TTE / person profiles
  - score people, rank candidates, or recommend hire/reject
  - implement Supply × Demand coverage
  - modify Team Gap (Team Function × Workflow Coverage remains parallel)

Parallel domains (intentionally not interchangeable):
  Team Gap        → Team Function × Workflow Coverage
  Project Demand  → Contribution Dimension × work demand levels
"""

from __future__ import annotations

from app.schemas.project_demand import (
    PROJECT_DEMAND_DIMENSION_ORDER,
    ProjectDemand,
    ProjectDemandDimension,
    ProjectDemandRequest,
)

PROJECT_DEMAND_NOTES: tuple[str, ...] = (
    "Project Demand describes work contribution requirements for a project.",
    "It is not a candidate ranking or person suitability judgment.",
    "It is not a performance prediction or technical-qualification assessment.",
    "Technical qualifications are evaluated separately.",
    "No hire/reject recommendation is produced.",
)


def build_project_demand(request: ProjectDemandRequest) -> ProjectDemand:
    """Validate/normalize an explicit complete demand into a canonical snapshot."""
    by_key = {item.dimension: item for item in request.dimensions}
    dimensions = [
        ProjectDemandDimension(
            dimension=key,
            demand_level=by_key[key].demand_level,
            rationale=by_key[key].rationale,
            source="user",
        )
        for key in PROJECT_DEMAND_DIMENSION_ORDER
    ]
    return ProjectDemand(
        label=request.label,
        description=request.description,
        dimensions=dimensions,
        assumptions=list(request.assumptions),
        created_from="explicit",
        notes=list(PROJECT_DEMAND_NOTES),
    )
