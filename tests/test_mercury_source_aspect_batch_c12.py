"""Tests for Mercury Source Profile v2 — Aspect Batch C12 (Venus reachable family)."""

from __future__ import annotations

import unittest
from collections import Counter
from datetime import date, time

from app.schemas.mercury_source_profile import MercurySourceProfileRequest
from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_aspect_reachability import (
    IMPOSSIBLE_NATAL_ASPECT_KEYS,
    REACHABLE_NATAL_ASPECT_KEYS,
    natal_aspect_reachability_summary,
)
from app.services.mercury_source_knowledge import (
    ALL_SOURCE_FACTS,
    ASPECT_PACK_ALIASES,
    REPEATED_SIGNAL_SPECS,
    SUPPORTED_ASPECT_KEYS,
    SUPPORTED_HOUSE_KEYS,
    SUPPORTED_SIGN_KEYS,
)
from app.services.mercury_source_knowledge_c12_aspects import (
    REF_VENUS_SX_CJ,
    VENUS_CONJUNCTION,
    VENUS_CONJUNCTION_AUTOMATISM,
    VENUS_SEXTILE,
)
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
    detect_repeated_signals,
)

ENGINE_ASPECT_SLOTS = 45
EXPECTED_MISSING_REACHABLE = frozenset(
    {
        "conjunction_Neptune",
        "sextile_Neptune",
        "square_Neptune",
        "trine_Neptune",
        "opposition_Neptune",
        "conjunction_Pluto",
        "opposition_Pluto",
    }
)
VENUS_REACHABLE_FAMILY = frozenset({"conjunction_Venus", "sextile_Venus"})
VENUS_IMPOSSIBLE_FAMILY = frozenset({"square_Venus", "trine_Venus", "opposition_Venus"})
MOON_PUBLIC_FAMILY = {
    "conjunction_Moon",
    "sextile_Moon",
    "square_Moon",
    "trine_Moon",
    "opposition_Moon",
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
MARS_PUBLIC_FAMILY = {
    "conjunction_Mars",
    "sextile_Mars",
    "square_Mars",
    "trine_Mars",
    "opposition_Mars",
}
URANUS_PUBLIC_FAMILY = {
    "conjunction_Uranus",
    "sextile_Uranus",
    "square_Uranus",
    "trine_Uranus",
    "opposition_Uranus",
}


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


def _tags(facts) -> set[str]:
    out: set[str] = set()
    for item in facts:
        out.update(item.tags)
    return out


def _canonical_aspect_packs() -> set[str]:
    return {
        item.factor_key
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "aspect"
    }


def _synthetic_venus(aspect_type: str, orb_deg: float = 2.0):
    return build_source_profile_from_factors(
        MercurySourceFactors(
            birth_time_known=True,
            mercury_sign="Virgo",
            mercury_element="earth",
            mercury_motion="direct",
            mercury_house=3,
            aspects=[MercuryAspect(planet="Venus", type=aspect_type, orb_deg=orb_deg)],
        )
    )


class AspectBatchC12CoverageTests(unittest.TestCase):
    def test_supported_public_aspect_count_is_thirty_one(self):
        self.assertEqual(len(SUPPORTED_ASPECT_KEYS), 31)
        self.assertEqual(ENGINE_ASPECT_SLOTS - len(SUPPORTED_ASPECT_KEYS), 14)
        self.assertEqual(len(_canonical_aspect_packs()), 25)
        self.assertEqual(len(ASPECT_PACK_ALIASES), 6)
        self.assertEqual(len(SUPPORTED_SIGN_KEYS), 12)
        self.assertEqual(len(SUPPORTED_HOUSE_KEYS), 12)
        self.assertTrue(MOON_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(JUPITER_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(SATURN_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(MARS_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(URANUS_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertIn("conjunction_Sun", SUPPORTED_ASPECT_KEYS)
        self.assertNotIn("conjunction_Pluto", SUPPORTED_ASPECT_KEYS)
        self.assertNotIn("opposition_Pluto", SUPPORTED_ASPECT_KEYS)

    def test_venus_reachable_family_is_exactly_two_of_two(self):
        for key in VENUS_REACHABLE_FAMILY:
            self.assertIn(key, SUPPORTED_ASPECT_KEYS)
            self.assertNotIn(key, ASPECT_PACK_ALIASES)
            self.assertIn(key, _canonical_aspect_packs())
        for key in VENUS_IMPOSSIBLE_FAMILY:
            self.assertNotIn(key, SUPPORTED_ASPECT_KEYS)
            self.assertNotIn(key, _canonical_aspect_packs())
            self.assertIn(key, IMPOSSIBLE_NATAL_ASPECT_KEYS)
            self.assertNotIn(key, EXPECTED_MISSING_REACHABLE)

    def test_reachable_snapshot_after_c12(self):
        summary = natal_aspect_reachability_summary(SUPPORTED_ASPECT_KEYS)
        self.assertEqual(summary["reachable_total"], 38)
        self.assertEqual(summary["supported_reachable"], 31)
        self.assertEqual(summary["missing_reachable"], 7)
        self.assertEqual(summary["impossible_total"], 7)
        self.assertEqual(summary["missing_reachable_keys"], EXPECTED_MISSING_REACHABLE)
        self.assertTrue(IMPOSSIBLE_NATAL_ASPECT_KEYS.isdisjoint(EXPECTED_MISSING_REACHABLE))
        self.assertTrue(frozenset(SUPPORTED_ASPECT_KEYS) <= REACHABLE_NATAL_ASPECT_KEYS)
        self.assertEqual(VENUS_REACHABLE_FAMILY, frozenset(SUPPORTED_ASPECT_KEYS) & frozenset(
            k for k in REACHABLE_NATAL_ASPECT_KEYS if k.endswith("_Venus")
        ))

    def test_shared_ref_and_pack_sizes(self):
        self.assertEqual(REF_VENUS_SX_CJ, "bioastrology_mercury_venus_sextile_conjunction")
        self.assertTrue(all(item.source_reference == REF_VENUS_SX_CJ for item in VENUS_SEXTILE))
        self.assertTrue(all(item.source_reference == REF_VENUS_SX_CJ for item in VENUS_CONJUNCTION))
        self.assertEqual(len(VENUS_SEXTILE), 17)
        self.assertEqual(len(VENUS_CONJUNCTION_AUTOMATISM), 1)
        self.assertEqual(len(VENUS_CONJUNCTION), 18)

    def test_catalog_integrity(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])
        self.assertTrue(all(item.source_reference for item in ALL_SOURCE_FACTS))
        self.assertTrue(all(not item.unresolved for item in VENUS_SEXTILE))
        self.assertTrue(all(not item.unresolved for item in VENUS_CONJUNCTION))
        self.assertTrue(all(item.activation_condition is None for item in VENUS_SEXTILE))
        self.assertTrue(all(item.activation_condition is None for item in VENUS_CONJUNCTION))
        self.assertFalse(any(item.category == "compensation" for item in VENUS_SEXTILE + VENUS_CONJUNCTION))
        self.assertFalse(any("celebrity" in item.id for item in VENUS_SEXTILE + VENUS_CONJUNCTION))
        self.assertFalse(any("genesis" in item.id for item in VENUS_SEXTILE + VENUS_CONJUNCTION))
        self.assertEqual(len(REPEATED_SIGNAL_SPECS), 15)
        self.assertNotIn("writing", {spec["tag"] for spec in REPEATED_SIGNAL_SPECS})


class AspectBatchC12AtomTests(unittest.TestCase):
    def test_common_semantics_present_in_both_packs(self):
        shared_tags = {
            "predominantly_harmonious_source_classification",
            "concrete_thinking",
            "practical_thinking",
            "beautiful_handwriting",
            "beautiful_speech",
            "grounding_venus_from_esoteric_drift",
            "source_dependency_avoidance_venus_context",
            "verbalizes_financial_motives",
            "verbalizes_romantic_motives",
            "financial_reasonableness",
            "relationship_reasonableness",
            "commercial_talent",
            "writing",
            "copywriting_ability",
            "reasonable_emotional_switching",
            "understands_information_flows",
            "clear_self_expression",
        }
        self.assertTrue(shared_tags <= _tags(VENUS_SEXTILE))
        self.assertTrue(shared_tags <= _tags(VENUS_CONJUNCTION))

    def test_conjunction_automatism_only_on_conjunction(self):
        self.assertIn("love_thought_commercial_automatism", _tags(VENUS_CONJUNCTION))
        self.assertNotIn("love_thought_commercial_automatism", _tags(VENUS_SEXTILE))
        auto = VENUS_CONJUNCTION_AUTOMATISM[0]
        self.assertEqual(auto.factor_key, "conjunction_Venus")
        self.assertIn("automatism", auto.text.lower())

    def test_tag_safety_hardening(self):
        by_sx = {item.id: item for item in VENUS_SEXTILE}
        speech = by_sx["ven_sx_beautiful_speech"]
        self.assertEqual(speech.tags, ("beautiful_speech",))
        self.assertNotIn("soft_speech", speech.tags)
        self.assertNotIn("persuasion", speech.tags)
        self.assertNotIn("oratory", speech.tags)
        commercial = by_sx["ven_sx_commercial_talent"]
        self.assertEqual(commercial.tags, ("commercial_talent",))
        self.assertNotIn("sales", commercial.tags)
        self.assertNotIn("persuasion", commercial.tags)
        writing = by_sx["ven_sx_writing_ability"]
        self.assertEqual(writing.tags, ("writing",))
        copy = by_sx["ven_sx_copywriting_ability"]
        self.assertEqual(copy.tags, ("copywriting_ability",))
        self.assertNotIn("persuasion", copy.tags)
        self.assertNotIn("sales", copy.tags)
        concrete = by_sx["ven_sx_concrete_thinking"]
        self.assertNotIn("analytical_thinking", concrete.tags)
        self.assertNotIn("technical_ability", concrete.tags)
        flows = by_sx["ven_sx_understands_information_flows"]
        self.assertNotIn("analytical_thinking", flows.tags)
        self.assertNotIn("insight", flows.tags)
        clear = by_sx["ven_sx_clear_self_expression"]
        self.assertNotIn("persuasion", clear.tags)
        fin_reas = by_sx["ven_sx_financial_reasonableness"]
        self.assertEqual(fin_reas.tags, ("financial_reasonableness",))
        self.assertNotIn("reasonableness", fin_reas.tags)
        dep = by_sx["ven_sx_source_dependency_avoidance_venus_context"]
        self.assertIn("not a clinical", dep.text.lower())
        switch = by_sx["ven_sx_reasonable_emotional_switching"]
        self.assertIn("toxic", switch.text.lower())
        self.assertIn("does not assert", switch.text.lower())


class AspectBatchC12ActivationTests(unittest.TestCase):
    def test_sextile_activates_sextile_pack_only(self):
        profile = _synthetic_venus("sextile")
        self.assertEqual(profile.coverage.status, "complete")
        self.assertIn("aspect:sextile_Venus", profile.coverage.covered_factors)
        self.assertTrue(_ids(VENUS_SEXTILE).issubset(_ids(profile.aspect_facts)))
        self.assertTrue(_ids(VENUS_CONJUNCTION).isdisjoint(_ids(profile.aspect_facts)))
        self.assertFalse(any(item.factor_key == "conjunction_Venus" for item in profile.aspect_facts))

    def test_conjunction_activates_conjunction_pack_only(self):
        profile = _synthetic_venus("conjunction")
        self.assertEqual(profile.coverage.status, "complete")
        self.assertIn("aspect:conjunction_Venus", profile.coverage.covered_factors)
        self.assertTrue(_ids(VENUS_CONJUNCTION).issubset(_ids(profile.aspect_facts)))
        self.assertTrue(_ids(VENUS_SEXTILE).isdisjoint(_ids(profile.aspect_facts)))
        self.assertFalse(any(item.factor_key == "sextile_Venus" for item in profile.aspect_facts))

    def test_no_same_factor_self_repeat(self):
        for aspect_type, pack in (("sextile", VENUS_SEXTILE), ("conjunction", VENUS_CONJUNCTION)):
            with self.subTest(aspect=aspect_type):
                profile = _synthetic_venus(aspect_type)
                activated = [item for item in profile.aspect_facts if not item.unresolved]
                self.assertEqual(detect_repeated_signals(activated), [])
                self.assertTrue(_ids(pack).issubset(_ids(activated)))

    def test_unsupported_probe_remains_conjunction_neptune(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Leo",
                mercury_element="fire",
                mercury_motion="direct",
                mercury_house=1,
                aspects=[MercuryAspect(planet="Neptune", type="conjunction", orb_deg=2.0)],
            )
        )
        self.assertEqual(profile.coverage.status, "partial")
        self.assertEqual(profile.coverage.missing_factors, ["aspect:conjunction_Neptune"])
        self.assertIn("conjunction_Venus", SUPPORTED_ASPECT_KEYS)
        self.assertIn("sextile_Venus", SUPPORTED_ASPECT_KEYS)
        self.assertNotIn("conjunction_Neptune", SUPPORTED_ASPECT_KEYS)


class AspectBatchC12RegressionTests(unittest.TestCase):
    def test_golden_cases_and_venus_presence(self):
        cases = [
            ("Avdey", date(1986, 7, 14), time(7, 10), "Simferopol, Ukraine"),
            ("Vlad", date(1986, 5, 16), time(15, 0), "Dnipro, Ukraine"),
            ("Dzmitry", date(1985, 11, 12), time(14, 15), "Zhodino, Belarus"),
        ]
        expected_repeats = {
            "Avdey": {
                "analytical_thinking",
                "technical_ability",
                "debate",
                "argumentation",
                "nonstandard_thinking",
                "sales",
            },
            "Vlad": {
                "analytical_thinking",
                "persuasion",
                "lifelong_learning",
                "foreign_languages",
            },
            "Dzmitry": {
                "persuasion",
                "foreign_languages",
                "teaching",
            },
        }
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
                venus_facts = [
                    item
                    for item in profile.aspect_facts
                    if item.factor_key in VENUS_REACHABLE_FAMILY
                ]
                self.assertEqual(venus_facts, [])
                self.assertFalse(any(a.planet == "Venus" for a in profile.calculated.aspects))
                self.assertEqual(
                    {signal.signal for signal in profile.repeated_signals},
                    expected_repeats[name],
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
        self.assertFalse(
            any(item.factor_key in VENUS_REACHABLE_FAMILY for item in andrey.aspect_facts)
        )
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
