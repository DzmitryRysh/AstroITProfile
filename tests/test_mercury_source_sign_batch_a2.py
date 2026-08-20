"""Tests for Mercury Source Profile v2 — Sign Batch A2 (Virgo/Libra/Scorpio)."""

from __future__ import annotations

import unittest
from collections import Counter
from datetime import date, time

from app.schemas.mercury_source_profile import MercurySourceProfileRequest
from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS, SUPPORTED_SIGN_KEYS
from app.services.mercury_source_knowledge_a1_signs import ARIES_ALL, CANCER_ALL, GEMINI_ALL
from app.services.mercury_source_knowledge_a2_signs import (
    A2_SIGN_PACKS,
    LIBRA_AFFLICTED,
    LIBRA_BIOASTROLOGY,
    LIBRA_LESSON7,
    REF_LIBRA_BIO,
    REF_LIBRA_L7,
    REF_SCORPIO_BIO,
    REF_SCORPIO_L7,
    REF_VIRGO_BIO,
    REF_VIRGO_L7,
    SCORPIO_AFFLICTED,
    SCORPIO_BIOASTROLOGY,
    SCORPIO_LESSON7,
    VIRGO_AFFLICTED,
    VIRGO_BIOASTROLOGY,
    VIRGO_LESSON7,
)
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
    detect_repeated_signals,
)


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


class SignBatchA2CatalogTests(unittest.TestCase):
    def test_supported_signs_cover_nine(self):
        self.assertTrue(
            {
                "Aries",
                "Taurus",
                "Gemini",
                "Cancer",
                "Leo",
                "Virgo",
                "Libra",
                "Scorpio",
                "Sagittarius",
            }.issubset(SUPPORTED_SIGN_KEYS)
        )
        self.assertGreaterEqual(len(SUPPORTED_SIGN_KEYS), 9)

    def test_all_ids_unique(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])

    def test_virgo_source_reference_separation(self):
        self.assertTrue(all(item.source_reference == REF_VIRGO_L7 for item in VIRGO_LESSON7))
        self.assertTrue(
            all(item.source_reference == REF_VIRGO_BIO for item in VIRGO_BIOASTROLOGY + VIRGO_AFFLICTED)
        )
        self.assertIn("virgo_l7_analytical_thinking", _ids(VIRGO_LESSON7))
        self.assertIn("virgo_bio_strong_erudition", _ids(VIRGO_BIOASTROLOGY))
        self.assertTrue(all(item.activation_condition == "hard_aspected" for item in VIRGO_AFFLICTED))

    def test_libra_source_reference_separation(self):
        self.assertTrue(all(item.source_reference == REF_LIBRA_L7 for item in LIBRA_LESSON7))
        self.assertTrue(
            all(item.source_reference == REF_LIBRA_BIO for item in LIBRA_BIOASTROLOGY + LIBRA_AFFLICTED)
        )
        self.assertIn("libra_l7_view_issue_from_multiple_sides", _ids(LIBRA_LESSON7))
        self.assertIn("libra_bio_compromise_skill", _ids(LIBRA_BIOASTROLOGY))

    def test_scorpio_source_reference_separation(self):
        self.assertTrue(all(item.source_reference == REF_SCORPIO_L7 for item in SCORPIO_LESSON7))
        self.assertTrue(
            all(
                item.source_reference == REF_SCORPIO_BIO
                for item in SCORPIO_BIOASTROLOGY + SCORPIO_AFFLICTED
            )
        )
        self.assertIn("scorpio_l7_research_oriented_mind", _ids(SCORPIO_LESSON7))
        self.assertIn("scorpio_bio_psychological_penetration", _ids(SCORPIO_BIOASTROLOGY))
        # Strict taxonomy: influence != manipulation
        influence = next(item for item in SCORPIO_BIOASTROLOGY if item.id == "scorpio_bio_influence_people")
        manip = next(
            item for item in SCORPIO_LESSON7 if item.id == "scorpio_l7_env_manipulation_source_claim"
        )
        self.assertEqual(influence.tags, ("influence",))
        self.assertEqual(manip.tags, ("manipulation",))


class SignBatchA2ActivationTests(unittest.TestCase):
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

    def test_each_a2_sign_supported(self):
        for sign, element in (("Virgo", "earth"), ("Libra", "air"), ("Scorpio", "water")):
            with self.subTest(sign=sign):
                profile = self._sign_profile(sign, element, [])
                self.assertIn(f"sign:{sign}", profile.coverage.covered_factors)
                self.assertGreater(len(profile.sign_facts), 0)
                self.assertTrue(all(item.factor_key == sign for item in profile.sign_facts))

    def test_afflicted_requires_hard_aspected_for_all_a2_signs(self):
        cases = [
            ("Virgo", "earth", "virgo_bio_afflicted_tediousness"),
            ("Libra", "air", "libra_bio_afflicted_intellectual_indecision"),
            ("Scorpio", "water", "scorpio_bio_afflicted_causticity"),
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
        for sign, element in (("Virgo", "earth"), ("Libra", "air"), ("Scorpio", "water")):
            with self.subTest(sign=sign):
                profile = self._sign_profile(sign, element, [])
                for signal in detect_repeated_signals(profile.sign_facts):
                    sign_sources = [src for src in signal.sources if src.startswith("sign:")]
                    self.assertLessEqual(len(sign_sources), 1, signal)


class SignBatchA2RegressionTests(unittest.TestCase):
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

    def test_a1_pack_sizes_unchanged(self):
        self.assertEqual(len(ARIES_ALL), 51)
        self.assertEqual(len(GEMINI_ALL), 50)
        self.assertEqual(len(CANCER_ALL), 74)

    def test_a2_pack_nonempty(self):
        self.assertGreater(len(A2_SIGN_PACKS), 0)
        self.assertEqual(
            len(A2_SIGN_PACKS),
            len(VIRGO_LESSON7)
            + len(VIRGO_BIOASTROLOGY)
            + len(VIRGO_AFFLICTED)
            + len(LIBRA_LESSON7)
            + len(LIBRA_BIOASTROLOGY)
            + len(LIBRA_AFFLICTED)
            + len(SCORPIO_LESSON7)
            + len(SCORPIO_BIOASTROLOGY)
            + len(SCORPIO_AFFLICTED),
        )


if __name__ == "__main__":
    unittest.main()
