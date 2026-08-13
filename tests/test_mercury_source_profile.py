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

    def test_analytical_thinking_pluto_and_saturn(self):
        signal = _signal(self.profile, "analytical_thinking")
        self.assertIsNotNone(signal)
        self.assertIn("aspect:square_Pluto", signal.sources)
        self.assertIn("aspect:trine_Saturn", signal.sources)
        self.assertIsNone(_signal(self.profile, "analytical_or_technical"))

    def test_technical_ability_pluto_and_saturn(self):
        signal = _signal(self.profile, "technical_ability")
        self.assertIsNotNone(signal)
        self.assertIn("aspect:square_Pluto", signal.sources)
        self.assertIn("aspect:trine_Saturn", signal.sources)

    def test_debate_leo_and_pluto_not_saturn(self):
        signal = _signal(self.profile, "debate")
        self.assertIsNotNone(signal)
        self.assertIn("sign:Leo", signal.sources)
        self.assertIn("aspect:square_Pluto", signal.sources)
        self.assertNotIn("aspect:trine_Saturn", signal.sources)
        self.assertIsNone(_signal(self.profile, "debate_argumentation"))

    def test_argumentation_pluto_and_saturn(self):
        signal = _signal(self.profile, "argumentation")
        self.assertIsNotNone(signal)
        self.assertIn("aspect:square_Pluto", signal.sources)
        self.assertIn("aspect:trine_Saturn", signal.sources)

    def test_persuasion_not_created_by_leo_sales(self):
        # Sales ability is not persuasion; Avdey has Pluto persuasion only → no repeat.
        self.assertIsNone(_signal(self.profile, "persuasion"))
        sales = next(item for item in self.profile.sign_facts if item.id == "leo_sales_ability")
        self.assertEqual(sales.tags, ["sales"])
        self.assertNotIn("persuasion", sales.tags)

    def test_nonstandard_thinking_leo_and_retrograde(self):
        thinking = _signal(self.profile, "nonstandard_thinking")
        self.assertIsNotNone(thinking)
        self.assertIn("sign:Leo", thinking.sources)
        self.assertIn("motion:retrograde", thinking.sources)
        self.assertIn("leo_nonstandard_speech_thinking", thinking.fact_ids)
        self.assertIn("rx_nonstandard_solutions", thinking.fact_ids)
        self.assertNotIn("rx_unexpected_conclusions", thinking.fact_ids)
        self.assertNotIn("leo_learns_through_independent_investigation", thinking.fact_ids)
        self.assertIsNone(_signal(self.profile, "nonstandard_learning"))
        self.assertIsNone(_signal(self.profile, "nonstandard_thinking_learning"))

    def test_sales_includes_leo_and_house_1(self):
        signal = _signal(self.profile, "sales")
        self.assertIsNotNone(signal)
        self.assertIn("sign:Leo", signal.sources)
        self.assertIn("house:1", signal.sources)
        self.assertIsNone(_signal(self.profile, "sales_persuasive_presentation"))

    def test_repeated_signal_provenance_is_prefixed(self):
        for signal in self.profile.repeated_signals:
            for source in signal.sources:
                self.assertRegex(source, r"^(sign|house|motion|aspect):")

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

    def test_contrasting_superficiality_preserved(self):
        ids = _ids(self.profile.sign_facts) | _ids(self.profile.aspect_facts)
        self.assertIn("leo_risk_intellectual_superficiality", ids)
        self.assertIn("pluto_sq_identify_vulnerabilities", ids)
        self.assertIn("saturn_tr_analytical_ability", ids)
        pairs = {(item.tag_a, item.tag_b) for item in self.profile.contrasting_signals}
        # Depth was removed from broad Pluto conflict tags; analytical contrast remains exact.
        self.assertIn(("superficiality", "analytical_thinking"), pairs)
        self.assertNotIn(("superficiality", "depth"), pairs)

    def test_coverage_complete_for_engine_factors(self):
        self.assertEqual(self.profile.coverage.status, "complete")
        self.assertEqual(self.profile.coverage.missing_factors, [])

    def test_unsupported_factor_returns_partial_coverage(self):
        """After B1 house coverage, exercise missing packs via house 5 / aspect."""
        factors = MercurySourceFactors(
            birth_time_known=True,
            mercury_sign="Leo",
            mercury_element="fire",
            mercury_motion="direct",
            mercury_house=5,
            aspects=[MercuryAspect(planet="Mars", type="square", orb_deg=2.0)],
        )
        profile = build_source_profile_from_factors(factors)
        self.assertEqual(profile.coverage.status, "partial")
        self.assertNotIn("sign:Leo", profile.coverage.missing_factors)
        self.assertIn("house:5", profile.coverage.missing_factors)
        self.assertIn("aspect:square_Mars", profile.coverage.missing_factors)
        self.assertNotIn("motion:direct", profile.coverage.missing_factors)
        self.assertGreater(len(profile.sign_facts), 0)
        self.assertTrue(any("house 5" in item for item in profile.limitations))
        self.assertTrue(any("square Mars" in item for item in profile.limitations))

    def test_route_registered(self):
        app = create_app()
        paths = {getattr(route, "path", None) for route in app.routes}
        self.assertIn("/api/v1/mercury-source-profile", paths)
        self.assertIn("/api/v1/mercury-work-profile", paths)


