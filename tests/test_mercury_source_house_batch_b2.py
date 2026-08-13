"""Tests for Mercury Source Profile v2 — House Batch B2 (Houses 5/6/7)."""

from __future__ import annotations

import unittest
from collections import Counter
from datetime import date, time

from app.schemas.mercury_source_profile import MercurySourceProfileRequest
from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS, SUPPORTED_HOUSE_KEYS
from app.services.mercury_source_knowledge_b2_houses import (
    B2_HOUSE_PACKS,
    HOUSE_5,
    HOUSE_6,
    HOUSE_7,
    REF_H5_L7,
    REF_H6_L7,
    REF_H7_L7,
)
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
    detect_repeated_signals,
)


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


def _house_keys_with_facts() -> set[str]:
    return {
        item.factor_key
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "house"
    }


class HouseBatchB2CoverageTests(unittest.TestCase):
    def test_houses_5_6_7_supported(self):
        self.assertEqual(
            SUPPORTED_HOUSE_KEYS,
            {"1", "2", "3", "4", "5", "6", "7", "9", "10"},
        )
        self.assertEqual(
            _house_keys_with_facts(),
            {"1", "2", "3", "4", "5", "6", "7", "9", "10"},
        )
        self.assertEqual(len(SUPPORTED_HOUSE_KEYS), 9)

    def test_b2_source_references_and_counts(self):
        self.assertEqual(len(HOUSE_5), 14)
        self.assertEqual(len(HOUSE_6), 14)
        self.assertEqual(len(HOUSE_7), 16)
        self.assertEqual(len(B2_HOUSE_PACKS), 44)
        self.assertTrue(all(item.source_reference == REF_H5_L7 for item in HOUSE_5))
        self.assertTrue(all(item.source_reference == REF_H6_L7 for item in HOUSE_6))
        self.assertTrue(all(item.source_reference == REF_H7_L7 for item in HOUSE_7))
        self.assertTrue(all(item.factor_type == "house" for item in B2_HOUSE_PACKS))

    def test_ids_globally_unique(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])

    def test_house_5_6_7_activate(self):
        for house, expected_ref, sample_id in (
            ("5", REF_H5_L7, "h5_creativity_connected_with_intellectual_work"),
            ("6", REF_H6_L7, "h6_duties_performed_diligently"),
            ("7", REF_H7_L7, "h7_master_of_dialogue"),
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
                self.assertTrue(
                    all(item.source_reference == expected_ref for item in profile.house_facts)
                )


class House7PartnerAndUnresolvedSafetyTests(unittest.TestCase):
    def test_partner_facts_do_not_use_native_repeat_tags(self):
        partner_ids = [
            "h7_partner_may_be_communicative",
            "h7_partner_from_intellectual_profession",
            "h7_partner_often_younger",
            "h7_partner_may_be_two_faced",
            "h7_partner_may_be_lying",
        ]
        forbidden = {
            "lying",
            "debate",
            "argumentation",
            "persuasion",
            "communication_skill",
            "communication",
            "sales",
            "teaching",
        }
        by_id = {item.id: item for item in HOUSE_7}
        for fact_id in partner_ids:
            tags = set(by_id[fact_id].tags)
            self.assertTrue(tags.isdisjoint(forbidden), (fact_id, tags))
            self.assertTrue(any("partner" in tag for tag in tags), fact_id)

    def test_unresolved_dependencies_excluded_from_repeats(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Gemini",
                mercury_element="air",
                mercury_motion="direct",
                mercury_house=7,
                aspects=[],
            )
        )
        unresolved_ids = {
            "h7_partner_intellectual_expectation_mutable_dependency",
            "h7_partner_argumentativeness_fire_element_dependency",
        }
        for fact_id in unresolved_ids:
            fact = next(item for item in profile.house_facts if item.id == fact_id)
            self.assertTrue(fact.unresolved)
            self.assertIsNone(fact.activation_condition)
            self.assertIn(fact.id, _ids(profile.conditional_unresolved))

        for signal in detect_repeated_signals(
            list(profile.house_facts) + list(profile.sign_facts)
        ):
            self.assertTrue(unresolved_ids.isdisjoint(signal.fact_ids), signal)


class HouseBatchB2SemanticSafetyTests(unittest.TestCase):
    def test_house_6_task_scatter_not_multitasking(self):
        fact = next(
            item
            for item in HOUSE_6
            if item.id == "h6_tendency_to_grab_several_tasks_at_once"
        )
        self.assertEqual(fact.tags, ("multiple_tasks_at_once_risk",))
        self.assertNotIn("multitasking", fact.tags)
        self.assertEqual(fact.polarity, "risk")

    def test_house_5_occupations_are_associations_not_abilities(self):
        fact = next(item for item in HOUSE_5 if item.id == "h5_occupation_associations")
        self.assertEqual(fact.category, "source_specific")
        self.assertEqual(fact.tags, ("occupation_associations",))
        self.assertNotIn("teaching", fact.tags)
        self.assertNotIn("writing", fact.tags)
        self.assertNotIn("creative", fact.tags)

    def test_same_house_cannot_create_repeat_alone(self):
        for house in (5, 6, 7):
            with self.subTest(house=house):
                profile = build_source_profile_from_factors(
                    MercurySourceFactors(
                        birth_time_known=True,
                        mercury_sign="Leo",
                        mercury_element="fire",
                        mercury_motion="direct",
                        mercury_house=house,
                        aspects=[],
                    )
                )
                self.assertEqual(detect_repeated_signals(profile.house_facts), [])

    def test_narrow_tags_avoid_broad_collisions(self):
        by_id = {item.id: item for item in B2_HOUSE_PACKS}
        self.assertNotIn("persuasion", by_id["h5_romantic_beautiful_speech"].tags)
        self.assertNotIn("sales", by_id["h5_romantic_beautiful_speech"].tags)
        self.assertNotIn("lifelong_learning", by_id["h5_pleasure_from_studying"].tags)
        self.assertNotIn("books", by_id["h5_pleasure_from_books"].tags)
        self.assertNotIn("writing", by_id["h5_creativity_connected_with_writing"].tags)
        self.assertNotIn("oratory", by_id["h5_circumstances_public_speaking"].tags)
        self.assertNotIn("sales", by_id["h6_active_use_of_professional_contacts"].tags)
        self.assertNotIn("multitasking", by_id["h6_work_involves_processing_lots_of_information"].tags)
        self.assertNotIn("persuasion", by_id["h7_master_of_compromise"].tags)
        self.assertNotIn("lying", by_id["h7_partner_may_be_lying"].tags)


class HouseBatchB2RegressionTests(unittest.TestCase):
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

    def test_andrey_missing_only_trine_uranus(self):
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
        self.assertEqual(profile.coverage.status, "partial")
        self.assertEqual(profile.coverage.missing_factors, ["aspect:trine_Uranus"])
        self.assertIn("house:5", profile.coverage.covered_factors)
        self.assertIn("h5_creativity_connected_with_intellectual_work", _ids(profile.house_facts))

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


if __name__ == "__main__":
    unittest.main()
