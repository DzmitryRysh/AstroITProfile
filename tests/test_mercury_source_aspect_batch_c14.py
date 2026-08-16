"""Tests for Mercury Source Profile v2 — Aspect Batch C14 (Pluto completion)."""

from __future__ import annotations

import subprocess
import unittest
from collections import Counter
from datetime import date, time
from pathlib import Path

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
from app.services.mercury_source_knowledge_c14_aspects import (
    PLUTO_CONJUNCTION,
    PLUTO_CONJUNCTION_UNIQUE,
    PLUTO_OPPOSITION,
    PLUTO_OPPOSITION_UNIQUE,
    REF_PLUTO_CJ,
    REF_PLUTO_OPP,
)
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
    detect_repeated_signals,
)

ENGINE_ASPECT_SLOTS = 45
REPO_ROOT = Path(__file__).resolve().parents[1]
PLUTO_PUBLIC_FAMILY = {
    "conjunction_Pluto",
    "sextile_Pluto",
    "square_Pluto",
    "trine_Pluto",
    "opposition_Pluto",
}
NEPTUNE_PUBLIC_FAMILY = {
    "conjunction_Neptune",
    "sextile_Neptune",
    "square_Neptune",
    "trine_Neptune",
    "opposition_Neptune",
}
RAW_UNSUPPORTED_IMPOSSIBLE = frozenset(
    {
        "sextile_Sun",
        "square_Sun",
        "trine_Sun",
        "opposition_Sun",
        "square_Venus",
        "trine_Venus",
        "opposition_Venus",
    }
)


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


def _synthetic_pluto(aspect_type: str, orb_deg: float = 2.0):
    return build_source_profile_from_factors(
        MercurySourceFactors(
            birth_time_known=True,
            mercury_sign="Virgo",
            mercury_element="earth",
            mercury_motion="direct",
            mercury_house=3,
            aspects=[MercuryAspect(planet="Pluto", type=aspect_type, orb_deg=orb_deg)],
        )
    )


