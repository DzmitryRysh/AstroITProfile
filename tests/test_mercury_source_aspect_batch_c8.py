"""Tests for Mercury Source Profile v2 — Aspect Batch C8 (Uranus square / opposition)."""

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
    URANUS_CONJUNCTION,
)
from app.services.mercury_source_knowledge_c1_aspects import REF_URANUS_HARM, URANUS_HARMONIOUS
from app.services.mercury_source_knowledge_c8_aspects import (
    REF_URANUS_OPP,
    REF_URANUS_SQ,
    URANUS_OPPOSITION,
    URANUS_OPPOSITION_COMMON,
    URANUS_OPPOSITION_CORE,
    URANUS_SQUARE,
    URANUS_SQUARE_COMMON,
    URANUS_SQUARE_MERCURY_WINS,
    URANUS_SQUARE_URANUS_WINS,
)
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
    detect_repeated_signals,
)

URANUS_PUBLIC_FAMILY = {
    "conjunction_Uranus",
    "sextile_Uranus",
    "square_Uranus",
    "trine_Uranus",
    "opposition_Uranus",
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


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


def _canonical_aspect_packs() -> set[str]:
    return {
        item.factor_key
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "aspect"
    }


def _synthetic_uranus(aspect_type: str):
    return build_source_profile_from_factors(
        MercurySourceFactors(
            birth_time_known=True,
            mercury_sign="Virgo",
            mercury_element="earth",
            mercury_motion="direct",
            mercury_house=3,
            aspects=[MercuryAspect(planet="Uranus", type=aspect_type, orb_deg=1.2)],
        )
    )


class AspectBatchC8CoverageTests(unittest.TestCase):
    def test_c8_uranus_family_remains_complete(self):
        # Historical C8 batch: factor-specific guarantee. Exact public count owned by C9+.
        self.assertTrue(URANUS_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(JUPITER_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(SATURN_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(MARS_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertEqual(len(SUPPORTED_SIGN_KEYS), 12)
        self.assertEqual(len(SUPPORTED_HOUSE_KEYS), 12)

    def test_uranus_family_is_exactly_five_of_five(self):
        self.assertIn("conjunction_Uranus", SUPPORTED_ASPECT_KEYS)
        self.assertIn("square_Uranus", SUPPORTED_ASPECT_KEYS)
        self.assertIn("opposition_Uranus", SUPPORTED_ASPECT_KEYS)
        self.assertIn("trine_Uranus", SUPPORTED_ASPECT_KEYS)
        self.assertEqual(ASPECT_PACK_ALIASES["sextile_Uranus"], "trine_Uranus")
        self.assertNotIn("square_Uranus", ASPECT_PACK_ALIASES)
        self.assertNotIn("opposition_Uranus", ASPECT_PACK_ALIASES)
        self.assertNotIn("conjunction_Uranus", ASPECT_PACK_ALIASES)
        self.assertNotEqual(ASPECT_PACK_ALIASES.get("square_Uranus"), "conjunction_Uranus")
        self.assertNotEqual(ASPECT_PACK_ALIASES.get("opposition_Uranus"), "square_Uranus")
        self.assertIn("conjunction_Uranus", _canonical_aspect_packs())
        self.assertIn("square_Uranus", _canonical_aspect_packs())
        self.assertIn("trine_Uranus", _canonical_aspect_packs())
        self.assertIn("opposition_Uranus", _canonical_aspect_packs())
        self.assertNotIn("sextile_Uranus", _canonical_aspect_packs())

    def test_distinct_refs_and_catalog_identity(self):
        self.assertEqual(REF_URANUS_SQ, "bioastrology_mercury_uranus_square")
        self.assertEqual(REF_URANUS_OPP, "bioastrology_mercury_uranus_opposition")
        self.assertNotEqual(REF_URANUS_SQ, REF_URANUS_OPP)
        self.assertNotEqual(REF_URANUS_SQ, REF_URANUS_HARM)
        self.assertTrue(all(item.source_reference == REF_URANUS_SQ for item in URANUS_SQUARE))
        self.assertTrue(all(item.source_reference == REF_URANUS_OPP for item in URANUS_OPPOSITION))
        self.assertTrue(_ids(URANUS_SQUARE).isdisjoint(_ids(URANUS_OPPOSITION)))
        self.assertTrue(_ids(URANUS_SQUARE).isdisjoint(_ids(URANUS_CONJUNCTION)))
        self.assertTrue(_ids(URANUS_OPPOSITION).isdisjoint(_ids(URANUS_CONJUNCTION)))
        self.assertTrue(_ids(URANUS_SQUARE).isdisjoint(_ids(URANUS_HARMONIOUS)))
        self.assertTrue(_ids(URANUS_OPPOSITION).isdisjoint(_ids(URANUS_HARMONIOUS)))

    def test_catalog_integrity(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])
        self.assertTrue(all(item.source_reference for item in ALL_SOURCE_FACTS))
        self.assertEqual(len(URANUS_SQUARE_COMMON), 16)
        self.assertEqual(len(URANUS_SQUARE_MERCURY_WINS), 6)
        self.assertEqual(len(URANUS_SQUARE_URANUS_WINS), 7)
        self.assertEqual(len(URANUS_SQUARE), 29)
        self.assertEqual(len(URANUS_OPPOSITION_CORE), 2)
        self.assertEqual(len(URANUS_OPPOSITION_COMMON), 16)
        self.assertEqual(len(URANUS_OPPOSITION), 18)
        self.assertTrue(all(not item.unresolved for item in URANUS_SQUARE_COMMON))
        self.assertTrue(all(item.unresolved for item in URANUS_SQUARE_MERCURY_WINS))
        self.assertTrue(all(item.unresolved for item in URANUS_SQUARE_URANUS_WINS))
        self.assertTrue(all(not item.unresolved for item in URANUS_OPPOSITION))
        self.assertTrue(
            all(
                item.activation_condition == "strength_unresolved"
                for item in URANUS_SQUARE_MERCURY_WINS + URANUS_SQUARE_URANUS_WINS
            )
        )
        all_c8 = URANUS_SQUARE + URANUS_OPPOSITION
        self.assertFalse(any(item.category == "compensation" for item in all_c8))
        self.assertFalse(any("supergift" in item.id for item in all_c8))
        self.assertFalse(any("celebrity" in item.id for item in all_c8))
        self.assertFalse(any("secondary_gain" in item.id for item in all_c8))
        self.assertFalse(any(item.activation_condition for item in URANUS_OPPOSITION))


class AspectBatchC8AtomTests(unittest.TestCase):
    def test_square_common_and_branch_atoms(self):
        by_id = {item.id: item for item in URANUS_SQUARE}
        self.assertEqual(
            by_id["uranus_sq_source_genius_fresh_open_mind"].tags,
            ("source_genius_fresh_open_mind",),
        )
        self.assertIn("not an objectively validated", by_id["uranus_sq_source_genius_fresh_open_mind"].text.lower())
        self.assertEqual(by_id["uranus_sq_distractibility"].tags, ("distractibility",))
        adhd = by_id["uranus_sq_source_adhd_association"]
        self.assertEqual(adhd.tags, ("source_adhd_association",))
        self.assertIn("not a medical diagnosis", adhd.text.lower())
        self.assertNotIn("distractibility", adhd.tags)
        self.assertEqual(by_id["uranus_sq_strange_concept_drift"].tags, ("strange_concept_drift",))
        self.assertNotIn("nonstandard_thinking", by_id["uranus_sq_strange_concept_drift"].tags)
        self.assertNotIn("driving_ability", by_id["uranus_sq_driving_accident_risk"].tags)
        speech = by_id["uranus_sq_fast_sometimes_disfluent_speech"]
        self.assertEqual(set(speech.tags), {"fast_speech", "speech_disfluency_or_compression"})
        self.assertNotIn("fast_thinking", speech.tags)
        self.assertEqual(by_id["uranus_sq_technical_talents"].tags, ("technical_ability",))
        self.assertEqual(by_id["uranus_sq_rebellious_free_thinking"].tags, ("rebellious_free_thinking",))
        self.assertNotIn("nonstandard_thinking", by_id["uranus_sq_rebellious_free_thinking"].tags)
        self.assertEqual(
            by_id["uranus_sq_interest_ability_psychology"].tags,
            ("source_psychology_interest_ability",),
        )
        self.assertEqual(
            by_id["uranus_sq_interest_ability_numerology"].tags,
            ("source_numerology_interest_ability",),
        )
        self.assertEqual(
            by_id["uranus_sq_interest_ability_astrology"].tags,
            ("source_astrology_interest_ability",),
        )
        self.assertEqual(by_id["uranus_sq_claircognizance"].tags, ("source_claircognizance",))
        self.assertEqual(by_id["uranus_sq_sense_of_humor"].tags, ("sense_of_humor",))
        persuasion = by_id["uranus_sq_piercing_persuasiveness_madman_framing"]
        self.assertEqual(persuasion.tags, ("persuasion",))
        self.assertIn("madman", persuasion.text.lower())
        self.assertIn("not a psychiatric diagnosis", persuasion.text.lower())

        freak = by_id["uranus_sq_branch_mercury_freak_or_professional_manipulator"]
        self.assertTrue(freak.unresolved)
        self.assertEqual(freak.activation_condition, "strength_unresolved")
        self.assertIn("if the mercury side dominates", freak.text.lower())
        self.assertNotIn("persuasion", freak.tags)
        self.assertNotIn(
            "persuasion",
            by_id["uranus_sq_branch_mercury_speech_insensitive_to_interlocutor"].tags,
        )
        self.assertNotIn(
            "argumentation",
            by_id["uranus_sq_branch_mercury_speech_insensitive_to_interlocutor"].tags,
        )
        self.assertNotIn(
            "debate",
            by_id["uranus_sq_branch_mercury_speech_insensitive_to_interlocutor"].tags,
        )
        blunt = by_id["uranus_sq_branch_uranus_blunt_truth_without_regard_for_consequences"]
        self.assertEqual(blunt.tags, ("blunt_truth_without_regard_for_consequences",))
        self.assertNotIn("blunt_truth_speech", blunt.tags)
        self.assertNotIn("argumentation", blunt.tags)
        self.assertNotIn("debate", blunt.tags)
        research = by_id["uranus_sq_branch_uranus_independent_research"]
        self.assertEqual(research.tags, ("independent_research",))
        self.assertNotIn("analytical_thinking", research.tags)
        skept = by_id["uranus_sq_branch_uranus_skeptical_questioning"]
        self.assertEqual(skept.tags, ("skeptical_questioning",))
        self.assertNotIn("evidence_requirement", skept.tags)
        self.assertEqual(by_id["uranus_sq_branch_uranus_believes_no_one"].tags, ("believes_no_one",))
        self.assertNotIn("distrust", by_id["uranus_sq_branch_uranus_believes_no_one"].tags)

    def test_opposition_core_and_common_atoms(self):
        by_id = {item.id: item for item in URANUS_OPPOSITION}
        self.assertEqual(
            by_id["uranus_opp_ordinary_learning_vs_uranian_creative_detachment_conflict"].tags,
            ("ordinary_learning_vs_uranian_creative_detachment_conflict",),
        )
        osc = by_id["uranus_opp_ordinary_vs_transcendent_thinking_oscillation"]
        self.assertEqual(osc.tags, ("ordinary_vs_transcendent_thinking_oscillation",))
        self.assertNotIn("genius", osc.tags)
        self.assertNotIn("fast_thinking", osc.tags)
        self.assertIn("source metaphorical", osc.text.lower())
        self.assertEqual(by_id["uranus_opp_technical_talents"].tags, ("technical_ability",))
        self.assertEqual(
            by_id["uranus_opp_piercing_persuasiveness_madman_framing"].tags,
            ("persuasion",),
        )
        self.assertNotIn("driving_ability", by_id["uranus_opp_driving_accident_risk"].tags)
        self.assertNotIn(
            "fast_thinking",
            by_id["uranus_opp_fast_sometimes_disfluent_speech"].tags,
        )
        self.assertEqual(by_id["uranus_opp_source_adhd_association"].tags, ("source_adhd_association",))
        self.assertFalse(any(item.unresolved for item in URANUS_OPPOSITION))
        self.assertFalse(any("branch_" in item.id and "wins" in item.id for item in URANUS_OPPOSITION))
        self.assertFalse(any(item.activation_condition == "strength_unresolved" for item in URANUS_OPPOSITION))


class AspectBatchC8ActivationTests(unittest.TestCase):
    def test_square_activates_only_square_pack_with_unresolved_branches(self):
        profile = _synthetic_uranus("square")
        self.assertEqual(profile.coverage.status, "complete")
        self.assertIn("aspect:square_Uranus", profile.coverage.covered_factors)
        self.assertEqual(_ids(profile.aspect_facts), _ids(URANUS_SQUARE))
        self.assertTrue(all(item.factor_key == "square_Uranus" for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("uranus_cj_") for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("uranus_opp_") for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("uranus_harm_") for item in profile.aspect_facts))
        resolved = {item.id for item in profile.aspect_facts if not item.unresolved}
        self.assertEqual(resolved, _ids(URANUS_SQUARE_COMMON))
        unresolved = _ids(profile.conditional_unresolved)
        self.assertTrue(_ids(URANUS_SQUARE_MERCURY_WINS).issubset(unresolved))
        self.assertTrue(_ids(URANUS_SQUARE_URANUS_WINS).issubset(unresolved))
        branch_ids = _ids(URANUS_SQUARE_MERCURY_WINS) | _ids(URANUS_SQUARE_URANUS_WINS)
        self.assertTrue(branch_ids.isdisjoint(resolved))
        self.assertTrue(
            any("if the mercury side dominates" in item.text.lower() for item in profile.conditional_unresolved)
        )
        self.assertTrue(
            any("if the uranus side dominates" in item.text.lower() for item in profile.conditional_unresolved)
        )
        all_facts = list(profile.aspect_facts) + list(profile.conditional_unresolved)
        for signal in detect_repeated_signals(all_facts):
            for fact_id in signal.fact_ids:
                fact = next(item for item in all_facts if item.id == fact_id)
                self.assertFalse(fact.unresolved, signal)
        self.assertEqual(
            detect_repeated_signals([item for item in profile.aspect_facts if not item.unresolved]),
            [],
        )

    def test_opposition_activates_only_opposition_pack(self):
        profile = _synthetic_uranus("opposition")
        self.assertEqual(profile.coverage.status, "complete")
        self.assertIn("aspect:opposition_Uranus", profile.coverage.covered_factors)
        self.assertEqual(_ids(profile.aspect_facts), _ids(URANUS_OPPOSITION))
        self.assertTrue(all(item.factor_key == "opposition_Uranus" for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("uranus_sq_") for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("uranus_cj_") for item in profile.aspect_facts))
        self.assertFalse(any(item.id.startswith("uranus_harm_") for item in profile.aspect_facts))
        self.assertTrue(all(not item.unresolved for item in profile.aspect_facts))
        self.assertEqual(_ids(profile.conditional_unresolved) & _ids(URANUS_OPPOSITION), set())
        self.assertEqual(
            detect_repeated_signals([item for item in profile.aspect_facts if not item.unresolved]),
            [],
        )

    def test_conjunction_and_harmonious_remain_separate(self):
        conjunction = _synthetic_uranus("conjunction")
        trine = _synthetic_uranus("trine")
        sextile = _synthetic_uranus("sextile")
        self.assertTrue(all(item.factor_key == "conjunction_Uranus" for item in conjunction.aspect_facts))
        self.assertFalse(any(item.id.startswith("uranus_sq_") for item in conjunction.aspect_facts))
        self.assertFalse(any(item.id.startswith("uranus_opp_") for item in conjunction.aspect_facts))
        self.assertEqual(_ids(conjunction.aspect_facts), _ids(URANUS_CONJUNCTION))
        self.assertTrue(all(item.factor_key == "trine_Uranus" for item in trine.aspect_facts))
        self.assertTrue(all(item.factor_key == "sextile_Uranus" for item in sextile.aspect_facts))
        self.assertEqual(_ids(trine.aspect_facts), _ids(URANUS_HARMONIOUS))
        self.assertFalse(any(item.id.startswith("uranus_sq_") for item in trine.aspect_facts))
        self.assertFalse(any(item.id.startswith("uranus_opp_") for item in sextile.aspect_facts))

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
        self.assertIn("square_Uranus", SUPPORTED_ASPECT_KEYS)
        self.assertIn("opposition_Uranus", SUPPORTED_ASPECT_KEYS)


class AspectBatchC8RegressionTests(unittest.TestCase):
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
                    any(item.factor_key in {"square_Uranus", "opposition_Uranus"} for item in profile.aspect_facts)
                )

    def test_andrey_keeps_trine_uranus_only(self):
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
        uranus = [item for item in andrey.aspect_facts if "Uranus" in item.factor_key]
        self.assertTrue(uranus)
        self.assertTrue(all(item.factor_key == "trine_Uranus" for item in uranus))
        self.assertFalse(any(item.id.startswith("uranus_sq_") for item in andrey.aspect_facts))
        self.assertFalse(any(item.id.startswith("uranus_opp_") for item in andrey.aspect_facts))
        tech = next(s for s in andrey.repeated_signals if s.signal == "technical_ability")
        self.assertIn("aspect:trine_Uranus", tech.sources)
        self.assertNotIn("aspect:square_Uranus", tech.sources)
        self.assertNotIn("aspect:opposition_Uranus", tech.sources)

    def test_milka_unchanged(self):
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
