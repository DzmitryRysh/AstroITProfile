"""Tests for Mercury Source Profile v2 — Aspect Batch C6 (Saturn opposition / conjunction)."""

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
from app.services.mercury_source_knowledge_c2_aspects import SATURN_SQUARE, REF_SATURN_SQ
from app.services.mercury_source_knowledge_c6_aspects import (
    REF_SATURN_CONJ,
    REF_SATURN_OPP,
    SATURN_CONJUNCTION,
    SATURN_CONJUNCTION_RESOLVED,
    SATURN_CONJUNCTION_UNRESOLVED,
    SATURN_OPPOSITION,
)
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
    detect_repeated_signals,
)

ENGINE_ASPECT_SLOTS = 45
SATURN_PUBLIC_FAMILY = {
    "conjunction_Saturn",
    "sextile_Saturn",
    "square_Saturn",
    "trine_Saturn",
    "opposition_Saturn",
}
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


def _synthetic_saturn(aspect_type: str):
    return build_source_profile_from_factors(
        MercurySourceFactors(
            birth_time_known=True,
            mercury_sign="Virgo",
            mercury_element="earth",
            mercury_motion="direct",
            mercury_house=3,
            aspects=[MercuryAspect(planet="Saturn", type=aspect_type, orb_deg=1.2)],
        )
    )


class AspectBatchC6CoverageTests(unittest.TestCase):
    def test_supported_public_aspect_count_is_twenty_two(self):
        self.assertEqual(len(SUPPORTED_ASPECT_KEYS), 22)
        self.assertEqual(ENGINE_ASPECT_SLOTS - len(SUPPORTED_ASPECT_KEYS), 23)
        self.assertEqual(len(_canonical_aspect_packs()), 16)
        self.assertEqual(len(ASPECT_PACK_ALIASES), 6)
        self.assertEqual(len(SUPPORTED_SIGN_KEYS), 12)
        self.assertEqual(len(SUPPORTED_HOUSE_KEYS), 12)
        self.assertTrue(JUPITER_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(SATURN_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))

    def test_saturn_family_is_exactly_five_of_five(self):
        self.assertIn("conjunction_Saturn", SUPPORTED_ASPECT_KEYS)
        self.assertIn("opposition_Saturn", SUPPORTED_ASPECT_KEYS)
        self.assertIn("square_Saturn", SUPPORTED_ASPECT_KEYS)
        self.assertIn("trine_Saturn", SUPPORTED_ASPECT_KEYS)
        self.assertEqual(ASPECT_PACK_ALIASES["sextile_Saturn"], "trine_Saturn")
        self.assertNotIn("conjunction_Saturn", ASPECT_PACK_ALIASES)
        self.assertNotIn("opposition_Saturn", ASPECT_PACK_ALIASES)
        self.assertNotEqual(ASPECT_PACK_ALIASES.get("conjunction_Saturn"), "square_Saturn")
        self.assertNotEqual(ASPECT_PACK_ALIASES.get("opposition_Saturn"), "square_Saturn")
        self.assertIn("conjunction_Saturn", _canonical_aspect_packs())
        self.assertIn("opposition_Saturn", _canonical_aspect_packs())
        self.assertIn("square_Saturn", _canonical_aspect_packs())
        self.assertIn("trine_Saturn", _canonical_aspect_packs())
        self.assertNotIn("sextile_Saturn", _canonical_aspect_packs())

    def test_distinct_refs_and_catalog_identity(self):
        self.assertEqual(REF_SATURN_OPP, "bioastrology_mercury_saturn_opposition")
        self.assertEqual(REF_SATURN_CONJ, "bioastrology_mercury_saturn_conjunction")
        self.assertNotEqual(REF_SATURN_OPP, REF_SATURN_SQ)
        self.assertNotEqual(REF_SATURN_CONJ, REF_SATURN_SQ)
        self.assertNotEqual(REF_SATURN_OPP, REF_SATURN_CONJ)
        self.assertTrue(all(item.source_reference == REF_SATURN_OPP for item in SATURN_OPPOSITION))
        self.assertTrue(all(item.source_reference == REF_SATURN_CONJ for item in SATURN_CONJUNCTION))
        self.assertTrue(_ids(SATURN_OPPOSITION).isdisjoint(_ids(SATURN_SQUARE)))
        self.assertTrue(_ids(SATURN_CONJUNCTION).isdisjoint(_ids(SATURN_SQUARE)))
        self.assertTrue(_ids(SATURN_OPPOSITION).isdisjoint(_ids(SATURN_CONJUNCTION)))

    def test_catalog_integrity(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])
        self.assertTrue(all(item.source_reference for item in ALL_SOURCE_FACTS))
        self.assertEqual(len(SATURN_OPPOSITION), 19)
        self.assertEqual(len(SATURN_CONJUNCTION_RESOLVED), 17)
        self.assertEqual(len(SATURN_CONJUNCTION_UNRESOLVED), 1)
        self.assertEqual(len(SATURN_CONJUNCTION), 18)
        self.assertTrue(all(not item.unresolved for item in SATURN_OPPOSITION))
        self.assertTrue(all(not item.unresolved for item in SATURN_CONJUNCTION_RESOLVED))
        self.assertTrue(all(item.unresolved for item in SATURN_CONJUNCTION_UNRESOLVED))
        self.assertTrue(
            all(
                item.activation_condition == "creative_core_strength_unresolved"
                for item in SATURN_CONJUNCTION_UNRESOLVED
            )
        )
        self.assertFalse(any(item.category == "compensation" for item in SATURN_OPPOSITION + SATURN_CONJUNCTION))
        self.assertFalse(any("supergift" in item.id for item in SATURN_OPPOSITION + SATURN_CONJUNCTION))
        self.assertFalse(any("celebrity" in item.id for item in SATURN_OPPOSITION + SATURN_CONJUNCTION))
        self.assertFalse(
            any("secondary_gain" in item.id for item in SATURN_OPPOSITION + SATURN_CONJUNCTION)
        )


