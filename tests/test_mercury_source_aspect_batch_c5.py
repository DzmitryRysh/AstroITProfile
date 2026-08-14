"""Tests for Mercury Source Profile v2 — Aspect Batch C5 (Jupiter opposition / conjunction)."""

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
from app.services.mercury_source_knowledge_c4_aspects import JUPITER_SQUARE, REF_JUPITER_SQ
from app.services.mercury_source_knowledge_c5_aspects import (
    JUPITER_CONJUNCTION,
    JUPITER_OPPOSITION,
    REF_JUPITER_CONJ,
    REF_JUPITER_OPP,
)
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
    detect_repeated_signals,
)

JUPITER_PUBLIC_FAMILY = {
    "conjunction_Jupiter",
    "sextile_Jupiter",
    "square_Jupiter",
    "trine_Jupiter",
    "opposition_Jupiter",
}


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


def _canonical_aspect_packs() -> set[str]:
    return {
        item.factor_key
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "aspect"
    }


def _synthetic(aspect_type: str):
    return build_source_profile_from_factors(
        MercurySourceFactors(
            birth_time_known=True,
            mercury_sign="Virgo",
            mercury_element="earth",
            mercury_motion="direct",
            mercury_house=3,
            aspects=[MercuryAspect(planet="Jupiter", type=aspect_type, orb_deg=1.2)],
        )
    )


class AspectBatchC5CoverageTests(unittest.TestCase):
    def test_c5_jupiter_family_remains_complete(self):
        # Historical C5 batch: factor-specific guarantee. Exact public count owned by C6+.
        self.assertTrue(JUPITER_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertIn("opposition_Jupiter", SUPPORTED_ASPECT_KEYS)
        self.assertIn("conjunction_Jupiter", SUPPORTED_ASPECT_KEYS)
        self.assertNotIn("opposition_Jupiter", ASPECT_PACK_ALIASES)
        self.assertNotIn("conjunction_Jupiter", ASPECT_PACK_ALIASES)
        self.assertIn("opposition_Jupiter", _canonical_aspect_packs())
        self.assertIn("conjunction_Jupiter", _canonical_aspect_packs())
        self.assertNotEqual(ASPECT_PACK_ALIASES.get("opposition_Jupiter"), "square_Jupiter")
        self.assertNotEqual(ASPECT_PACK_ALIASES.get("conjunction_Jupiter"), "square_Jupiter")

    def test_distinct_canonical_refs_and_catalog_identity(self):
        self.assertEqual(REF_JUPITER_OPP, "bioastrology_mercury_jupiter_opposition")
        self.assertEqual(REF_JUPITER_CONJ, "bioastrology_mercury_jupiter_conjunction")
        self.assertNotEqual(REF_JUPITER_OPP, REF_JUPITER_SQ)
        self.assertNotEqual(REF_JUPITER_CONJ, REF_JUPITER_SQ)
        self.assertNotEqual(REF_JUPITER_OPP, REF_JUPITER_CONJ)
        self.assertTrue(all(item.source_reference == REF_JUPITER_OPP for item in JUPITER_OPPOSITION))
        self.assertTrue(all(item.source_reference == REF_JUPITER_CONJ for item in JUPITER_CONJUNCTION))
        self.assertTrue(_ids(JUPITER_OPPOSITION).isdisjoint(_ids(JUPITER_SQUARE)))
        self.assertTrue(_ids(JUPITER_CONJUNCTION).isdisjoint(_ids(JUPITER_SQUARE)))
        self.assertTrue(_ids(JUPITER_OPPOSITION).isdisjoint(_ids(JUPITER_CONJUNCTION)))

    def test_catalog_integrity(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])
        self.assertTrue(all(item.source_reference for item in ALL_SOURCE_FACTS))
        self.assertTrue(all(not item.unresolved for item in JUPITER_OPPOSITION))
        self.assertTrue(all(not item.unresolved for item in JUPITER_CONJUNCTION))
        self.assertTrue(all(item.activation_condition is None for item in JUPITER_OPPOSITION))
        self.assertTrue(all(item.activation_condition is None for item in JUPITER_CONJUNCTION))
        self.assertFalse(any(item.category == "compensation" for item in JUPITER_OPPOSITION))
        self.assertFalse(any(item.category == "compensation" for item in JUPITER_CONJUNCTION))
        self.assertFalse(any("supergift" in item.id for item in JUPITER_OPPOSITION + JUPITER_CONJUNCTION))
        self.assertFalse(any("genius" in item.text.lower() for item in JUPITER_OPPOSITION + JUPITER_CONJUNCTION))

    def test_prior_aliases_unchanged(self):
        self.assertEqual(ASPECT_PACK_ALIASES["sextile_Mars"], "trine_Mars")
        self.assertEqual(ASPECT_PACK_ALIASES["trine_Moon"], "sextile_Moon")
        self.assertEqual(ASPECT_PACK_ALIASES["trine_Jupiter"], "sextile_Jupiter")
        self.assertEqual(ASPECT_PACK_ALIASES["sextile_Saturn"], "trine_Saturn")
        self.assertEqual(ASPECT_PACK_ALIASES["sextile_Uranus"], "trine_Uranus")
        self.assertEqual(ASPECT_PACK_ALIASES["sextile_Pluto"], "trine_Pluto")


