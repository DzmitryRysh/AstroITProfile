"""Tests for Mercury Source Profile v2 — Aspect Batch C13 (Neptune reachable family)."""

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
from app.services.mercury_source_knowledge_c13_aspects import (
    NEPTUNE_CONJUNCTION,
    NEPTUNE_CONJUNCTION_UNIQUE,
    NEPTUNE_HARMONIOUS,
    NEPTUNE_OPPOSITION,
    NEPTUNE_OPPOSITION_UNIQUE,
    NEPTUNE_SQUARE,
    NEPTUNE_SQUARE_COMMON,
    NEPTUNE_SQUARE_MERCURY_STRONGER,
    NEPTUNE_SQUARE_NEPTUNE_STRONGER,
    REF_NEPTUNE_CJ,
    REF_NEPTUNE_HARM,
    REF_NEPTUNE_OPP,
    REF_NEPTUNE_SQ,
)
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
    detect_repeated_signals,
)

ENGINE_ASPECT_SLOTS = 45
NEPTUNE_PUBLIC_FAMILY = {
    "conjunction_Neptune",
    "sextile_Neptune",
    "square_Neptune",
    "trine_Neptune",
    "opposition_Neptune",
}
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
VENUS_REACHABLE_FAMILY = frozenset({"conjunction_Venus", "sextile_Venus"})


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


def _synthetic_neptune(aspect_type: str, orb_deg: float = 2.0):
    return build_source_profile_from_factors(
        MercurySourceFactors(
            birth_time_known=True,
            mercury_sign="Virgo",
            mercury_element="earth",
            mercury_motion="direct",
            mercury_house=3,
            aspects=[MercuryAspect(planet="Neptune", type=aspect_type, orb_deg=orb_deg)],
        )
    )


