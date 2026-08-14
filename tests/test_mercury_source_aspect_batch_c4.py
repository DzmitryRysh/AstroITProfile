"""Tests for Mercury Source Profile v2 — Aspect Batch C4 (Jupiter square)."""

from __future__ import annotations

import unittest
from collections import Counter
from datetime import date, time

from app.schemas.mercury_source_profile import MercurySourceProfileRequest
from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_source_knowledge import (
    ALL_SOURCE_FACTS,
    ASPECT_PACK_ALIASES,
    SUPPORTED_ASPECT_KEYS,
)
from app.services.mercury_source_knowledge_c4_aspects import (
    JUPITER_SQUARE,
    JUPITER_SQUARE_COMMON,
    JUPITER_SQUARE_JUPITER_WINS,
    JUPITER_SQUARE_MERCURY_WINS,
    REF_JUPITER_SQ,
)
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
    detect_repeated_signals,
)

ENGINE_ASPECT_SLOTS = 45
REF_JUPITER_HARM = "bioastrology_mercury_jupiter_harmonious"


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


def _refs(facts) -> set[str]:
    return {item.source_reference for item in facts}


def _canonical_aspect_packs() -> set[str]:
    return {
        item.factor_key
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "aspect"
    }


class AspectBatchC4CoverageTests(unittest.TestCase):
    def test_supported_public_aspect_count_is_eighteen(self):
        self.assertEqual(len(SUPPORTED_ASPECT_KEYS), 18)
        self.assertEqual(ENGINE_ASPECT_SLOTS - len(SUPPORTED_ASPECT_KEYS), 27)
        self.assertIn("square_Jupiter", SUPPORTED_ASPECT_KEYS)
        self.assertNotIn("conjunction_Jupiter", SUPPORTED_ASPECT_KEYS)
        self.assertNotIn("opposition_Jupiter", SUPPORTED_ASPECT_KEYS)

    def test_canonical_packs_and_aliases(self):
        self.assertEqual(len(_canonical_aspect_packs()), 12)
        self.assertEqual(len(ASPECT_PACK_ALIASES), 6)
        self.assertNotIn("square_Jupiter", ASPECT_PACK_ALIASES)
        self.assertIn("square_Jupiter", _canonical_aspect_packs())
        for canonical in ASPECT_PACK_ALIASES.values():
            self.assertNotIn(canonical, ASPECT_PACK_ALIASES)

    def test_prior_batch_invariants_remain(self):
        self.assertEqual(ASPECT_PACK_ALIASES["sextile_Mars"], "trine_Mars")
        self.assertEqual(ASPECT_PACK_ALIASES["trine_Moon"], "sextile_Moon")
        self.assertEqual(ASPECT_PACK_ALIASES["trine_Jupiter"], "sextile_Jupiter")
        self.assertEqual(ASPECT_PACK_ALIASES["sextile_Saturn"], "trine_Saturn")
        self.assertEqual(ASPECT_PACK_ALIASES["sextile_Uranus"], "trine_Uranus")
        self.assertEqual(ASPECT_PACK_ALIASES["sextile_Pluto"], "trine_Pluto")
        self.assertIn("square_Mars", SUPPORTED_ASPECT_KEYS)
        self.assertIn("square_Saturn", SUPPORTED_ASPECT_KEYS)
        self.assertIn("trine_Pluto", SUPPORTED_ASPECT_KEYS)
        self.assertIn("sextile_Pluto", SUPPORTED_ASPECT_KEYS)

    def test_catalog_integrity(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])
        self.assertTrue(all(item.source_reference for item in ALL_SOURCE_FACTS))
        self.assertEqual(len(JUPITER_SQUARE_COMMON), 13)
        self.assertEqual(len(JUPITER_SQUARE_JUPITER_WINS), 14)
        self.assertEqual(len(JUPITER_SQUARE_MERCURY_WINS), 9)
        self.assertEqual(len(JUPITER_SQUARE), 36)
        self.assertTrue(all(item.source_reference == REF_JUPITER_SQ for item in JUPITER_SQUARE))
        self.assertTrue(all(not item.unresolved for item in JUPITER_SQUARE_COMMON))
        self.assertTrue(all(item.unresolved for item in JUPITER_SQUARE_JUPITER_WINS))
        self.assertTrue(all(item.unresolved for item in JUPITER_SQUARE_MERCURY_WINS))
        self.assertTrue(
            all(
                item.activation_condition == "strength_unresolved"
                for item in JUPITER_SQUARE_JUPITER_WINS + JUPITER_SQUARE_MERCURY_WINS
            )
        )
        # No road-accident material in square Jupiter.
        texts = " ".join(item.text.lower() for item in JUPITER_SQUARE)
        self.assertNotIn("accident", texts)
        self.assertNotIn("road accident", texts)
        # No compensation category forced into this pack.
        self.assertFalse(any(item.category == "compensation" for item in JUPITER_SQUARE))
        self.assertFalse(any("compensation" in item.tags for item in JUPITER_SQUARE))
        # Supergift intentionally omitted (no always-true genius claim).
        self.assertFalse(any("supergift" in item.id for item in JUPITER_SQUARE))
        self.assertFalse(any("genius" in item.text.lower() for item in JUPITER_SQUARE))


