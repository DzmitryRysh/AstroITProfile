import unittest
from datetime import date, time
from unittest.mock import patch

from pydantic import ValidationError

from app.core.app import create_app
from app.schemas.mercury_work_profile import (
    MercurySourceFactors,
    MercuryWorkProfileResponse,
)
from app.schemas.team_gap import TeamGapRequest
from app.schemas.team_map import TeamMemberInput
from app.services.team_coverage_profiles import AI_ML_PRODUCT_DELIVERY
from app.services.team_gap import analyze_team_gap
from app.services.team_map import build_team_map

PLACE = "Miami, USA"
EXPLORER = "Explorer / Innovator"
VALIDATOR = "Precision Analyst / Validator"
STRUCTURER = "Structurer / Planner"
CONNECTOR = "Connector / Communicator"
INVESTIGATOR = "Investigator / Root-Cause Analyst"
WORKFLOW_ORDER = ["Explore", "Validate", "Productionize", "Connect"]
REQUIRED_ORDER = [EXPLORER, VALIDATOR, STRUCTURER, CONNECTOR]

PROHIBITED_KEYS = {
    "coverage_score",
    "coverage_percentage",
    "balance_score",
    "gap_score",
    "team_health",
    "fit_score",
    "priority_score",
    "recommended_function_to_hire",
    "recommended_candidate",
    "best_candidate",
    "hire_next",
    "priority_hire",
    "rank",
    "score",
}
JUDGMENT_PHRASES = (
    "insufficient employee",
    "low performer",
    "hire candidate",
    "you must hire",
    "you need to hire",
    "recommended hire",
)


