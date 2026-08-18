"""Tests for Mercury Source Profile v2 — House Batch B3 (Houses 8/11/12)."""

from __future__ import annotations

import unittest
from collections import Counter
from datetime import date, time

from app.schemas.mercury_source_profile import MercurySourceProfileRequest
from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS, SUPPORTED_HOUSE_KEYS
from app.services.mercury_source_knowledge_b3_houses import (
    B3_HOUSE_PACKS,
    HOUSE_8,
    HOUSE_8_BIO,
    HOUSE_11,
    HOUSE_11_BIO,
    HOUSE_12,
    HOUSE_12_BIO,
    REF_H8_BIO,
    REF_H8_L7,
    REF_H11_BIO,
    REF_H11_L7,
    REF_H12_BIO,
    REF_H12_L7,
)
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
    detect_repeated_signals,
)


CANONICAL_HOUSES = {str(i) for i in range(1, 13)}


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


def _house_keys_with_facts() -> set[str]:
    return {
        item.factor_key
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "house"
    }


class HouseBatchB3CoverageTests(unittest.TestCase):
    def test_exact_twelve_house_support(self):
        self.assertEqual(SUPPORTED_HOUSE_KEYS, CANONICAL_HOUSES)
        self.assertEqual(_house_keys_with_facts(), CANONICAL_HOUSES)
        self.assertEqual(len(SUPPORTED_HOUSE_KEYS), 12)

    def test_b1_and_b2_historical_subsets_still_valid(self):
        self.assertTrue(
            {"1", "2", "3", "4", "9", "10"}.issubset(SUPPORTED_HOUSE_KEYS)
        )
        self.assertTrue(
            {"1", "2", "3", "4", "5", "6", "7", "9", "10"}.issubset(SUPPORTED_HOUSE_KEYS)
        )
        self.assertTrue({"2", "3", "4", "5", "6", "7"}.issubset(_house_keys_with_facts()))

    def test_b3_source_references_and_counts(self):
        self.assertEqual(len(HOUSE_8), 18)
        self.assertEqual(len(HOUSE_8_BIO), 20)
        self.assertEqual(len(HOUSE_11), 22)
        self.assertEqual(len(HOUSE_11_BIO), 15)
        self.assertEqual(len(HOUSE_12), 20)
        self.assertEqual(len(HOUSE_12_BIO), 20)
        self.assertEqual(len(B3_HOUSE_PACKS), 115)
        self.assertTrue(all(item.source_reference == REF_H8_L7 for item in HOUSE_8))
        self.assertTrue(all(item.source_reference == REF_H8_BIO for item in HOUSE_8_BIO))
        self.assertTrue(all(item.source_reference == REF_H11_L7 for item in HOUSE_11))
        self.assertTrue(all(item.source_reference == REF_H11_BIO for item in HOUSE_11_BIO))
        self.assertTrue(all(item.source_reference == REF_H12_L7 for item in HOUSE_12))
        self.assertTrue(all(item.source_reference == REF_H12_BIO for item in HOUSE_12_BIO))
        self.assertTrue(all(item.factor_type == "house" for item in B3_HOUSE_PACKS))

    def test_ids_globally_unique(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])

    def test_house_8_11_12_activate(self):
        for house, expected_refs, sample_id in (
            ("8", {REF_H8_L7, REF_H8_BIO}, "h8_ability_to_influence_people_through_words"),
            ("11", {REF_H11_L7, REF_H11_BIO}, "h11_constant_social_interaction"),
            ("12", {REF_H12_L7, REF_H12_BIO}, "h12_ability_to_think_alone"),
        ):
            with self.subTest(house=house):
                profile = build_source_profile_from_factors(
                    MercurySourceFactors(
                        birth_time_known=True,
                        mercury_sign="Virgo",
                        mercury_element="earth",
                        mercury_motion="direct",
                        mercury_house=int(house),
                        aspects=[],
                    )
                )
                self.assertIn(f"house:{house}", profile.coverage.covered_factors)
                self.assertNotIn(f"house:{house}", profile.coverage.missing_factors)
                self.assertIn(sample_id, _ids(profile.house_facts))
                self.assertEqual(
                    {item.source_reference for item in profile.house_facts},
                    expected_refs,
                )


