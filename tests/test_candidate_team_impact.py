import unittest
from datetime import date, time

from pydantic import ValidationError

from app.core.app import create_app
from app.schemas.candidate_compare import CandidateInput
from app.schemas.candidate_team_impact import CandidateTeamImpactRequest
from app.schemas.team_map import TeamMemberInput
from app.services.candidate_team_impact import analyze_candidate_team_impact

PLACE = "Miami, USA"
EXPLORER = "Explorer / Innovator"
VALIDATOR = "Precision Analyst / Validator"
STRUCTURER = "Structurer / Planner"
CONNECTOR = "Connector / Communicator"
INVESTIGATOR = "Investigator / Root-Cause Analyst"
REQUIRED_ORDER = [EXPLORER, VALIDATOR, STRUCTURER, CONNECTOR]

PROHIBITED_KEYS = {
    "impact_score",
    "fit_score",
    "team_fit",
    "match_percentage",
    "coverage_percentage",
    "candidate_rank",
    "rank",
    "best_candidate",
    "recommended_candidate",
    "hire",
    "reject",
    "hire_recommendation",
    "decision",
    "better_than",
    "score",
}


def _member(
    member_id: str,
    birth_date: date,
    *,
    birth_time: time | None = time(14, 30),
    birth_place: str = PLACE,
    display_name: str | None = None,
    current_role: str | None = "Engineer",
) -> TeamMemberInput:
    return TeamMemberInput(
        member_id=member_id,
        display_name=display_name or f"Member {member_id}",
        current_role=current_role,
        birth_date=birth_date,
        birth_time=birth_time,
        birth_place=birth_place,
    )


def _candidate(
    candidate_id: str,
    birth_date: date,
    *,
    birth_time: time | None = time(14, 30),
    birth_place: str = PLACE,
    display_name: str | None = None,
) -> CandidateInput:
    return CandidateInput(
        candidate_id=candidate_id,
        display_name=display_name or f"Candidate {candidate_id}",
        birth_date=birth_date,
        birth_time=birth_time,
        birth_place=birth_place,
    )


def alex(**kwargs) -> TeamMemberInput:
    defaults = dict(
        member_id="A",
        birth_date=date(1986, 2, 8),
        birth_time=time(20, 20),
        birth_place="Kingisepp, Russia",
        display_name="Alex",
    )
    defaults.update(kwargs)
    return _member(**defaults)


def bella(**kwargs) -> TeamMemberInput:
    defaults = dict(
        member_id="B",
        birth_date=date(1985, 9, 11),
        birth_time=time(0, 21),
        birth_place="Kazan, Russia",
        display_name="Bella",
    )
    defaults.update(kwargs)
    return _member(**defaults)


def chris_member(**kwargs) -> TeamMemberInput:
    defaults = dict(
        member_id="C",
        birth_date=date(1997, 1, 28),
        birth_time=time(10, 0),
        display_name="Chris",
    )
    defaults.update(kwargs)
    return _member(**defaults)


def daniel(**kwargs) -> TeamMemberInput:
    defaults = dict(
        member_id="D",
        birth_date=date(1990, 6, 15),
        display_name="Daniel",
    )
    defaults.update(kwargs)
    return _member(**defaults)


def investigator_member(**kwargs) -> TeamMemberInput:
    defaults = dict(
        member_id="E",
        birth_date=date(1983, 10, 29),
        display_name="Elena",
    )
    defaults.update(kwargs)
    return _member(**defaults)


def chris_candidate(**kwargs) -> CandidateInput:
    defaults = dict(
        candidate_id="C",
        birth_date=date(1997, 1, 28),
        birth_time=time(10, 0),
        display_name="Chris",
    )
    defaults.update(kwargs)
    return _candidate(**defaults)


def explorer_candidate(**kwargs) -> CandidateInput:
    defaults = dict(
        candidate_id="X",
        birth_date=date(1986, 2, 8),
        birth_time=time(20, 20),
        birth_place="Kingisepp, Russia",
        display_name="Ava",
    )
    defaults.update(kwargs)
    return _candidate(**defaults)


def investigator_candidate(**kwargs) -> CandidateInput:
    defaults = dict(
        candidate_id="I",
        birth_date=date(1983, 10, 29),
        display_name="Ivan",
    )
    defaults.update(kwargs)
    return _candidate(**defaults)


def _team_without_structurer() -> list[TeamMemberInput]:
    return [alex(), bella(), daniel()]


