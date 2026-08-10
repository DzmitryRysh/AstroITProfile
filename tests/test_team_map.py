import unittest
from datetime import date, time
from unittest.mock import patch

from pydantic import ValidationError

from app.core.app import create_app
from app.schemas.mercury_work_profile import (
    MercurySourceFactors,
    MercuryWorkProfileRequest,
    MercuryWorkProfileResponse,
)
from app.schemas.team_map import TeamMapRequest, TeamMemberInput
from app.services.mercury_work_profile import build_mercury_work_profile
from app.services.team_map import build_team_map

PLACE = "Miami, USA"
ASTRO_SOURCE_KEYS = {
    "mercury_sign",
    "mercury_element",
    "mercury_longitude",
    "mercury_motion",
    "mercury_house",
    "house_system_used",
    "aspects",
    "major_dispositor",
    "minor_dispositor",
    "source_factors",
}
PROHIBITED_KEYS = {
    "missing_functions",
    "team_gaps",
    "coverage_score",
    "balance_score",
    "diversity_score",
    "recommended_hire",
    "rank",
    "score",
}
ASTRO_TERMS = ("mercury", "house", "aspect", "dispositor", "retrograde", "zodiac")
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


def _request(members: list[TeamMemberInput], team_name: str = "AI Platform Team"):
    return TeamMapRequest(team_name=team_name, members=members)


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


class TeamMapValidationTests(unittest.TestCase):
    def test_empty_members_rejected(self):
        with self.assertRaises(ValidationError):
            TeamMapRequest(team_name="Empty", members=[])

    def test_more_than_thirty_members_rejected(self):
        members = [_member(str(index), date(1990, 3, 21)) for index in range(31)]
        with self.assertRaises(ValidationError):
            _request(members)

    def test_duplicate_member_id_rejected(self):
        with self.assertRaises(ValidationError):
            _request(
                [
                    _member("A", date(1990, 3, 21)),
                    _member("A", date(1990, 6, 15)),
                ]
            )


