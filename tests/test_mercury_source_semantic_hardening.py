"""Semantic hardening regression tests for Mercury Source Profile repeated signals."""

from __future__ import annotations

import unittest

from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_source_knowledge import (
    ALL_SOURCE_FACTS,
    REPEATED_SIGNAL_SPECS,
    SUPPORTED_SIGN_KEYS,
)
from app.services.mercury_source_profile import (
    build_source_profile_from_factors,
    detect_repeated_signals,
)


ALL_TWELVE = {
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


def _fact(fact_id: str):
    return next(item for item in ALL_SOURCE_FACTS if item.id == fact_id)


class SemanticHardeningCatalogTests(unittest.TestCase):
    def test_all_twelve_signs_still_supported(self):
        self.assertEqual(SUPPORTED_SIGN_KEYS, ALL_TWELVE)

    def test_leo_sales_does_not_imply_persuasion(self):
        fact = _fact("leo_sales_ability")
        self.assertEqual(fact.tags, ("sales",))
        self.assertNotIn("persuasion", fact.tags)

    def test_persuasion_contributors_are_explicit(self):
        contributors = [item for item in ALL_SOURCE_FACTS if "persuasion" in item.tags]
        self.assertTrue(contributors)
        for item in contributors:
            self.assertNotEqual(item.id, "leo_sales_ability")
            blob = item.text.lower()
            self.assertTrue(
                "persuasi" in blob or "persuasive" in blob,
                msg=f"{item.id} tagged persuasion without persuasion wording: {item.text}",
            )

    def test_strong_memory_spec_uses_exact_tag(self):
        spec = next(item for item in REPEATED_SIGNAL_SPECS if item["signal"] == "strong_memory")
        self.assertEqual(spec["tag"], "strong_memory")
        memory_tagged = [item.id for item in ALL_SOURCE_FACTS if "memory" in item.tags]
        self.assertEqual(memory_tagged, [])
        strong = [item for item in ALL_SOURCE_FACTS if "strong_memory" in item.tags]
        ids = {item.id for item in strong}
        self.assertIn("saturn_tr_strong_sticky_memory", ids)
        self.assertIn("moon_sx_strong_sticky_memory", ids)
        self.assertIn("gemini_bio_strong_memory", ids)
        self.assertNotIn("uranus_cj_comp_super_memory_practices", ids)

    def test_insight_contributors_are_exact(self):
        insight_facts = [item for item in ALL_SOURCE_FACTS if "insight" in item.tags]
        forbidden = {
            "pluto_sq_speak_uncomfortable_truth",
            "pluto_sq_identify_vulnerabilities",
            "pluto_sq_penetrate_hack_systems",
            "moon_sx_rational_mind_more_alive",
            "moon_sx_intuition",
            "moon_sx_read_between_lines",
            "moon_sx_emotional_background_processed",
        }
        ids = {item.id for item in insight_facts}
        self.assertTrue(ids.isdisjoint(forbidden))
        self.assertIn("pluto_sq_strong_insight", ids)
        self.assertIn("pluto_sq_psychological_insight", ids)
        self.assertIn("moon_sx_increased_insight", ids)
        self.assertIn("aquarius_bio_insights", ids)

    def test_nonstandard_learning_spec_removed(self):
        keys = {item["signal"] for item in REPEATED_SIGNAL_SPECS}
        self.assertNotIn("nonstandard_learning", keys)

    def test_nonstandard_thinking_excludes_uranus_free_thinking(self):
        uranus = _fact("uranus_cj_rebellious_free_thinking")
        self.assertNotIn("nonstandard_thinking", uranus.tags)
        self.assertIn("rebellious_free_thinking", uranus.tags)

    def test_leo_afflicted_proxy_wording(self):
        for item in ALL_SOURCE_FACTS:
            if item.id.startswith("leo_afflicted_"):
                self.assertIn("project hard_aspected proxy", item.text)
                self.assertIn("при поражении", item.text)


class SemanticHardeningActivationTests(unittest.TestCase):
    def test_dual_source_same_sign_still_no_false_repeat(self):
        for sign, element in (
            ("Virgo", "earth"),
            ("Aquarius", "air"),
            ("Pisces", "water"),
        ):
            with self.subTest(sign=sign):
                profile = build_source_profile_from_factors(
                    MercurySourceFactors(
                        birth_time_known=False,
                        mercury_sign=sign,
                        mercury_element=element,
                        mercury_motion="direct",
                        mercury_house=None,
                        aspects=[],
                    )
                )
                for signal in detect_repeated_signals(profile.sign_facts):
                    sign_sources = [src for src in signal.sources if src.startswith("sign:")]
                    self.assertLessEqual(len(sign_sources), 1, signal)

    def test_insight_still_repeats_across_pluto_and_moon(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=False,
                mercury_sign="Leo",
                mercury_element="fire",
                mercury_motion="direct",
                mercury_house=None,
                aspects=[
                    MercuryAspect(planet="Pluto", type="square", orb_deg=1.0),
                    MercuryAspect(planet="Moon", type="sextile", orb_deg=1.0),
                ],
            )
        )
        signal = next(
            (item for item in profile.repeated_signals if item.signal == "insight_seeing_not_obvious"),
            None,
        )
        self.assertIsNotNone(signal)
        self.assertIn("aspect:square_Pluto", signal.sources)
        self.assertIn("aspect:sextile_Moon", signal.sources)

    def test_strong_memory_repeats_saturn_and_moon(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=False,
                mercury_sign="Leo",
                mercury_element="fire",
                mercury_motion="direct",
                mercury_house=None,
                aspects=[
                    MercuryAspect(planet="Saturn", type="trine", orb_deg=1.0),
                    MercuryAspect(planet="Moon", type="sextile", orb_deg=1.0),
                ],
            )
        )
        signal = next(
            (item for item in profile.repeated_signals if item.signal == "strong_memory"),
            None,
        )
        self.assertIsNotNone(signal)
        self.assertIn("aspect:trine_Saturn", signal.sources)
        self.assertIn("aspect:sextile_Moon", signal.sources)


if __name__ == "__main__":
    unittest.main()