def _member(
    member_id: str,
    birth_date: date,
    *,
    birth_time: time | None = time(14, 30),
    birth_place: str = PLACE,
    display_name: str | None = None,
    current_role: str | None = "ML Engineer",
) -> TeamMemberInput:
    return TeamMemberInput(
        member_id=member_id,
        display_name=display_name or f"Member {member_id}",
        current_role=current_role,
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


def chris(**kwargs) -> TeamMemberInput:
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


def investigator(**kwargs) -> TeamMemberInput:
    defaults = dict(
        member_id="E",
        birth_date=date(1983, 10, 29),
        display_name="Elena",
    )
    defaults.update(kwargs)
    return _member(**defaults)


def _request(members: list[TeamMemberInput], team_name: str = "AI Platform Team"):
    return TeamGapRequest(
        team_name=team_name,
        coverage_profile="ai_ml_product_delivery",
        members=members,
    )


def _status_by_function(result):
    return {item.team_function: item for item in result.required_functions}


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


class TeamGapValidationTests(unittest.TestCase):
    def test_empty_members_rejected(self):
        with self.assertRaises(ValidationError):
            TeamGapRequest(
                team_name="Empty",
                coverage_profile="ai_ml_product_delivery",
                members=[],
            )

    def test_more_than_thirty_members_rejected(self):
        members = [_member(str(index), date(1990, 3, 21)) for index in range(31)]
        with self.assertRaises(ValidationError):
            _request(members)

    def test_duplicate_member_id_rejected(self):
        with self.assertRaises(ValidationError):
            _request([alex(), alex(display_name="Alex 2")])

    def test_coverage_profile_only_accepts_ai_ml_product_delivery(self):
        with self.assertRaises(ValidationError):
            TeamGapRequest(
                team_name="AI Platform Team",
                coverage_profile="full_engineering_org",
                members=[alex()],
            )


class TeamGapServiceTests(unittest.TestCase):
    def test_full_ai_ml_coverage_has_no_missing_functions(self):
        result = analyze_team_gap(_request([alex(), bella(), chris(), daniel()]))
        self.assertEqual(result.coverage_profile, "ai_ml_product_delivery")
        self.assertEqual(result.coverage_profile_name, "AI / ML Product Delivery")
        self.assertEqual(result.missing_required_functions, [])
        self.assertEqual(result.uncovered_workflow_stages, [])
        self.assertEqual(result.represented_required_functions, REQUIRED_ORDER)
        self.assertEqual(result.single_coverage_functions, REQUIRED_ORDER)
        statuses = _status_by_function(result)
        self.assertEqual(statuses[EXPLORER].team_function, EXPLORER)
        self.assertEqual(statuses[VALIDATOR].status, "single_coverage")
        self.assertEqual(statuses[STRUCTURER].status, "single_coverage")
        self.assertEqual(statuses[CONNECTOR].status, "single_coverage")
        self.assertEqual(statuses[EXPLORER].status, "single_coverage")
        self.assertEqual(statuses[EXPLORER].count, 1)
        self.assertEqual(statuses[EXPLORER].member_ids, ["A"])
        self.assertEqual(statuses[VALIDATOR].member_ids, ["B"])
        self.assertEqual(statuses[STRUCTURER].member_ids, ["C"])
        self.assertEqual(statuses[CONNECTOR].member_ids, ["D"])

    def test_missing_structurer_uncovers_productionize(self):
        result = analyze_team_gap(_request([alex(), bella(), daniel()]))
        statuses = _status_by_function(result)
        self.assertEqual(statuses[STRUCTURER].status, "missing")
        self.assertEqual(statuses[STRUCTURER].count, 0)
        self.assertEqual(statuses[STRUCTURER].member_ids, [])
        self.assertEqual(
            result.represented_required_functions,
            [EXPLORER, VALIDATOR, CONNECTOR],
        )
        self.assertEqual(result.missing_required_functions, [STRUCTURER])
        self.assertIn("Productionize", result.uncovered_workflow_stages)
        self.assertNotIn(STRUCTURER, result.represented_required_functions)
        notes = " ".join(result.gap_notes)
        self.assertIn(
            "The current profiled team has no member whose primary Team Function is "
            f"{STRUCTURER} for this coverage profile.",
            notes,
        )
        self.assertIn("structured, repeatable, maintainable", statuses[STRUCTURER].why_it_matters)

    def test_missing_explorer_marks_explore_missing(self):
        result = analyze_team_gap(_request([bella(), chris(), daniel()]))
        statuses = _status_by_function(result)
        self.assertEqual(statuses[EXPLORER].status, "missing")
        self.assertEqual(statuses[EXPLORER].workflow_stage, "Explore")
        self.assertIn(EXPLORER, result.missing_required_functions)
        self.assertNotIn(EXPLORER, result.represented_required_functions)
        self.assertEqual(result.represented_required_functions, [VALIDATOR, STRUCTURER, CONNECTOR])
        self.assertIn("Explore", result.uncovered_workflow_stages)

    def test_represented_required_functions_means_present_and_can_overlap_single_coverage(self):
        result = analyze_team_gap(_request([alex(), bella(), chris(), daniel()]))
        self.assertEqual(result.represented_required_functions, REQUIRED_ORDER)
        self.assertEqual(result.single_coverage_functions, REQUIRED_ORDER)
        self.assertEqual(result.missing_required_functions, [])
        for item in result.required_functions:
            self.assertGreaterEqual(item.count, 1)
            self.assertEqual(item.status, "single_coverage")
            self.assertIn(item.team_function, result.represented_required_functions)
            self.assertIn(item.team_function, result.single_coverage_functions)

    def test_one_member_per_required_function_is_single_coverage_not_weak(self):
        result = analyze_team_gap(_request([alex(), bella(), chris(), daniel()]))
        for item in result.required_functions:
            self.assertEqual(item.status, "single_coverage")
            self.assertNotEqual(item.status, "weak")
        blob = result.model_dump_json().lower()
        self.assertNotIn('"weak"', blob)
        self.assertNotIn("employee is weak", blob)
        for phrase in JUDGMENT_PHRASES:
            self.assertNotIn(phrase, blob)

    def test_two_explorer_members_are_represented_with_count_two(self):
        result = analyze_team_gap(
            _request(
                [
                    alex(),
                    alex(member_id="A2", display_name="Ava"),
                    bella(),
                    chris(),
                    daniel(),
                ]
            )
        )
        statuses = _status_by_function(result)
        self.assertEqual(statuses[EXPLORER].status, "represented")
        self.assertEqual(statuses[EXPLORER].count, 2)
        self.assertEqual(statuses[EXPLORER].member_ids, ["A", "A2"])
        self.assertEqual(
            result.represented_required_functions,
            [EXPLORER, VALIDATOR, STRUCTURER, CONNECTOR],
        )
        self.assertIn(EXPLORER, result.represented_required_functions)
        self.assertNotIn(EXPLORER, result.single_coverage_functions)
        self.assertNotIn(EXPLORER, result.missing_required_functions)

    def test_repeated_explorer_does_not_fill_missing_structurer(self):
        result = analyze_team_gap(
            _request(
                [
                    alex(),
                    alex(member_id="A2", display_name="Ava"),
                    bella(),
                    daniel(),
                ]
            )
        )
        statuses = _status_by_function(result)
        self.assertEqual(statuses[EXPLORER].status, "represented")
        self.assertEqual(statuses[EXPLORER].count, 2)
        self.assertIn(EXPLORER, result.represented_required_functions)
        self.assertEqual(statuses[STRUCTURER].status, "missing")
        self.assertEqual(
            result.represented_required_functions,
            [EXPLORER, VALIDATOR, CONNECTOR],
        )
        self.assertEqual(result.missing_required_functions, [STRUCTURER])
        self.assertIn("Productionize", result.uncovered_workflow_stages)

    def test_investigator_is_additional_and_does_not_substitute_validator(self):
        result = analyze_team_gap(_request([alex(), chris(), daniel(), investigator()]))
        statuses = _status_by_function(result)
        self.assertEqual(result.members[3].team_function, INVESTIGATOR)
        self.assertIn(INVESTIGATOR, result.additional_represented_functions)
        self.assertEqual(statuses[VALIDATOR].status, "missing")
        self.assertIn(VALIDATOR, result.missing_required_functions)
        self.assertNotIn(INVESTIGATOR, result.missing_required_functions)
        self.assertNotIn(INVESTIGATOR, result.represented_required_functions)
        notes = " ".join(result.gap_notes).lower()
        self.assertNotIn("unnecessary", notes)

    def test_member_order_is_preserved(self):
        result = analyze_team_gap(_request([daniel(), alex(), bella(), chris()]))
        self.assertEqual([item.member_id for item in result.members], ["D", "A", "B", "C"])

    def test_unknown_birth_time_works_when_profile_available(self):
        result = analyze_team_gap(
            _request(
                [
                    alex(),
                    bella(),
                    chris(),
                    daniel(birth_time=None),
                ]
            )
        )
        connector = next(item for item in result.members if item.member_id == "D")
        self.assertTrue(connector.profile_available)
        self.assertEqual(connector.team_function, CONNECTOR)
        self.assertEqual(result.unavailable_member_count, 0)
        statuses = _status_by_function(result)
        self.assertEqual(statuses[CONNECTOR].status, "single_coverage")

    def test_invalid_place_member_is_isolated(self):
        result = analyze_team_gap(
            _request(
                [
                    alex(),
                    bella(),
                    chris(),
                    _member("X", date(1990, 6, 15), birth_place="Atlantis, Ocean", display_name="Unknown"),
                ]
            )
        )
        self.assertTrue(result.members[0].profile_available)
        self.assertTrue(result.members[1].profile_available)
        self.assertTrue(result.members[2].profile_available)
        failed = result.members[3]
        self.assertFalse(failed.profile_available)
        self.assertIsNone(failed.team_function)
        self.assertIsNotNone(failed.error)
        self.assertIn("Unknown place", failed.error)
        self.assertEqual(result.profiled_member_count, 3)
        self.assertEqual(result.unavailable_member_count, 1)
        statuses = _status_by_function(result)
        self.assertEqual(statuses[CONNECTOR].status, "missing")
        self.assertNotIn("X", [mid for item in result.required_functions for mid in item.member_ids])

    def test_gap_conclusions_use_only_profiled_members(self):
        result = analyze_team_gap(
            _request(
                [
                    alex(),
                    _member("X", date(1997, 1, 28), birth_time=time(10, 0), birth_place="Atlantis, Ocean"),
                ]
            )
        )
        statuses = _status_by_function(result)
        self.assertEqual(statuses[EXPLORER].member_ids, ["A"])
        self.assertEqual(statuses[STRUCTURER].status, "missing")
        self.assertEqual(statuses[STRUCTURER].count, 0)
        self.assertNotIn("X", statuses[STRUCTURER].member_ids)
        self.assertEqual(result.profiled_member_count, 1)

    def test_unavailable_member_adds_explanatory_note(self):
        result = analyze_team_gap(
            _request(
                [
                    alex(),
                    bella(),
                    chris(),
                    daniel(birth_place="Atlantis, Ocean"),
                ]
            )
        )
        self.assertGreater(result.unavailable_member_count, 0)
        self.assertIn(
            "Gap analysis is based only on members with available profiles.",
            result.gap_notes,
        )

    def test_current_role_does_not_affect_gap_calculation(self):
        first = analyze_team_gap(
            _request(
                [
                    alex(current_role="Research Scientist"),
                    bella(current_role="QA Lead"),
                    chris(current_role="Delivery Manager"),
                    daniel(current_role="Product Engineer"),
                ]
            )
        )
        second = analyze_team_gap(
            _request(
                [
                    alex(current_role="Intern"),
                    bella(current_role="Intern"),
                    chris(current_role="Intern"),
                    daniel(current_role="Intern"),
                ]
            )
        )
        self.assertEqual(first.members[0].current_role, "Research Scientist")
        self.assertEqual(second.members[0].current_role, "Intern")
        self.assertEqual(
            [item.team_function for item in first.members],
            [item.team_function for item in second.members],
        )
        self.assertEqual(
            [item.model_dump() for item in first.required_functions],
            [item.model_dump() for item in second.required_functions],
        )
        self.assertEqual(first.missing_required_functions, second.missing_required_functions)
        self.assertEqual(first.single_coverage_functions, second.single_coverage_functions)

    def test_required_functions_remain_in_workflow_order(self):
        result = analyze_team_gap(_request([daniel(), bella(), alex()]))
        self.assertEqual([item.workflow_stage for item in result.required_functions], WORKFLOW_ORDER)
        self.assertEqual([item.team_function for item in result.required_functions], REQUIRED_ORDER)
        self.assertEqual(
            [item.team_function for item in AI_ML_PRODUCT_DELIVERY.required_functions],
            REQUIRED_ORDER,
        )

    def test_payload_has_no_score_percentage_rank_or_hiring_fields(self):
        result = analyze_team_gap(_request([alex(), bella(), chris(), daniel()]))
        dumped = result.model_dump()
        keys = _all_keys(dumped)
        self.assertTrue(PROHIBITED_KEYS.isdisjoint(keys), keys & PROHIBITED_KEYS)
        blob = result.model_dump_json()
        self.assertNotIn("%", blob)
        self.assertNotIn("3/4", blob)
        self.assertNotIn("75%", blob)

    def test_gap_notes_are_architectural_not_evaluative(self):
        result = analyze_team_gap(_request([alex(), bella(), daniel()]))
        notes = " ".join(result.gap_notes)
        self.assertIn("selected workflow profile", notes)
        self.assertIn("not a performance judgment", notes)
        self.assertIn("one profiled member currently represents that workflow function", notes)
        self.assertIn("does not recommend a specific hiring decision", notes)
        self.assertNotIn("Capricorn", notes)
        self.assertNotIn("cannot succeed", notes.lower())

    def test_reuses_team_map_member_order_and_failures(self):
        from app.schemas.team_map import TeamMapRequest

        members = [
            alex(),
            _member("X", date(1990, 6, 15), birth_place="Atlantis, Ocean"),
            bella(),
        ]
        mapped_result = build_team_map(TeamMapRequest(team_name="AI Platform Team", members=members))
        result = analyze_team_gap(_request(members))
        self.assertEqual(
            [item.member_id for item in result.members],
            [item.member_id for item in mapped_result.members],
        )
        self.assertEqual(result.profiled_member_count, mapped_result.profiled_member_count)
        self.assertEqual(result.unavailable_member_count, mapped_result.unavailable_member_count)
        self.assertEqual(
            [item.team_function for item in result.members],
            [item.team_function for item in mapped_result.members],
        )

    def test_null_recruiter_view_does_not_count_toward_coverage(self):
        empty = MercuryWorkProfileResponse(
            thinking="",
            learning="",
            communication="",
            strengths=[],
            risks=[],
            team_value="",
            possible_roles=[],
            source_factors=MercurySourceFactors(birth_time_known=False),
            limitations=["Interpretation omitted because Mercury sign is unavailable; no guess was made."],
            recruiter_view=None,
        )
        with patch("app.services.team_map.build_mercury_work_profile", return_value=empty):
            result = analyze_team_gap(_request([alex(), bella(), chris(), daniel()]))
        self.assertEqual(result.profiled_member_count, 0)
        self.assertEqual(result.unavailable_member_count, 4)
        self.assertEqual(result.missing_required_functions, REQUIRED_ORDER)
        self.assertEqual(result.uncovered_workflow_stages, WORKFLOW_ORDER)
        self.assertEqual(result.represented_required_functions, [])
        self.assertIn(
            "Gap analysis is based only on members with available profiles.",
            result.gap_notes,
        )


class TeamGapRouteTests(unittest.TestCase):
    def test_routes_include_team_gap_and_existing_endpoints(self):
        app = create_app()
        paths = {getattr(route, "path", None) for route in app.routes}
        self.assertIn("/api/v1/profile", paths)
        self.assertIn("/api/v1/mercury-work-profile", paths)
        self.assertIn("/api/v1/candidate-compare", paths)
        self.assertIn("/api/v1/team-map", paths)
        self.assertIn("/api/v1/team-gap", paths)


if __name__ == "__main__":
    unittest.main()