class AspectBatchC14CoverageTests(unittest.TestCase):
    def test_supported_public_aspect_count_is_thirty_eight(self):
        self.assertEqual(len(SUPPORTED_ASPECT_KEYS), 38)
        self.assertEqual(ENGINE_ASPECT_SLOTS - len(SUPPORTED_ASPECT_KEYS), 7)
        self.assertEqual(len(_canonical_aspect_packs()), 31)
        self.assertEqual(len(ASPECT_PACK_ALIASES), 7)
        self.assertEqual(len(SUPPORTED_SIGN_KEYS), 12)
        self.assertEqual(len(SUPPORTED_HOUSE_KEYS), 12)
        self.assertTrue(PLUTO_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))
        self.assertTrue(NEPTUNE_PUBLIC_FAMILY.issubset(SUPPORTED_ASPECT_KEYS))

    def test_pluto_family_is_exactly_five_of_five(self):
        for key in PLUTO_PUBLIC_FAMILY:
            self.assertIn(key, SUPPORTED_ASPECT_KEYS)
            self.assertIn(key, REACHABLE_NATAL_ASPECT_KEYS)
        self.assertEqual(ASPECT_PACK_ALIASES["sextile_Pluto"], "trine_Pluto")
        self.assertNotIn("opposition_Pluto", ASPECT_PACK_ALIASES)
        self.assertNotIn("conjunction_Pluto", ASPECT_PACK_ALIASES)
        self.assertIn("opposition_Pluto", _canonical_aspect_packs())
        self.assertIn("conjunction_Pluto", _canonical_aspect_packs())

    def test_reachable_coverage_is_complete(self):
        summary = natal_aspect_reachability_summary(SUPPORTED_ASPECT_KEYS)
        self.assertEqual(summary["raw_total"], 45)
        self.assertEqual(summary["reachable_total"], 38)
        self.assertEqual(summary["supported_reachable"], 38)
        self.assertEqual(summary["missing_reachable"], 0)
        self.assertEqual(summary["impossible_total"], 7)
        self.assertEqual(summary["missing_reachable_keys"], frozenset())
        self.assertEqual(frozenset(SUPPORTED_ASPECT_KEYS), REACHABLE_NATAL_ASPECT_KEYS)
        self.assertEqual(RAW_UNSUPPORTED_IMPOSSIBLE, IMPOSSIBLE_NATAL_ASPECT_KEYS)
        self.assertTrue(RAW_UNSUPPORTED_IMPOSSIBLE.isdisjoint(SUPPORTED_ASPECT_KEYS))
        self.assertEqual(
            ENGINE_ASPECT_SLOTS - len(SUPPORTED_ASPECT_KEYS),
            len(IMPOSSIBLE_NATAL_ASPECT_KEYS),
        )

    def test_refs_and_pack_sizes(self):
        self.assertEqual(REF_PLUTO_OPP, "bioastrology_mercury_pluto_opposition")
        self.assertEqual(REF_PLUTO_CJ, "bioastrology_mercury_pluto_conjunction")
        self.assertTrue(all(item.source_reference == REF_PLUTO_OPP for item in PLUTO_OPPOSITION))
        self.assertTrue(all(item.source_reference == REF_PLUTO_CJ for item in PLUTO_CONJUNCTION))
        self.assertEqual(len(PLUTO_OPPOSITION_UNIQUE), 2)
        self.assertEqual(len(PLUTO_CONJUNCTION_UNIQUE), 2)
        self.assertEqual(len(PLUTO_OPPOSITION), 35)
        self.assertEqual(len(PLUTO_CONJUNCTION), 35)
        self.assertEqual(len(PLUTO_OPPOSITION) - len(PLUTO_OPPOSITION_UNIQUE), 33)

    def test_catalog_integrity_and_profile_unchanged(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])
        self.assertTrue(all(item.source_reference for item in ALL_SOURCE_FACTS))
        all_c14 = PLUTO_OPPOSITION + PLUTO_CONJUNCTION
        self.assertTrue(all(item.activation_condition is None for item in all_c14))
        self.assertTrue(all(not item.unresolved for item in all_c14))
        self.assertFalse(any(item.category == "compensation" for item in all_c14))
        self.assertFalse(any("celebrity" in item.id for item in all_c14))
        self.assertFalse(any("supergift" in item.id for item in all_c14))
        self.assertFalse(any("secondary_gain" in item.id for item in all_c14))
        self.assertEqual(len(REPEATED_SIGNAL_SPECS), 15)
        self.assertFalse(
            any(
                item.activation_condition == "pluto_strength_unresolved"
                for item in PLUTO_CONJUNCTION
            )
        )
        diff = subprocess.run(
            ["git", "diff", "--", "app/services/mercury_source_profile.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(diff.stdout, "", msg="mercury_source_profile.py must remain unchanged for C14")


class AspectBatchC14AtomTests(unittest.TestCase):
    def test_unique_opposition_and_conjunction_atoms(self):
        opp = {item.id: item for item in PLUTO_OPPOSITION}
        cj = {item.id: item for item in PLUTO_CONJUNCTION}
        self.assertIn("thinking_pluto_cold_war_source_metaphor", opp["plu_opp_thinking_pluto_cold_war_source_metaphor"].tags)
        self.assertIn(
            "learning_openness_omniscience_rejection_oscillation",
            opp["plu_opp_learning_openness_omniscience_rejection_oscillation"].tags,
        )
        self.assertIn(
            "thinking_pluto_full_absorption_source_metaphor",
            cj["plu_cj_thinking_pluto_full_absorption_source_metaphor"].tags,
        )
        self.assertIn(
            "resembles_square_pluto_stronger_source_relationship",
            cj["plu_cj_resembles_square_pluto_stronger_source_relationship"].tags,
        )
        self.assertTrue(_ids(PLUTO_OPPOSITION_UNIQUE).isdisjoint(_ids(PLUTO_CONJUNCTION)))
        self.assertTrue(_ids(PLUTO_CONJUNCTION_UNIQUE).isdisjoint(_ids(PLUTO_OPPOSITION)))

    def test_common_body_independent_and_tag_safety(self):
        opp_tags = _tags(PLUTO_OPPOSITION) - _tags(PLUTO_OPPOSITION_UNIQUE)
        cj_tags = _tags(PLUTO_CONJUNCTION) - _tags(PLUTO_CONJUNCTION_UNIQUE)
        self.assertEqual(opp_tags, cj_tags)
        by_opp = {item.id: item for item in PLUTO_OPPOSITION}
        toxic = by_opp["plu_opp_source_toxic_conflict_atmosphere_association"]
        self.assertIn("source or victim", toxic.text.lower())
        road = by_opp["plu_opp_source_road_accident_risk_association"]
        self.assertNotIn("driving_ability", road.tags)
        drive = by_opp["plu_opp_aggressive_driving_tendency_source_claim"]
        self.assertNotIn("driving_ability", drive.tags)
        manifest = by_opp["plu_opp_source_negative_thought_word_manifestation_association"]
        self.assertIn("not a claim that", manifest.text.lower())
        diag = by_opp["plu_opp_source_diagnostic_aptitude"]
        self.assertIn("not a medical", diag.text.lower())
        mind = by_opp["plu_opp_source_mind_hacking_metaphor"]
        self.assertIn("not literal mind control", mind.text.lower())
        self.assertEqual(by_opp["plu_opp_persuasion"].tags, ("persuasion",))
        self.assertEqual(by_opp["plu_opp_debate"].tags, ("debate",))
        self.assertEqual(by_opp["plu_opp_argumentation"].tags, ("argumentation",))
        self.assertEqual(by_opp["plu_opp_technical_ability"].tags, ("technical_ability",))
        self.assertEqual(by_opp["plu_opp_analytical_thinking"].tags, ("analytical_thinking",))
        self.assertEqual(by_opp["plu_opp_sense_of_humor"].tags, ("sense_of_humor",))
        self.assertEqual(by_opp["plu_opp_insight"].tags, ("insight",))
        self.assertNotIn("persuasion", by_opp["plu_opp_sharp_hurtful_speech_source_claim"].tags)


class AspectBatchC14ActivationTests(unittest.TestCase):
    def test_opposition_and_conjunction_activate_complete(self):
        opposition = _synthetic_pluto("opposition")
        conjunction = _synthetic_pluto("conjunction")
        self.assertEqual(opposition.coverage.status, "complete")
        self.assertEqual(conjunction.coverage.status, "complete")
        self.assertIn("aspect:opposition_Pluto", opposition.coverage.covered_factors)
        self.assertIn("aspect:conjunction_Pluto", conjunction.coverage.covered_factors)
        self.assertEqual(opposition.coverage.missing_factors, [])
        self.assertEqual(conjunction.coverage.missing_factors, [])
        self.assertTrue(_ids(PLUTO_OPPOSITION).issubset(_ids(opposition.aspect_facts)))
        self.assertTrue(_ids(PLUTO_CONJUNCTION).issubset(_ids(conjunction.aspect_facts)))
        self.assertTrue(_ids(PLUTO_CONJUNCTION).isdisjoint(_ids(opposition.aspect_facts)))
        self.assertTrue(_ids(PLUTO_OPPOSITION).isdisjoint(_ids(conjunction.aspect_facts)))
        self.assertFalse(any(item.id.startswith("pluto_sq_") for item in conjunction.aspect_facts))
        self.assertFalse(
            any(
                item.activation_condition == "pluto_strength_unresolved"
                for item in conjunction.conditional_unresolved
            )
        )

    def test_no_same_factor_self_repeat(self):
        for aspect_type, pack in (("opposition", PLUTO_OPPOSITION), ("conjunction", PLUTO_CONJUNCTION)):
            with self.subTest(aspect=aspect_type):
                profile = _synthetic_pluto(aspect_type)
                activated = [item for item in profile.aspect_facts if not item.unresolved]
                self.assertEqual(detect_repeated_signals(activated), [])
                self.assertTrue(_ids(pack).issubset(_ids(activated)))

    def test_synthetic_unknown_aspect_still_marks_partial(self):
        # After C14 there is no reachable unsupported aspect; synthetic probe remains
        # the only legitimate generic missing-aspect source-gap demonstration.
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
        self.assertIn("sign:Leo", profile.coverage.covered_factors)
        self.assertIn("house:1", profile.coverage.covered_factors)


class AspectBatchC14RegressionTests(unittest.TestCase):
    def test_golden_cases_and_pluto_conj_opp_presence(self):
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
                        a.planet == "Pluto" and a.type in {"conjunction", "opposition"}
                        for a in profile.calculated.aspects
                    )
                )
                self.assertFalse(
                    any(
                        item.factor_key in {"conjunction_Pluto", "opposition_Pluto"}
                        for item in profile.aspect_facts
                    )
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
