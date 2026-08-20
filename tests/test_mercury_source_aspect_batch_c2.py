"""Tests for Mercury Source Profile v2 — Aspect Batch C2 (square Mars / Saturn)."""

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
from app.services.mercury_source_knowledge_c1_aspects import REF_URANUS_HARM, URANUS_HARMONIOUS
from app.services.mercury_source_knowledge_c2_aspects import (
    MARS_SQUARE,
    MARS_SQUARE_COMMON,
    MARS_SQUARE_MARS_WINS,
    MARS_SQUARE_MERCURY_WINS,
    REF_MARS_SQ,
    REF_SATURN_SQ,
    SATURN_SQUARE,
    SATURN_SQUARE_COMMON,
    SATURN_SQUARE_MERCURY_WINS,
    SATURN_SQUARE_SATURN_WINS,
)
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
    detect_repeated_signals,
)


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


def _canonical_aspect_packs() -> set[str]:
    return {
        item.factor_key
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "aspect"
    }


class AspectBatchC2CoverageTests(unittest.TestCase):
    def test_c2_public_aspect_keys_remain_supported(self):
        # Historical C2 batch: subset guarantee only. Exact public count owned by C3+.
        self.assertTrue({"square_Mars", "square_Saturn"}.issubset(SUPPORTED_ASPECT_KEYS))
        # Pre-C2 public aspect keys remain supported.
        self.assertTrue(
            {
                "sextile_Moon",
                "square_Moon",
                "trine_Mars",
                "sextile_Mars",
                "sextile_Jupiter",
                "trine_Jupiter",
                "trine_Saturn",
                "sextile_Saturn",
                "trine_Moon",
                "conjunction_Uranus",
                "trine_Uranus",
                "sextile_Uranus",
                "square_Pluto",
            }.issubset(SUPPORTED_ASPECT_KEYS)
        )

    def test_c2_square_packs_are_not_aliases_and_mars_opposition_conjunction_not_aliased_to_square(self):
        # Historical C2: square Mars/Saturn are exact packs, not aliases.
        self.assertNotIn("square_Mars", ASPECT_PACK_ALIASES)
        self.assertNotIn("square_Saturn", ASPECT_PACK_ALIASES)
        # Later batches may support Mars/Saturn opposition/conjunction, but must
        # not alias them to the C2 square packs.
        self.assertNotEqual(ASPECT_PACK_ALIASES.get("opposition_Mars"), "square_Mars")
        self.assertNotEqual(ASPECT_PACK_ALIASES.get("conjunction_Mars"), "square_Mars")
        self.assertNotEqual(ASPECT_PACK_ALIASES.get("opposition_Saturn"), "square_Saturn")
        self.assertNotEqual(ASPECT_PACK_ALIASES.get("conjunction_Saturn"), "square_Saturn")

    def test_catalog_integrity(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])
        self.assertTrue(all(item.source_reference for item in ALL_SOURCE_FACTS))
        self.assertEqual(len(MARS_SQUARE_COMMON), 12)
        self.assertEqual(len(MARS_SQUARE_MERCURY_WINS), 11)
        self.assertEqual(len(MARS_SQUARE_MARS_WINS), 12)
        self.assertEqual(len(MARS_SQUARE), 35)
        self.assertEqual(len(SATURN_SQUARE_COMMON), 10)
        self.assertEqual(len(SATURN_SQUARE_MERCURY_WINS), 7)
        self.assertEqual(len(SATURN_SQUARE_SATURN_WINS), 2)
        self.assertEqual(len(SATURN_SQUARE), 19)
        self.assertTrue(all(item.source_reference == REF_MARS_SQ for item in MARS_SQUARE))
        self.assertTrue(all(item.source_reference == REF_SATURN_SQ for item in SATURN_SQUARE))
        self.assertTrue(all(item.unresolved for item in MARS_SQUARE_MERCURY_WINS))
        self.assertTrue(all(item.unresolved for item in MARS_SQUARE_MARS_WINS))
        self.assertTrue(all(not item.unresolved for item in MARS_SQUARE_COMMON))
        self.assertTrue(all(item.unresolved for item in SATURN_SQUARE_MERCURY_WINS))
        self.assertTrue(all(item.unresolved for item in SATURN_SQUARE_SATURN_WINS))
        self.assertTrue(all(not item.unresolved for item in SATURN_SQUARE_COMMON))
        # C2 packs remain present as distinct catalog keys.
        self.assertIn("square_Mars", _canonical_aspect_packs())
        self.assertIn("square_Saturn", _canonical_aspect_packs())


