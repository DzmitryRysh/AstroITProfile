import unittest
from datetime import date, time

from app.core.app import create_app
from app.schemas.mercury_source_profile import MercurySourceProfileRequest
from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
    is_hard_aspected,
)

AVDEY = MercurySourceProfileRequest(
    birth_date=date(1986, 7, 14),
    birth_time=time(7, 10),
    birth_place="Simferopol, Ukraine",
)


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


def _signal(profile, name: str):
    return next((item for item in profile.repeated_signals if item.signal == name), None)


def _avdey_like_with_moon() -> MercurySourceFactors:
    """Synthetic factors matching Avdey plus an in-orb Mercury–Moon sextile."""
    return MercurySourceFactors(
        birth_time_known=True,
        mercury_sign="Leo",
        mercury_element="fire",
        mercury_motion="retrograde",
        mercury_house=1,
        aspects=[
            MercuryAspect(planet="Pluto", type="square", orb_deg=1.17),
            MercuryAspect(planet="Saturn", type="trine", orb_deg=2.19),
            MercuryAspect(planet="Moon", type="sextile", orb_deg=1.0),
        ],
    )


class MercuryHardAspectHelperTests(unittest.TestCase):
    def test_square_marks_hard_aspected(self):
        self.assertTrue(
            is_hard_aspected([MercuryAspect(planet="Pluto", type="square", orb_deg=1.0)])
        )

    def test_trine_alone_is_not_hard_aspected(self):
        self.assertFalse(
            is_hard_aspected([MercuryAspect(planet="Saturn", type="trine", orb_deg=1.0)])
        )


class AvdeyGoldenCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = build_mercury_source_profile(AVDEY)

    def test_calculated_mercury_basics(self):
        calc = self.profile.calculated
        self.assertEqual(calc.mercury_sign, "Leo")
        self.assertEqual(calc.mercury_house, 1)
        self.assertEqual(calc.mercury_motion, "retrograde")
        self.assertTrue(calc.hard_aspected)

    def test_required_aspects_present(self):
        """Engine truth for Avdey: square Pluto + trine Saturn; Moon at ~66.8° is out of sextile orb."""
        pairs = {(item.type, item.planet) for item in self.profile.calculated.aspects}
        self.assertIn(("square", "Pluto"), pairs)
        self.assertIn(("trine", "Saturn"), pairs)
        self.assertNotIn(("sextile", "Moon"), pairs)

    def test_all_four_source_layers_present(self):
        self.assertGreater(len(self.profile.sign_facts), 0)
        self.assertGreater(len(self.profile.house_facts), 0)
        self.assertGreater(len(self.profile.motion_facts), 0)
        self.assertGreater(len(self.profile.aspect_facts), 0)

    def test_retrograde_is_visible_as_first_class_facts(self):
        self.assertTrue(all(item.factor_key == "retrograde" for item in self.profile.motion_facts))
        self.assertIn("rx_works_more_inwardly", _ids(self.profile.motion_facts))
        self.assertIn("rx_nonstandard_solutions", _ids(self.profile.motion_facts))

    def test_hard_square_activates_afflicted_leo_facts(self):
        ids = _ids(self.profile.sign_facts)
        self.assertIn("leo_afflicted_appearance_of_competence", ids)
        self.assertIn("leo_afflicted_lying_distortion", ids)
        self.assertIn("leo_afflicted_putting_on_a_show", ids)
        self.assertIn("leo_afflicted_extreme_stubbornness", ids)

    def test_afflicted_leo_not_active_without_hard_aspect(self):
        factors = MercurySourceFactors(
            birth_time_known=True,
            mercury_sign="Leo",
            mercury_element="fire",
            mercury_motion="direct",
            mercury_house=1,
            aspects=[MercuryAspect(planet="Saturn", type="trine", orb_deg=1.0)],
        )
        profile = build_source_profile_from_factors(factors)
        ids = _ids(profile.sign_facts)
        self.assertNotIn("leo_afflicted_lying_distortion", ids)
        self.assertIn("leo_strong_debate_potential", ids)

    def test_strong_memory_not_repeated_without_moon(self):
        # Only Saturn contributes memory for live Avdey; repeated signal needs >=2 factor keys.
        self.assertIsNone(_signal(self.profile, "strong_memory"))

    def test_analytical_or_technical_pluto_and_saturn(self):
        signal = _signal(self.profile, "analytical_or_technical")
        self.assertIsNotNone(signal)
        self.assertIn("square_Pluto", signal.sources)
        self.assertIn("trine_Saturn", signal.sources)

    def test_debate_argumentation_leo_pluto_saturn(self):
        signal = _signal(self.profile, "debate_argumentation")
        self.assertIsNotNone(signal)
        self.assertIn("Leo", signal.sources)
        self.assertIn("square_Pluto", signal.sources)
        self.assertIn("trine_Saturn", signal.sources)

    def test_nonstandard_thinking_includes_leo_rx_pluto(self):
        signal = _signal(self.profile, "nonstandard_thinking_learning")
        self.assertIsNotNone(signal)
        self.assertIn("Leo", signal.sources)
        self.assertIn("retrograde", signal.sources)
        self.assertIn("square_Pluto", signal.sources)

    def test_sales_presentation_includes_leo_and_house_1(self):
        signal = _signal(self.profile, "sales_persuasive_presentation")
        self.assertIsNotNone(signal)
        self.assertIn("Leo", signal.sources)
        self.assertIn("1", signal.sources)

    def test_source_references_present(self):
        all_facts = (
            self.profile.sign_facts
            + self.profile.house_facts
            + self.profile.motion_facts
            + self.profile.aspect_facts
        )
        self.assertTrue(all(item.source_reference for item in all_facts))
        refs = {item.source_reference for item in all_facts}
        self.assertIn("bioastrology_mercury_leo", refs)
        self.assertIn("bioastrology_mercury_house_1", refs)
        self.assertIn("methodology_mercury_retrograde", refs)
        self.assertIn("bioastrology_mercury_pluto_square", refs)
        self.assertIn("bioastrology_mercury_saturn_harmonious", refs)
        self.assertNotIn("bioastrology_mercury_moon_harmonious", refs)

    def test_source_fidelity_leo_risks_preserved(self):
        ids = _ids(self.profile.sign_facts)
        superficial = next(
            item
            for item in self.profile.sign_facts
            if item.id == "leo_risk_intellectual_superficiality"
        )
        self.assertIn("superficiality", superficial.text.lower())
        self.assertIn("primitiveness", superficial.text.lower())
        self.assertNotIn("insufficient depth", superficial.text.lower())
        lying = next(
            item for item in self.profile.sign_facts if item.id == "leo_afflicted_lying_distortion"
        )
        self.assertIn("lying", lying.text.lower())
        self.assertIn("distortion", lying.text.lower())
        self.assertNotIn("source-backed risk signal", lying.text.lower())
        self.assertIn("leo_afflicted_appearance_of_competence", ids)
        self.assertIn("leo_afflicted_extreme_stubbornness", ids)

    def test_source_fidelity_house_1_professions(self):
        work = next(
            item for item in self.profile.house_facts if item.id == "h1_support_intellectual_work"
        )
        text = work.text.lower()
        self.assertIn("intellectual", text)
        self.assertIn("transport", text)
        self.assertNotIn("information-oriented", text)
        talk = next(
            item
            for item in self.profile.house_facts
            if item.id == "h1_talkative_or_writing_tendency"
        )
        self.assertIn("talkativeness", talk.text.lower())
        self.assertIn("writing", talk.text.lower())
        self.assertNotIn("depending on chart context", talk.text.lower())

    def test_source_fidelity_pluto_common_toxic_and_razor(self):
        by_id = {item.id: item for item in self.profile.aspect_facts}
        toxic = by_id["pluto_sq_conflictual_communication"].text.lower()
        self.assertIn("toxic", toxic)
        self.assertIn("conflictual", toxic)
        sharp = by_id["pluto_sq_extremely_sharp_speech"].text.lower()
        self.assertIn("razor", sharp)
        self.assertTrue("poisonous" in sharp or "venomous" in sharp)
        self.assertIn("hurt", sharp)
        self.assertIn("pluto_sq_words_can_hurt", by_id)

    def test_pluto_strength_branches_both_unresolved(self):
        unresolved = [
            item for item in self.profile.conditional_unresolved if item.unresolved
        ]
        merc_ids = {
            item.id
            for item in unresolved
            if item.id.startswith("pluto_sq_branch_mercury_stronger")
        }
        pluto_ids = {
            item.id
            for item in unresolved
            if item.id.startswith("pluto_sq_branch_pluto_stronger")
        }
        self.assertGreaterEqual(len(merc_ids), 4)
        self.assertGreaterEqual(len(pluto_ids), 3)
        self.assertTrue(
            all(item.activation_condition == "pluto_strength_unresolved" for item in unresolved)
        )
        texts = " ".join(item.text.lower() for item in unresolved)
        self.assertIn("primitive", texts)
        self.assertIn("quarrel", texts)
        self.assertIn("damaged", texts)
        self.assertIn("pseudo-philosophizing", texts)
        self.assertIn("super-will", texts)
        self.assertIn("energetic depth", texts)
        self.assertIn("penetrates mercury", texts)
        self.assertNotIn("investigative force", texts)
        self.assertNotIn("overwhelm mercury", texts)
        self.assertNotIn("destructive speech dynamics", texts)

    def test_no_silent_pluto_strength_selection(self):
        unresolved = self.profile.conditional_unresolved
        self.assertTrue(any("when mercury dominates" in item.text.lower() for item in unresolved))
        self.assertTrue(any("when pluto dominates" in item.text.lower() for item in unresolved))
        # Common Pluto facts remain active outside unresolved branches.
        common_ids = _ids(
            [item for item in self.profile.aspect_facts if not item.unresolved]
        )
        for required in (
            "pluto_sq_conflictual_communication",
            "pluto_sq_aggressive_driving_accident_risk",
            "pluto_sq_neighbors_siblings_problems",
            "pluto_sq_trip_crises",
            "pluto_sq_dangerous_curiosity",
            "pluto_sq_pessimistic_fatalistic_tone",
            "pluto_sq_extremely_sharp_speech",
            "pluto_sq_words_can_hurt",
            "pluto_sq_sarcasm",
            "pluto_sq_strong_sense_of_humor",
            "pluto_sq_destroy_dig_defeat_through_speech",
            "pluto_sq_strong_persuasiveness",
            "pluto_sq_strong_insight",
            "pluto_sq_powerful_words",
            "pluto_sq_speak_uncomfortable_truth",
            "pluto_sq_debate_ability",
            "pluto_sq_find_strong_arguments",
            "pluto_sq_technical_talent",
            "pluto_sq_diagnose_problems",
            "pluto_sq_identify_vulnerabilities",
            "pluto_sq_analytical_ability",
            "pluto_sq_psychological_insight",
            "pluto_sq_penetrate_hack_systems",
            "pluto_sq_understand_weaknesses_in_reasoning",
            "pluto_sq_fast_learning_through_criticism",
        ):
            self.assertIn(required, common_ids)

    def test_moon_not_activated_for_live_avdey(self):
        aspect_keys = {item.factor_key for item in self.profile.aspect_facts}
        self.assertNotIn("sextile_Moon", aspect_keys)
        refs = {
            item.source_reference
            for item in (
                self.profile.sign_facts
                + self.profile.house_facts
                + self.profile.motion_facts
                + self.profile.aspect_facts
            )
        }
        self.assertNotIn("bioastrology_mercury_moon_harmonious", refs)

    def test_contrasting_superficiality_and_depth_preserved(self):
        ids = _ids(self.profile.sign_facts) | _ids(self.profile.aspect_facts)
        self.assertIn("leo_risk_intellectual_superficiality", ids)
        self.assertIn("pluto_sq_identify_vulnerabilities", ids)
        self.assertIn("saturn_tr_analytical_ability", ids)
        pairs = {(item.tag_a, item.tag_b) for item in self.profile.contrasting_signals}
        self.assertIn(("superficiality", "depth"), pairs)

    def test_coverage_complete_for_engine_factors(self):
        self.assertEqual(self.profile.coverage.status, "complete")
        self.assertEqual(self.profile.coverage.missing_factors, [])

    def test_unsupported_sign_returns_partial_coverage(self):
        factors = MercurySourceFactors(
            birth_time_known=True,
            mercury_sign="Virgo",
            mercury_element="earth",
            mercury_motion="direct",
            mercury_house=3,
            aspects=[MercuryAspect(planet="Mars", type="square", orb_deg=2.0)],
        )
        profile = build_source_profile_from_factors(factors)
        self.assertEqual(profile.coverage.status, "partial")
        self.assertIn("sign:Virgo", profile.coverage.missing_factors)
        self.assertIn("house:3", profile.coverage.missing_factors)
        self.assertIn("aspect:square_Mars", profile.coverage.missing_factors)
        self.assertEqual(profile.sign_facts, [])
        self.assertTrue(any("Virgo" in item for item in profile.limitations))

    def test_route_registered(self):
        app = create_app()
        paths = {getattr(route, "path", None) for route in app.routes}
        self.assertIn("/api/v1/mercury-source-profile", paths)
        self.assertIn("/api/v1/mercury-work-profile", paths)