class DirectMotionCoverageTests(unittest.TestCase):
    def test_direct_motion_is_not_unsupported_by_itself(self):
        factors = MercurySourceFactors(
            birth_time_known=True,
            mercury_sign="Taurus",
            mercury_element="earth",
            mercury_motion="direct",
            mercury_house=9,
            aspects=[
                MercuryAspect(planet="Moon", type="square", orb_deg=1.0),
                MercuryAspect(planet="Mars", type="trine", orb_deg=2.48),
                MercuryAspect(planet="Jupiter", type="sextile", orb_deg=0.55),
            ],
        )
        profile = build_source_profile_from_factors(factors)
        self.assertNotIn("motion:direct", profile.coverage.missing_factors)
        self.assertEqual(profile.motion_facts, [])
        self.assertEqual(profile.coverage.status, "complete")


class VladGoldenCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = build_mercury_source_profile(
            MercurySourceProfileRequest(
                birth_date=date(1986, 5, 16),
                birth_time=time(15, 0),
                birth_place="Dnipro, Ukraine",
            )
        )

    def test_calculated_mercury_basics(self):
        calc = self.profile.calculated
        self.assertEqual(calc.mercury_sign, "Taurus")
        self.assertEqual(calc.mercury_house, 9)
        self.assertEqual(calc.mercury_motion, "direct")
        self.assertTrue(calc.hard_aspected)

    def test_required_aspects_and_no_sun_conjunction(self):
        pairs = {(item.type, item.planet) for item in self.profile.calculated.aspects}
        self.assertIn(("square", "Moon"), pairs)
        self.assertIn(("trine", "Mars"), pairs)
        self.assertIn(("sextile", "Jupiter"), pairs)
        self.assertNotIn(("conjunction", "Sun"), pairs)

    def test_vlad_source_layers_activate(self):
        self.assertTrue(all(item.factor_key == "Taurus" for item in self.profile.sign_facts))
        self.assertTrue(all(item.factor_key == "9" for item in self.profile.house_facts))
        self.assertEqual(self.profile.motion_facts, [])
        aspect_keys = {item.factor_key for item in self.profile.aspect_facts}
        self.assertEqual(aspect_keys, {"square_Moon", "trine_Mars", "sextile_Jupiter"})
        self.assertIn("taurus_productive_thinking", _ids(self.profile.sign_facts))
        self.assertIn("taurus_harmonious_thinking", _ids(self.profile.sign_facts))
        self.assertIn("taurus_unhurried_thinking", _ids(self.profile.sign_facts))
        self.assertIn("taurus_thorough_thinking", _ids(self.profile.sign_facts))
        self.assertNotIn(
            "taurus_productive_unhurried_thorough_thinking",
            _ids(self.profile.sign_facts),
        )
        self.assertIn("h9_eternal_student", _ids(self.profile.house_facts))
        self.assertIn("moon_sq_emotion_rational_conflict", _ids(self.profile.aspect_facts))
        self.assertIn("moon_sq_difficulty_understanding_feelings", _ids(self.profile.aspect_facts))
        self.assertIn("moon_sq_moves_despite_fixation_need", _ids(self.profile.aspect_facts))
        self.assertIn("mars_tr_thinking_more_analytical", _ids(self.profile.aspect_facts))
        self.assertIn("jupiter_sx_oratory_and_persuasion", _ids(self.profile.aspect_facts))
        self.assertIn(
            "jupiter_sx_low_expression_excessive_empty_talking",
            _ids(self.profile.aspect_facts),
        )
        learning = next(
            item
            for item in self.profile.sign_facts
            if item.id == "taurus_learning_needs_time_without_pressure"
        )
        self.assertIn("enough time to process", learning.text.lower())
        self.assertIn("pressure interferes", learning.text.lower())
        self.assertNotIn("learns better", learning.text.lower())

    def test_no_avdey_only_packs_activate(self):
        all_facts = (
            self.profile.sign_facts
            + self.profile.house_facts
            + self.profile.motion_facts
            + self.profile.aspect_facts
        )
        ids = _ids(all_facts)
        refs = {item.source_reference for item in all_facts}
        self.assertFalse(any(item_id.startswith("leo_") for item_id in ids))
        self.assertFalse(any(item_id.startswith("h1_") for item_id in ids))
        self.assertFalse(any(item_id.startswith("rx_") for item_id in ids))
        self.assertFalse(any(item_id.startswith("pluto_sq_") for item_id in ids))
        self.assertFalse(any(item_id.startswith("saturn_tr_") for item_id in ids))
        self.assertNotIn("bioastrology_mercury_leo", refs)
        self.assertNotIn("bioastrology_mercury_house_1", refs)
        self.assertNotIn("methodology_mercury_retrograde", refs)

    def test_coverage_complete_without_direct_as_missing(self):
        self.assertEqual(self.profile.coverage.status, "complete")
        self.assertEqual(self.profile.coverage.missing_factors, [])
        self.assertNotIn("motion:direct", self.profile.coverage.covered_factors)
        self.assertNotIn("motion:direct", self.profile.coverage.missing_factors)

    def test_repeated_signals_have_provenance(self):
        self.assertIsNone(_signal(self.profile, "analytical_or_technical"))
        self.assertIsNone(_signal(self.profile, "debate_argumentation"))
        self.assertIsNone(_signal(self.profile, "foreign_languages_cultures"))
        self.assertIsNone(_signal(self.profile, "persuasive_communication"))
        self.assertIsNone(_signal(self.profile, "analytical_plus_abstract"))

        lifelong = _signal(self.profile, "lifelong_learning")
        self.assertIsNotNone(lifelong)
        self.assertIn("house:9", lifelong.sources)
        self.assertIn("aspect:sextile_Jupiter", lifelong.sources)
        self.assertNotIn("h9_elevates_intellectual_social_level", lifelong.fact_ids)
        self.assertTrue(
            {"h9_eternal_student", "h9_multiple_educations"} & set(lifelong.fact_ids)
        )

        languages = _signal(self.profile, "foreign_languages")
        self.assertIsNotNone(languages)
        self.assertIn("house:9", languages.sources)
        self.assertIn("aspect:sextile_Jupiter", languages.sources)
        self.assertIn("h9_interest_foreign_languages", languages.fact_ids)
        self.assertNotIn("h9_interest_geography_travel", languages.fact_ids)
        self.assertNotIn("h9_interest_other_cultures", languages.fact_ids)

        analytical = _signal(self.profile, "analytical_thinking")
        self.assertIsNotNone(analytical)
        self.assertIn("house:9", analytical.sources)
        self.assertIn("aspect:trine_Mars", analytical.sources)
        self.assertIn("h9_analytical_with_abstract", analytical.fact_ids)
        self.assertIn("mars_tr_thinking_more_analytical", analytical.fact_ids)
        self.assertNotIn("mars_tr_thinking_sharper", analytical.fact_ids)
        self.assertNotIn("mars_tr_action_more_rational", analytical.fact_ids)
        self.assertNotIn("aspect:sextile_Jupiter", analytical.sources)

        persuasion = _signal(self.profile, "persuasion")
        self.assertIsNotNone(persuasion)
        self.assertEqual(
            set(persuasion.sources),
            {"aspect:trine_Mars", "aspect:sextile_Jupiter"},
        )
        self.assertIn("mars_tr_persuasive", persuasion.fact_ids)
        self.assertIn("jupiter_sx_oratory_and_persuasion", persuasion.fact_ids)
        self.assertNotIn("mars_tr_speech_clearer_more_forceful", persuasion.fact_ids)

        self.assertIsNone(_signal(self.profile, "debate"))
        self.assertIsNone(_signal(self.profile, "argumentation"))

        for signal in self.profile.repeated_signals:
            for source in signal.sources:
                self.assertRegex(source, r"^(sign|house|motion|aspect):")

    def test_deliberate_vs_fast_contrast_if_present(self):
        pairs = {(item.tag_a, item.tag_b) for item in self.profile.contrasting_signals}
        self.assertIn(("deliberate_processing", "fast_thinking"), pairs)
        self.assertIn(("deliberate_processing", "mental_switching_pressure"), pairs)


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
        self.assertIn("aspect:trine_Saturn", signal.sources)
        self.assertIn("aspect:sextile_Moon", signal.sources)

    def test_insight_repeated_signal_pluto_and_moon(self):
        signal = _signal(self.profile, "insight_seeing_not_obvious")
        self.assertIsNotNone(signal)
        self.assertIn("aspect:square_Pluto", signal.sources)
        self.assertIn("aspect:sextile_Moon", signal.sources)


class DzmitryGoldenCaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = build_mercury_source_profile(
            MercurySourceProfileRequest(
                birth_date=date(1985, 11, 12),
                birth_time=time(14, 15),
                birth_place="Zhodino, Belarus",
            )
        )

    def test_calculated_mercury_basics(self):
        calc = self.profile.calculated
        self.assertEqual(calc.mercury_sign, "Sagittarius")
        self.assertEqual(calc.mercury_house, 10)
        self.assertEqual(calc.mercury_motion, "direct")
        self.assertFalse(calc.hard_aspected)

    def test_required_aspects(self):
        pairs = {(item.type, item.planet) for item in self.profile.calculated.aspects}
        self.assertIn(("sextile", "Mars"), pairs)
        self.assertIn(("sextile", "Jupiter"), pairs)
        self.assertIn(("conjunction", "Uranus"), pairs)

    def test_source_layers_activate(self):
        self.assertTrue(all(item.factor_key == "Sagittarius" for item in self.profile.sign_facts))
        self.assertTrue(all(item.factor_key == "10" for item in self.profile.house_facts))
        self.assertEqual(self.profile.motion_facts, [])
        aspect_keys = {item.factor_key for item in self.profile.aspect_facts}
        self.assertEqual(aspect_keys, {"sextile_Mars", "sextile_Jupiter", "conjunction_Uranus"})
        self.assertIn("sag_thinks_in_categories_globally", _ids(self.profile.sign_facts))
        self.assertIn("h10_mission_informing_people", _ids(self.profile.house_facts))
        self.assertIn("mars_tr_thinking_more_analytical", _ids(self.profile.aspect_facts))
        self.assertTrue(
            all(
                item.factor_key == "sextile_Mars"
                for item in self.profile.aspect_facts
                if item.id.startswith("mars_tr_")
            )
        )
        self.assertIn("jupiter_sx_oratory_and_persuasion", _ids(self.profile.aspect_facts))

    def test_uranus_conjunction_required_facts(self):
        uranus = [item for item in self.profile.aspect_facts if item.factor_key == "conjunction_Uranus"]
        ids = _ids(uranus)
        for required in (
            "uranus_cj_genius_potential",
            "uranus_cj_freshness_of_mind",
            "uranus_cj_openness_of_mind",
            "uranus_cj_distractibility_loss_of_focus",
            "uranus_cj_adhd_like_attention_scatter",
            "uranus_cj_impractical_thinking",
            "uranus_cj_drifting_into_strange_concepts",
            "uranus_cj_fast_speech",
            "uranus_cj_speech_may_become_disjointed",
            "uranus_cj_technical_talent",
            "uranus_cj_rebellious_free_thinking",
            "uranus_cj_interest_psychology",
            "uranus_cj_interest_numerology",
            "uranus_cj_interest_astrology",
            "uranus_cj_claircognizance",
            "uranus_cj_strong_sense_of_humor",
            "uranus_cj_piercing_unusual_persuasiveness",
            "uranus_cj_intellectual_chosenness_elitism",
            "uranus_cj_comp_laugh_joke_satire",
            "uranus_cj_intellect_of_the_future",
            "uranus_cj_spontaneous_creativity",
            "uranus_cj_antenna_with_cosmos",
        ):
            self.assertIn(required, ids)
        adhd = next(item for item in uranus if item.id == "uranus_cj_adhd_like_attention_scatter")
        self.assertIn("non-diagnostic", adhd.text.lower())
        self.assertIn("not a medical conclusion", adhd.text.lower())
        self.assertNotIn("uranus_sq_", "".join(ids))

    def test_no_accidental_other_golden_packs(self):
        all_facts = (
            self.profile.sign_facts
            + self.profile.house_facts
            + self.profile.motion_facts
            + self.profile.aspect_facts
        )
        ids = _ids(all_facts)
        self.assertFalse(any(item_id.startswith("leo_") for item_id in ids))
        self.assertFalse(any(item_id.startswith("taurus_") for item_id in ids))
        self.assertFalse(any(item_id.startswith("h1_") for item_id in ids))
        self.assertFalse(any(item_id.startswith("h9_") for item_id in ids))
        self.assertFalse(any(item_id.startswith("rx_") for item_id in ids))
        self.assertFalse(any(item_id.startswith("pluto_sq_") for item_id in ids))
        self.assertFalse(any(item_id.startswith("saturn_tr_") for item_id in ids))
        self.assertFalse(any(item_id.startswith("moon_") for item_id in ids))

    def test_coverage_complete(self):
        self.assertEqual(self.profile.coverage.status, "complete")
        self.assertEqual(self.profile.coverage.missing_factors, [])
        self.assertIn("sign:Sagittarius", self.profile.coverage.covered_factors)
        self.assertIn("house:10", self.profile.coverage.covered_factors)
        self.assertIn("aspect:sextile_Mars", self.profile.coverage.covered_factors)
        self.assertIn("aspect:sextile_Jupiter", self.profile.coverage.covered_factors)
        self.assertIn("aspect:conjunction_Uranus", self.profile.coverage.covered_factors)

    def test_repeated_signals_strict_and_provenance(self):
        persuasion = _signal(self.profile, "persuasion")
        self.assertIsNotNone(persuasion)
        self.assertIn("aspect:sextile_Mars", persuasion.sources)
        self.assertIn("aspect:sextile_Jupiter", persuasion.sources)
        self.assertIn("aspect:conjunction_Uranus", persuasion.sources)

        teaching = _signal(self.profile, "teaching")
        self.assertIsNotNone(teaching)
        self.assertIn("sign:Sagittarius", teaching.sources)
        self.assertIn("aspect:sextile_Jupiter", teaching.sources)

        # Rebellious/free thinking is not the same atom as nonstandard thinking.
        self.assertIsNone(_signal(self.profile, "nonstandard_thinking"))

        # Fast speech must not create fake fast_thinking with Uranus.
        fast = _signal(self.profile, "fast_thinking")
        if fast is not None:
            self.assertNotIn("aspect:conjunction_Uranus", fast.sources)

        for signal in self.profile.repeated_signals:
            for source in signal.sources:
                self.assertRegex(source, r"^(sign|house|motion|aspect):")


if __name__ == "__main__":
    unittest.main()
