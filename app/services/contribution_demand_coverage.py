"""Contribution × Project Demand Coverage v1.

Joins canonical Project Demand with Contribution Profile into qualitative
requirement coverage. Does not re-read Mercury/Mars facts, invent dimensions,
score people, or recommend hiring.
"""

from __future__ import annotations

from app.schemas.contribution_demand_coverage import (
    ContributionDemandCoverageRequest,
    ContributionDemandCoverageResponse,
    CoverageDimension,
    CoverageStatus,
)
from app.schemas.contribution_profile import (
    ContributionProfileRequest,
    ContributionProfileResponse,
    ContributionState,
)
from app.schemas.mercury_source_profile import MercurySourceProfileRequest
from app.schemas.project_demand import (
    PROJECT_DEMAND_DIMENSION_ORDER,
    ProjectDemand,
    ProjectDemandLevel,
)
from app.services.contribution_profile import (
    CONTRIBUTION_DIMENSION_SPECS,
    build_contribution_profile,
)
from app.services.mars_source_profile import build_mars_source_profile
from app.services.mercury_source_profile import build_mercury_source_profile
from app.services.person_perspective import build_person_perspective
from app.services.thinking_to_execution import build_thinking_to_execution

COVERAGE_NOTES: tuple[str, ...] = (
    "Coverage describes how current contribution evidence relates to project requirements.",
    "It is not a candidate ranking or suitability score.",
    "It is not a performance prediction or technical-qualification assessment.",
    "No hire/reject recommendation is produced.",
)

_DIMENSION_TITLES: dict[str, str] = {
    spec.key: spec.title for spec in CONTRIBUTION_DIMENSION_SPECS
}

# Frozen coverage matrix: demand_level × contribution_state|None → coverage_status
_COVERAGE_MATRIX: dict[ProjectDemandLevel, dict[ContributionState | None, CoverageStatus]] = {
    "critical": {
        "primary": "covered",
        "strong": "covered",
        "supporting": "partially_covered",
        "conditional": "conditional_coverage",
        None: "gap",
    },
    "important": {
        "primary": "covered",
        "strong": "covered",
        "supporting": "partially_covered",
        "conditional": "conditional_coverage",
        None: "gap",
    },
    "useful": {
        "primary": "covered",
        "strong": "covered",
        "supporting": "covered",
        "conditional": "conditional_coverage",
        None: "gap",
    },
    "not_required": {
        "primary": "not_required",
        "strong": "not_required",
        "supporting": "not_required",
        "conditional": "not_required",
        None: "not_required",
    },
}


def resolve_coverage_status(
    demand_level: ProjectDemandLevel,
    contribution_state: ContributionState | None,
) -> CoverageStatus:
    """Pure matrix lookup. No natal or source catalog work."""
    by_state = _COVERAGE_MATRIX[demand_level]
    return by_state[contribution_state]


def _explanation_for(
    *,
    demand_level: ProjectDemandLevel,
    coverage_status: CoverageStatus,
    contribution_state: ContributionState | None,
) -> str:
    if coverage_status == "not_required":
        return "This contribution is explicitly not required for this project."
    if coverage_status == "gap":
        if demand_level == "useful":
            return (
                "This contribution would be useful for the project, but the current "
                "Contribution Profile does not contain this dimension."
            )
        return (
            "The project requires this contribution, but the current "
            "Contribution Profile does not contain this dimension."
        )
    if coverage_status == "conditional_coverage":
        return (
            "The matching contribution is present, but current evidence shows "
            "conditions or friction in how consistently it may appear."
        )
    if coverage_status == "partially_covered":
        if demand_level == "critical":
            return (
                "This requirement is critical to the project, while the current "
                "contribution evidence is supporting rather than strong."
            )
        return (
            "This requirement is important to the project, while the current "
            "contribution evidence is supporting rather than strong."
        )
    # covered
    if contribution_state == "supporting":
        return (
            "This useful requirement is supported by a supporting contribution pattern."
        )
    if contribution_state == "primary":
        return (
            "This requirement is supported by a primary contribution pattern."
        )
    return "This requirement is supported by a strong contribution pattern."


def apply_coverage_matrix(
    project_demand: ProjectDemand,
    contribution_profile: ContributionProfileResponse,
) -> list[CoverageDimension]:
    """Map Project Demand rows to coverage using Contribution lookup.

    Iterates Project Demand canonical order. Does not invent Contribution dimensions.
    """
    demand_by_key = {item.dimension: item for item in project_demand.dimensions}
    contribution_by_key = {
        item.key: item for item in contribution_profile.dimensions
    }
    rows: list[CoverageDimension] = []
    for key in PROJECT_DEMAND_DIMENSION_ORDER:
        demand_dim = demand_by_key[key]
        contrib = contribution_by_key.get(key)
        contribution_state: ContributionState | None = (
            contrib.state if contrib is not None else None
        )
        coverage_status = resolve_coverage_status(
            demand_dim.demand_level,
            contribution_state,
        )
        title = (
            contrib.title
            if contrib is not None
            else _DIMENSION_TITLES.get(key, key.replace("_", " ").title())
        )
        rows.append(
            CoverageDimension(
                dimension=key,
                title=title,
                demand_level=demand_dim.demand_level,
                demand_rationale=demand_dim.rationale,
                contribution_state=contribution_state,
                coverage_status=coverage_status,
                explanation=_explanation_for(
                    demand_level=demand_dim.demand_level,
                    coverage_status=coverage_status,
                    contribution_state=contribution_state,
                ),
            )
        )
    return rows


def build_contribution_profile_for_person(
    person: ContributionProfileRequest,
) -> ContributionProfileResponse:
    """Reuse the same natal → Contribution pipeline as the Contribution Profile route."""
    mercury_request = MercurySourceProfileRequest(
        birth_date=person.birth_date,
        birth_place=person.birth_place,
        birth_time=person.birth_time,
    )
    mercury = build_mercury_source_profile(mercury_request)
    mars = build_mars_source_profile(
        birth_date=person.birth_date,
        birth_place=person.birth_place,
        birth_time=person.birth_time,
    )
    perspective = build_person_perspective(
        name=person.display_name or "",
        sex=person.sex,
    )
    tte = build_thinking_to_execution(mercury, mars, perspective)
    return build_contribution_profile(mercury, mars, perspective, tte)


def build_contribution_demand_coverage(
    request: ContributionDemandCoverageRequest,
) -> ContributionDemandCoverageResponse:
    """Orchestrate person Contribution Profile, then apply pure coverage matrix."""
    contribution = build_contribution_profile_for_person(request.person)
    dimensions = apply_coverage_matrix(request.project_demand, contribution)
    return ContributionDemandCoverageResponse(
        project_label=request.project_demand.label,
        person_display_name=request.person.display_name,
        dimensions=dimensions,
        notes=list(COVERAGE_NOTES),
    )
