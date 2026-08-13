"""Tests for Mercury Source Profile v2 — Sign Batch A3 (Capricorn/Aquarius/Pisces)."""

from __future__ import annotations

import unittest
from collections import Counter
from datetime import date, time

from app.schemas.mercury_source_profile import MercurySourceProfileRequest
from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS, SUPPORTED_SIGN_KEYS
from app.services.mercury_source_knowledge_a1_signs import ARIES_ALL, CANCER_ALL, GEMINI_ALL
from app.services.mercury_source_knowledge_a2_signs import LIBRA_ALL, SCORPIO_ALL, VIRGO_ALL
from app.services.mercury_source_knowledge_a3_signs import (
    A3_SIGN_PACKS,
    AQUARIUS_AFFLICTED,
    AQUARIUS_BIOASTROLOGY,
    AQUARIUS_LESSON7,
    CAPRICORN_AFFLICTED,
    CAPRICORN_BIOASTROLOGY,
    CAPRICORN_LESSON7,
    PISCES_AFFLICTED,
    PISCES_BIOASTROLOGY,
    PISCES_LESSON7,
    REF_AQUARIUS_BIO,
    REF_AQUARIUS_L7,
    REF_CAPRICORN_BIO,
    REF_CAPRICORN_L7,
    REF_PISCES_BIO,
    REF_PISCES_L7,
)
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
    detect_repeated_signals,
)


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


ALL_TWELVE_SIGNS = {
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
}


class SignBatchA3CatalogTests(unittest.TestCase):
    def test_supported_signs_cover_all_twelve(self):
        self.assertEqual(SUPPORTED_SIGN_KEYS, ALL_TWELVE_SIGNS)
        self.assertEqual(len(SUPPORTED_SIGN_KEYS), 12)

    def test_all_ids_unique(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])

    def test_capricorn_source_reference_separation(self):
        self.assertTrue(all(item.source_reference == REF_CAPRICORN_L7 for item in CAPRICORN_LESSON7))
        self.assertTrue(
            all(
                item.source_reference == REF_CAPRICORN_BIO
                for item in CAPRICORN_BIOASTROLOGY + CAPRICORN_AFFLICTED
            )
        )
        self.assertIn("capricorn_l7_structured_thinking", _ids(CAPRICORN_LESSON7))
        self.assertIn("capricorn_bio_planning", _ids(CAPRICORN_BIOASTROLOGY))
        self.assertTrue(all(item.activation_condition == "hard_aspected" for item in CAPRICORN_AFFLICTED))

    def test_aquarius_source_reference_separation(self):
        self.assertTrue(all(item.source_reference == REF_AQUARIUS_L7 for item in AQUARIUS_LESSON7))
        self.assertTrue(
            all(
                item.source_reference == REF_AQUARIUS_BIO
                for item in AQUARIUS_BIOASTROLOGY + AQUARIUS_AFFLICTED
            )
        )
        self.assertIn("aquarius_l7_independent_thinking", _ids(AQUARIUS_LESSON7))
        self.assertIn("aquarius_bio_inventor_aptitude", _ids(AQUARIUS_BIOASTROLOGY))

    def test_pisces_source_reference_separation(self):
        self.assertTrue(all(item.source_reference == REF_PISCES_L7 for item in PISCES_LESSON7))
        self.assertTrue(
            all(
                item.source_reference == REF_PISCES_BIO
                for item in PISCES_BIOASTROLOGY + PISCES_AFFLICTED
            )
        )
        self.assertIn("pisces_l7_image_based_perception", _ids(PISCES_LESSON7))
        self.assertIn("pisces_bio_minor_exile", _ids(PISCES_BIOASTROLOGY))

    def test_aquarius_adhd_effect_is_non_diagnostic_source_specific(self):
        fact = next(
            item
            for item in AQUARIUS_AFFLICTED
            if item.id == "aquarius_bio_afflicted_source_adhd_effect_wording"
        )
        self.assertEqual(fact.category, "source_specific")
        self.assertEqual(fact.tags, ("source_adhd_effect_wording",))
        self.assertNotIn("adhd", fact.tags)
        self.assertNotIn("distractibility", fact.tags)
        self.assertIn("non-diagnostic", fact.text)
        self.assertIn("not a medical conclusion", fact.text)

    def test_pisces_memory_not_flattened_to_absolute(self):
        selective = next(item for item in PISCES_BIOASTROLOGY if item.id == "pisces_bio_selective_memory")
        context = next(
            item for item in PISCES_BIOASTROLOGY if item.id == "pisces_bio_context_dependent_memory"
        )
        ranged = next(
            item for item in PISCES_BIOASTROLOGY if item.id == "pisces_bio_memory_range_chart_context"
        )
        self.assertEqual(selective.tags, ("selective_memory",))
        self.assertEqual(context.tags, ("context_dependent_memory",))
        self.assertEqual(ranged.tags, ("context_variable_memory_range",))
        for fact in (selective, context, ranged):
            self.assertNotIn("strong_memory", fact.tags)
            self.assertNotIn("poor_memory", fact.tags)
            self.assertNotIn("memory", fact.tags)


