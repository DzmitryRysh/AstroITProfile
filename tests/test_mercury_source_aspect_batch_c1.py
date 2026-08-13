"""Tests for Mercury Source Profile v2 — Aspect Batch C1 (harmonious parity)."""

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
from app.services.mercury_source_knowledge_c1_aspects import (
    REF_URANUS_HARM,
    URANUS_HARMONIOUS,
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


class AspectBatchC1CoverageTests(unittest.TestCase):
    def test_supported_public_aspect_count_is_thirteen(self):
        self.assertEqual(len(SUPPORTED_ASPECT_KEYS), 13)
        self.assertTrue(
            {
                "trine_Moon",
                "trine_Jupiter",
                "sextile_Saturn",
                "trine_Uranus",
                "sextile_Uranus",
            }.issubset(SUPPORTED_ASPECT_KEYS)
        )
        # Pre-C1 factors remain.
        self.assertTrue(
            {
                "sextile_Moon",
                "square_Moon",
                "trine_Mars",
                "sextile_Mars",
                "sextile_Jupiter",
                "trine_Saturn",
                "conjunction_Uranus",
                "square_Pluto",
            }.issubset(SUPPORTED_ASPECT_KEYS)
        )

    def test_aliases_are_source_justified_and_acyclic(self):
        expected = {
            "sextile_Mars": "trine_Mars",
            "trine_Moon": "sextile_Moon",
            "trine_Jupiter": "sextile_Jupiter",
            "sextile_Saturn": "trine_Saturn",
            "sextile_Uranus": "trine_Uranus",
        }
        self.assertEqual(ASPECT_PACK_ALIASES, expected)
        for alias, canonical in ASPECT_PACK_ALIASES.items():
            self.assertIn(alias, SUPPORTED_ASPECT_KEYS)
            self.assertIn(canonical, SUPPORTED_ASPECT_KEYS)
            self.assertNotIn(canonical, ASPECT_PACK_ALIASES)
            self.assertTrue(
                any(
                    item.factor_type == "aspect" and item.factor_key == canonical
                    for item in ALL_SOURCE_FACTS
                ),
                canonical,
            )

    def test_catalog_integrity(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])
        self.assertTrue(all(item.source_reference for item in ALL_SOURCE_FACTS))
        self.assertEqual(len(URANUS_HARMONIOUS), 10)
        self.assertTrue(all(item.source_reference == REF_URANUS_HARM for item in URANUS_HARMONIOUS))
        # Exactly one canonical Uranus harmonious pack in catalog (no sextile duplicates).
        uranus_harm = [
            item
            for item in ALL_SOURCE_FACTS
            if item.factor_type == "aspect" and item.factor_key == "trine_Uranus"
        ]
        self.assertEqual(len(uranus_harm), 10)
        self.assertFalse(
            any(
                item.factor_type == "aspect" and item.factor_key == "sextile_Uranus"
                for item in ALL_SOURCE_FACTS
            )
        )