class HouseBatchB3SafetyTests(unittest.TestCase):
    def test_h11_friend_deception_not_native_lying(self):
        by_id = {item.id: item for item in HOUSE_11}
        for fact_id in (
            "h11_gossip_from_friends",
            "h11_lying_from_friends",
            "h11_deception_from_friends",
        ):
            tags = set(by_id[fact_id].tags)
            self.assertTrue(any(tag.startswith("friend_") for tag in tags), fact_id)
            self.assertNotIn("lying", tags)
            self.assertNotIn("gossip", tags)
            self.assertNotIn("deception", tags)

    def test_h8_medical_facts_are_source_specific_non_diagnostic(self):
        medical_ids = (
            "h8_source_vascular_problem_risk",
            "h8_source_hand_injury_risk",
            "h8_source_finger_injury_risk",
        )
        by_id = {item.id: item for item in HOUSE_8}
        for fact_id in medical_ids:
            fact = by_id[fact_id]
            self.assertEqual(fact.category, "source_specific")
            self.assertTrue(fact.tags[0].startswith("source_"))
            self.assertIn("not a medical diagnosis", fact.text.lower())

    def test_h12_occult_facts_are_source_specific(self):
        by_id = {item.id: item for item in HOUSE_12}
        for fact_id in (
            "h12_mind_brightest_in_occult",
            "h12_mind_brightest_in_unknown_unexplored",
        ):
            fact = by_id[fact_id]
            self.assertEqual(fact.category, "source_specific")
            self.assertIn("source-framework", fact.text.lower())

    def test_narrow_tags_avoid_broad_collisions(self):
        by_id = {item.id: item for item in B3_HOUSE_PACKS}
        self.assertNotIn("persuasion", by_id["h8_ability_to_influence_people_through_words"].tags)
        self.assertNotIn("analytical_thinking", by_id["h8_research_talent"].tags)
        self.assertNotIn("depth", by_id["h8_deep_thinking"].tags)
        self.assertNotIn("insight", by_id["h8_decipher_information_from_hidden_sources"].tags)
        self.assertNotIn("teaching", by_id["h11_teach_others"].tags)
        self.assertEqual(by_id["h11_teach_others"].tags, ("teaching_others",))
        self.assertNotIn("debate", by_id["h11_fierce_bitter_arguments"].tags)
        self.assertNotIn("argumentation", by_id["h11_fierce_bitter_arguments"].tags)
        self.assertNotIn("insight", by_id["h12_ability_to_decipher_hidden_meanings"].tags)
        self.assertNotIn("independent_learning", by_id["h12_ability_to_learn_alone"].tags)
        self.assertNotIn("writing", by_id["h12_writes_for_the_drawer"].tags)


class HouseAcceptanceMatrixTests(unittest.TestCase):
    def test_every_house_1_to_12_assembles(self):
        for house in range(1, 13):
            with self.subTest(house=house):
                profile = build_source_profile_from_factors(
                    MercurySourceFactors(
                        birth_time_known=True,
                        mercury_sign="Virgo",
                        mercury_element="earth",
                        mercury_motion="direct",
                        mercury_house=house,
                        aspects=[],
                    )
                )
                key = f"house:{house}"
                self.assertGreater(len(profile.house_facts), 0)
                self.assertTrue(all(item.factor_key == str(house) for item in profile.house_facts))
                self.assertIn(key, profile.coverage.covered_factors)
                self.assertNotIn(key, profile.coverage.missing_factors)
                self.assertEqual(detect_repeated_signals(profile.house_facts), [])


class HouseBatchB3RegressionTests(unittest.TestCase):
    def test_golden_cases_remain_complete(self):
        cases = [
            MercurySourceProfileRequest(
                birth_date=date(1986, 7, 14),
                birth_time=time(7, 10),
                birth_place="Simferopol, Ukraine",
            ),
            MercurySourceProfileRequest(
                birth_date=date(1986, 5, 16),
                birth_time=time(15, 0),
                birth_place="Dnipro, Ukraine",
            ),
            MercurySourceProfileRequest(
                birth_date=date(1985, 11, 12),
                birth_time=time(14, 15),
                birth_place="Zhodino, Belarus",
            ),
        ]
        for req in cases:
            with self.subTest(place=req.birth_place):
                profile = build_mercury_source_profile(req)
                self.assertEqual(profile.coverage.status, "complete")
                self.assertEqual(profile.coverage.missing_factors, [])

    def test_andrey_now_complete_with_trine_uranus(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Cancer",
                mercury_element="water",
                mercury_motion="direct",
                mercury_house=5,
                aspects=[
                    MercuryAspect(planet="Uranus", type="trine", orb_deg=1.0),
                    MercuryAspect(planet="Pluto", type="square", orb_deg=1.0),
                ],
            )
        )
        self.assertEqual(profile.coverage.status, "complete")
        self.assertEqual(profile.coverage.missing_factors, [])
        self.assertIn("house:5", profile.coverage.covered_factors)
        self.assertTrue(any(item.factor_key == "trine_Uranus" for item in profile.aspect_facts))

    def test_milka_like_still_complete(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=False,
                mercury_sign="Pisces",
                mercury_element="water",
                mercury_motion="direct",
                mercury_house=None,
                aspects=[],
            )
        )
        self.assertEqual(profile.coverage.status, "complete")
        self.assertIn("sign:Pisces", profile.coverage.covered_factors)

    def test_unknown_birth_time_house_is_calculation_limitation(self):
        profile = build_mercury_source_profile(
            MercurySourceProfileRequest(
                birth_date=date(1986, 7, 14),
                birth_time=None,
                birth_place="Simferopol, Ukraine",
            )
        )
        self.assertIsNone(profile.calculated.mercury_house)
        self.assertFalse(profile.calculated.birth_time_known)
        self.assertEqual(len(profile.house_facts), 0)
        self.assertFalse(any(item.startswith("house:") for item in profile.coverage.missing_factors))
        self.assertTrue(
            any("birth time unknown" in item.lower() for item in profile.limitations)
        )

    def test_house_remains_covered_when_synthetic_aspect_unsupported(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Leo",
                mercury_element="fire",
                mercury_motion="direct",
                mercury_house=8,
                aspects=[MercuryAspect(planet="SyntheticProbe", type="conjunction", orb_deg=2.0)],
            )
        )
        self.assertEqual(profile.coverage.status, "partial")
        self.assertIn("house:8", profile.coverage.covered_factors)
        self.assertNotIn("house:8", profile.coverage.missing_factors)
        self.assertEqual(profile.coverage.missing_factors, ["aspect:conjunction_SyntheticProbe"])


if __name__ == "__main__":
    unittest.main()
