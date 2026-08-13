"""Tests for Mercury sign source parity (12/12 dual-source)."""

from __future__ import annotations

import unittest
from collections import Counter
from datetime import date, time

from app.schemas.mercury_source_profile import MercurySourceProfileRequest
from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_source_knowledge import (
    ALL_SOURCE_FACTS,
    LEO_AFFLICTED,
    LEO_GENERAL,
    LEO_LESSON7,
    REF_LEO_BIO,
    REF_LEO_L7,
    REF_SAGITTARIUS,
    REF_SAGITTARIUS_BIO,
    REF_TAURUS,
    REF_TAURUS_BIO,
    SAGITTARIUS_AFFLICTED,
    SAGITTARIUS_BIOASTROLOGY,
    SAGITTARIUS_GENERAL,
    SUPPORTED_SIGN_KEYS,
    TAURUS_AFFLICTED,
    TAURUS_BIOASTROLOGY,
    TAURUS_GENERAL,
)
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
    detect_repeated_signals,
)


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


def _sign_refs(sign: str) -> set[str]:
    return {
        item.source_reference
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "sign" and item.factor_key == sign
    }


def _dual_source_signs() -> set[str]:
    dual = set()
    for sign in SUPPORTED_SIGN_KEYS:
        refs = _sign_refs(sign)
        has_l7 = any(ref.startswith("lesson7_") for ref in refs)
        has_bio = any(ref.startswith("bioastrology_") for ref in refs)
        if has_l7 and has_bio:
            dual.add(sign)
    return dual


class LeoLesson7ParityTests(unittest.TestCase):
    def test_leo_contains_lesson7_and_bio_refs(self):
        self.assertEqual(_sign_refs("Leo"), {REF_LEO_L7, REF_LEO_BIO})
        self.assertTrue(all(item.source_reference == REF_LEO_L7 for item in LEO_LESSON7))
        self.assertTrue(
            all(item.source_reference == REF_LEO_BIO for item in LEO_GENERAL + LEO_AFFLICTED)
        )
        self.assertIn("leo_l7_monologue_thinking", _ids(LEO_LESSON7))
        self.assertIn("leo_l7_lying_source_claim", _ids(LEO_LESSON7))
        self.assertIn("leo_l7_transforms_others_idea_into_own", _ids(LEO_LESSON7))
        self.assertGreater(len(LEO_LESSON7), 0)
        self.assertGreater(len(LEO_GENERAL), 0)

    def test_leo_l7_does_not_sanitize_harsh_claims(self):
        lying = next(item for item in LEO_LESSON7 if item.id == "leo_l7_lying_source_claim")
        dust = next(item for item in LEO_LESSON7 if item.id == "leo_l7_throwing_dust_in_eyes")
        appearance = next(
            item
            for item in LEO_LESSON7
            if item.id == "leo_l7_prepared_phrases_appearance_of_competence"
        )
        appropriation = next(
            item for item in LEO_LESSON7 if item.id == "leo_l7_transforms_others_idea_into_own"
        )
        self.assertEqual(lying.tags, ("lying",))
        self.assertEqual(dust.tags, ("dust_in_eyes",))
        self.assertEqual(appearance.tags, ("appearance_of_competence",))
        self.assertEqual(appropriation.tags, ("idea_appropriation",))
        self.assertNotIn("confidence", lying.tags)
        self.assertNotIn("presentation", dust.tags)
        self.assertNotIn("creative", appropriation.tags)

    def test_leo_dual_source_does_not_create_false_repeat(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=False,
                mercury_sign="Leo",
                mercury_element="fire",
                mercury_motion="direct",
                mercury_house=None,
                aspects=[],
            )
        )
        self.assertGreater(len(profile.sign_facts), len(LEO_GENERAL))
        for signal in detect_repeated_signals(profile.sign_facts):
            sign_sources = [src for src in signal.sources if src.startswith("sign:")]
            self.assertLessEqual(len(sign_sources), 1, signal)

    def test_leo_afflicted_still_hard_aspected_only(self):
        soft = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=False,
                mercury_sign="Leo",
                mercury_element="fire",
                mercury_motion="direct",
                mercury_house=None,
                aspects=[MercuryAspect(planet="Jupiter", type="trine", orb_deg=1.0)],
            )
        )
        hard = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=False,
                mercury_sign="Leo",
                mercury_element="fire",
                mercury_motion="direct",
                mercury_house=None,
                aspects=[MercuryAspect(planet="Pluto", type="square", orb_deg=1.0)],
            )
        )
        self.assertNotIn("leo_afflicted_lying_distortion", _ids(soft.sign_facts))
        self.assertIn("leo_afflicted_lying_distortion", _ids(hard.sign_facts))
        self.assertIn("leo_l7_lying_source_claim", _ids(soft.sign_facts))


