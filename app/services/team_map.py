"""Team Map v1 — orchestration over existing Mercury Recruiter View."""

from __future__ import annotations

from app.schemas.mercury_work_profile import MercuryWorkProfileRequest
from app.schemas.team_map import (
    RepeatedFunction,
    TeamFunctionGroup,
    TeamMapMember,
    TeamMapRequest,
    TeamMapResponse,
    TeamMemberInput,
)
from app.services.mercury_work_profile import build_mercury_work_profile

TEAM_NOTES = [
    "Team Map describes represented work-style functions and does not measure employee performance.",
    "Repeated functions are descriptive and are not automatically strengths or weaknesses.",
    "Profiles are hypotheses for team design and development, not employment decisions.",
]

UNAVAILABLE_PROFILE_ERROR = (
    "Stable work-style interpretation is unavailable for this birth data; no profile was guessed."
)


def _unavailable_member(
    member: TeamMemberInput,
    *,
    limitations: list[str],
    error: str,
) -> TeamMapMember:
    return TeamMapMember(
        member_id=member.member_id,
        display_name=member.display_name,
        current_role=member.current_role,
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


def _build_member(member: TeamMemberInput) -> TeamMapMember:
    try:
        profile = build_mercury_work_profile(
            MercuryWorkProfileRequest(
                birth_date=member.birth_date,
                birth_place=member.birth_place,
                birth_time=member.birth_time,
            )
        )
    except ValueError as exc:
        return _unavailable_member(member, limitations=[], error=str(exc))

    view = profile.recruiter_view
    if view is None:
        return _unavailable_member(
            member,
            limitations=list(profile.limitations),
            error=UNAVAILABLE_PROFILE_ERROR,
        )

    return TeamMapMember(
        member_id=member.member_id,
        display_name=member.display_name,
        current_role=member.current_role,
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


def _function_distribution(members: list[TeamMapMember]) -> list[TeamFunctionGroup]:
    grouped: dict[str, list[str]] = {}
    order: list[str] = []
    for member in members:
        if not member.profile_available or not member.team_function:
            continue
        if member.team_function not in grouped:
            grouped[member.team_function] = []
            order.append(member.team_function)
        grouped[member.team_function].append(member.member_id)
    return [
        TeamFunctionGroup(
            team_function=name,
            member_ids=grouped[name],
            count=len(grouped[name]),
        )
        for name in order
    ]


def build_team_map(payload: TeamMapRequest) -> TeamMapResponse:
    members = [_build_member(member) for member in payload.members]
    distribution = _function_distribution(members)
    profiled = sum(1 for member in members if member.profile_available)
    return TeamMapResponse(
        team_name=payload.team_name,
        member_count=len(members),
        profiled_member_count=profiled,
        unavailable_member_count=len(members) - profiled,
        members=members,
        function_distribution=distribution,
        represented_functions=[group.team_function for group in distribution],
        repeated_functions=[
            RepeatedFunction(
                team_function=group.team_function,
                member_ids=list(group.member_ids),
                count=group.count,
            )
            for group in distribution
            if group.count > 1
        ],
        team_notes=list(TEAM_NOTES),
    )