class AspectBatchC6AtomTests(unittest.TestCase):
    def test_opposition_key_atoms_and_tag_safety(self):
        by_id = {item.id: item for item in SATURN_OPPOSITION}
        self.assertEqual(
            by_id["saturn_opp_curiosity_vs_social_requirement_conflict"].tags,
            ("curiosity_vs_social_requirement_conflict",),
        )
        self.assertEqual(
            by_id["saturn_opp_verification_requirement"].tags,
            ("verification_requirement",),
        )
        self.assertNotIn(
            "evidence_requirement",
            by_id["saturn_opp_verification_requirement"].tags,
        )
        self.assertEqual(by_id["saturn_opp_argumentation"].tags, ("argumentation",))
        self.assertEqual(by_id["saturn_opp_logic"].tags, ("logic",))
        self.assertEqual(by_id["saturn_opp_planning"].tags, ("planning",))
        self.assertEqual(by_id["saturn_opp_forecasting"].tags, ("forecasting",))
        self.assertEqual(by_id["saturn_opp_organization"].tags, ("organization",))
        self.assertEqual(by_id["saturn_opp_driving_ability"].tags, ("driving_ability",))
        self.assertNotIn("strong_memory", by_id["saturn_opp_unlearning_difficulty"].tags)
        self.assertNotIn("analytical_thinking", by_id["saturn_opp_logic"].tags)
        self.assertNotIn(
            "technical_ability",
            by_id["saturn_opp_everyday_scatter_work_hyperfocus_contrast"].tags,
        )

    def test_conjunction_atoms_and_creative_core_unresolved(self):
        by_id = {item.id: item for item in SATURN_CONJUNCTION}
        self.assertEqual(
            by_id["saturn_cj_narrow_prescribed_thinking"].tags,
            ("narrow_prescribed_thinking",),
        )
        unresolved = by_id["saturn_cj_branch_creative_core_deep_analytical_focus"]
        self.assertTrue(unresolved.unresolved)
        self.assertEqual(unresolved.activation_condition, "creative_core_strength_unresolved")
        self.assertEqual(unresolved.tags, ("deep_analytical_focus",))
        self.assertNotIn("analytical_thinking", unresolved.tags)
        self.assertNotIn("technical_ability", unresolved.tags)
        self.assertEqual(
            by_id["saturn_cj_verification_requirement"].tags,
            ("verification_requirement",),
        )
        self.assertNotIn("evidence_requirement", by_id["saturn_cj_verification_requirement"].tags)


