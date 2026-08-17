"""Tests for Mercury Source Profile v2 — Aspect Batch C11 (Sun conjunction)."""

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
from app.services.mercury_source_knowledge_c11_aspects import (
    REF_SUN_CONJ,
    SUN_CONJUNCTION,
    SUN_CONJUNCTION_BASE,
    SUN_CONJUNCTION_COMBUSTION,
    SUN_CONJUNCTION_EXTERNAL_AFFLICTION,
)
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
    detect_repeated_signals,
)

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


def _canonical_aspect_packs() -> set[str]:
    return {
        item.factor_key
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "aspect"
    }


def _synthetic_sun(orb_deg: float):
    return build_source_profile_from_factors(
        MercurySourceFactors(
            birth_time_known=True,
            mercury_sign="Virgo",
            mercury_element="earth",
            mercury_motion="direct",
            mercury_house=3,
            aspects=[MercuryAspect(planet="Sun", type="conjunction", orb_deg=orb_deg)],
        )
    )


class AspectBatchC11CoverageTests(unittest.TestCase):
    def test_c11_sun_family_and_catalog_guarantees(self):
        # Exact raw/reachable totals are owned by the latest aspect batch (C14+).
        self.assertEqual(len(SUPPORTED_SIGN_KEYS), 12)
        self.assertEqual(len(SUPPORTED_HOUSE_KEYS), 12)
        self.assertTrue(MOON_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(JUPITER_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(SATURN_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(MARS_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(URANUS_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))

    def test_sun_reachable_family_is_exactly_one_of_one(self):
        self.assertIn("conjunction_Sun", SUPPORTED_ASPECT_KEYS)
        self.assertNotIn("conjunction_Sun", ASPECT_PACK_ALIASES)
        self.assertIn("conjunction_Sun", _canonical_aspect_packs())
        for aspect in ("sextile", "square", "trine", "opposition"):
            key = f"{aspect}_Sun"
            self.assertNotIn(key, SUPPORTED_ASPECT_KEYS)
            self.assertNotIn(key, _canonical_aspect_packs())
            self.assertIn(key, IMPOSSIBLE_NATAL_ASPECT_KEYS)

    def test_reachable_geometry_unchanged_after_c11(self):
        summary = natal_aspect_reachability_summary(SUPPORTED_ASPECT_KEYS)
        self.assertEqual(summary["reachable_total"], 38)
        self.assertEqual(summary["impossible_total"], 7)
        self.assertIn("conjunction_Sun", summary["supported_reachable_keys"])
        self.assertNotIn("conjunction_Sun", summary["missing_reachable_keys"])
        self.assertTrue(frozenset(SUPPORTED_ASPECT_KEYS) <= REACHABLE_NATAL_ASPECT_KEYS)

    def test_distinct_ref_and_catalog_identity(self):
        self.assertEqual(REF_SUN_CONJ, "bioastrology_mercury_sun_conjunction")
        self.assertTrue(all(item.source_reference == REF_SUN_CONJ for item in SUN_CONJUNCTION))
        self.assertEqual(len(SUN_CONJUNCTION_BASE), 11)
        self.assertEqual(len(SUN_CONJUNCTION_COMBUSTION), 4)
        self.assertEqual(len(SUN_CONJUNCTION_EXTERNAL_AFFLICTION), 4)
        self.assertEqual(len(SUN_CONJUNCTION), 19)

    def test_catalog_integrity(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])
        self.assertTrue(all(item.source_reference for item in ALL_SOURCE_FACTS))
        self.assertTrue(all(not item.unresolved for item in SUN_CONJUNCTION_BASE))
        self.assertTrue(all(not item.unresolved for item in SUN_CONJUNCTION_COMBUSTION))
        self.assertTrue(all(item.unresolved for item in SUN_CONJUNCTION_EXTERNAL_AFFLICTION))
        self.assertTrue(
            all(
                item.activation_condition == "sun_mercury_combustion_orb_lt_5"
                for item in SUN_CONJUNCTION_COMBUSTION
            )
        )
        self.assertTrue(
            all(
                item.activation_condition == "external_affliction_context_unresolved"
                for item in SUN_CONJUNCTION_EXTERNAL_AFFLICTION
            )
        )
        self.assertFalse(any(item.category == "compensation" for item in SUN_CONJUNCTION))
        self.assertFalse(any("celebrity" in item.id for item in SUN_CONJUNCTION))
        self.assertFalse(any("genesis" in item.id for item in SUN_CONJUNCTION))
        self.assertEqual(len(REPEATED_SIGNAL_SPECS), 15)


class AspectBatchC11AtomTests(unittest.TestCase):
    def test_base_atoms_and_tag_safety(self):
        by_id = {item.id: item for item in SUN_CONJUNCTION}
        self.assertEqual(by_id["sun_cj_identity_thought_fusion"].tags, ("identity_thought_fusion",))
        self.assertEqual(by_id["sun_cj_creative_phrasing"].tags, ("creative_phrasing",))
        self.assertNotIn("creative", by_id["sun_cj_creative_phrasing"].tags)
        oratory = by_id["sun_cj_oratory_mastery"]
        self.assertEqual(oratory.tags, ("source_oratory_aptitude",))
        self.assertNotIn("persuasion", oratory.tags)
        self.assertNotIn("debate", oratory.tags)
        self.assertEqual(by_id["sun_cj_sense_of_humor"].tags, ("sense_of_humor",))
        self.assertEqual(by_id["sun_cj_writing_ability"].tags, ("writing",))
        self.assertEqual(by_id["sun_cj_enjoys_books"].tags, ("enjoys_books",))
        self.assertNotIn("books", by_id["sun_cj_enjoys_books"].tags)
        self.assertEqual(by_id["sun_cj_enjoys_trips"].tags, ("enjoys_trips",))
        self.assertNotIn("trips", by_id["sun_cj_enjoys_trips"].tags)
        self.assertEqual(by_id["sun_cj_enjoys_learning"].tags, ("enjoys_learning",))
        self.assertNotIn("lifelong_learning", by_id["sun_cj_enjoys_learning"].tags)
        intellect = by_id["sun_cj_source_intellectual_ability_contextual"]
        self.assertEqual(intellect.tags, ("source_intellectual_ability_contextual",))
        self.assertNotIn("technical_ability", intellect.tags)
        self.assertNotIn("analytical_thinking", intellect.tags)
        self.assertIn("not an iq", intellect.text.lower())

    def test_combustion_and_affliction_atoms(self):
        by_id = {item.id: item for item in SUN_CONJUNCTION}
        speech = by_id["sun_cj_combustion_excessive_speech"]
        self.assertEqual(speech.tags, ("excessive_speech",))
        self.assertNotIn("fast_speech", speech.tags)
        self.assertFalse(speech.unresolved)
        lying = by_id["sun_cj_branch_external_affliction_lying"]
        self.assertTrue(lying.unresolved)
        self.assertEqual(lying.tags, ("source_external_affliction_lying_association",))
        self.assertNotEqual(lying.tags, ("source_lying_association",))
        self.assertIn("unresolved", lying.text.lower())


class AspectBatchC11ActivationTests(unittest.TestCase):
    def test_base_activation_at_non_combustion_orb(self):
        profile = _synthetic_sun(5.5)
        self.assertEqual(profile.coverage.status, "complete")
        self.assertIn("aspect:conjunction_Sun", profile.coverage.covered_factors)
        self.assertTrue(_ids(SUN_CONJUNCTION_BASE).issubset(_ids(profile.aspect_facts)))
        self.assertTrue(_ids(SUN_CONJUNCTION_COMBUSTION).isdisjoint(_ids(profile.aspect_facts)))
        self.assertTrue(
            _ids(SUN_CONJUNCTION_EXTERNAL_AFFLICTION).issubset(_ids(profile.conditional_unresolved))
        )
        self.assertFalse(any(item.id.startswith("moon_") for item in profile.aspect_facts))

    def test_combustion_boundary_orb_rules(self):
        under = _synthetic_sun(4.99)
        at = _synthetic_sun(5.0)
        over = _synthetic_sun(5.5)
        self.assertTrue(_ids(SUN_CONJUNCTION_COMBUSTION).issubset(_ids(under.aspect_facts)))
        self.assertTrue(all(not item.unresolved for item in under.aspect_facts if item.id in _ids(SUN_CONJUNCTION_COMBUSTION)))
        self.assertTrue(_ids(SUN_CONJUNCTION_COMBUSTION).isdisjoint(_ids(at.aspect_facts)))
        self.assertTrue(_ids(SUN_CONJUNCTION_COMBUSTION).isdisjoint(_ids(over.aspect_facts)))
        self.assertTrue(_ids(SUN_CONJUNCTION_BASE).issubset(_ids(at.aspect_facts)))
        self.assertTrue(_ids(SUN_CONJUNCTION_BASE).issubset(_ids(over.aspect_facts)))

    def test_external_affliction_unresolved_and_excluded_from_repeats(self):
        profile = _synthetic_sun(2.0)
        unresolved = _ids(profile.conditional_unresolved)
        self.assertTrue(_ids(SUN_CONJUNCTION_EXTERNAL_AFFLICTION).issubset(unresolved))
        for item in profile.conditional_unresolved:
            if item.id in _ids(SUN_CONJUNCTION_EXTERNAL_AFFLICTION):
                self.assertEqual(item.activation_condition, "external_affliction_context_unresolved")
        all_facts = list(profile.aspect_facts) + list(profile.conditional_unresolved)
        for signal in detect_repeated_signals(all_facts):
            for fact_id in signal.fact_ids:
                fact = next(item for item in all_facts if item.id == fact_id)
                self.assertFalse(fact.unresolved, signal)
        self.assertEqual(
            detect_repeated_signals([item for item in profile.aspect_facts if not item.unresolved]),
            [],
        )

    def test_hard_aspected_does_not_resolve_external_affliction_branch(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Leo",
                mercury_element="fire",
                mercury_motion="direct",
                mercury_house=1,
                aspects=[
                    MercuryAspect(planet="Sun", type="conjunction", orb_deg=2.0),
                    MercuryAspect(planet="Mars", type="square", orb_deg=1.0),
                ],
            )
        )
        self.assertTrue(profile.calculated.hard_aspected)
        affliction = [
            item
            for item in profile.conditional_unresolved
            if item.id in _ids(SUN_CONJUNCTION_EXTERNAL_AFFLICTION)
        ]
        self.assertEqual(len(affliction), 4)
        self.assertTrue(all(item.unresolved for item in affliction))

    def test_synthetic_unknown_aspect_still_marks_partial(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Leo",
                mercury_element="fire",
                mercury_motion="direct",
                mercury_house=1,
                aspects=[MercuryAspect(planet="SyntheticProbe", type="conjunction", orb_deg=2.0)],
            )
        )
        self.assertEqual(profile.coverage.status, "partial")
        self.assertEqual(profile.coverage.missing_factors, ["aspect:conjunction_SyntheticProbe"])
        self.assertIn("conjunction_Sun", SUPPORTED_ASPECT_KEYS)


class AspectBatchC11RegressionTests(unittest.TestCase):
    def test_golden_cases_and_sun_conjunction_presence(self):
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
                "teaching",
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
                sun = [item for item in profile.aspect_facts if item.factor_key == "conjunction_Sun"]
                self.assertEqual(sun, [])
                self.assertFalse(
                    any(a.planet == "Sun" for a in profile.calculated.aspects)
                )
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
        self.assertFalse(any(item.factor_key == "conjunction_Sun" for item in andrey.aspect_facts))
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
