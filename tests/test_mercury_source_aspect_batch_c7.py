"""Tests for Mercury Source Profile v2 — Aspect Batch C7 (Mars opposition / conjunction)."""

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
    SUPPORTED_HOUSE_KEYS,
    SUPPORTED_SIGN_KEYS,
)
from app.services.mercury_source_knowledge_c2_aspects import MARS_SQUARE, REF_MARS_SQ
from app.services.mercury_source_knowledge_c7_aspects import (
    MARS_CONJUNCTION,
    MARS_CONJUNCTION_RESOLVED,
    MARS_CONJUNCTION_UNRESOLVED,
    MARS_OPPOSITION,
    MARS_OPPOSITION_RESOLVED,
    MARS_OPPOSITION_UNRESOLVED,
    REF_MARS_CONJ,
    REF_MARS_OPP,
)
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
    detect_repeated_signals,
)

MARS_PUBLIC_FAMILY = {
    "conjunction_Mars",
    "sextile_Mars",
    "square_Mars",
    "trine_Mars",
    "opposition_Mars",
}
JUPITER_PUBLIC_FAMILY = {
    "conjunction_Jupiter",
    "sextile_Jupiter",
    "square_Jupiter",
    "trine_Jupiter",
    "opposition_Jupiter",
}
SATURN_PUBLIC_FAMILY = {
    "conjunction_Saturn",
    "sextile_Saturn",
    "square_Saturn",
    "trine_Saturn",
    "opposition_Saturn",
}


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


def _canonical_aspect_packs() -> set[str]:
    return {
        item.factor_key
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "aspect"
    }


def _synthetic_mars(aspect_type: str):
    return build_source_profile_from_factors(
        MercurySourceFactors(
            birth_time_known=True,
            mercury_sign="Virgo",
            mercury_element="earth",
            mercury_motion="direct",
            mercury_house=3,
            aspects=[MercuryAspect(planet="Mars", type=aspect_type, orb_deg=1.2)],
        )
    )