class AspectBatchC4ActivationTests(unittest.TestCase):
    def setUp(self):
        self.profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Virgo",
                mercury_element="earth",
                mercury_motion="direct",
                mercury_house=3,
                aspects=[MercuryAspect(planet="Jupiter", type="square", orb_deg=1.2)],
            )
        )

    def test_common_facts_resolved_and_branches_unresolved(self):
        self.assertEqual(self.profile.coverage.status, "complete")
        self.assertIn("aspect:square_Jupiter", self.profile.coverage.covered_factors)
        common_ids = _ids(JUPITER_SQUARE_COMMON)
        self.assertEqual(
            {item.id for item in self.profile.aspect_facts if item.id in common_ids},
            common_ids,
        )
        unresolved_ids = _ids(self.profile.conditional_unresolved)
        self.assertTrue(_ids(JUPITER_SQUARE_JUPITER_WINS).issubset(unresolved_ids))
        self.assertTrue(_ids(JUPITER_SQUARE_MERCURY_WINS).issubset(unresolved_ids))
        resolved_ids = {
            item.id for item in self.profile.aspect_facts if not item.unresolved
        }
        branch_ids = _ids(JUPITER_SQUARE_JUPITER_WINS) | _ids(JUPITER_SQUARE_MERCURY_WINS)
        self.assertTrue(branch_ids.isdisjoint(resolved_ids))
        self.assertTrue(branch_ids.issubset(_ids(self.profile.aspect_facts)))
        self.assertTrue(
            any("if jupiter dominates" in item.text.lower() for item in self.profile.conditional_unresolved)
        )
        self.assertTrue(
            any("if mercury dominates" in item.text.lower() for item in self.profile.conditional_unresolved)
        )

    def test_unresolved_excluded_from_repeats(self):
        all_facts = (
            list(self.profile.sign_facts)
            + list(self.profile.house_facts)
            + list(self.profile.aspect_facts)
            + list(self.profile.conditional_unresolved)
        )
        for signal in detect_repeated_signals(all_facts):
            for fact_id in signal.fact_ids:
                fact = next(item for item in all_facts if item.id == fact_id)
                self.assertFalse(fact.unresolved, signal)
                self.assertNotEqual(fact.tags, ("source_lying_tendency",))


class AspectBatchC4TagHardeningTests(unittest.TestCase):
    def test_narrow_tags_avoid_hardened_collisions(self):
        by_id = {item.id: item for item in JUPITER_SQUARE}
        self.assertEqual(
            by_id["jupiter_sq_branch_jupiter_oratory_with_demagogy"].tags,
            ("source_oratory_with_demagogy",),
        )
        self.assertNotIn(
            "persuasion",
            by_id["jupiter_sq_branch_jupiter_oratory_with_demagogy"].tags,
        )
        self.assertEqual(
            by_id["jupiter_sq_branch_jupiter_mentorizing"].tags,
            ("mentorizing_tendency",),
        )
        self.assertNotIn("teaching", by_id["jupiter_sq_branch_jupiter_mentorizing"].tags)
        arg = by_id["jupiter_sq_branch_mercury_argumentative_behavior"]
        self.assertEqual(arg.tags, ("argumentative_behavior",))
        self.assertNotIn("debate", arg.tags)
        self.assertNotIn("argumentation", arg.tags)
        lying = by_id["jupiter_sq_branch_mercury_lying_tendency"]
        self.assertEqual(lying.tags, ("source_lying_tendency",))
        self.assertNotIn("lying", lying.tags)
        for fact_id in (
            "jupiter_sq_fact_evaluation_substitution",
            "jupiter_sq_fact_image_substitution",
            "jupiter_sq_rightness_over_truth_orientation",
            "jupiter_sq_source_secondary_gain_being_right",
        ):
            self.assertNotIn("evidence_requirement", by_id[fact_id].tags)
        self.assertEqual(
            by_id["jupiter_sq_prestigious_car_orientation"].tags,
            ("prestigious_car_orientation",),
        )
        self.assertNotIn(
            "prestige_orientation",
            by_id["jupiter_sq_prestigious_car_orientation"].tags,
        )


