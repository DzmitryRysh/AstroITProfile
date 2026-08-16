"""Tests for Mercury Source Profile v2 — Aspect Batch C3 (Pluto harmonious)."""

from __future__ import annotations

import unittest
from collections import Counter
from datetime import date, time

from app.schemas.mercury_source_profile import MercurySourceProfileRequest
from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_source_knowledge import (
    ALL_SOURCE_FACTS,
    ASPECT_PACK_ALIASES,
    PLUTO_SQUARE,
    SUPPORTED_ASPECT_KEYS,
)
from app.services.mercury_source_knowledge_c3_aspects import (
    PLUTO_HARMONIOUS,
    REF_PLUTO_HARM,
)
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
    detect_repeated_signals,
)

REF_PLUTO_SQ = "bioastrology_mercury_pluto_square"


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


class AspectBatchC3CoverageTests(unittest.TestCase):
    def test_c3_public_aspect_keys_remain_supported(self):
        # Historical C3 batch: harmonious Pluto subset guarantee only.
        # Exact Pluto conj/opp ownership is C14+.
        self.assertTrue({"trine_Pluto", "sextile_Pluto"}.issubset(SUPPORTED_ASPECT_KEYS))

    def test_c3_pluto_harmonious_alias_and_square_separation(self):
        self.assertEqual(ASPECT_PACK_ALIASES["sextile_Pluto"], "trine_Pluto")
        # SOURCE_JUSTIFIED: pair-specific Bioastrology labels this branch "трин/секстиль".
        self.assertIn("trine_Pluto", _canonical_aspect_packs())
        self.assertNotIn("sextile_Pluto", _canonical_aspect_packs())
        harm = [
            item
            for item in ALL_SOURCE_FACTS
            if item.factor_type == "aspect" and item.factor_key == "trine_Pluto"
        ]
        self.assertEqual(len(harm), len(PLUTO_HARMONIOUS))
        self.assertEqual(len(PLUTO_HARMONIOUS), 14)
        self.assertIn("square_Pluto", _canonical_aspect_packs())
        self.assertNotEqual(REF_PLUTO_HARM, REF_PLUTO_SQ)
        self.assertTrue(all(item.source_reference == REF_PLUTO_SQ for item in PLUTO_SQUARE))
        self.assertTrue(all(item.source_reference == REF_PLUTO_HARM for item in PLUTO_HARMONIOUS))
        self.assertTrue(_ids(PLUTO_HARMONIOUS).isdisjoint(_ids(PLUTO_SQUARE)))

    def test_c1_aliases_remain_unchanged(self):
        self.assertEqual(ASPECT_PACK_ALIASES["sextile_Mars"], "trine_Mars")
        self.assertEqual(ASPECT_PACK_ALIASES["trine_Moon"], "sextile_Moon")
        self.assertEqual(ASPECT_PACK_ALIASES["trine_Jupiter"], "sextile_Jupiter")
        self.assertEqual(ASPECT_PACK_ALIASES["sextile_Saturn"], "trine_Saturn")
        self.assertEqual(ASPECT_PACK_ALIASES["sextile_Uranus"], "trine_Uranus")

    def test_c2_square_keys_remain(self):
        self.assertIn("square_Mars", SUPPORTED_ASPECT_KEYS)
        self.assertIn("square_Saturn", SUPPORTED_ASPECT_KEYS)

    def test_catalog_integrity(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])
        self.assertTrue(all(item.source_reference for item in ALL_SOURCE_FACTS))
        self.assertTrue(all(item.source_reference == REF_PLUTO_HARM for item in PLUTO_HARMONIOUS))
        self.assertTrue(all(not item.unresolved for item in PLUTO_HARMONIOUS))
        self.assertTrue(
            all(item.activation_condition is None for item in PLUTO_HARMONIOUS)
        )