class TeamMapServiceTests(unittest.TestCase):
    def test_one_member_team_works(self):
        result = build_team_map(_request([_member("A", date(1990, 3, 21))]))
        self.assertEqual(result.member_count, 1)
        self.assertEqual(result.profiled_member_count, 1)
        self.assertEqual(result.unavailable_member_count, 0)
        self.assertTrue(result.members[0].profile_available)
        self.assertTrue(result.members[0].team_function)
        self.assertEqual(len(result.team_notes), 3)

    def test_four_member_team_works(self):
        result = build_team_map(
            _request(
                [
                    _member("A", date(1986, 2, 8), birth_time=time(20, 20), birth_place="Kingisepp, Russia"),
                    _member("B", date(1985, 9, 11), birth_time=time(0, 21), birth_place="Kazan, Russia"),
                    _member("C", date(1997, 1, 28), birth_time=time(10, 0)),
                    _member("D", date(1990, 6, 15)),
                ]
            )
        )
        self.assertEqual(result.member_count, 4)
        self.assertEqual(result.profiled_member_count, 4)
        self.assertEqual([item.member_id for item in result.members], ["A", "B", "C", "D"])
        self.assertTrue(all(item.profile_available for item in result.members))

    def test_member_order_is_preserved(self):
        result = build_team_map(
            _request(
                [
                    _member("Z", date(1990, 6, 15)),
                    _member("A", date(1990, 3, 21)),
                    _member("M", date(1992, 12, 25)),
                ]
            )
        )
        self.assertEqual([item.member_id for item in result.members], ["Z", "A", "M"])

    def test_current_role_is_echoed_without_changing_profile(self):
        birth = date(1990, 6, 15)
        first = build_team_map(
            _request([_member("A", birth, current_role="ML Engineer"), _member("B", date(1990, 3, 21))])
        )
        second = build_team_map(
            _request([_member("A", birth, current_role="Backend Engineer"), _member("B", date(1990, 3, 21))])
        )
        self.assertEqual(first.members[0].current_role, "ML Engineer")
        self.assertEqual(second.members[0].current_role, "Backend Engineer")
        skip = {"member_id", "display_name", "current_role"}
        self.assertEqual(
            first.members[0].model_dump(exclude=skip),
            second.members[0].model_dump(exclude=skip),
        )

    def test_recruiter_view_fields_are_reused_exactly(self):
        birth = date(1990, 6, 15)
        mercury = build_mercury_work_profile(
            MercuryWorkProfileRequest(birth_date=birth, birth_place=PLACE, birth_time=time(14, 30))
        )
        result = build_team_map(_request([_member("A", birth), _member("B", date(1990, 3, 21))]))
        item = result.members[0]
        view = mercury.recruiter_view
        self.assertIsNotNone(view)
        self.assertEqual(item.team_function, view.team_function)
        self.assertEqual(item.thinking_style, view.thinking_style)
        self.assertEqual(item.top_skills, view.top_skills)
        self.assertEqual(item.key_risks, view.key_risks)
        self.assertEqual(item.team_contribution, view.team_contribution)
        self.assertEqual(item.communication_style, view.communication_style)
        self.assertEqual(item.onboarding_guidance, view.onboarding_guidance)
        self.assertEqual(item.role_directions, view.role_directions)

    def test_function_distribution_groups_and_preserves_first_appearance(self):
        result = build_team_map(
            _request(
                [
                    _member("A", date(1990, 6, 15)),
                    _member("B", date(1990, 3, 21)),
                    _member("D", date(1990, 6, 15), display_name="Second Gemini"),
                ]
            )
        )
        names = [group.team_function for group in result.function_distribution]
        self.assertEqual(names, result.represented_functions)
        self.assertEqual(names[0], result.members[0].team_function)
        self.assertEqual(result.function_distribution[0].member_ids, ["A", "D"])
        self.assertEqual(result.function_distribution[0].count, 2)
        self.assertEqual(result.function_distribution[1].member_ids, ["B"])
        self.assertEqual(result.function_distribution[1].count, 1)

    def test_represented_functions_are_unique_and_deterministic(self):
        result = build_team_map(
            _request(
                [
                    _member("A", date(1990, 6, 15)),
                    _member("B", date(1990, 3, 21)),
                    _member("D", date(1990, 6, 15)),
                ]
            )
        )
        self.assertEqual(len(result.represented_functions), len(set(result.represented_functions)))
        self.assertEqual(
            result.represented_functions,
            [group.team_function for group in result.function_distribution],
        )

    def test_repeated_functions_only_count_above_one_without_judgment(self):
        result = build_team_map(
            _request(
                [
                    _member("A", date(1990, 6, 15), display_name="Daniel"),
                    _member("B", date(1990, 3, 21)),
                    _member("D", date(1990, 6, 15), display_name="Dana"),
                ]
            )
        )
        self.assertEqual(len(result.repeated_functions), 1)
        repeated = result.repeated_functions[0]
        self.assertEqual(repeated.team_function, result.members[0].team_function)
        self.assertEqual(repeated.member_ids, ["A", "D"])
        self.assertEqual(repeated.count, 2)
        notes = " ".join(result.team_notes).lower()
        self.assertIn("not automatically strengths or weaknesses", notes)
        self.assertNotIn("redundancy", notes)
        self.assertNotIn("imbalance", notes)
        dumped = result.model_dump()
        self.assertNotIn("redundancy", _all_keys(dumped))

    def test_unknown_birth_time_works_when_sign_is_stable(self):
        result = build_team_map(
            _request(
                [
                    _member("A", date(1990, 3, 21), birth_time=None),
                    _member("B", date(1990, 6, 15)),
                ]
            )
        )
        self.assertTrue(result.members[0].profile_available)
        self.assertTrue(result.members[0].team_function)
        self.assertEqual(result.profiled_member_count, 2)
        self.assertEqual(result.unavailable_member_count, 0)

    def test_unknown_place_does_not_destroy_valid_members(self):
        result = build_team_map(
            _request(
                [
                    _member("A", date(1990, 3, 21)),
                    _member("B", date(1990, 6, 15), birth_place="Atlantis, Ocean"),
                    _member("C", date(1992, 12, 25)),
                ]
            )
        )
        self.assertTrue(result.members[0].profile_available)
        self.assertTrue(result.members[2].profile_available)
        failed = result.members[1]
        self.assertFalse(failed.profile_available)
        self.assertIsNotNone(failed.error)
        self.assertIn("Unknown place", failed.error)
        self.assertEqual(result.profiled_member_count, 2)
        self.assertEqual(result.unavailable_member_count, 1)
        self.assertNotIn("B", [mid for group in result.function_distribution for mid in group.member_ids])

    def test_payload_has_no_astrology_or_gap_fields(self):
        result = build_team_map(
            _request(
                [
                    _member("A", date(1990, 3, 21)),
                    _member("B", date(1990, 6, 15)),
                ]
            )
        )
        dumped = result.model_dump()
        keys = _all_keys(dumped)
        self.assertTrue(ASTRO_SOURCE_KEYS.isdisjoint(keys), keys & ASTRO_SOURCE_KEYS)
        self.assertTrue(PROHIBITED_KEYS.isdisjoint(keys), keys & PROHIBITED_KEYS)
        for member in dumped["members"]:
            blob = " ".join(
                str(value) for value in member.values() if not isinstance(value, list)
            ).lower()
            blob = (
                f"{blob} {' '.join(member['top_skills'] + member['key_risks'] + member['onboarding_guidance'] + member['role_directions'])}"
            ).lower()
            for term in ASTRO_TERMS:
                self.assertNotIn(term, blob.split(), msg=f"{member['member_id']} contains {term}")

    def test_null_recruiter_view_counts_as_unavailable(self):
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
            result = build_team_map(_request([_member("A", date(1990, 3, 21))]))
        self.assertFalse(result.members[0].profile_available)
        self.assertEqual(result.profiled_member_count, 0)
        self.assertEqual(result.unavailable_member_count, 1)
        self.assertEqual(result.function_distribution, [])
        self.assertEqual(result.represented_functions, [])
        self.assertEqual(result.repeated_functions, [])


class TeamMapRouteTests(unittest.TestCase):
    def test_routes_include_all_profile_endpoints(self):
        app = create_app()
        paths = {getattr(route, "path", None) for route in app.routes}
        self.assertIn("/api/v1/profile", paths)
        self.assertIn("/api/v1/mercury-work-profile", paths)
        self.assertIn("/api/v1/candidate-compare", paths)
        self.assertIn("/api/v1/team-map", paths)


if __name__ == "__main__":
    unittest.main()