def _request(
    members: list[TeamMemberInput],
    candidate: CandidateInput,
    *,
    target_role: str | None = "ML Engineer",
    team_name: str = "AI Platform Team",
) -> CandidateTeamImpactRequest:
    return CandidateTeamImpactRequest(
        team_name=team_name,
        coverage_profile="ai_ml_product_delivery",
        target_role=target_role,
        members=members,
        candidate=candidate,
    )


def _status_map(snapshot):
    return {item.team_function: item for item in snapshot.required_functions}


def _all_keys(payload) -> set[str]:
    if isinstance(payload, dict):
        keys = set(payload.keys())
        for value in payload.values():
            keys |= _all_keys(value)
        return keys
    if isinstance(payload, list):
        keys: set[str] = set()
        for value in payload:
            keys |= _all_keys(value)
        return keys
    return set()


class CandidateTeamImpactValidationTests(unittest.TestCase):
    def test_candidate_id_collision_rejected(self):
        with self.assertRaises(ValidationError):
            _request(_team_without_structurer(), chris_candidate(candidate_id="A"))

    def test_duplicate_member_ids_rejected(self):
        with self.assertRaises(ValidationError):
            _request([alex(), alex(display_name="Alex2")], chris_candidate())

    def test_more_than_twenty_nine_members_rejected(self):
        members = [_member(str(index), date(1990, 3, 21)) for index in range(30)]
        with self.assertRaises(ValidationError):
            _request(members, chris_candidate(candidate_id="CAND"))

    def test_empty_members_rejected(self):
        with self.assertRaises(ValidationError):
            CandidateTeamImpactRequest(
                team_name="Empty",
                coverage_profile="ai_ml_product_delivery",
                members=[],
                candidate=chris_candidate(),
            )