class AspectBatchC3AliasAndSeparationTests(unittest.TestCase):
    def _profile(self, aspect_type: str, planet: str = "Pluto"):
        return build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Virgo",
                mercury_element="earth",
                mercury_motion="direct",
                mercury_house=3,
                aspects=[MercuryAspect(planet=planet, type=aspect_type, orb_deg=1.0)],
            )
        )

    def test_trine_and_sextile_share_canonical_family_with_public_provenance(self):
        trine = self._profile("trine")
        sextile = self._profile("sextile")
        self.assertEqual(_refs(trine.aspect_facts), {REF_PLUTO_HARM})
        self.assertEqual(_refs(sextile.aspect_facts), {REF_PLUTO_HARM})
        self.assertEqual(_ids(trine.aspect_facts), _ids(sextile.aspect_facts))
        self.assertTrue(all(item.factor_key == "trine_Pluto" for item in trine.aspect_facts))
        self.assertTrue(all(item.factor_key == "sextile_Pluto" for item in sextile.aspect_facts))
        self.assertIn("aspect:trine_Pluto", trine.coverage.covered_factors)
        self.assertIn("aspect:sextile_Pluto", sextile.coverage.covered_factors)
        self.assertNotIn("aspect:trine_Pluto", sextile.coverage.covered_factors)

    def test_square_pluto_remains_separate(self):
        square = self._profile("square")
        trine = self._profile("trine")
        self.assertTrue(all(item.source_reference == REF_PLUTO_SQ for item in PLUTO_SQUARE))
        self.assertEqual(_refs(square.aspect_facts), {REF_PLUTO_SQ})
        self.assertNotEqual(_refs(square.aspect_facts), {REF_PLUTO_HARM})
        self.assertTrue(_ids(square.aspect_facts).isdisjoint(_ids(trine.aspect_facts)))
        unresolved = [
            item
            for item in square.conditional_unresolved
            if item.id.startswith("pluto_sq_branch_")
        ]
        self.assertGreaterEqual(len(unresolved), 7)
        self.assertTrue(
            all(item.activation_condition == "pluto_strength_unresolved" for item in unresolved)
        )
        self.assertFalse(any(item.unresolved for item in trine.aspect_facts))
        self.assertFalse(
            any(item.id.startswith("pluto_sq_") for item in trine.aspect_facts)
        )
        self.assertFalse(
            any(item.id.startswith("pluto_harm_") for item in square.aspect_facts)
        )


class AspectBatchC3TagHardeningTests(unittest.TestCase):
    def test_exact_atoms_and_insight_separation(self):
        by_id = {item.id: item for item in PLUTO_HARMONIOUS}
        self.assertEqual(by_id["pluto_harm_persuasiveness"].tags, ("persuasion",))
        self.assertEqual(by_id["pluto_harm_perceptiveness"].tags, ("perceptiveness",))
        self.assertNotIn("insight", by_id["pluto_harm_perceptiveness"].tags)
        self.assertEqual(by_id["pluto_harm_verbal_force"].tags, ("verbal_force",))
        self.assertEqual(by_id["pluto_harm_blunt_truth_speech"].tags, ("blunt_truth_speech",))
        self.assertEqual(by_id["pluto_harm_source_nlp_aptitude"].tags, ("source_nlp_aptitude",))
        self.assertEqual(by_id["pluto_harm_debate_ability"].tags, ("debate",))
        self.assertEqual(by_id["pluto_harm_weighty_arguments"].tags, ("argumentation",))
        self.assertEqual(by_id["pluto_harm_technical_talents"].tags, ("technical_ability",))
        self.assertEqual(
            by_id["pluto_harm_source_diagnostic_aptitude"].tags,
            ("source_diagnostic_aptitude",),
        )
        self.assertNotIn("insight", by_id["pluto_harm_source_diagnostic_aptitude"].tags)
        self.assertEqual(
            by_id["pluto_harm_vulnerability_detection"].tags,
            ("vulnerability_detection",),
        )
        self.assertNotIn("insight", by_id["pluto_harm_vulnerability_detection"].tags)
        self.assertEqual(by_id["pluto_harm_analytical_quality"].tags, ("analytical_thinking",))
        self.assertEqual(
            by_id["pluto_harm_source_psychological_aptitude"].tags,
            ("source_psychological_aptitude",),
        )
        self.assertNotIn("insight", by_id["pluto_harm_source_psychological_aptitude"].tags)
        self.assertEqual(
            by_id["pluto_harm_source_hypnotic_aptitude"].tags,
            ("source_hypnotic_aptitude",),
        )
        for fact_id in (
            "pluto_harm_source_nlp_aptitude",
            "pluto_harm_source_diagnostic_aptitude",
            "pluto_harm_source_psychological_aptitude",
            "pluto_harm_source_hypnotic_aptitude",
        ):
            self.assertEqual(by_id[fact_id].category, "source_specific")