class AspectBatchC2MarsActivationTests(unittest.TestCase):
    def setUp(self):
        self.profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Virgo",
                mercury_element="earth",
                mercury_motion="direct",
                mercury_house=3,
                aspects=[MercuryAspect(planet="Mars", type="square", orb_deg=1.2)],
            )
        )

    def test_square_mars_supported_and_common_resolved(self):
        self.assertIn("aspect:square_Mars", self.profile.coverage.covered_factors)
        self.assertNotIn("aspect:square_Mars", self.profile.coverage.missing_factors)
        common_ids = _ids(MARS_SQUARE_COMMON)
        activated_common = {
            item.id for item in self.profile.aspect_facts if item.id in common_ids
        }
        self.assertEqual(activated_common, common_ids)
        self.assertTrue(
            all(
                not item.unresolved
                for item in self.profile.aspect_facts
                if item.id in common_ids
            )
        )

    def test_both_mars_winner_branches_unresolved_simultaneously(self):
        unresolved_ids = _ids(self.profile.conditional_unresolved)
        self.assertTrue(_ids(MARS_SQUARE_MERCURY_WINS).issubset(unresolved_ids))
        self.assertTrue(_ids(MARS_SQUARE_MARS_WINS).issubset(unresolved_ids))
        # Both branches present in aspect_facts as unresolved; neither resolved as sole winner.
        resolved_ids = {
            item.id for item in self.profile.aspect_facts if not item.unresolved
        }
        branch_ids = _ids(MARS_SQUARE_MERCURY_WINS) | _ids(MARS_SQUARE_MARS_WINS)
        self.assertTrue(branch_ids.isdisjoint(resolved_ids))
        self.assertTrue(branch_ids.issubset(_ids(self.profile.aspect_facts)))
        self.assertTrue(
            any("if the mercury side dominates" in item.text.lower() for item in self.profile.conditional_unresolved)
        )
        self.assertTrue(
            any("if the mars side dominates" in item.text.lower() for item in self.profile.conditional_unresolved)
        )

    def test_mars_branch_facts_excluded_from_repeats(self):
        all_facts = (
            list(self.profile.sign_facts)
            + list(self.profile.house_facts)
            + list(self.profile.aspect_facts)
            + list(self.profile.conditional_unresolved)
        )
        # Even if sales appears in an unresolved Mars branch, it must not create a repeat
        # from unresolved material alone.
        for signal in detect_repeated_signals(all_facts):
            for fact_id in signal.fact_ids:
                fact = next(item for item in all_facts if item.id == fact_id)
                self.assertFalse(fact.unresolved, signal)

    def test_semantic_hardening_tags(self):
        by_id = {item.id: item for item in MARS_SQUARE}
        self.assertNotIn("multitasking", by_id["mars_sq_scattered_activity"].tags)
        self.assertEqual(by_id["mars_sq_scattered_activity"].tags, ("scattered_activity",))
        self.assertNotIn(
            "fast_thinking",
            by_id["mars_sq_branch_mars_action_precedes_reflection"].tags,
        )
        self.assertEqual(
            by_id["mars_sq_branch_mars_action_precedes_reflection"].tags,
            ("action_precedes_reflection",),
        )
        conflict_ids = {
            "mars_sq_social_network_quarrels",
            "mars_sq_road_quarrels",
            "mars_sq_close_surroundings_neighbor_quarrels",
        }
        for fact_id in conflict_ids:
            tags = set(by_id[fact_id].tags)
            self.assertNotIn("debate", tags)
            self.assertNotIn("argumentation", tags)
            self.assertNotIn("persuasion", tags)