class CandidateTeamImpactServiceTests(unittest.TestCase):
    def test_candidate_closes_missing_structurer_gap(self):
        result = analyze_candidate_team_impact(
            _request(_team_without_structurer(), chris_candidate())
        )
        before = _status_map(result.before)
        after = _status_map(result.after)
        self.assertEqual(before[STRUCTURER].status, "missing")
        self.assertEqual(after[STRUCTURER].status, "single_coverage")
        self.assertEqual(after[STRUCTURER].count, 1)
        self.assertEqual(result.impact.closed_missing_functions, [STRUCTURER])
        self.assertEqual(result.impact.closed_workflow_stages, ["Productionize"])
        self.assertEqual(result.impact.remaining_missing_functions, [])
        self.assertEqual(result.impact.remaining_uncovered_workflow_stages, [])
        self.assertTrue(result.impact.required_coverage_changed)
        self.assertTrue(result.impact.impact_available)
        self.assertEqual(result.candidate.team_function, STRUCTURER)

    def test_candidate_closes_missing_explorer_gap(self):
        result = analyze_candidate_team_impact(
            _request([bella(), chris_member(), daniel()], explorer_candidate())
        )
        before = _status_map(result.before)
        after = _status_map(result.after)
        self.assertEqual(before[EXPLORER].status, "missing")
        self.assertEqual(after[EXPLORER].status, "single_coverage")
        self.assertEqual(result.impact.closed_missing_functions, [EXPLORER])
        self.assertEqual(result.impact.closed_workflow_stages, ["Explore"])
        self.assertTrue(result.impact.required_coverage_changed)

    def test_single_explorer_plus_explorer_is_strengthened(self):
        result = analyze_candidate_team_impact(
            _request(_team_without_structurer(), explorer_candidate())
        )
        before = _status_map(result.before)
        after = _status_map(result.after)
        self.assertEqual(before[EXPLORER].status, "single_coverage")
        self.assertEqual(after[EXPLORER].status, "represented")
        self.assertEqual(after[EXPLORER].count, 2)
        self.assertEqual(result.impact.strengthened_single_coverage_functions, [EXPLORER])
        self.assertEqual(result.impact.closed_missing_functions, [])
        self.assertIn(STRUCTURER, result.impact.remaining_missing_functions)
        self.assertIn("Productionize", result.impact.remaining_uncovered_workflow_stages)
        self.assertTrue(result.impact.required_coverage_changed)

    def test_two_explorers_plus_explorer_is_reinforced_not_coverage_change(self):
        result = analyze_candidate_team_impact(
            _request(
                [alex(), alex(member_id="A2", display_name="Ava"), bella(), chris_member(), daniel()],
                explorer_candidate(candidate_id="X"),
            )
        )
        before = _status_map(result.before)
        after = _status_map(result.after)
        self.assertEqual(before[EXPLORER].status, "represented")
        self.assertEqual(before[EXPLORER].count, 2)
        self.assertEqual(after[EXPLORER].status, "represented")
        self.assertEqual(after[EXPLORER].count, 3)
        self.assertEqual(result.impact.reinforced_represented_functions, [EXPLORER])
        self.assertEqual(result.impact.strengthened_single_coverage_functions, [])
        self.assertFalse(result.impact.required_coverage_changed)

    def test_additional_explorer_does_not_close_structurer_gap(self):
        result = analyze_candidate_team_impact(
            _request(_team_without_structurer(), explorer_candidate())
        )
        self.assertEqual(result.before.missing_required_functions, [STRUCTURER])
        self.assertEqual(result.after.missing_required_functions, [STRUCTURER])
        self.assertIn(STRUCTURER, result.impact.remaining_missing_functions)
        self.assertNotIn(STRUCTURER, result.impact.closed_missing_functions)

    def test_investigator_adds_additional_without_closing_required_gaps(self):
        result = analyze_candidate_team_impact(
            _request(_team_without_structurer(), investigator_candidate())
        )
        self.assertEqual(result.candidate.team_function, INVESTIGATOR)
        self.assertEqual(result.impact.added_additional_functions, [INVESTIGATOR])
        self.assertEqual(result.impact.reinforced_additional_functions, [])
        self.assertEqual(result.impact.closed_missing_functions, [])
        self.assertEqual(result.impact.remaining_missing_functions, [STRUCTURER])
        self.assertEqual(result.impact.remaining_uncovered_workflow_stages, ["Productionize"])
        self.assertFalse(result.impact.required_coverage_changed)

    def test_existing_investigator_plus_investigator_is_reinforced_additional(self):
        result = analyze_candidate_team_impact(
            _request(
                [alex(), bella(), chris_member(), daniel(), investigator_member()],
                investigator_candidate(),
            )
        )
        self.assertIn(INVESTIGATOR, result.before.additional_represented_functions)
        self.assertEqual(result.impact.reinforced_additional_functions, [INVESTIGATOR])
        self.assertEqual(result.impact.added_additional_functions, [])
        self.assertFalse(result.impact.required_coverage_changed)

    def test_investigator_does_not_substitute_for_validator(self):
        result = analyze_candidate_team_impact(
            _request([alex(), chris_member(), daniel()], investigator_candidate())
        )
        self.assertEqual(result.candidate.team_function, INVESTIGATOR)
        self.assertIn(VALIDATOR, result.before.missing_required_functions)
        self.assertIn(VALIDATOR, result.after.missing_required_functions)
        self.assertIn(VALIDATOR, result.impact.remaining_missing_functions)
        self.assertNotIn(VALIDATOR, result.impact.closed_missing_functions)

    def test_investigator_does_not_substitute_for_structurer(self):
        result = analyze_candidate_team_impact(
            _request(_team_without_structurer(), investigator_candidate())
        )
        self.assertIn(STRUCTURER, result.after.missing_required_functions)
        self.assertNotIn(STRUCTURER, result.impact.closed_missing_functions)

    def test_before_member_order_unchanged_in_snapshots_via_required_member_ids(self):
        members = [daniel(), alex(), bella()]
        result = analyze_candidate_team_impact(_request(members, chris_candidate()))
        # Before snapshot member_ids on functions preserve profiling of original team only
        connector = _status_map(result.before)[CONNECTOR]
        explorer = _status_map(result.before)[EXPLORER]
        self.assertEqual(connector.member_ids, ["D"])
        self.assertEqual(explorer.member_ids, ["A"])
        self.assertNotIn("C", [mid for item in result.before.required_functions for mid in item.member_ids])

    def test_after_appends_candidate_last_in_structurer_member_ids(self):
        result = analyze_candidate_team_impact(
            _request([alex(), bella(), daniel()], chris_candidate())
        )
        after_structurer = _status_map(result.after)[STRUCTURER]
        self.assertEqual(after_structurer.member_ids, ["C"])
        self.assertEqual(result.after.member_count, 4)
        self.assertEqual(result.before.member_count, 3)

    def test_target_role_echoed_without_affecting_impact(self):
        first = analyze_candidate_team_impact(
            _request(_team_without_structurer(), chris_candidate(), target_role="Staff Engineer")
        )
        second = analyze_candidate_team_impact(
            _request(_team_without_structurer(), chris_candidate(), target_role="Intern")
        )
        self.assertEqual(first.target_role, "Staff Engineer")
        self.assertEqual(second.target_role, "Intern")
        self.assertEqual(first.impact.model_dump(), second.impact.model_dump())
        self.assertEqual(first.candidate.team_function, second.candidate.team_function)
        self.assertEqual(
            [item.model_dump() for item in first.before.required_functions],
            [item.model_dump() for item in second.before.required_functions],
        )

    def test_candidate_unknown_birth_time_works_when_stable(self):
        result = analyze_candidate_team_impact(
            _request(
                _team_without_structurer(),
                chris_candidate(birth_time=None),
            )
        )
        self.assertTrue(result.candidate.profile_available)
        self.assertEqual(result.candidate.team_function, STRUCTURER)
        self.assertTrue(result.impact.impact_available)
        self.assertEqual(result.impact.closed_missing_functions, [STRUCTURER])

    def test_unavailable_candidate_yields_no_false_no_impact(self):
        result = analyze_candidate_team_impact(
            _request(
                _team_without_structurer(),
                chris_candidate(birth_place="Nowhere, XX"),
            )
        )
        self.assertFalse(result.candidate.profile_available)
        self.assertIsNone(result.candidate.team_function)
        self.assertIsNotNone(result.candidate.error)
        self.assertFalse(result.impact.impact_available)
        self.assertEqual(result.impact.closed_missing_functions, [])
        self.assertEqual(result.impact.strengthened_single_coverage_functions, [])
        self.assertEqual(result.impact.reinforced_represented_functions, [])
        self.assertEqual(result.impact.added_additional_functions, [])
        self.assertFalse(result.impact.required_coverage_changed)
        self.assertEqual(result.before.missing_required_functions, [STRUCTURER])
        notes = " ".join(result.impact_notes)
        self.assertIn("Candidate impact could not be determined because the candidate profile is unavailable.", notes)
        self.assertNotIn("does not change the team", notes.lower())
        self.assertNotIn("no impact", notes.lower())

    def test_unavailable_existing_member_does_not_block_candidate_impact(self):
        result = analyze_candidate_team_impact(
            _request(
                [
                    alex(),
                    bella(),
                    _member("Z", date(1990, 6, 15), birth_place="Atlantis, Ocean", display_name="Zed"),
                ],
                chris_candidate(),
            )
        )
        self.assertGreater(result.before.unavailable_member_count, 0)
        self.assertTrue(result.candidate.profile_available)
        self.assertTrue(result.impact.impact_available)
        self.assertEqual(result.impact.closed_missing_functions, [STRUCTURER])
        self.assertIn(
            "Impact analysis is based only on team members with available profiles.",
            result.impact_notes,
        )

    def test_represented_required_semantics_remain_count_at_least_one(self):
        result = analyze_candidate_team_impact(
            _request(_team_without_structurer(), chris_candidate())
        )
        self.assertEqual(result.before.represented_required_functions, [EXPLORER, VALIDATOR, CONNECTOR])
        self.assertEqual(result.after.represented_required_functions, REQUIRED_ORDER)
        for name in result.after.single_coverage_functions:
            self.assertIn(name, result.after.represented_required_functions)

    def test_single_coverage_semantics_remain_count_one(self):
        result = analyze_candidate_team_impact(
            _request(_team_without_structurer(), chris_candidate())
        )
        for item in result.after.required_functions:
            if item.team_function in result.after.single_coverage_functions:
                self.assertEqual(item.count, 1)
                self.assertEqual(item.status, "single_coverage")

    def test_payload_has_no_score_ranking_or_hiring_fields(self):
        result = analyze_candidate_team_impact(
            _request(_team_without_structurer(), chris_candidate())
        )
        keys = _all_keys(result.model_dump())
        self.assertTrue(PROHIBITED_KEYS.isdisjoint(keys), keys & PROHIBITED_KEYS)
        blob = result.model_dump_json().lower()
        self.assertNotIn("%", blob)
        self.assertNotIn("recommended hire", blob)
        self.assertNotIn("perfect candidate", blob)
        self.assertNotIn("strong fit", blob)
        self.assertNotIn('"better"', blob)


class CandidateTeamImpactRouteTests(unittest.TestCase):
    def test_routes_include_candidate_team_impact_and_existing_endpoints(self):
        app = create_app()
        paths = {getattr(route, "path", None) for route in app.routes}
        self.assertIn("/api/v1/profile", paths)
        self.assertIn("/api/v1/mercury-work-profile", paths)
        self.assertIn("/api/v1/candidate-compare", paths)
        self.assertIn("/api/v1/team-map", paths)
        self.assertIn("/api/v1/team-gap", paths)
        self.assertIn("/api/v1/candidate-team-impact", paths)


if __name__ == "__main__":
    unittest.main()
