import unittest
from datetime import date, time
from unittest.mock import patch

from pydantic import ValidationError

from app.core.app import create_app
from app.schemas.candidate_compare import (
    CandidateCompareRequest,
    CandidateInput,
)
from app.schemas.mercury_work_profile import (
    MercurySourceFactors,
    MercuryWorkProfileRequest,
    MercuryWorkProfileResponse,
)
from app.services.candidate_compare import compare_candidates
from app.services.mercury_work_profile import build_mercury_work_profile

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
RANKING_KEYS = {
    "score",
    "rank",
    "match_percentage",
    "recommended_candidate",
    "hire",
    "reject",
}
ASTRO_TERMS = ("mercury", "house", "aspect", "dispositor", "retrograde", "zodiac")


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


def _request(candidates: list[CandidateInput], target_role: str = "ML Engineer"):
    return CandidateCompareRequest(target_role=target_role, candidates=candidates)


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


class CandidateCompareValidationTests(unittest.TestCase):
    def test_less_than_two_candidates_rejected(self):
        with self.assertRaises(ValidationError):
            _request([_candidate("A", date(1990, 3, 21))])

    def test_more_than_eight_candidates_rejected(self):
        people = [
            _candidate(str(index), date(1990, 3, 21))
            for index in range(9)
        ]
        with self.assertRaises(ValidationError):
            _request(people)

    def test_duplicate_candidate_id_rejected(self):
        with self.assertRaises(ValidationError):
            _request(
                [
                    _candidate("A", date(1990, 3, 21)),
                    _candidate("A", date(1990, 6, 15)),
                ]
            )