class AspectBatchC4HarmoniousRegressionTests(unittest.TestCase):
    def test_sextile_and_trine_jupiter_remain_harmonious_only(self):
        for aspect_type, expected_key in (("sextile", "sextile_Jupiter"), ("trine", "trine_Jupiter")):
            with self.subTest(aspect=aspect_type):
                profile = build_source_profile_from_factors(
                    MercurySourceFactors(
                        birth_time_known=True,
                        mercury_sign="Virgo",
                        mercury_element="earth",
                        mercury_motion="direct",
                        mercury_house=3,
                        aspects=[MercuryAspect(planet="Jupiter", type=aspect_type, orb_deg=1.0)],
                    )
                )
                self.assertTrue(profile.aspect_facts)
                self.assertEqual(_refs(profile.aspect_facts), {REF_JUPITER_HARM})
                self.assertTrue(all(item.factor_key == expected_key for item in profile.aspect_facts))
                self.assertFalse(any(item.id.startswith("jupiter_sq_") for item in profile.aspect_facts))
                self.assertNotIn(REF_JUPITER_SQ, _refs(profile.aspect_facts))


class AspectBatchC4RegressionTests(unittest.TestCase):
    def test_golden_cases_remain_complete(self):
        cases = [
            ("Avdey", date(1986, 7, 14), time(7, 10), "Simferopol, Ukraine"),
            ("Vlad", date(1986, 5, 16), time(15, 0), "Dnipro, Ukraine"),
            ("Dzmitry", date(1985, 11, 12), time(14, 15), "Zhodino, Belarus"),
        ]
        for name, birth_date, birth_time, place in cases:
            with self.subTest(name=name):
                profile = build_mercury_source_profile(
                    MercurySourceProfileRequest(
                        birth_date=birth_date,
                        birth_time=birth_time,
                        birth_place=place,
                    )
                )
                self.assertEqual(profile.coverage.status, "complete")
                self.assertEqual(profile.coverage.missing_factors, [])
                self.assertFalse(
                    any(item.id.startswith("jupiter_sq_") for item in profile.aspect_facts)
                )

    def test_vlad_dzmitry_harmonious_jupiter_only(self):
        for name, birth_date, birth_time, place in (
            ("Vlad", date(1986, 5, 16), time(15, 0), "Dnipro, Ukraine"),
            ("Dzmitry", date(1985, 11, 12), time(14, 15), "Zhodino, Belarus"),
        ):
            with self.subTest(name=name):
                profile = build_mercury_source_profile(
                    MercurySourceProfileRequest(
                        birth_date=birth_date,
                        birth_time=birth_time,
                        birth_place=place,
                    )
                )
                jupiter = [item for item in profile.aspect_facts if "Jupiter" in item.factor_key]
                self.assertTrue(jupiter)
                self.assertTrue(
                    all(item.factor_key in {"sextile_Jupiter", "trine_Jupiter"} for item in jupiter)
                )
                self.assertTrue(all(item.source_reference == REF_JUPITER_HARM for item in jupiter))
                self.assertFalse(any(item.factor_key == "square_Jupiter" for item in jupiter))

    def test_andrey_and_milka_unchanged(self):
        andrey = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Cancer",
                mercury_element="water",
                mercury_motion="direct",
                mercury_house=5,
                aspects=[
                    MercuryAspect(planet="Uranus", type="trine", orb_deg=1.65),
                    MercuryAspect(planet="Pluto", type="square", orb_deg=2.68),
                ],
            )
        )
        self.assertEqual(andrey.coverage.status, "complete")
        self.assertFalse(any(item.id.startswith("jupiter_sq_") for item in andrey.aspect_facts))
        milka = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=False,
                mercury_sign="Pisces",
                mercury_element="water",
                mercury_motion="direct",
                mercury_house=None,
                aspects=[],
            )
        )
        self.assertEqual(milka.coverage.status, "complete")


if __name__ == "__main__":
    unittest.main()
