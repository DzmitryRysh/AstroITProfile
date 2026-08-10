"""Candidate Compare v1 — orchestration over existing Mercury Recruiter View."""

from __future__ import annotations

from app.schemas.candidate_compare import (
    CandidateCompareItem,
    CandidateCompareRequest,
    CandidateCompareResponse,
    CandidateInput,
    FunctionDistributionItem,
)
from app.schemas.mercury_work_profile import MercuryWorkProfileRequest
from app.services.mercury_work_profile import build_mercury_work_profile

COMPARISON_NOTES = [
    "Profiles describe different work-style hypotheses and are not candidate rankings.",
    "No hire/reject recommendation is produced.",
    "Role directions describe areas worth exploring and do not replace technical qualification assessment.",
]

UNAVAILABLE_PROFILE_ERROR = (
    "Stable work-style interpretation is unavailable for this birth data; no profile was guessed."
)


def _unavailable_item(
    candidate: CandidateInput,
    *,
    limitations: list[str],
    error: str,
) -> CandidateCompareItem:
    return CandidateCompareItem(
        candidate_id=candidate.candidate_id,
        display_name=candidate.display_name,
        profile_available=False,
        team_function=None,
        thinking_style=None,
        top_skills=[],
        key_risks=[],
        team_contribution=None,
        communication_style=None,
        onboarding_guidance=[],
        role_directions=[],
        limitations=list(limitations),
        error=error,
    )


def _build_candidate_item(candidate: CandidateInput) -> CandidateCompareItem:
    try:
        profile = build_mercury_work_profile(
            MercuryWorkProfileRequest(
                birth_date=candidate.birth_date,
                birth_place=candidate.birth_place,
                birth_time=candidate.birth_time,
            )
        )
    except ValueError as exc:
        return _unavailable_item(candidate, limitations=[], error=str(exc))

    view = profile.recruiter_view
    if view is None:
        return _unavailable_item(
            candidate,
            limitations=list(profile.limitations),
            error=UNAVAILABLE_PROFILE_ERROR,
        )

    return CandidateCompareItem(
        candidate_id=candidate.candidate_id,
        display_name=candidate.display_name,
        profile_available=True,
        team_function=view.team_function,
        thinking_style=view.thinking_style,
        top_skills=list(view.top_skills),
        key_risks=list(view.key_risks),
        team_contribution=view.team_contribution,
        communication_style=view.communication_style,
        onboarding_guidance=list(view.onboarding_guidance),
        role_directions=list(view.role_directions),
        limitations=list(profile.limitations),
        error=None,
    )


def _function_distribution(
    items: list[CandidateCompareItem],
) -> list[FunctionDistributionItem]:
    grouped: dict[str, list[str]] = {}
    order: list[str] = []
    for item in items:
        if not item.profile_available or not item.team_function:
            continue
        if item.team_function not in grouped:
            grouped[item.team_function] = []
            order.append(item.team_function)
        grouped[item.team_function].append(item.candidate_id)
    return [
        FunctionDistributionItem(team_function=name, candidate_ids=grouped[name])
        for name in order
    ]


def compare_candidates(payload: CandidateCompareRequest) -> CandidateCompareResponse:
    items = [_build_candidate_item(candidate) for candidate in payload.candidates]
    return CandidateCompareResponse(
        target_role=payload.target_role,
        candidate_count=len(items),
        candidates=items,
        function_distribution=_function_distribution(items),
        comparison_notes=list(COMPARISON_NOTES),
    )