class AspectBatchC13CoverageTests(unittest.TestCase):
    def test_c13_neptune_family_and_catalog_guarantees(self):
        # Exact raw/reachable totals are owned by the latest aspect batch (C14+).
        self.assertEqual(len(ASPECT_PACK_ALIASES), 7)
        self.assertEqual(len(SUPPORTED_SIGN_KEYS), 12)
        self.assertEqual(len(SUPPORTED_HOUSE_KEYS), 12)
        self.assertTrue(NEPTUNE_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(MOON_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(JUPITER_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(SATURN_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(MARS_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(URANUS_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(VENUS_REACHABLE_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertIn("conjunction_Sun", SUPPORTED_ASPECT_KEYS)

    def test_neptune_family_is_exactly_five_of_five(self):
        for key in NEPTUNE_PUBLIC_FAMILY:
            self.assertIn(key, SUPPORTED_ASPECT_KEYS)
            self.assertIn(key, REACHABLE_NATAL_ASPECT_KEYS)
            self.assertNotIn(key, IMPOSSIBLE_NATAL_ASPECT_KEYS)
        self.assertEqual(ASPECT_PACK_ALIASES["sextile_Neptune"], "trine_Neptune")
        self.assertIn("trine_Neptune", _canonical_aspect_packs())
        self.assertNotIn("sextile_Neptune", _canonical_aspect_packs())
        for key in ("square_Neptune", "opposition_Neptune", "conjunction_Neptune"):
            self.assertIn(key, _canonical_aspect_packs())
            self.assertNotIn(key, ASPECT_PACK_ALIASES)

    def test_reachable_geometry_unchanged_after_c13(self):
        summary = natal_aspect_reachability_summary(SUPPORTED_ASPECT_KEYS)
        self.assertEqual(summary["raw_total"], 45)
        self.assertEqual(summary["reachable_total"], 38)
        self.assertEqual(summary["impossible_total"], 7)
        for key in NEPTUNE_PUBLIC_FAMILY:
            self.assertIn(key, summary["supported_reachable_keys"])
            self.assertNotIn(key, summary["missing_reachable_keys"])
        self.assertTrue(frozenset(SUPPORTED_ASPECT_KEYS) <= REACHABLE_NATAL_ASPECT_KEYS)

    def test_refs_and_pack_sizes(self):
        self.assertEqual(REF_NEPTUNE_HARM, "bioastrology_mercury_neptune_harmonious")
        self.assertEqual(REF_NEPTUNE_SQ, "bioastrology_mercury_neptune_square")
        self.assertEqual(REF_NEPTUNE_OPP, "bioastrology_mercury_neptune_opposition")
        self.assertEqual(REF_NEPTUNE_CJ, "bioastrology_mercury_neptune_conjunction")
        self.assertTrue(all(item.source_reference == REF_NEPTUNE_HARM for item in NEPTUNE_HARMONIOUS))
        self.assertTrue(all(item.source_reference == REF_NEPTUNE_SQ for item in NEPTUNE_SQUARE))
        self.assertTrue(all(item.source_reference == REF_NEPTUNE_OPP for item in NEPTUNE_OPPOSITION))
        self.assertTrue(all(item.source_reference == REF_NEPTUNE_CJ for item in NEPTUNE_CONJUNCTION))
        self.assertEqual(len(NEPTUNE_HARMONIOUS), 11)
        self.assertEqual(len(NEPTUNE_SQUARE_COMMON), 17)
        self.assertEqual(len(NEPTUNE_SQUARE_MERCURY_STRONGER), 6)
        self.assertEqual(len(NEPTUNE_SQUARE_NEPTUNE_STRONGER), 9)
        self.assertEqual(len(NEPTUNE_SQUARE), 32)
        self.assertEqual(len(NEPTUNE_OPPOSITION_UNIQUE), 3)
        self.assertEqual(len(NEPTUNE_OPPOSITION), 19)
        self.assertEqual(len(NEPTUNE_CONJUNCTION_UNIQUE), 2)
        self.assertEqual(len(NEPTUNE_CONJUNCTION), 18)

    def test_catalog_integrity(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])
        self.assertTrue(all(item.source_reference for item in ALL_SOURCE_FACTS))
        all_nep = NEPTUNE_HARMONIOUS + NEPTUNE_SQUARE + NEPTUNE_OPPOSITION + NEPTUNE_CONJUNCTION
        self.assertFalse(any(item.category == "compensation" for item in all_nep))
        self.assertFalse(any("celebrity" in item.id for item in all_nep))
        self.assertFalse(any("supergift" in item.id for item in all_nep))
        self.assertFalse(any("secondary_gain" in item.id for item in all_nep))
        self.assertFalse(any("genesis" in item.id for item in all_nep))
        self.assertEqual(len(REPEATED_SIGNAL_SPECS), 15)


class AspectBatchC13AtomTests(unittest.TestCase):
    def test_harmonious_tags_and_safety(self):
        by_id = {item.id: item for item in NEPTUNE_HARMONIOUS}
        self.assertEqual(by_id["nep_harm_foreign_languages"].tags, ("foreign_languages",))
        self.assertEqual(by_id["nep_harm_excellent_memory"].tags, ("strong_memory",))
        self.assertEqual(by_id["nep_harm_literary_talent"].tags, ("literary_talent",))
        self.assertNotIn("writing", by_id["nep_harm_literary_talent"].tags)
        self.assertEqual(by_id["nep_harm_source_nlp_aptitude"].tags, ("source_nlp_aptitude",))
        self.assertEqual(by_id["nep_harm_source_hypnotic_aptitude"].tags, ("source_hypnotic_aptitude",))
        self.assertEqual(
            by_id["nep_harm_source_psychological_aptitude"].tags,
            ("source_psychological_aptitude",),
        )
        extrasensory = by_id["nep_harm_source_extrasensory_aptitude"]
        self.assertEqual(extrasensory.tags, ("source_extrasensory_aptitude",))
        self.assertNotIn("claircognizance", extrasensory.tags)
        self.assertNotIn("insight", extrasensory.tags)
        right = by_id["nep_harm_source_right_hemisphere_development"]
        self.assertIn("not a neuroscience", right.text.lower())
        forbidden = {
            "analytical_thinking",
            "technical_ability",
            "nonstandard_thinking",
            "persuasion",
            "debate",
            "argumentation",
            "evidence_requirement",
        }
        self.assertTrue(forbidden.isdisjoint(_tags(NEPTUNE_HARMONIOUS)))

    def test_square_strength_branches_unresolved(self):
        self.assertTrue(all(item.unresolved for item in NEPTUNE_SQUARE_MERCURY_STRONGER))
        self.assertTrue(all(item.unresolved for item in NEPTUNE_SQUARE_NEPTUNE_STRONGER))
        self.assertTrue(
            all(item.activation_condition == "strength_unresolved" for item in NEPTUNE_SQUARE_MERCURY_STRONGER)
        )
        self.assertTrue(
            all(item.activation_condition == "strength_unresolved" for item in NEPTUNE_SQUARE_NEPTUNE_STRONGER)
        )
        story = next(
            item for item in NEPTUNE_SQUARE_NEPTUNE_STRONGER if "storyteller" in item.id
        )
        self.assertNotIn("persuasion", story.tags)
        musical = next(item for item in NEPTUNE_SQUARE_NEPTUNE_STRONGER if "musical" in item.id)
        self.assertNotIn("beautiful_speech", musical.tags)
        deep = next(item for item in NEPTUNE_SQUARE_NEPTUNE_STRONGER if "voluminous" in item.id)
        self.assertNotIn("analytical_thinking", deep.tags)
        vivid = next(item for item in NEPTUNE_SQUARE_NEPTUNE_STRONGER if "vivid" in item.id)
        self.assertNotIn("insight", vivid.tags)

    def test_tense_safety_associations(self):
        for pack, prefix in (
            (NEPTUNE_SQUARE, "nep_sq"),
            (NEPTUNE_OPPOSITION, "nep_opp"),
            (NEPTUNE_CONJUNCTION, "nep_cj"),
        ):
            by_id = {item.id: item for item in pack}
            theft = by_id[f"{prefix}_source_theft_risk_association"]
            self.assertEqual(theft.tags, ("source_theft_risk_association",))
            self.assertIn("not a deterministic accusation", theft.text.lower())
            road = by_id[f"{prefix}_source_road_accident_risk_association"]
            self.assertEqual(road.tags, ("source_road_accident_risk_association",))
            self.assertNotIn("driving_ability", road.tags)
            plag = by_id[f"{prefix}_source_plagiarism_association"]
            self.assertIn("unintentional", plag.text.lower())
            female = by_id[f"{prefix}_source_female_logic_label"]
            self.assertEqual(female.tags, ("source_female_logic_label",))
            self.assertIn("not a claim about women", female.text.lower())
            lying = by_id[f"{prefix}_source_lying_distortion_association"]
            self.assertEqual(lying.tags, ("source_lying_distortion_association",))
            self.assertNotIn("lying", lying.tags)
            complex_ease = by_id[f"{prefix}_relative_ease_with_complex_material"]
            self.assertIn("not an iq", complex_ease.text.lower())
            diction = by_id[f"{prefix}_branch_multiple_affliction_diction_pronunciation"]
            self.assertTrue(diction.unresolved)
            self.assertEqual(
                diction.activation_condition,
                "multiple_affliction_context_unresolved",
            )


class AspectBatchC13ActivationTests(unittest.TestCase):
    def test_harmonious_alias_resolves_identical_catalog_facts(self):
        trine = _synthetic_neptune("trine")
        sextile = _synthetic_neptune("sextile")
        self.assertEqual(trine.coverage.status, "complete")
        self.assertEqual(sextile.coverage.status, "complete")
        self.assertEqual(_ids(trine.aspect_facts), _ids(NEPTUNE_HARMONIOUS))
        self.assertEqual(_ids(sextile.aspect_facts), _ids(NEPTUNE_HARMONIOUS))
        self.assertTrue(all(item.factor_key == "trine_Neptune" for item in trine.aspect_facts))
        self.assertTrue(all(item.factor_key == "sextile_Neptune" for item in sextile.aspect_facts))
        self.assertFalse(any(item.id.startswith("nep_sq_") for item in trine.aspect_facts))

    def test_square_opposition_conjunction_are_distinct(self):
        square = _synthetic_neptune("square")
        opposition = _synthetic_neptune("opposition")
        conjunction = _synthetic_neptune("conjunction")
        self.assertTrue(_ids(NEPTUNE_SQUARE).issubset(_ids(square.aspect_facts) | _ids(square.conditional_unresolved)))
        self.assertTrue(
            _ids(NEPTUNE_OPPOSITION).issubset(
                _ids(opposition.aspect_facts) | _ids(opposition.conditional_unresolved)
            )
        )
        self.assertTrue(
            _ids(NEPTUNE_CONJUNCTION).issubset(
                _ids(conjunction.aspect_facts) | _ids(conjunction.conditional_unresolved)
            )
        )
        self.assertTrue(_ids(NEPTUNE_SQUARE).isdisjoint(_ids(opposition.aspect_facts)))
        self.assertTrue(_ids(NEPTUNE_SQUARE).isdisjoint(_ids(conjunction.aspect_facts)))
        self.assertFalse(any(item.id.startswith("nep_sq_") for item in conjunction.aspect_facts))
        self.assertFalse(
            any(
                item.activation_condition == "strength_unresolved"
                for item in conjunction.conditional_unresolved
            )
        )

    def test_square_strength_and_multiple_affliction_unresolved(self):
        profile = _synthetic_neptune("square")
        unresolved_ids = _ids(profile.conditional_unresolved)
        self.assertTrue(_ids(NEPTUNE_SQUARE_MERCURY_STRONGER).issubset(unresolved_ids))
        self.assertTrue(_ids(NEPTUNE_SQUARE_NEPTUNE_STRONGER).issubset(unresolved_ids))
        diction = next(
            item
            for item in profile.conditional_unresolved
            if item.id == "nep_sq_branch_multiple_affliction_diction_pronunciation"
        )
        self.assertEqual(diction.activation_condition, "multiple_affliction_context_unresolved")
        self.assertTrue(diction.unresolved)
        # Strength branches are present unresolved; no fake winner calculated.
        self.assertTrue(
            any(item.id.startswith("nep_sq_branch_mercury_") for item in profile.conditional_unresolved)
        )
        self.assertTrue(
            any(item.id.startswith("nep_sq_branch_neptune_") for item in profile.conditional_unresolved)
        )

    def test_unresolved_excluded_from_repeats(self):
        profile = _synthetic_neptune("square")
        all_facts = list(profile.aspect_facts) + list(profile.conditional_unresolved)
        for signal in detect_repeated_signals(all_facts):
            for fact_id in signal.fact_ids:
                fact = next(item for item in all_facts if item.id == fact_id)
                self.assertFalse(fact.unresolved, signal)
        resolved_only = [item for item in profile.aspect_facts if not item.unresolved]
        # Single Neptune factor alone cannot create a cross-factor repeat.
        self.assertEqual(detect_repeated_signals(resolved_only), [])

    def test_synthetic_unknown_aspect_still_marks_partial(self):
        # After C14 there is no reachable unsupported aspect; synthetic probe only.
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
        self.assertTrue(NEPTUNE_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))


class AspectBatchC13RegressionTests(unittest.TestCase):
    def test_golden_cases_and_neptune_presence(self):
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
                self.assertFalse(any(a.planet == "Neptune" for a in profile.calculated.aspects))
                self.assertFalse(
                    any(item.factor_key in NEPTUNE_PUBLIC_FAMILY for item in profile.aspect_facts)
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