class AspectBatchC2SaturnActivationTests(unittest.TestCase):
    def setUp(self):
        self.profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Virgo",
                mercury_element="earth",
                mercury_motion="direct",
                mercury_house=3,
                aspects=[MercuryAspect(planet="Saturn", type="square", orb_deg=1.5)],
            )
        )

    def test_square_saturn_supported_and_common_resolved(self):
        self.assertIn("aspect:square_Saturn", self.profile.coverage.covered_factors)
        common_ids = _ids(SATURN_SQUARE_COMMON)
        self.assertEqual(
            {item.id for item in self.profile.aspect_facts if item.id in common_ids},
            common_ids,
        )

    def test_both_saturn_winner_branches_unresolved(self):
        unresolved_ids = _ids(self.profile.conditional_unresolved)
        self.assertTrue(_ids(SATURN_SQUARE_MERCURY_WINS).issubset(unresolved_ids))
        self.assertTrue(_ids(SATURN_SQUARE_SATURN_WINS).issubset(unresolved_ids))
        resolved_ids = {
            item.id for item in self.profile.aspect_facts if not item.unresolved
        }
        branch_ids = _ids(SATURN_SQUARE_MERCURY_WINS) | _ids(SATURN_SQUARE_SATURN_WINS)
        self.assertTrue(branch_ids.isdisjoint(resolved_ids))
        self.assertTrue(branch_ids.issubset(_ids(self.profile.aspect_facts)))
        self.assertTrue(
            any("if the mercury side dominates" in item.text.lower() for item in self.profile.conditional_unresolved)
        )
        self.assertTrue(
            any("if the saturn side dominates" in item.text.lower() for item in self.profile.conditional_unresolved)
        )

    def test_saturn_branch_facts_excluded_from_repeats(self):
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

    def test_unlearning_not_memory_and_tech_fixation_not_ability(self):
        by_id = {item.id: item for item in SATURN_SQUARE}
        unlearn_tags = set(by_id["saturn_sq_unlearning_difficulty"].tags)
        self.assertEqual(unlearn_tags, {"unlearning_difficulty"})
        self.assertNotIn("strong_memory", unlearn_tags)
        self.assertNotIn("sticky_memory", unlearn_tags)
        self.assertNotIn("memory_aptitude", unlearn_tags)
        tech = by_id["saturn_sq_branch_mercury_technical_detail_fixation"]
        self.assertEqual(tech.tags, ("excessive_technical_detail_fixation",))
        self.assertNotIn("technical_ability", tech.tags)
        verify = by_id["saturn_sq_verification_requirement"]
        self.assertEqual(verify.tags, ("verification_requirement",))
        self.assertNotIn("evidence_requirement", verify.tags)


class AspectBatchC2RegressionTests(unittest.TestCase):
    def test_c1_uranus_harmonious_unchanged(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Virgo",
                mercury_element="earth",
                mercury_motion="direct",
                mercury_house=3,
                aspects=[MercuryAspect(planet="Uranus", type="trine", orb_deg=1.0)],
            )
        )
        self.assertEqual(_ids(profile.aspect_facts), _ids(URANUS_HARMONIOUS))
        self.assertEqual({item.source_reference for item in profile.aspect_facts}, {REF_URANUS_HARM})

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
                aspect_keys = {item.factor_key for item in profile.aspect_facts}
                self.assertNotIn("square_Mars", aspect_keys)
                self.assertNotIn("square_Saturn", aspect_keys)

    def test_milka_like_complete(self):
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
