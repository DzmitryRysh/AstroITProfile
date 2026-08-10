"""Team Gap v1 — workflow coverage analysis over Team Map."""

from __future__ import annotations

from app.schemas.team_gap import (
    RequiredFunctionStatus,
    TeamGapMember,
    TeamGapRequest,
    TeamGapResponse,
)
from app.schemas.team_map import TeamMapRequest
from app.services.team_coverage_profiles import COVERAGE_PROFILES
from app.services.team_map import build_team_map

BASE_GAP_NOTES = [
    "Team Gap compares represented Team Functions with the selected workflow profile.",
    "A missing function means that no currently profiled member has that primary Team Function; it is not a performance judgment.",
    "Single coverage means one profiled member currently represents that workflow function.",
    "Gap analysis does not recommend a specific hiring decision.",
]

UNAVAILABLE_NOTE = "Gap analysis is based only on members with available profiles."


def _status_for_count(count: int) -> str:
    if count <= 0:
        return "missing"
    if count == 1:
        return "single_coverage"
    return "represented"


def analyze_team_gap(payload: TeamGapRequest) -> TeamGapResponse:
    profile = COVERAGE_PROFILES[payload.coverage_profile]
    team_map = build_team_map(
        TeamMapRequest(team_name=payload.team_name, members=payload.members)
    )

    members_by_function: dict[str, list[str]] = {
        group.team_function: list(group.member_ids)
        for group in team_map.function_distribution
    }

    required_statuses: list[RequiredFunctionStatus] = []
    represented_required: list[str] = []
    missing_required: list[str] = []
    single_coverage: list[str] = []
    uncovered_stages: list[str] = []

    for definition in profile.required_functions:
        member_ids = members_by_function.get(definition.team_function, [])
        count = len(member_ids)
        status = _status_for_count(count)
        required_statuses.append(
            RequiredFunctionStatus(
                team_function=definition.team_function,
                workflow_stage=definition.workflow_stage,
                why_it_matters=definition.why_it_matters,
                status=status,
                member_ids=member_ids,
                count=count,
            )
        )
        if count >= 1:
            represented_required.append(definition.team_function)
        if status == "single_coverage":
            single_coverage.append(definition.team_function)
        elif status == "missing":
            missing_required.append(definition.team_function)
            uncovered_stages.append(definition.workflow_stage)

    required_set = {item.team_function for item in profile.required_functions}
    additional = [
        name for name in team_map.represented_functions if name not in required_set
    ]

    notes = list(BASE_GAP_NOTES)
    if team_map.unavailable_member_count > 0:
        notes.append(UNAVAILABLE_NOTE)
    for item in required_statuses:
        if item.status == "missing":
            notes.append(
                "The current profiled team has no member whose primary Team Function is "
                f"{item.team_function} for this coverage profile."
            )

    members = [
        TeamGapMember(
            member_id=member.member_id,
            display_name=member.display_name,
            current_role=member.current_role,
            profile_available=member.profile_available,
            team_function=member.team_function,
            limitations=list(member.limitations),
            error=member.error,
        )
        for member in team_map.members
    ]

    return TeamGapResponse(
        team_name=team_map.team_name,
        coverage_profile=profile.key,
        coverage_profile_name=profile.name,
        member_count=team_map.member_count,
        profiled_member_count=team_map.profiled_member_count,
        unavailable_member_count=team_map.unavailable_member_count,
        required_functions=required_statuses,
        represented_required_functions=represented_required,
        missing_required_functions=missing_required,
        single_coverage_functions=single_coverage,
        uncovered_workflow_stages=uncovered_stages,
        additional_represented_functions=additional,
        members=members,
        gap_notes=notes,
    )