class TaurusSagBioParityTests(unittest.TestCase):
    def test_taurus_contains_lesson7_and_bio_refs(self):
        self.assertEqual(_sign_refs("Taurus"), {REF_TAURUS, REF_TAURUS_BIO})
        self.assertTrue(all(item.source_reference == REF_TAURUS for item in TAURUS_GENERAL))
        self.assertTrue(
            all(
                item.source_reference == REF_TAURUS_BIO
                for item in TAURUS_BIOASTROLOGY + TAURUS_AFFLICTED
            )
        )
        self.assertEqual(len(TAURUS_GENERAL), 23)
        self.assertEqual(len(TAURUS_BIOASTROLOGY), 12)
        self.assertEqual(len(TAURUS_AFFLICTED), 3)

    def test_sagittarius_contains_lesson7_and_bio_refs(self):
        self.assertEqual(_sign_refs("Sagittarius"), {REF_SAGITTARIUS, REF_SAGITTARIUS_BIO})
        self.assertTrue(all(item.source_reference == REF_SAGITTARIUS for item in SAGITTARIUS_GENERAL))
        self.assertTrue(
            all(
                item.source_reference == REF_SAGITTARIUS_BIO
                for item in SAGITTARIUS_BIOASTROLOGY + SAGITTARIUS_AFFLICTED
            )
        )
        self.assertEqual(len(SAGITTARIUS_GENERAL), 24)
        self.assertEqual(len(SAGITTARIUS_BIOASTROLOGY), 25)
        self.assertEqual(len(SAGITTARIUS_AFFLICTED), 9)

    def test_taurus_narrow_tags_not_polluted(self):
        by_id = {item.id: item for item in TAURUS_BIOASTROLOGY + TAURUS_AFFLICTED}
        self.assertEqual(by_id["taurus_bio_vocal_artistic_aptitude"].tags, ("vocal_artistic_aptitude",))
        self.assertEqual(by_id["taurus_bio_beautiful_voice"].tags, ("beautiful_voice",))
        self.assertEqual(by_id["taurus_bio_beautiful_speech"].tags, ("beautiful_speech",))
        self.assertEqual(by_id["taurus_bio_beautiful_handwriting"].tags, ("beautiful_handwriting",))
        self.assertEqual(by_id["taurus_bio_strong_attention"].tags, ("strong_attention",))
        self.assertEqual(
            by_id["taurus_bio_slowness_dispute_disadvantage"].tags,
            ("slowness_dispute_disadvantage",),
        )
        self.assertEqual(
            by_id["taurus_bio_money_learning_motivation"].tags,
            ("money_learning_motivation",),
        )
        for item in TAURUS_BIOASTROLOGY:
            self.assertNotIn("persuasion", item.tags)
            self.assertNotIn("oratory", item.tags)

    def test_sagittarius_teaching_atoms_remain_distinct(self):
        l7_teach = next(item for item in SAGITTARIUS_GENERAL if item.id == "sag_tends_to_teach_lecture")
        bio_aptitude = next(
            item
            for item in SAGITTARIUS_BIOASTROLOGY
            if item.id == "sag_bio_teacher_instructor_quality"
        )
        bio_learn = next(
            item
            for item in SAGITTARIUS_BIOASTROLOGY
            if item.id == "sag_bio_learning_through_teaching"
        )
        self.assertEqual(l7_teach.tags, ("teaching",))
        self.assertEqual(bio_aptitude.tags, ("teacher_instructor_quality",))
        self.assertEqual(bio_learn.tags, ("learning_through_teaching",))

    def test_sagittarius_motivation_not_prestige_orientation(self):
        for item in SAGITTARIUS_BIOASTROLOGY:
            if "motivation" in item.id:
                self.assertNotIn("prestige_orientation", item.tags)

    def test_taurus_afflicted_hard_aspected_only(self):
        soft = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=False,
                mercury_sign="Taurus",
                mercury_element="earth",
                mercury_motion="direct",
                mercury_house=None,
                aspects=[MercuryAspect(planet="Jupiter", type="trine", orb_deg=1.0)],
            )
        )
        hard_sq = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=False,
                mercury_sign="Taurus",
                mercury_element="earth",
                mercury_motion="direct",
                mercury_house=None,
                aspects=[MercuryAspect(planet="Mars", type="square", orb_deg=1.0)],
            )
        )
        hard_opp = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=False,
                mercury_sign="Taurus",
                mercury_element="earth",
                mercury_motion="direct",
                mercury_house=None,
                aspects=[MercuryAspect(planet="Saturn", type="opposition", orb_deg=1.0)],
            )
        )
        afflicted_id = "taurus_bio_afflicted_cognitive_sluggishness"
        self.assertNotIn(afflicted_id, _ids(soft.sign_facts))
        self.assertIn(afflicted_id, _ids(hard_sq.sign_facts))
        self.assertIn(afflicted_id, _ids(hard_opp.sign_facts))

    def test_sagittarius_afflicted_hard_aspected_only(self):
        soft = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=False,
                mercury_sign="Sagittarius",
                mercury_element="fire",
                mercury_motion="direct",
                mercury_house=None,
                aspects=[MercuryAspect(planet="Venus", type="sextile", orb_deg=1.0)],
            )
        )
        hard = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=False,
                mercury_sign="Sagittarius",
                mercury_element="fire",
                mercury_motion="direct",
                mercury_house=None,
                aspects=[MercuryAspect(planet="Pluto", type="opposition", orb_deg=1.0)],
            )
        )
        afflicted_id = "sag_bio_afflicted_accuracy_problems"
        self.assertNotIn(afflicted_id, _ids(soft.sign_facts))
        self.assertIn(afflicted_id, _ids(hard.sign_facts))
        # Baseline L7 precision risk remains active without hard aspect.
        self.assertIn("sag_calculation_errors_neglect_precision", _ids(soft.sign_facts))

    def test_same_sign_dual_source_cannot_create_repeated_signal(self):
        for sign, element in (("Taurus", "earth"), ("Sagittarius", "fire"), ("Leo", "fire")):
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