class AspectBatchC5AtomTests(unittest.TestCase):
    def test_opposition_source_atoms_present(self):
        by_id = {item.id: item for item in JUPITER_OPPOSITION}
        self.assertEqual(
            by_id["jupiter_opp_knowledge_certainty_oscillation"].tags,
            ("knowledge_certainty_oscillation",),
        )
        self.assertEqual(
            by_id["jupiter_opp_practical_abstract_thinking_oscillation"].tags,
            ("practical_abstract_thinking_oscillation",),
        )
        self.assertNotIn(
            "analytical_plus_abstract",
            by_id["jupiter_opp_practical_abstract_thinking_oscillation"].tags,
        )
        self.assertEqual(by_id["jupiter_opp_foreign_languages"].tags, ("foreign_languages",))
        self.assertEqual(by_id["jupiter_opp_persuasion"].tags, ("persuasion",))
        self.assertEqual(by_id["jupiter_opp_lifelong_learning"].tags, ("lifelong_learning",))
        self.assertEqual(by_id["jupiter_opp_legal_aptitude"].tags, ("legal_aptitude",))
        self.assertNotIn("argumentation", by_id["jupiter_opp_legal_aptitude"].tags)
        self.assertEqual(by_id["jupiter_opp_oratory"].tags, ("oratory",))
        self.assertNotIn("persuasion", by_id["jupiter_opp_oratory"].tags)
        self.assertNotIn("analytical_plus_abstract", by_id["jupiter_opp_philosophy_interest"].tags)
        self.assertNotIn("analytical_plus_abstract", by_id["jupiter_opp_science_interest"].tags)
        self.assertNotIn("analytical_plus_abstract", by_id["jupiter_opp_esoteric_interest"].tags)

    def test_conjunction_source_atoms_present(self):
        by_id = {item.id: item for item in JUPITER_CONJUNCTION}
        self.assertIn(
            "jupiter_cj_resembles_jupiter_dominant_square_less_intensity",
            by_id,
        )
        self.assertEqual(by_id["jupiter_cj_intellectual_showing_off"].tags, ("intellectual_showing_off",))
        self.assertNotIn("intelligence", by_id["jupiter_cj_intellectual_showing_off"].tags)
        self.assertNotIn("intelligence", by_id["jupiter_cj_intellectual_superiority_framing"].tags)
        self.assertEqual(by_id["jupiter_cj_promise_execution_gap"].tags, ("promise_execution_gap",))
        self.assertNotIn("dishonesty", by_id["jupiter_cj_promise_execution_gap"].tags)
        self.assertNotIn("dishonesty", by_id["jupiter_cj_empty_promises"].tags)
        self.assertNotIn("lying", by_id["jupiter_cj_empty_promises"].tags)
        self.assertEqual(by_id["jupiter_cj_legal_aptitude"].tags, ("legal_aptitude",))
        self.assertNotIn("argumentation", by_id["jupiter_cj_legal_aptitude"].tags)
        self.assertEqual(by_id["jupiter_cj_foreign_languages"].tags, ("foreign_languages",))
        self.assertEqual(by_id["jupiter_cj_persuasion"].tags, ("persuasion",))
        self.assertEqual(by_id["jupiter_cj_lifelong_learning"].tags, ("lifelong_learning",))
        self.assertNotIn("analytical_plus_abstract", by_id["jupiter_cj_philosophy_interest"].tags)
        self.assertNotIn("analytical_thinking", by_id["jupiter_cj_evaluative_judgment_habit"].tags)
        self.assertNotIn("debate", by_id["jupiter_cj_teacher_conflicts"].tags)
        self.assertNotIn("teaching", by_id["jupiter_cj_self_elevation_over_teacher"].tags)
        self.assertNotIn("foreign_languages", by_id["jupiter_cj_foreign_word_display"].tags)

    def test_road_risk_is_source_described_not_predictive(self):
        road_facts = [
            item
            for item in JUPITER_OPPOSITION + JUPITER_CONJUNCTION
            if "road" in item.id
        ]
        self.assertEqual(len(road_facts), 4)
        for item in road_facts:
            text = item.text.lower()
            self.assertIn("source", text)
            self.assertTrue("source-described" in text or "source describes" in text)
            self.assertIn("not a prediction", text)
            self.assertNotIn("you will", text)