class AspectBatchC3SyntheticAcceptanceTests(unittest.TestCase):
    def test_synthetic_trine_pluto_complete(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Virgo",
                mercury_element="earth",
                mercury_motion="direct",
                mercury_house=3,
                aspects=[MercuryAspect(planet="Pluto", type="trine", orb_deg=1.0)],
            )
        )
        self.assertEqual(profile.coverage.status, "complete")
        self.assertEqual(profile.coverage.missing_factors, [])
        self.assertIn("aspect:trine_Pluto", profile.coverage.covered_factors)
        self.assertEqual(_ids(profile.aspect_facts), _ids(PLUTO_HARMONIOUS))
        self.assertFalse(any(item.id.startswith("pluto_sq_") for item in profile.aspect_facts))
        self.assertFalse(
            any(
                item.activation_condition in {"pluto_strength_unresolved", "strength_unresolved"}
                for item in profile.aspect_facts
            )
        )
        # Same factor cannot create a repeat by itself from multiple pack tags.
        self.assertEqual(
            detect_repeated_signals(list(profile.aspect_facts)),
            [],
        )

    def test_synthetic_sextile_pluto_provenance(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Virgo",
                mercury_element="earth",
                mercury_motion="direct",
                mercury_house=3,
                aspects=[MercuryAspect(planet="Pluto", type="sextile", orb_deg=1.0)],
            )
        )
        self.assertEqual(profile.coverage.status, "complete")
        self.assertIn("aspect:sextile_Pluto", profile.coverage.covered_factors)
        self.assertNotIn("aspect:trine_Pluto", profile.coverage.covered_factors)
        self.assertEqual(_ids(profile.aspect_facts), _ids(PLUTO_HARMONIOUS))
        self.assertTrue(all(item.factor_key == "sextile_Pluto" for item in profile.aspect_facts))
        self.assertEqual(detect_repeated_signals(list(profile.aspect_facts)), [])


class AspectBatchC3RegressionTests(unittest.TestCase):
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
                harm_ids = {item.id for item in profile.aspect_facts if item.id.startswith("pluto_harm_")}
                self.assertEqual(harm_ids, set())

    def test_avdey_and_andrey_use_square_pluto_only(self):
        avdey = build_mercury_source_profile(
            MercurySourceProfileRequest(
                birth_date=date(1986, 7, 14),
                birth_time=time(7, 10),
                birth_place="Simferopol, Ukraine",
            )
        )
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
        for profile, label in ((avdey, "Avdey"), (andrey, "Andrey")):
            with self.subTest(person=label):
                pluto = [item for item in profile.aspect_facts if "Pluto" in item.factor_key]
                self.assertTrue(pluto)
                self.assertTrue(all(item.factor_key == "square_Pluto" for item in pluto))
                self.assertTrue(all(item.source_reference == REF_PLUTO_SQ for item in pluto))
                self.assertFalse(any(item.id.startswith("pluto_harm_") for item in pluto))

    def test_dzmitry_uranus_conjunction_unchanged(self):
        profile = build_mercury_source_profile(
            MercurySourceProfileRequest(
                birth_date=date(1985, 11, 12),
                birth_time=time(14, 15),
                birth_place="Zhodino, Belarus",
            )
        )
        uranus = [item for item in profile.aspect_facts if "Uranus" in item.factor_key]
        self.assertTrue(uranus)
        self.assertTrue(all(item.factor_key == "conjunction_Uranus" for item in uranus))

    def test_milka_like_unchanged(self):
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
        self.assertEqual(profile.coverage.missing_factors, [])


if __name__ == "__main__":
    unittest.main()