class AspectBatchC6ActivationTests(unittest.TestCase):
    def test_opposition_activates_only_opposition_pack(self):
        profile = _synthetic_saturn("opposition")
        self.assertEqual(profile.coverage.status, "complete")
        self.assertIn("aspect:opposition_Saturn", profile.coverage.covered_factors)
        self.assertEqual(_ids(profile.aspect_facts), _ids(SATURN_OPPOSITION))
        self.assertTrue(all(item.factor_key == "opposition_Saturn" for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("saturn_sq_") for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("saturn_cj_") for item in profile.aspect_facts))
        self.assertFalse(any(item.unresolved for item in profile.aspect_facts))
        self.assertEqual(detect_repeated_signals(list(profile.aspect_facts)), [])

    def test_conjunction_resolved_and_unresolved_split(self):
        profile = _synthetic_saturn("conjunction")
        self.assertEqual(profile.coverage.status, "complete")
        self.assertIn("aspect:conjunction_Saturn", profile.coverage.covered_factors)
        self.assertEqual(_ids(profile.aspect_facts), _ids(SATURN_CONJUNCTION))
        resolved = {item.id for item in profile.aspect_facts if not item.unresolved}
        unresolved = {item.id for item in profile.conditional_unresolved}
        self.assertEqual(resolved, _ids(SATURN_CONJUNCTION_RESOLVED))
        self.assertTrue(_ids(SATURN_CONJUNCTION_UNRESOLVED).issubset(unresolved))
        creative = next(
            item
            for item in profile.conditional_unresolved
            if item.id == "saturn_cj_branch_creative_core_deep_analytical_focus"
        )
        self.assertEqual(creative.activation_condition, "creative_core_strength_unresolved")
        self.assertTrue(creative.unresolved)
        # Unresolved excluded from repeats; single factor does not self-repeat.
        all_facts = list(profile.aspect_facts) + list(profile.conditional_unresolved)
        for signal in detect_repeated_signals(all_facts):
            for fact_id in signal.fact_ids:
                fact = next(item for item in all_facts if item.id == fact_id)
                self.assertFalse(fact.unresolved, signal)
        self.assertEqual(
            detect_repeated_signals([item for item in profile.aspect_facts if not item.unresolved]),
            [],
        )

    def test_square_does_not_activate_c6_packs(self):
        profile = _synthetic_saturn("square")
        self.assertTrue(all(item.factor_key == "square_Saturn" for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("saturn_opp_") for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("saturn_cj_") for item in profile.aspect_facts))

    def test_trine_and_sextile_remain_harmonious_only(self):
        for aspect_type, expected_key in (("trine", "trine_Saturn"), ("sextile", "sextile_Saturn")):
            with self.subTest(aspect=aspect_type):
                profile = _synthetic_saturn(aspect_type)
                self.assertTrue(profile.aspect_facts)
                self.assertTrue(all(item.factor_key == expected_key for item in profile.aspect_facts))
                self.assertFalse(any(item.id.startswith("saturn_opp_") for item in profile.aspect_facts))
                self.assertFalse(any(item.id.startswith("saturn_cj_") for item in profile.aspect_facts))
                self.assertFalse(any(item.id.startswith("saturn_sq_") for item in profile.aspect_facts))


class AspectBatchC6RegressionTests(unittest.TestCase):
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
                    any(item.id.startswith("saturn_opp_") for item in profile.aspect_facts)
                )
                self.assertFalse(
                    any(item.id.startswith("saturn_cj_") for item in profile.aspect_facts)
                )

    def test_avdey_keeps_trine_saturn_only(self):
        profile = build_mercury_source_profile(
            MercurySourceProfileRequest(
                birth_date=date(1986, 7, 14),
                birth_time=time(7, 10),
                birth_place="Simferopol, Ukraine",
            )
        )
        saturn = [item for item in profile.aspect_facts if "Saturn" in item.factor_key]
        self.assertTrue(saturn)
        self.assertTrue(all(item.factor_key == "trine_Saturn" for item in saturn))
        arg = next(
            (s for s in profile.repeated_signals if s.signal == "argumentation"),
            None,
        )
        self.assertIsNotNone(arg)
        self.assertIn("aspect:trine_Saturn", arg.sources)
        self.assertNotIn("aspect:opposition_Saturn", arg.sources)
        self.assertNotIn("aspect:conjunction_Saturn", arg.sources)

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