class AspectBatchC1AliasResolutionTests(unittest.TestCase):
    def _profile(self, aspect_type: str, planet: str):
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

    def test_moon_jupiter_saturn_aliases_share_canonical_refs(self):
        cases = [
            ("trine", "Moon", "sextile", "Moon", "bioastrology_mercury_moon_harmonious"),
            ("trine", "Jupiter", "sextile", "Jupiter", "bioastrology_mercury_jupiter_harmonious"),
            ("sextile", "Saturn", "trine", "Saturn", "bioastrology_mercury_saturn_harmonious"),
        ]
        for alias_type, planet, canon_type, canon_planet, expected_ref in cases:
            with self.subTest(alias=f"{alias_type}_{planet}"):
                alias_profile = self._profile(alias_type, planet)
                canon_profile = self._profile(canon_type, canon_planet)
                alias_key = f"{alias_type}_{planet}"
                canon_key = f"{canon_type}_{canon_planet}"
                self.assertTrue(alias_profile.aspect_facts)
                self.assertTrue(canon_profile.aspect_facts)
                self.assertEqual(_refs(alias_profile.aspect_facts), {expected_ref})
                self.assertEqual(_refs(canon_profile.aspect_facts), {expected_ref})
                self.assertEqual(_ids(alias_profile.aspect_facts), _ids(canon_profile.aspect_facts))
                self.assertTrue(all(item.factor_key == alias_key for item in alias_profile.aspect_facts))
                self.assertTrue(all(item.factor_key == canon_key for item in canon_profile.aspect_facts))
                self.assertIn(f"aspect:{alias_key}", alias_profile.coverage.covered_factors)
                self.assertNotIn(f"aspect:{canon_key}", alias_profile.coverage.covered_factors)

    def test_uranus_harmonious_shared_and_separate_from_conjunction(self):
        trine = self._profile("trine", "Uranus")
        sextile = self._profile("sextile", "Uranus")
        conjunction = self._profile("conjunction", "Uranus")

        self.assertEqual(_refs(trine.aspect_facts), {REF_URANUS_HARM})
        self.assertEqual(_refs(sextile.aspect_facts), {REF_URANUS_HARM})
        self.assertEqual(_ids(trine.aspect_facts), _ids(sextile.aspect_facts))
        self.assertTrue(all(item.factor_key == "trine_Uranus" for item in trine.aspect_facts))
        self.assertTrue(all(item.factor_key == "sextile_Uranus" for item in sextile.aspect_facts))

        self.assertTrue(conjunction.aspect_facts)
        self.assertNotEqual(_refs(conjunction.aspect_facts), {REF_URANUS_HARM})
        self.assertTrue(
            all("uranus_conjunction" in item.source_reference or "uranus_conj" in item.source_reference
                or item.source_reference == "bioastrology_mercury_uranus_conjunction"
                for item in conjunction.aspect_facts)
        )
        self.assertTrue(_ids(conjunction.aspect_facts).isdisjoint(_ids(trine.aspect_facts)))
        self.assertIn("uranus_harm_technical_talents", _ids(trine.aspect_facts))
        self.assertNotIn("uranus_harm_technical_talents", _ids(conjunction.aspect_facts))

    def test_alias_does_not_double_count_same_factor(self):
        # One calculated sextile_Uranus must contribute one provenance only.
        profile = self._profile("sextile", "Uranus")
        for signal in detect_repeated_signals(profile.aspect_facts):
            self.assertLessEqual(signal.source_count, 1, signal)


class AspectBatchC1AndreyAndRegressionTests(unittest.TestCase):
    def test_andrey_becomes_complete(self):
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
        self.assertEqual(profile.coverage.missing_factors, [])
        self.assertIn("aspect:trine_Uranus", profile.coverage.covered_factors)
        self.assertIn("uranus_harm_technical_talents", _ids(profile.aspect_facts))
        # Valid distinct-factor technical_ability repeat with square Pluto.
        tech = next(
            (item for item in detect_repeated_signals(
                list(profile.sign_facts) + list(profile.house_facts) + list(profile.aspect_facts)
            ) if item.signal == "technical_ability"),
            None,
        )
        self.assertIsNotNone(tech)
        self.assertIn("aspect:trine_Uranus", tech.sources)
        self.assertIn("aspect:square_Pluto", tech.sources)

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

    def test_dzmitry_still_uses_conjunction_not_harmonious(self):
        profile = build_mercury_source_profile(
            MercurySourceProfileRequest(
                birth_date=date(1985, 11, 12),
                birth_time=time(14, 15),
                birth_place="Zhodino, Belarus",
            )
        )
        uranus_facts = [
            item for item in profile.aspect_facts if "Uranus" in item.factor_key
        ]
        self.assertTrue(uranus_facts)
        self.assertTrue(all(item.factor_key == "conjunction_Uranus" for item in uranus_facts))
        self.assertFalse(any(item.id.startswith("uranus_harm_") for item in uranus_facts))
        self.assertNotIn(REF_URANUS_HARM, _refs(uranus_facts))

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

    def test_uranus_harmonious_tags_avoid_hardened_collisions(self):
        by_id = {item.id: item for item in URANUS_HARMONIOUS}
        self.assertEqual(
            by_id["uranus_harm_technical_talents"].tags,
            ("technical_ability",),
        )
        self.assertEqual(
            by_id["uranus_harm_rebellious_free_thinking"].tags,
            ("rebellious_free_thinking",),
        )
        self.assertNotIn("nonstandard_thinking", by_id["uranus_harm_rebellious_free_thinking"].tags)
        self.assertNotIn("fast_thinking", by_id["uranus_harm_thinking_imagination_acceleration"].tags)
        self.assertNotIn("insight", by_id["uranus_harm_claircognizance"].tags)
        self.assertNotIn("analytical_thinking", by_id["uranus_harm_interest_ability_psychology"].tags)


if __name__ == "__main__":
    unittest.main()
