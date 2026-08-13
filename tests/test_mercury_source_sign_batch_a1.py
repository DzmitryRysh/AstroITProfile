"""Tests for Mercury Source Profile v2 — Sign Batch A1 (Aries/Gemini/Cancer)."""

from __future__ import annotations

import unittest
from datetime import date, time

from app.schemas.mercury_source_profile import MercurySourceProfileRequest
from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_source_knowledge import SUPPORTED_SIGN_KEYS
from app.services.mercury_source_knowledge_a1_signs import (
    ARIES_BIOASTROLOGY,
    ARIES_LESSON7,
    CANCER_AFFLICTED,
    CANCER_BIOASTROLOGY,
    CANCER_LESSON7,
    GEMINI_AFFLICTED,
    GEMINI_BIOASTROLOGY,
    GEMINI_LESSON7,
    REF_ARIES_BIO,
    REF_ARIES_L7,
    REF_CANCER_BIO,
    REF_CANCER_L7,
    REF_GEMINI_BIO,
    REF_GEMINI_L7,
)
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
    detect_repeated_signals,
)


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


def _refs(facts) -> set[str]:
    return {item.source_reference for item in facts}


class SignBatchA1CatalogTests(unittest.TestCase):
    def test_supported_signs_include_a1(self):
        self.assertTrue(
            {"Aries", "Taurus", "Gemini", "Cancer", "Leo", "Sagittarius"}.issubset(
                SUPPORTED_SIGN_KEYS
            )
        )

    def test_aries_split_and_source_refs(self):
        self.assertGreater(len(ARIES_LESSON7), 0)
        self.assertGreater(len(ARIES_BIOASTROLOGY), 0)
        self.assertTrue(all(item.source_reference == REF_ARIES_L7 for item in ARIES_LESSON7))
        self.assertTrue(all(item.source_reference == REF_ARIES_BIO for item in ARIES_BIOASTROLOGY))
        self.assertIn("aries_l7_fast_thinking", {item.id for item in ARIES_LESSON7})
        self.assertIn("aries_bio_martian_speed_coloring", {item.id for item in ARIES_BIOASTROLOGY})
        self.assertIn(
            "aries_bio_source_sexual_motivation_wording",
            {item.id for item in ARIES_BIOASTROLOGY},
        )
        sexual = next(
            item for item in ARIES_BIOASTROLOGY if item.id == "aries_bio_source_sexual_motivation_wording"
        )
        self.assertEqual(sexual.category, "source_specific")

    def test_gemini_split_and_source_refs(self):
        self.assertTrue(all(item.source_reference == REF_GEMINI_L7 for item in GEMINI_LESSON7))
        self.assertTrue(all(item.source_reference == REF_GEMINI_BIO for item in GEMINI_BIOASTROLOGY))
        self.assertTrue(all(item.source_reference == REF_GEMINI_BIO for item in GEMINI_AFFLICTED))
        self.assertIn("gemini_l7_high_working_memory_speed", {item.id for item in GEMINI_LESSON7})
        self.assertIn("gemini_bio_strong_memory", {item.id for item in GEMINI_BIOASTROLOGY})
        # Distinct tags: working-memory speed != strong memory
        speed = next(item for item in GEMINI_LESSON7 if item.id == "gemini_l7_high_working_memory_speed")
        memory = next(item for item in GEMINI_BIOASTROLOGY if item.id == "gemini_bio_strong_memory")
        self.assertIn("working_memory_speed", speed.tags)
        self.assertNotIn("strong_memory", speed.tags)
        self.assertNotIn("memory", speed.tags)
        self.assertIn("strong_memory", memory.tags)
        self.assertNotIn("working_memory_speed", memory.tags)

    def test_cancer_split_and_source_refs(self):
        self.assertTrue(all(item.source_reference == REF_CANCER_L7 for item in CANCER_LESSON7))
        self.assertTrue(
            all(item.source_reference == REF_CANCER_BIO for item in CANCER_BIOASTROLOGY + CANCER_AFFLICTED)
        )
        self.assertIn("cancer_l7_sticky_memory_emotions", {item.id for item in CANCER_LESSON7})
        self.assertIn("cancer_bio_notice_subtext", {item.id for item in CANCER_BIOASTROLOGY})
        moon_dep = next(item for item in CANCER_BIOASTROLOGY if item.id == "cancer_bio_depends_on_moon_sign")
        self.assertTrue(moon_dep.unresolved)
        self.assertEqual(moon_dep.category, "source_specific")
        ei = next(
            item
            for item in CANCER_BIOASTROLOGY
            if item.id == "cancer_bio_emotional_intelligence_source_claim"
        )
        self.assertEqual(ei.category, "source_specific")

    def test_no_sexist_afflicted_label_reproduced(self):
        texts = " ".join(item.text.lower() for item in CANCER_AFFLICTED)
        self.assertNotIn("баб", texts)
        self.assertIn("disregard for facts", texts)