class MoonSextileSourcePackTests(unittest.TestCase):
    """Moon harmonious pack is implemented; Avdey's live chart is outside orb."""

    @classmethod
    def setUpClass(cls):
        cls.profile = build_source_profile_from_factors(_avdey_like_with_moon())

    def test_moon_facts_and_reference_present(self):
        moon_facts = [item for item in self.profile.aspect_facts if item.factor_key == "sextile_Moon"]
        self.assertGreater(len(moon_facts), 0)
        self.assertTrue(
            all(item.source_reference == "bioastrology_mercury_moon_harmonious" for item in moon_facts)
        )
        self.assertIn("moon_sx_strong_sticky_memory", _ids(moon_facts))

    def test_strong_memory_repeated_signal_saturn_and_moon(self):
        signal = _signal(self.profile, "strong_memory")
        self.assertIsNotNone(signal)
        self.assertGreaterEqual(signal.source_count, 2)
        self.assertIn("trine_Saturn", signal.sources)
        self.assertIn("sextile_Moon", signal.sources)

    def test_insight_repeated_signal_pluto_and_moon(self):
        signal = _signal(self.profile, "insight_seeing_not_obvious")
        self.assertIsNotNone(signal)
        self.assertIn("square_Pluto", signal.sources)
        self.assertIn("sextile_Moon", signal.sources)


if __name__ == "__main__":
    unittest.main()