class SourceParityCompleteTests(unittest.TestCase):
    def test_all_ids_unique(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])

    def test_exactly_twelve_of_twelve_dual_source(self):
        self.assertEqual(len(SUPPORTED_SIGN_KEYS), 12)
        dual = _dual_source_signs()
        self.assertEqual(dual, set(SUPPORTED_SIGN_KEYS))
        self.assertEqual(len(dual), 12)
        self.assertEqual(_sign_refs("Leo"), {REF_LEO_L7, REF_LEO_BIO})
        self.assertEqual(_sign_refs("Taurus"), {REF_TAURUS, REF_TAURUS_BIO})
        self.assertEqual(_sign_refs("Sagittarius"), {REF_SAGITTARIUS, REF_SAGITTARIUS_BIO})


class ParityRegressionTests(unittest.TestCase):
    def test_golden_coverage_unchanged(self):
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

    def test_andrey_still_partial(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Cancer",
                mercury_element="water",
                mercury_motion="direct",
                mercury_house=5,
                aspects=[
                    MercuryAspect(planet="Uranus", type="trine", orb_deg=1.0),
                    MercuryAspect(planet="Pluto", type="square", orb_deg=1.0),
                ],
            )
        )
        self.assertEqual(profile.coverage.status, "partial")
        self.assertIn("house:5", profile.coverage.missing_factors)
        self.assertIn("aspect:trine_Uranus", profile.coverage.missing_factors)

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
        self.assertIn("sign:Pisces", profile.coverage.covered_factors)


if __name__ == "__main__":
    unittest.main()