class AspectBatchC7CoverageTests(unittest.TestCase):
    def test_c7_mars_family_remains_complete(self):
        # Historical C7 batch: factor-specific guarantee. Exact public count owned by C8+.
        self.assertTrue(MARS_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(JUPITER_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(SATURN_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertEqual(len(SUPPORTED_SIGN_KEYS), 12)
        self.assertEqual(len(SUPPORTED_HOUSE_KEYS), 12)

    def test_mars_family_is_exactly_five_of_five(self):
        self.assertIn("conjunction_Mars", SUPPORTED_ASPECT_KEYS)
        self.assertIn("opposition_Mars", SUPPORTED_ASPECT_KEYS)
        self.assertIn("square_Mars", SUPPORTED_ASPECT_KEYS)
        self.assertIn("trine_Mars", SUPPORTED_ASPECT_KEYS)
        self.assertEqual(ASPECT_PACK_ALIASES["sextile_Mars"], "trine_Mars")
        self.assertNotIn("conjunction_Mars", ASPECT_PACK_ALIASES)
        self.assertNotIn("opposition_Mars", ASPECT_PACK_ALIASES)
        self.assertNotEqual(ASPECT_PACK_ALIASES.get("conjunction_Mars"), "square_Mars")
        self.assertNotEqual(ASPECT_PACK_ALIASES.get("opposition_Mars"), "square_Mars")
        self.assertIn("conjunction_Mars", _canonical_aspect_packs())
        self.assertIn("opposition_Mars", _canonical_aspect_packs())
        self.assertIn("square_Mars", _canonical_aspect_packs())
        self.assertIn("trine_Mars", _canonical_aspect_packs())
        self.assertNotIn("sextile_Mars", _canonical_aspect_packs())

    def test_distinct_refs_and_catalog_identity(self):
        self.assertEqual(REF_MARS_OPP, "bioastrology_mercury_mars_opposition")
        self.assertEqual(REF_MARS_CONJ, "bioastrology_mercury_mars_conjunction")
        self.assertNotEqual(REF_MARS_OPP, REF_MARS_SQ)
        self.assertNotEqual(REF_MARS_CONJ, REF_MARS_SQ)
        self.assertNotEqual(REF_MARS_OPP, REF_MARS_CONJ)
        self.assertTrue(all(item.source_reference == REF_MARS_OPP for item in MARS_OPPOSITION))
        self.assertTrue(all(item.source_reference == REF_MARS_CONJ for item in MARS_CONJUNCTION))
        self.assertTrue(_ids(MARS_OPPOSITION).isdisjoint(_ids(MARS_SQUARE)))
        self.assertTrue(_ids(MARS_CONJUNCTION).isdisjoint(_ids(MARS_SQUARE)))
        self.assertTrue(_ids(MARS_OPPOSITION).isdisjoint(_ids(MARS_CONJUNCTION)))

    def test_catalog_integrity(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])
        self.assertTrue(all(item.source_reference for item in ALL_SOURCE_FACTS))
        self.assertEqual(len(MARS_OPPOSITION_RESOLVED), 12)
        self.assertEqual(len(MARS_OPPOSITION_UNRESOLVED), 1)
        self.assertEqual(len(MARS_OPPOSITION), 13)
        self.assertEqual(len(MARS_CONJUNCTION_RESOLVED), 19)
        self.assertEqual(len(MARS_CONJUNCTION_UNRESOLVED), 1)
        self.assertEqual(len(MARS_CONJUNCTION), 20)
        self.assertTrue(all(not item.unresolved for item in MARS_OPPOSITION_RESOLVED))
        self.assertTrue(all(not item.unresolved for item in MARS_CONJUNCTION_RESOLVED))
        self.assertTrue(all(item.unresolved for item in MARS_OPPOSITION_UNRESOLVED))
        self.assertTrue(all(item.unresolved for item in MARS_CONJUNCTION_UNRESOLVED))
        self.assertTrue(
            all(
                item.activation_condition == "female_chart_context_unresolved"
                for item in MARS_OPPOSITION_UNRESOLVED + MARS_CONJUNCTION_UNRESOLVED
            )
        )
        all_c7 = MARS_OPPOSITION + MARS_CONJUNCTION
        self.assertFalse(any(item.category == "compensation" for item in all_c7))
        self.assertFalse(any("supergift" in item.id for item in all_c7))
        self.assertFalse(any("celebrity" in item.id for item in all_c7))
        self.assertFalse(any("secondary_gain" in item.id for item in all_c7))


class AspectBatchC7AtomTests(unittest.TestCase):
    def test_opposition_key_atoms(self):
        by_id = {item.id: item for item in MARS_OPPOSITION}
        self.assertEqual(by_id["mars_opp_word_action_mismatch"].tags, ("word_action_mismatch",))
        self.assertEqual(
            by_id["mars_opp_action_interferes_with_thought_formulation"].tags,
            ("action_interferes_with_thought_formulation",),
        )
        self.assertEqual(
            by_id["mars_opp_aggressive_driving_accident_association"].tags,
            ("source_aggressive_driving_accident_association",),
        )
        self.assertNotIn(
            "driving_ability",
            by_id["mars_opp_aggressive_driving_accident_association"].tags,
        )
        self.assertEqual(by_id["mars_opp_scattered_activity"].tags, ("scattered_activity",))
        self.assertEqual(by_id["mars_opp_goal_setting_difficulty"].tags, ("goal_setting_difficulty",))
        self.assertNotIn("planning", by_id["mars_opp_goal_setting_difficulty"].tags)
        self.assertNotIn("intelligence", by_id["mars_opp_source_cognitive_slowdown_episode"].tags)
        self.assertNotIn("analytical_thinking", by_id["mars_opp_source_cognitive_slowdown_episode"].tags)
        self.assertIn("source", by_id["mars_opp_injury_fracture_association"].text.lower())
        self.assertIn("non-diagnostic", by_id["mars_opp_injury_fracture_association"].text.lower())

    def test_conjunction_key_atoms(self):
        by_id = {item.id: item for item in MARS_CONJUNCTION}
        self.assertIn("mars_cj_action_overrides_free_curiosity", by_id)
        self.assertIn("mars_cj_action_when_reflection_needed", by_id)
        self.assertIn("mars_cj_reflection_when_action_needed", by_id)
        self.assertEqual(by_id["mars_cj_sales"].tags, ("sales",))
        self.assertNotIn("persuasion", by_id["mars_cj_sales"].tags)
        self.assertNotIn("persuasion", by_id["mars_cj_convincing_voice"].tags)
        self.assertEqual(by_id["mars_cj_technical_mindset"].tags, ("technical_mindset",))
        self.assertNotIn("technical_ability", by_id["mars_cj_technical_mindset"].tags)
        quarrel = by_id["mars_cj_quarrelsome_interaction"]
        self.assertEqual(quarrel.tags, ("quarrelsome_interaction",))
        self.assertNotIn("debate", quarrel.tags)
        self.assertNotIn("argumentation", quarrel.tags)
        self.assertNotIn("argumentation", by_id["mars_cj_dialogue_building_difficulty"].tags)
        self.assertNotIn("planning", by_id["mars_cj_goal_setting_difficulty"].tags)
        self.assertNotIn("driving_ability", by_id["mars_cj_aggressive_driving_accident_association"].tags)
        self.assertNotIn("intelligence", by_id["mars_cj_source_speech_cognition_variability"].tags)
        self.assertNotIn("fast_thinking", by_id["mars_cj_source_speech_cognition_variability"].tags)
        psych = by_id["mars_cj_source_psychiatry_association"]
        self.assertEqual(psych.tags, ("source_psychiatry_association",))
        self.assertIn("non-diagnostic", psych.text.lower())


class AspectBatchC7ActivationTests(unittest.TestCase):
    def test_opposition_activates_only_opposition_pack(self):
        profile = _synthetic_mars("opposition")
        self.assertEqual(profile.coverage.status, "complete")
        self.assertIn("aspect:opposition_Mars", profile.coverage.covered_factors)
        self.assertEqual(_ids(profile.aspect_facts), _ids(MARS_OPPOSITION))
        self.assertTrue(all(item.factor_key == "opposition_Mars" for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("mars_sq_") for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("mars_cj_") for item in profile.aspect_facts))
        resolved = {item.id for item in profile.aspect_facts if not item.unresolved}
        self.assertEqual(resolved, _ids(MARS_OPPOSITION_RESOLVED))
        unresolved = _ids(profile.conditional_unresolved)
        self.assertTrue(_ids(MARS_OPPOSITION_UNRESOLVED).issubset(unresolved))
        female = next(
            item
            for item in profile.conditional_unresolved
            if item.id == "mars_opp_branch_female_chart_younger_partner"
        )
        self.assertEqual(female.activation_condition, "female_chart_context_unresolved")
        all_facts = list(profile.aspect_facts) + list(profile.conditional_unresolved)
        for signal in detect_repeated_signals(all_facts):
            for fact_id in signal.fact_ids:
                fact = next(item for item in all_facts if item.id == fact_id)
                self.assertFalse(fact.unresolved, signal)
        self.assertEqual(
            detect_repeated_signals([item for item in profile.aspect_facts if not item.unresolved]),
            [],
        )

    def test_conjunction_activates_only_conjunction_pack(self):
        profile = _synthetic_mars("conjunction")
        self.assertEqual(profile.coverage.status, "complete")
        self.assertIn("aspect:conjunction_Mars", profile.coverage.covered_factors)
        self.assertEqual(_ids(profile.aspect_facts), _ids(MARS_CONJUNCTION))
        self.assertTrue(all(item.factor_key == "conjunction_Mars" for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("mars_sq_") for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("mars_opp_") for item in profile.aspect_facts))
        resolved = {item.id for item in profile.aspect_facts if not item.unresolved}
        self.assertEqual(resolved, _ids(MARS_CONJUNCTION_RESOLVED))
        self.assertTrue(_ids(MARS_CONJUNCTION_UNRESOLVED).issubset(_ids(profile.conditional_unresolved)))
        female = next(
            item
            for item in profile.conditional_unresolved
            if item.id == "mars_cj_branch_female_chart_younger_partner"
        )
        self.assertEqual(female.activation_condition, "female_chart_context_unresolved")
        all_facts = list(profile.aspect_facts) + list(profile.conditional_unresolved)
        for signal in detect_repeated_signals(all_facts):
            for fact_id in signal.fact_ids:
                fact = next(item for item in all_facts if item.id == fact_id)
                self.assertFalse(fact.unresolved, signal)
        self.assertEqual(
            detect_repeated_signals([item for item in profile.aspect_facts if not item.unresolved]),
            [],
        )

    def test_square_and_harmonious_remain_separate(self):
        square = _synthetic_mars("square")
        trine = _synthetic_mars("trine")
        sextile = _synthetic_mars("sextile")
        self.assertTrue(all(item.factor_key == "square_Mars" for item in square.aspect_facts))
        self.assertFalse(any(item.id.startswith("mars_opp_") for item in square.aspect_facts))
        self.assertFalse(any(item.id.startswith("mars_cj_") for item in square.aspect_facts))
        self.assertTrue(all(item.factor_key == "trine_Mars" for item in trine.aspect_facts))
        self.assertTrue(all(item.factor_key == "sextile_Mars" for item in sextile.aspect_facts))
        self.assertFalse(any(item.id.startswith("mars_opp_") for item in trine.aspect_facts))
        self.assertFalse(any(item.id.startswith("mars_cj_") for item in sextile.aspect_facts))

    def test_synthetic_unknown_aspect_still_marks_partial(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Leo",
                mercury_element="fire",
                mercury_motion="direct",
                mercury_house=1,
                aspects=[MercuryAspect(planet="SyntheticProbe", type="conjunction", orb_deg=2.0)],
            )
        )
        self.assertEqual(profile.coverage.status, "partial")
        self.assertEqual(profile.coverage.missing_factors, ["aspect:conjunction_SyntheticProbe"])
        self.assertIn("opposition_Mars", SUPPORTED_ASPECT_KEYS)
        self.assertIn("conjunction_Mars", SUPPORTED_ASPECT_KEYS)


class AspectBatchC7RegressionTests(unittest.TestCase):
    def test_golden_cases_remain_complete_and_stable(self):
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
                    any(item.id.startswith("mars_opp_") for item in profile.aspect_facts)
                )
                self.assertFalse(
                    any(item.id.startswith("mars_cj_") for item in profile.aspect_facts)
                )

    def test_dzmitry_keeps_harmonious_mars_only(self):
        profile = build_mercury_source_profile(
            MercurySourceProfileRequest(
                birth_date=date(1985, 11, 12),
                birth_time=time(14, 15),
                birth_place="Zhodino, Belarus",
            )
        )
        mars = [item for item in profile.aspect_facts if "Mars" in item.factor_key]
        self.assertTrue(mars)
        self.assertTrue(all(item.factor_key in {"sextile_Mars", "trine_Mars"} for item in mars))
        self.assertFalse(any(item.factor_key in {"opposition_Mars", "conjunction_Mars", "square_Mars"} for item in mars))

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