class AspectBatchC5ActivationTests(unittest.TestCase):
    def test_opposition_activates_only_opposition_pack(self):
        profile = _synthetic("opposition")
        self.assertEqual(profile.coverage.status, "complete")
        self.assertIn("aspect:opposition_Jupiter", profile.coverage.covered_factors)
        self.assertEqual(_ids(profile.aspect_facts), _ids(JUPITER_OPPOSITION))
        self.assertTrue(all(item.factor_key == "opposition_Jupiter" for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("jupiter_sq_") for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("jupiter_cj_") for item in profile.aspect_facts))
        self.assertFalse(any(item.unresolved for item in profile.aspect_facts))
        self.assertFalse(
            any(item.id.startswith("jupiter_opp_") for item in profile.conditional_unresolved)
        )

    def test_conjunction_activates_only_conjunction_pack(self):
        profile = _synthetic("conjunction")
        self.assertEqual(profile.coverage.status, "complete")
        self.assertIn("aspect:conjunction_Jupiter", profile.coverage.covered_factors)
        self.assertEqual(_ids(profile.aspect_facts), _ids(JUPITER_CONJUNCTION))
        self.assertTrue(all(item.factor_key == "conjunction_Jupiter" for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("jupiter_sq_") for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("jupiter_opp_") for item in profile.aspect_facts))
        self.assertFalse(any(item.unresolved for item in profile.aspect_facts))

    def test_square_does_not_activate_c5_packs(self):
        profile = _synthetic("square")
        self.assertTrue(all(item.factor_key == "square_Jupiter" for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("jupiter_opp_") for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("jupiter_cj_") for item in profile.aspect_facts))

    def test_single_jupiter_factor_does_not_self_repeat(self):
        for aspect_type in ("opposition", "conjunction"):
            with self.subTest(aspect=aspect_type):
                profile = _synthetic(aspect_type)
                self.assertEqual(detect_repeated_signals(list(profile.aspect_facts)), [])


class AspectBatchC5RegressionTests(unittest.TestCase):
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
                    any(item.id.startswith("jupiter_opp_") for item in profile.aspect_facts)
                )
                self.assertFalse(
                    any(item.id.startswith("jupiter_cj_") for item in profile.aspect_facts)
                )

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
