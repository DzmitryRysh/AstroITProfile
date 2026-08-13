"""Tests for Mercury Source Profile v2 — House Batch B1 (Houses 2/3/4)."""

from __future__ import annotations

import unittest
from collections import Counter
from datetime import date, time

from app.schemas.mercury_source_profile import MercurySourceProfileRequest
from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS, SUPPORTED_HOUSE_KEYS
from app.services.mercury_source_knowledge_b1_houses import (
    B1_HOUSE_PACKS,
    HOUSE_2,
    HOUSE_3,
    HOUSE_4,
    REF_H2_L7,
    REF_H3_L7,
    REF_H4_L7,
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


class HouseBatchB1CoverageTests(unittest.TestCase):
    def test_houses_2_3_4_supported(self):
        # Historical B1 subset guarantee: later batches may expand the set.
        self.assertTrue(
            {"1", "2", "3", "4", "9", "10"}.issubset(SUPPORTED_HOUSE_KEYS)
        )
        self.assertTrue({"2", "3", "4"}.issubset(_house_keys_with_facts()))

    def test_b1_source_references_and_counts(self):
        self.assertEqual(len(HOUSE_2), 20)
        self.assertEqual(len(HOUSE_3), 22)
        self.assertEqual(len(HOUSE_4), 10)
        self.assertEqual(len(B1_HOUSE_PACKS), 52)
        self.assertTrue(all(item.source_reference == REF_H2_L7 for item in HOUSE_2))
        self.assertTrue(all(item.source_reference == REF_H3_L7 for item in HOUSE_3))
        self.assertTrue(all(item.source_reference == REF_H4_L7 for item in HOUSE_4))
        self.assertTrue(all(item.factor_type == "house" for item in B1_HOUSE_PACKS))

    def test_ids_globally_unique(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])

    def test_house_2_3_4_activate(self):
        for house, expected_ref, sample_id in (
            ("2", REF_H2_L7, "h2_profit_through_public_speaking"),
            ("3", REF_H3_L7, "h3_extreme_curiosity"),
            ("4", REF_H4_L7, "h4_home_based_study"),
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


class House4WeakMercuryUnresolvedTests(unittest.TestCase):
    def test_weak_mercury_dependency_unresolved_and_excluded_from_repeats(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Cancer",
                mercury_element="water",
                mercury_motion="direct",
                mercury_house=4,
                aspects=[],
            )
        )
        weak = next(
            item
            for item in profile.house_facts
            if item.id == "h4_weak_mercury_others_speak_instead"
        )
        self.assertTrue(weak.unresolved)
        self.assertIsNone(weak.activation_condition)
        self.assertNotEqual(weak.activation_condition, "hard_aspected")
        self.assertIn(weak.id, _ids(profile.conditional_unresolved))
        self.assertEqual(weak.tags, ["mercury_strength_dependency"])

        # Even if we force-match the same tag on another factor, unresolved house
        # evidence must not contribute to repeated-signal detection.
        repeats = detect_repeated_signals(list(profile.house_facts) + list(profile.sign_facts))
        for signal in repeats:
            self.assertNotIn("h4_weak_mercury_others_speak_instead", signal.fact_ids)


class HouseBatchB1SemanticSafetyTests(unittest.TestCase):
    def test_same_house_cannot_create_repeat_alone(self):
        for house in (2, 3, 4):
            with self.subTest(house=house):
                profile = build_source_profile_from_factors(
                    MercurySourceFactors(
                        birth_time_known=True,
                        mercury_sign=None,
                        mercury_element=None,
                        mercury_motion="direct",
                        mercury_house=house,
                        aspects=[],
                    )
                )
                # Only house facts present (unsupported null sign omitted).
                for signal in detect_repeated_signals(profile.house_facts):
                    house_sources = [src for src in signal.sources if src.startswith("house:")]
                    self.assertLessEqual(len(house_sources), 1, signal)

    def test_narrow_tags_avoid_broad_collisions(self):
        by_id = {item.id: item for item in B1_HOUSE_PACKS}
        self.assertEqual(by_id["h2_trade_income_association"].tags, ("trade_income",))
        self.assertNotIn("sales", by_id["h2_trade_income_association"].tags)
        self.assertEqual(by_id["h2_accumulates_collects_books"].tags, ("collects_books",))
        self.assertNotIn("books", by_id["h2_accumulates_collects_books"].tags)
        self.assertEqual(by_id["h3_learns_languages"].tags, ("languages_learning",))
        self.assertNotIn("foreign_languages", by_id["h3_learns_languages"].tags)
        self.assertEqual(by_id["h3_knowledge_grasped_on_the_fly"].tags, ("quick_learning",))
        self.assertNotIn("fast_thinking", by_id["h3_knowledge_grasped_on_the_fly"].tags)
        self.assertEqual(
            by_id["h3_ability_to_switch_between_activities"].tags,
            ("activity_switching",),
        )
        self.assertNotIn("multitasking", by_id["h3_ability_to_switch_between_activities"].tags)
        self.assertEqual(by_id["h3_arguments_readily_available"].tags, ("argument_readiness",))
        self.assertNotIn("persuasion", by_id["h3_arguments_readily_available"].tags)
        self.assertNotIn("debate", by_id["h3_arguments_readily_available"].tags)
        self.assertEqual(by_id["h3_excellent_written_expression"].tags, ("written_expression",))
        self.assertNotIn("writing", by_id["h3_excellent_written_expression"].tags)
        self.assertEqual(by_id["h3_extreme_curiosity"].tags, ("extreme_curiosity",))
        self.assertNotIn("curiosity", by_id["h3_extreme_curiosity"].tags)

    def test_no_new_false_repeats_on_house_only_profiles(self):
        # House facts alone must not invent multi-factor repeats.
        for house in (2, 3, 4):
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
            house_only = detect_repeated_signals(profile.house_facts)
            self.assertEqual(house_only, [])


class HouseBatchB1RegressionTests(unittest.TestCase):
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
        self.assertIn("house:5", profile.coverage.covered_factors)
        self.assertNotIn("house:5", profile.coverage.missing_factors)
        self.assertEqual(profile.coverage.missing_factors, [])
        self.assertGreater(len(profile.house_facts), 0)
        self.assertTrue(any(item.factor_key == "trine_Uranus" for item in profile.aspect_facts))

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