class SignBatchA1ActivationTests(unittest.TestCase):
    def test_aries_activates_both_sources_under_one_factor(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=False,
                mercury_sign="Aries",
                mercury_element="fire",
                mercury_motion="direct",
                mercury_house=None,
                aspects=[],
            )
        )
        ids = _ids(profile.sign_facts)
        self.assertIn("aries_l7_fast_thinking", ids)
        self.assertIn("aries_bio_technical_practicality", ids)
        self.assertEqual(_refs(profile.sign_facts), {REF_ARIES_L7, REF_ARIES_BIO})
        self.assertTrue(all(item.factor_key == "Aries" for item in profile.sign_facts))

    def test_dual_source_same_sign_does_not_create_false_repeat(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=False,
                mercury_sign="Aries",
                mercury_element="fire",
                mercury_motion="direct",
                mercury_house=None,
                aspects=[],
            )
        )
        # Listening difficulty appears in both sources, but still one factor key.
        repeats = detect_repeated_signals(profile.sign_facts)
        for signal in repeats:
            self.assertGreaterEqual(signal.source_count, 2)
            self.assertTrue(all(":" in src for src in signal.sources))
            # Must not invent a second sign provenance from dual sources.
            sign_sources = [src for src in signal.sources if src.startswith("sign:")]
            self.assertLessEqual(len(sign_sources), 1, signal)

    def test_gemini_afflicted_requires_hard_aspected(self):
        soft = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Gemini",
                mercury_element="air",
                mercury_motion="direct",
                mercury_house=3,
                aspects=[MercuryAspect(planet="Jupiter", type="trine", orb_deg=1.0)],
            )
        )
        hard = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Gemini",
                mercury_element="air",
                mercury_motion="direct",
                mercury_house=3,
                aspects=[MercuryAspect(planet="Pluto", type="square", orb_deg=1.0)],
            )
        )
        soft_ids = _ids(soft.sign_facts)
        hard_ids = _ids(hard.sign_facts)
        for fact_id in (
            "gemini_bio_afflicted_lying",
            "gemini_bio_afflicted_excessive_verbal_output",
            "gemini_bio_afflicted_words_exceed_actions",
        ):
            self.assertNotIn(fact_id, soft_ids)
            self.assertIn(fact_id, hard_ids)
        self.assertFalse(soft.calculated.hard_aspected)
        self.assertTrue(hard.calculated.hard_aspected)

    def test_cancer_afflicted_requires_hard_aspected(self):
        soft = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Cancer",
                mercury_element="water",
                mercury_motion="direct",
                mercury_house=5,
                aspects=[MercuryAspect(planet="Uranus", type="trine", orb_deg=1.65)],
            )
        )
        hard = build_source_profile_from_factors(
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
        self.assertNotIn("cancer_bio_afflicted_disregard_for_facts", _ids(soft.sign_facts))
        self.assertIn("cancer_bio_afflicted_disregard_for_facts", _ids(hard.sign_facts))
        self.assertIn("cancer_bio_afflicted_losing_the_thread", _ids(hard.sign_facts))

    def test_cancer_moon_dependency_is_unresolved_not_resolved(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Cancer",
                mercury_element="water",
                mercury_motion="direct",
                mercury_house=5,
                aspects=[],
            )
        )
        dep = next(
            item for item in profile.sign_facts if item.id == "cancer_bio_depends_on_moon_sign"
        )
        self.assertTrue(dep.unresolved)
        self.assertIn(dep.id, _ids(profile.conditional_unresolved))

    def test_andrey_like_cancer_now_complete(self):
        profile = build_source_profile_from_factors(
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
        self.assertEqual(profile.coverage.status, "complete")
        self.assertIn("sign:Cancer", profile.coverage.covered_factors)
        self.assertIn("house:5", profile.coverage.covered_factors)
        self.assertNotIn("house:5", profile.coverage.missing_factors)
        self.assertEqual(profile.coverage.missing_factors, [])
        self.assertIn("aspect:square_Pluto", profile.coverage.covered_factors)
        self.assertIn("aspect:trine_Uranus", profile.coverage.covered_factors)
        self.assertGreater(len(profile.sign_facts), 0)
        self.assertTrue(any(item.id.startswith("cancer_l7_") for item in profile.sign_facts))
        self.assertTrue(any(item.id.startswith("cancer_bio_") for item in profile.sign_facts))
        # Afflicted Cancer activates because square Pluto makes hard_aspected.
        self.assertIn("cancer_bio_afflicted_disregard_for_facts", _ids(profile.sign_facts))
        self.assertGreater(len(profile.house_facts), 0)
        self.assertTrue(
            any(item.factor_key == "square_Pluto" for item in profile.aspect_facts)
        )
        self.assertTrue(
            any(item.factor_key == "trine_Uranus" for item in profile.aspect_facts)
        )


class SignBatchA1RegressionGoldenTests(unittest.TestCase):
    def test_avdey_vlad_dzmitry_remain_complete(self):
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


if __name__ == "__main__":
    unittest.main()
