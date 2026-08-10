"""Candidate Team Impact v1 — before/after Team Gap comparison."""

from __future__ import annotations

from app.schemas.candidate_compare import CandidateInput
from app.schemas.candidate_team_impact import (
    CandidateImpactProfile,
    CandidateImpactSummary,
    CandidateTeamImpactRequest,
    CandidateTeamImpactResponse,
    TeamCoverageSnapshot,
)
from app.schemas.team_gap import TeamGapRequest, TeamGapResponse
from app.schemas.team_map import TeamMemberInput
from app.services.team_gap import analyze_team_gap

BASE_IMPACT_NOTES = [
    "Candidate Team Impact compares workflow-function coverage before and after adding one candidate.",
    "Changes describe team-function coverage and are not candidate rankings.",
    "Closing a workflow gap does not by itself constitute a hiring recommendation.",
    "Strengthening an existing function is descriptive and is not automatically better or worse than adding a new function.",
]

CANDIDATE_UNAVAILABLE_NOTE = (
    "Candidate impact could not be determined because the candidate profile is unavailable."
)

TEAM_UNAVAILABLE_NOTE = (
    "Impact analysis is based only on team members with available profiles."
)

_STATUS_PROGRESSION = {
    ("missing", "single_coverage"),
    ("missing", "represented"),
    ("single_coverage", "represented"),
}


def _candidate_as_member(
    candidate: CandidateInput,
    *,
    current_role: str | None,
) -> TeamMemberInput:
    return TeamMemberInput(
        member_id=candidate.candidate_id,
        display_name=candidate.display_name,
        current_role=current_role,
        birth_date=candidate.birth_date,
        birth_time=candidate.birth_time,
        birth_place=candidate.birth_place,
    )


def _snapshot(gap: TeamGapResponse) -> TeamCoverageSnapshot:
    return TeamCoverageSnapshot(
        member_count=gap.member_count,
        profiled_member_count=gap.profiled_member_count,
        unavailable_member_count=gap.unavailable_member_count,
        required_functions=list(gap.required_functions),
        represented_required_functions=list(gap.represented_required_functions),
        missing_required_functions=list(gap.missing_required_functions),
        single_coverage_functions=list(gap.single_coverage_functions),
        uncovered_workflow_stages=list(gap.uncovered_workflow_stages),
        additional_represented_functions=list(gap.additional_represented_functions),
    )


def _empty_impact(*, remaining_missing: list[str], remaining_stages: list[str]) -> CandidateImpactSummary:
    return CandidateImpactSummary(
        impact_available=False,
        closed_missing_functions=[],
        closed_workflow_stages=[],
        strengthened_single_coverage_functions=[],
        reinforced_represented_functions=[],
        added_additional_functions=[],
        reinforced_additional_functions=[],
        remaining_missing_functions=list(remaining_missing),
        remaining_uncovered_workflow_stages=list(remaining_stages),
        required_coverage_changed=False,
    )


def _compare_gaps(
    before: TeamGapResponse,
    after: TeamGapResponse,
    candidate_function: str | None,
) -> CandidateImpactSummary:
    before_by_fn = {item.team_function: item for item in before.required_functions}

    closed_missing: list[str] = []
    closed_stages: list[str] = []
    strengthened: list[str] = []
    reinforced: list[str] = []
    required_coverage_changed = False

    for team_function, before_item in before_by_fn.items():
        after_item = next(
            item for item in after.required_functions if item.team_function == team_function
        )
        pair = (before_item.status, after_item.status)
        if pair in _STATUS_PROGRESSION:
            required_coverage_changed = True
        if before_item.status == "missing" and after_item.status != "missing":
            closed_missing.append(team_function)
            closed_stages.append(before_item.workflow_stage)
        elif before_item.status == "single_coverage" and after_item.status == "represented":
            strengthened.append(team_function)
        elif (
            before_item.status == "represented"
            and after_item.status == "represented"
            and after_item.count > before_item.count
        ):
            reinforced.append(team_function)

    before_additional = set(before.additional_represented_functions)
    after_additional = set(after.additional_represented_functions)
    added_additional: list[str] = []
    reinforced_additional: list[str] = []
    if candidate_function and candidate_function in after_additional:
        if candidate_function in before_additional:
            reinforced_additional.append(candidate_function)
        else:
            added_additional.append(candidate_function)

    return CandidateImpactSummary(
        impact_available=True,
        closed_missing_functions=closed_missing,
        closed_workflow_stages=closed_stages,
        strengthened_single_coverage_functions=strengthened,
        reinforced_represented_functions=reinforced,
        added_additional_functions=added_additional,
        reinforced_additional_functions=reinforced_additional,
        remaining_missing_functions=list(after.missing_required_functions),
        remaining_uncovered_workflow_stages=list(after.uncovered_workflow_stages),
        required_coverage_changed=required_coverage_changed,
    )


def analyze_candidate_team_impact(
    payload: CandidateTeamImpactRequest,
) -> CandidateTeamImpactResponse:
    before = analyze_team_gap(
        TeamGapRequest(
            team_name=payload.team_name,
            coverage_profile=payload.coverage_profile,
            members=list(payload.members),
        )
    )

    candidate_member = _candidate_as_member(
        payload.candidate,
        current_role=payload.target_role,
    )
    after_members = list(payload.members) + [candidate_member]
    after = analyze_team_gap(
        TeamGapRequest(
            team_name=payload.team_name,
            coverage_profile=payload.coverage_profile,
            members=after_members,
        )
    )

    candidate_gap_member = next(
        (item for item in after.members if item.member_id == payload.candidate.candidate_id),
        None,
    )
    if candidate_gap_member is None:
        candidate_profile = CandidateImpactProfile(
            candidate_id=payload.candidate.candidate_id,
            display_name=payload.candidate.display_name,
            profile_available=False,
            team_function=None,
            limitations=[],
            error="Candidate profile could not be located in the after-team analysis.",
        )
    else:
        candidate_profile = CandidateImpactProfile(
            candidate_id=candidate_gap_member.member_id,
            display_name=candidate_gap_member.display_name,
            profile_available=candidate_gap_member.profile_available,
            team_function=candidate_gap_member.team_function,
            limitations=list(candidate_gap_member.limitations),
            error=candidate_gap_member.error,
        )

    notes = list(BASE_IMPACT_NOTES)
    if before.unavailable_member_count > 0:
        notes.append(TEAM_UNAVAILABLE_NOTE)

    if not candidate_profile.profile_available:
        impact = _empty_impact(
            remaining_missing=after.missing_required_functions,
            remaining_stages=after.uncovered_workflow_stages,
        )
        notes.append(CANDIDATE_UNAVAILABLE_NOTE)
    else:
        impact = _compare_gaps(before, after, candidate_profile.team_function)

    return CandidateTeamImpactResponse(
        team_name=payload.team_name,
        coverage_profile=before.coverage_profile,
        coverage_profile_name=before.coverage_profile_name,
        target_role=payload.target_role,
        candidate=candidate_profile,
        before=_snapshot(before),
        after=_snapshot(after),
        impact=impact,
        impact_notes=notes,
    )