class CandidateCompareServiceTests(unittest.TestCase):
    def test_two_valid_candidates_work(self):
        result = compare_candidates(
            _request(
                [
                    _candidate("A", date(1990, 3, 21)),
                    _candidate("B", date(1990, 6, 15)),
                ]
            )
        )
        self.assertEqual(result.candidate_count, 2)
        self.assertEqual(result.target_role, "ML Engineer")
        self.assertTrue(all(item.profile_available for item in result.candidates))
        self.assertEqual(len(result.comparison_notes), 3)

    def test_four_valid_candidates_work(self):
        result = compare_candidates(
            _request(
                [
                    _candidate("A", date(1986, 2, 8), birth_time=time(20, 20), birth_place="Kingisepp, Russia"),
                    _candidate("B", date(1985, 9, 11), birth_time=time(0, 21), birth_place="Kazan, Russia"),
                    _candidate("C", date(1997, 1, 28), birth_time=time(10, 0)),
                    _candidate("D", date(1990, 6, 15)),
                ]
            )
        )
        self.assertEqual(result.candidate_count, 4)
        self.assertEqual([item.candidate_id for item in result.candidates], ["A", "B", "C", "D"])
        self.assertTrue(all(item.profile_available for item in result.candidates))

    def test_target_role_is_echoed_without_changing_profiles(self):
        candidates = [
            _candidate("A", date(1990, 3, 21)),
            _candidate("B", date(1990, 6, 15)),
        ]
        first = compare_candidates(_request(candidates, target_role="ML Engineer"))
        second = compare_candidates(_request(candidates, target_role="Backend Engineer"))
        self.assertEqual(first.target_role, "ML Engineer")
        self.assertEqual(second.target_role, "Backend Engineer")
        self.assertEqual(
            [item.model_dump(exclude={"candidate_id", "display_name"}) for item in first.candidates],
            [item.model_dump(exclude={"candidate_id", "display_name"}) for item in second.candidates],
        )

    def test_candidate_order_is_preserved(self):
        result = compare_candidates(
            _request(
                [
                    _candidate("Z", date(1990, 6, 15)),
                    _candidate("A", date(1990, 3, 21)),
                    _candidate("M", date(1992, 12, 25)),
                ]
            )
        )
        self.assertEqual([item.candidate_id for item in result.candidates], ["Z", "A", "M"])

    def test_recruiter_view_fields_are_reused_exactly(self):
        birth = date(1990, 6, 15)
        mercury = build_mercury_work_profile(
            MercuryWorkProfileRequest(birth_date=birth, birth_place=PLACE, birth_time=time(14, 30))
        )
        result = compare_candidates(_request([_candidate("A", birth), _candidate("B", date(1990, 3, 21))]))
        item = result.candidates[0]
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

    def test_function_distribution_groups_and_shares_same_function(self):
        aries = _candidate("A", date(1990, 3, 21))
        gemini = _candidate("B", date(1990, 6, 15))
        aries_again = _candidate("D", date(1990, 3, 21), display_name="Second Aries")
        result = compare_candidates(_request([aries, gemini, aries_again]))
        functions = {item.team_function: item.candidate_ids for item in result.function_distribution}
        self.assertEqual(result.function_distribution[0].candidate_ids[0], "A")
        self.assertIn("A", functions[result.candidates[0].team_function])
        self.assertIn("D", functions[result.candidates[0].team_function])
        self.assertEqual(
            functions[result.candidates[0].team_function],
            ["A", "D"],
        )
        self.assertEqual(functions[result.candidates[1].team_function], ["B"])

    def test_unknown_birth_time_still_works_when_sign_is_stable(self):
        result = compare_candidates(
            _request(
                [
                    _candidate("A", date(1990, 3, 21), birth_time=None),
                    _candidate("B", date(1990, 6, 15)),
                ]
            )
        )
        self.assertTrue(result.candidates[0].profile_available)
        self.assertTrue(result.candidates[0].team_function)
        self.assertTrue(result.candidates[1].profile_available)

    def test_unknown_place_does_not_destroy_valid_profiles(self):
        result = compare_candidates(
            _request(
                [
                    _candidate("A", date(1990, 3, 21)),
                    _candidate("B", date(1990, 6, 15), birth_place="Atlantis, Ocean"),
                    _candidate("C", date(1992, 12, 25)),
                ]
            )
        )
        self.assertTrue(result.candidates[0].profile_available)
        self.assertTrue(result.candidates[2].profile_available)
        failed = result.candidates[1]
        self.assertFalse(failed.profile_available)
        self.assertIsNotNone(failed.error)
        self.assertIn("Unknown place", failed.error)
        self.assertEqual(failed.top_skills, [])
        self.assertIsNone(failed.team_function)
        ids_in_distribution = [
            cid for item in result.function_distribution for cid in item.candidate_ids
        ]
        self.assertNotIn("B", ids_in_distribution)

    def test_null_recruiter_view_does_not_guess_profile(self):
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
        with patch(
            "app.services.candidate_compare.build_mercury_work_profile",
            return_value=empty,
        ):
            result = compare_candidates(
                _request(
                    [
                        _candidate("A", date(1990, 3, 21)),
                        _candidate("B", date(1990, 6, 15)),
                    ]
                )
            )
        for item in result.candidates:
            self.assertFalse(item.profile_available)
            self.assertIsNone(item.team_function)
            self.assertEqual(item.top_skills, [])
            self.assertEqual(item.key_risks, [])
            self.assertTrue(item.error)
        self.assertEqual(result.function_distribution, [])

    def test_compare_response_has_no_astrology_source_or_ranking_fields(self):
        result = compare_candidates(
            _request(
                [
                    _candidate("A", date(1990, 3, 21)),
                    _candidate("B", date(1990, 6, 15)),
                ]
            )
        )
        dumped = result.model_dump()
        keys = _all_keys(dumped)
        self.assertTrue(ASTRO_SOURCE_KEYS.isdisjoint(keys), keys & ASTRO_SOURCE_KEYS)
        self.assertTrue(RANKING_KEYS.isdisjoint(keys), keys & RANKING_KEYS)
        for item in dumped["candidates"]:
            blob = " ".join(
                str(value)
                for value in item.values()
                if not isinstance(value, list)
            ).lower()
            blob = f"{blob} {' '.join(item['top_skills'] + item['key_risks'] + item['onboarding_guidance'] + item['role_directions'])}".lower()
            for term in ASTRO_TERMS:
                self.assertNotIn(term, blob.split(), msg=f"{item['candidate_id']} contains {term}")


class CandidateCompareRouteTests(unittest.TestCase):
    def test_routes_include_profile_mercury_and_compare(self):
        app = create_app()
        paths = {getattr(route, "path", None) for route in app.routes}
        self.assertIn("/api/v1/profile", paths)
        self.assertIn("/api/v1/mercury-work-profile", paths)
        self.assertIn("/api/v1/candidate-compare", paths)


if __name__ == "__main__":
    unittest.main()
