"""Tests for Mercury Source Profile v2 — Aspect Batch C9 (Moon opposition / conjunction)."""

from __future__ import annotations

import unittest
from collections import Counter
from datetime import date, time

from app.schemas.mercury_source_profile import MercurySourceProfileRequest
from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_source_knowledge import (
    ALL_SOURCE_FACTS,
    ASPECT_PACK_ALIASES,
    MOON_SEXTILE,
    MOON_SQUARE,
    SUPPORTED_ASPECT_KEYS,
    SUPPORTED_HOUSE_KEYS,
    SUPPORTED_SIGN_KEYS,
)
from app.services.mercury_source_knowledge_c9_aspects import (
    MOON_CONJUNCTION,
    MOON_CONJUNCTION_RESOLVED,
    MOON_CONJUNCTION_UNRESOLVED,
    MOON_OPPOSITION,
    REF_MOON_CONJ,
    REF_MOON_OPP,
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
PLUTO_PARTIAL_FAMILY = {
    "sextile_Pluto",
    "square_Pluto",
    "trine_Pluto",
}


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


def _canonical_aspect_packs() -> set[str]:
    return {
        item.factor_key
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "aspect"
    }


def _synthetic_moon(aspect_type: str):
    return build_source_profile_from_factors(
        MercurySourceFactors(
            birth_time_known=True,
            mercury_sign="Virgo",
            mercury_element="earth",
            mercury_motion="direct",
            mercury_house=3,
            aspects=[MercuryAspect(planet="Moon", type=aspect_type, orb_deg=1.2)],
        )
    )


class AspectBatchC9CoverageTests(unittest.TestCase):
    def test_c9_moon_family_remains_complete(self):
        # Historical C9 batch: factor-specific guarantee. Exact public count owned by C11+.
        self.assertTrue(MOON_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(JUPITER_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(SATURN_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(MARS_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(URANUS_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(PLUTO_PARTIAL_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertEqual(len(SUPPORTED_SIGN_KEYS), 12)
        self.assertEqual(len(SUPPORTED_HOUSE_KEYS), 12)

    def test_moon_family_is_exactly_five_of_five(self):
        self.assertIn("conjunction_Moon", SUPPORTED_ASPECT_KEYS)
        self.assertIn("opposition_Moon", SUPPORTED_ASPECT_KEYS)
        self.assertIn("sextile_Moon", SUPPORTED_ASPECT_KEYS)
        self.assertIn("square_Moon", SUPPORTED_ASPECT_KEYS)
        self.assertEqual(ASPECT_PACK_ALIASES["trine_Moon"], "sextile_Moon")
        self.assertNotIn("conjunction_Moon", ASPECT_PACK_ALIASES)
        self.assertNotIn("opposition_Moon", ASPECT_PACK_ALIASES)
        self.assertNotEqual(ASPECT_PACK_ALIASES.get("conjunction_Moon"), "opposition_Moon")
        self.assertIn("conjunction_Moon", _canonical_aspect_packs())
        self.assertIn("opposition_Moon", _canonical_aspect_packs())
        self.assertIn("sextile_Moon", _canonical_aspect_packs())
        self.assertIn("square_Moon", _canonical_aspect_packs())
        self.assertNotIn("trine_Moon", _canonical_aspect_packs())

    def test_distinct_refs_and_catalog_identity(self):
        self.assertEqual(REF_MOON_OPP, "bioastrology_mercury_moon_opposition")
        self.assertEqual(REF_MOON_CONJ, "bioastrology_mercury_moon_conjunction")
        self.assertNotEqual(REF_MOON_OPP, REF_MOON_CONJ)
        self.assertTrue(all(item.source_reference == REF_MOON_OPP for item in MOON_OPPOSITION))
        self.assertTrue(all(item.source_reference == REF_MOON_CONJ for item in MOON_CONJUNCTION))
        self.assertTrue(_ids(MOON_OPPOSITION).isdisjoint(_ids(MOON_CONJUNCTION)))
        self.assertTrue(_ids(MOON_OPPOSITION).isdisjoint(_ids(MOON_SEXTILE)))
        self.assertTrue(_ids(MOON_OPPOSITION).isdisjoint(_ids(MOON_SQUARE)))
        self.assertTrue(_ids(MOON_CONJUNCTION).isdisjoint(_ids(MOON_SEXTILE)))
        self.assertTrue(_ids(MOON_CONJUNCTION).isdisjoint(_ids(MOON_SQUARE)))

    def test_catalog_integrity(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])
        self.assertTrue(all(item.source_reference for item in ALL_SOURCE_FACTS))
        self.assertEqual(len(MOON_OPPOSITION), 13)
        self.assertEqual(len(MOON_CONJUNCTION_RESOLVED), 11)
        self.assertEqual(len(MOON_CONJUNCTION_UNRESOLVED), 1)
        self.assertEqual(len(MOON_CONJUNCTION), 12)
        self.assertTrue(all(not item.unresolved for item in MOON_OPPOSITION))
        self.assertTrue(all(not item.unresolved for item in MOON_CONJUNCTION_RESOLVED))
        self.assertTrue(all(item.unresolved for item in MOON_CONJUNCTION_UNRESOLVED))
        self.assertTrue(
            all(
                item.activation_condition == "intellectual_work_context_unresolved"
                for item in MOON_CONJUNCTION_UNRESOLVED
            )
        )
        all_c9 = MOON_OPPOSITION + MOON_CONJUNCTION
        self.assertFalse(any(item.category == "compensation" for item in all_c9))
        self.assertFalse(any("supergift" in item.id for item in all_c9))
        self.assertFalse(any("celebrity" in item.id for item in all_c9))
        self.assertFalse(any("secondary_gain" in item.id for item in all_c9))
        self.assertEqual(len(MOON_SEXTILE), 17)
        self.assertEqual(len(MOON_SQUARE), 7)


class AspectBatchC9AtomTests(unittest.TestCase):
    def test_opposition_key_atoms_and_safety(self):
        by_id = {item.id: item for item in MOON_OPPOSITION}
        self.assertEqual(
            by_id["moon_opp_comfort_novelty_oscillation"].tags,
            ("comfort_novelty_oscillation",),
        )
        lying = by_id["moon_opp_source_lying_association"]
        self.assertEqual(lying.tags, ("source_lying_association",))
        self.assertNotIn("lying", lying.tags)
        self.assertIn("source", lying.text.lower())
        self.assertNotIn("this person is", lying.text.lower())
        theft = by_id["moon_opp_source_theft_association"]
        self.assertEqual(theft.tags, ("source_theft_association",))
        self.assertIn("not a crime prediction", theft.text.lower())
        self.assertEqual(
            by_id["moon_opp_directionless_brownian_activity"].tags,
            ("directionless_brownian_activity",),
        )
        self.assertNotIn("multitasking", by_id["moon_opp_directionless_brownian_activity"].tags)
        self.assertNotIn(
            "goal_setting_difficulty",
            by_id["moon_opp_goal_concentration_difficulty"].tags,
        )
        self.assertNotIn("planning", by_id["moon_opp_goal_concentration_difficulty"].tags)
        self.assertNotIn(
            "analytical_thinking",
            by_id["moon_opp_detail_stream_essence_loss"].tags,
        )
        mother = by_id["moon_opp_source_mother_strange_infantile_perception"]
        self.assertIn("perception", mother.text.lower())
        self.assertIn("not an objective fact", mother.text.lower())
        spouse = by_id["moon_opp_source_spouse_home_irritation"]
        self.assertEqual(spouse.tags, ("source_spouse_home_irritation",))
        self.assertIn("does not infer marital status", spouse.text.lower())

    def test_conjunction_key_atoms_and_unresolved(self):
        by_id = {item.id: item for item in MOON_CONJUNCTION}
        corpus = by_id["moon_cj_source_corpus_callosum_analogy"]
        self.assertEqual(corpus.tags, ("source_corpus_callosum_analogy",))
        self.assertIn("not a medical", corpus.text.lower())
        self.assertEqual(
            by_id["moon_cj_neutral_aspect_source_classification"].tags,
            ("neutral_aspect_source_classification",),
        )
        trips = by_id["moon_cj_feelings_expressed_through_trips"]
        self.assertEqual(trips.tags, ("feelings_expressed_through_trips",))
        self.assertNotIn("trips", trips.tags)
        psych = by_id["moon_cj_psychological_right_hemisphere_learning_context"]
        self.assertEqual(psych.tags, ("psychological_right_hemisphere_learning_context",))
        self.assertNotIn("intuition", psych.tags)
        self.assertEqual(by_id["moon_cj_writing_ability"].tags, ("writing",))
        self.assertEqual(by_id["moon_cj_poetic_ability"].tags, ("poetic_ability",))
        self.assertEqual(by_id["moon_cj_strong_sticky_memory"].tags, ("strong_memory",))
        self.assertEqual(by_id["moon_cj_softer_melodic_speech"].tags, ("soft_speech",))
        self.assertEqual(by_id["moon_cj_dexterity"].tags, ("dexterity",))
        self.assertNotIn("insight", by_id["moon_cj_writing_ability"].tags)
        self.assertNotIn("creative", by_id["moon_cj_poetic_ability"].tags)
        frozen = by_id["moon_cj_branch_non_intellectual_work_frozen_opposition"]
        self.assertTrue(frozen.unresolved)
        self.assertEqual(frozen.activation_condition, "intellectual_work_context_unresolved")
        self.assertEqual(frozen.tags, ("frozen_opposition_without_oscillation",))
        self.assertIn("does not activate opposition", frozen.text.lower())


class AspectBatchC9ActivationTests(unittest.TestCase):
    def test_opposition_activates_only_opposition_pack(self):
        profile = _synthetic_moon("opposition")
        self.assertEqual(profile.coverage.status, "complete")
        self.assertIn("aspect:opposition_Moon", profile.coverage.covered_factors)
        self.assertEqual(_ids(profile.aspect_facts), _ids(MOON_OPPOSITION))
        self.assertTrue(all(item.factor_key == "opposition_Moon" for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("moon_sx_") for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("moon_sq_") for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("moon_cj_") for item in profile.aspect_facts))
        self.assertTrue(all(not item.unresolved for item in profile.aspect_facts))
        self.assertEqual(
            detect_repeated_signals([item for item in profile.aspect_facts if not item.unresolved]),
            [],
        )

    def test_conjunction_activates_only_conjunction_pack_with_unresolved(self):
        profile = _synthetic_moon("conjunction")
        self.assertEqual(profile.coverage.status, "complete")
        self.assertIn("aspect:conjunction_Moon", profile.coverage.covered_factors)
        self.assertEqual(_ids(profile.aspect_facts), _ids(MOON_CONJUNCTION))
        self.assertTrue(all(item.factor_key == "conjunction_Moon" for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("moon_sx_") for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("moon_sq_") for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("moon_opp_") for item in profile.aspect_facts))
        resolved = {item.id for item in profile.aspect_facts if not item.unresolved}
        self.assertEqual(resolved, _ids(MOON_CONJUNCTION_RESOLVED))
        self.assertTrue(_ids(MOON_CONJUNCTION_UNRESOLVED).issubset(_ids(profile.conditional_unresolved)))
        frozen = next(
            item
            for item in profile.conditional_unresolved
            if item.id == "moon_cj_branch_non_intellectual_work_frozen_opposition"
        )
        self.assertEqual(frozen.activation_condition, "intellectual_work_context_unresolved")
        all_facts = list(profile.aspect_facts) + list(profile.conditional_unresolved)
        for signal in detect_repeated_signals(all_facts):
            for fact_id in signal.fact_ids:
                fact = next(item for item in all_facts if item.id == fact_id)
                self.assertFalse(fact.unresolved, signal)
        self.assertEqual(
            detect_repeated_signals([item for item in profile.aspect_facts if not item.unresolved]),
            [],
        )

    def test_harmonious_and_square_remain_separate(self):
        sextile = _synthetic_moon("sextile")
        trine = _synthetic_moon("trine")
        square = _synthetic_moon("square")
        self.assertEqual(_ids(sextile.aspect_facts), _ids(MOON_SEXTILE))
        self.assertTrue(all(item.factor_key == "sextile_Moon" for item in sextile.aspect_facts))
        self.assertTrue(all(item.factor_key == "trine_Moon" for item in trine.aspect_facts))
        self.assertEqual(_ids(trine.aspect_facts), _ids(MOON_SEXTILE))
        self.assertEqual(_ids(square.aspect_facts), _ids(MOON_SQUARE))
        self.assertFalse(any(item.id.startswith("moon_opp_") for item in sextile.aspect_facts))
        self.assertFalse(any(item.id.startswith("moon_cj_") for item in square.aspect_facts))

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
        self.assertIn("opposition_Moon", SUPPORTED_ASPECT_KEYS)
        self.assertIn("conjunction_Moon", SUPPORTED_ASPECT_KEYS)


class AspectBatchC9RegressionTests(unittest.TestCase):
    def test_golden_cases_remain_complete_and_stable(self):
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
                self.assertFalse(
                    any(
                        item.factor_key in {"opposition_Moon", "conjunction_Moon"}
                        for item in profile.aspect_facts
                    )
                )
                self.assertEqual(
                    {signal.signal for signal in profile.repeated_signals},
                    expected_repeats[name],
                )

    def test_vlad_keeps_square_moon_only(self):
        profile = build_mercury_source_profile(
            MercurySourceProfileRequest(
                birth_date=date(1986, 5, 16),
                birth_time=time(15, 0),
                birth_place="Dnipro, Ukraine",
            )
        )
        moon = [item for item in profile.aspect_facts if "Moon" in item.factor_key]
        self.assertTrue(moon)
        self.assertTrue(all(item.factor_key == "square_Moon" for item in moon))
        self.assertEqual(_ids(moon), _ids(MOON_SQUARE))

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
        self.assertFalse(any("Moon" in item.factor_key for item in andrey.aspect_facts))
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