class SignBatchA3ActivationTests(unittest.TestCase):
    def _sign_profile(self, sign: str, element: str, aspects: list[MercuryAspect]):
        return build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=False,
                mercury_sign=sign,
                mercury_element=element,
                mercury_motion="direct",
                mercury_house=None,
                aspects=aspects,
            )
        )

    def test_each_a3_sign_supported(self):
        for sign, element in (
            ("Capricorn", "earth"),
            ("Aquarius", "air"),
            ("Pisces", "water"),
        ):
            with self.subTest(sign=sign):
                profile = self._sign_profile(sign, element, [])
                self.assertIn(f"sign:{sign}", profile.coverage.covered_factors)
                self.assertGreater(len(profile.sign_facts), 0)
                self.assertTrue(all(item.factor_key == sign for item in profile.sign_facts))

    def test_afflicted_requires_hard_aspected_for_all_a3_signs(self):
        cases = [
            ("Capricorn", "earth", "capricorn_bio_afflicted_closedness"),
            ("Aquarius", "air", "aquarius_bio_afflicted_source_adhd_effect_wording"),
            ("Pisces", "water", "pisces_bio_afflicted_mystification"),
        ]
        soft_aspect = [MercuryAspect(planet="Jupiter", type="trine", orb_deg=1.0)]
        hard_aspects = [
            [MercuryAspect(planet="Pluto", type="square", orb_deg=1.0)],
            [MercuryAspect(planet="Saturn", type="opposition", orb_deg=1.0)],
        ]
        for sign, element, afflicted_id in cases:
            with self.subTest(sign=sign):
                soft = self._sign_profile(sign, element, soft_aspect)
                self.assertNotIn(afflicted_id, _ids(soft.sign_facts))
                self.assertFalse(soft.calculated.hard_aspected)
                for hard_aspect in hard_aspects:
                    hard = self._sign_profile(sign, element, hard_aspect)
                    self.assertIn(afflicted_id, _ids(hard.sign_facts))
                    self.assertTrue(hard.calculated.hard_aspected)

    def test_dual_source_same_sign_does_not_create_false_repeat(self):
        for sign, element in (
            ("Capricorn", "earth"),
            ("Aquarius", "air"),
            ("Pisces", "water"),
        ):
            with self.subTest(sign=sign):
                profile = self._sign_profile(sign, element, [])
                for signal in detect_repeated_signals(profile.sign_facts):
                    sign_sources = [src for src in signal.sources if src.startswith("sign:")]
                    self.assertLessEqual(len(sign_sources), 1, signal)


class SignBatchA3MilkaAndRegressionTests(unittest.TestCase):
    def test_milka_like_pisces_source_covered_without_house_knowledge_gap(self):
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
        self.assertIn("sign:Pisces", profile.coverage.covered_factors)
        self.assertNotIn("motion:direct", profile.coverage.missing_factors)
        self.assertFalse(any("Pisces" in item and "not implemented" in item for item in profile.limitations))
        self.assertFalse(any("house" in item.lower() and "not implemented" in item for item in profile.limitations))
        self.assertGreater(len(profile.sign_facts), 0)
        self.assertEqual(profile.house_facts, [])
        self.assertEqual(profile.aspect_facts, [])

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

    def test_andrey_like_remains_partial_for_unsupported_house_and_aspect(self):
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
        self.assertIn("sign:Cancer", profile.coverage.covered_factors)
        self.assertIn("aspect:square_Pluto", profile.coverage.covered_factors)
        self.assertIn("house:5", profile.coverage.covered_factors)
        self.assertNotIn("house:5", profile.coverage.missing_factors)
        self.assertEqual(profile.coverage.missing_factors, ["aspect:trine_Uranus"])
        self.assertFalse(
            any(item.factor_key == "trine_Uranus" for item in profile.aspect_facts)
        )

    def test_prior_batch_pack_sizes_unchanged(self):
        self.assertEqual(len(ARIES_ALL), 51)
        self.assertEqual(len(GEMINI_ALL), 50)
        self.assertEqual(len(CANCER_ALL), 74)
        self.assertEqual(len(VIRGO_ALL), 60)
        self.assertEqual(len(LIBRA_ALL), 58)
        self.assertEqual(len(SCORPIO_ALL), 66)

    def test_a3_pack_nonempty(self):
        self.assertGreater(len(A3_SIGN_PACKS), 0)
        self.assertEqual(
            len(A3_SIGN_PACKS),
            len(CAPRICORN_LESSON7)
            + len(CAPRICORN_BIOASTROLOGY)
            + len(CAPRICORN_AFFLICTED)
            + len(AQUARIUS_LESSON7)
            + len(AQUARIUS_BIOASTROLOGY)
            + len(AQUARIUS_AFFLICTED)
            + len(PISCES_LESSON7)
            + len(PISCES_BIOASTROLOGY)
            + len(PISCES_AFFLICTED),
        )


if __name__ == "__main__":
    unittest.main()
