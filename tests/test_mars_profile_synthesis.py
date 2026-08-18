import inspect
import unittest
from datetime import date, time

from app.services.mars_profile_synthesis import (
    SECTION_SPECS,
    build_mars_profile_synthesis,
)
from app.services.mars_source_profile import build_mars_source_profile
from app.services import mars_profile_synthesis as mars_synth_module
from app.services import mars_source_knowledge as mars_knowledge_module

AVDEY = dict(
    birth_date=date(1986, 7, 14),
    birth_time=time(7, 10),
    birth_place="Simferopol, Ukraine",
)
VLAD = dict(
    birth_date=date(1986, 5, 16),
    birth_time=time(15, 0),
    birth_place="Dnipro, Ukraine",
)
DZMITRY = dict(
    birth_date=date(1985, 11, 12),
    birth_time=time(14, 15),
    birth_place="Zhodino, Belarus",
)

PRIMARY_NONEMPTY_KEYS = (
    "how_you_start",
    "how_you_execute",
    "work_rhythm",
    "when_you_get_stuck",
    "under_pressure",
    "conflict_style",
    "best_work_conditions",
    "watchouts",
)


def _sections(synthesis):
    return {item.key: item for item in synthesis.sections}


def _all_ids(synthesis):
    return set(synthesis.facts_by_id)


class MarsSynthesisStructureTests(unittest.TestCase):
    def test_stable_section_order(self):
        profile = build_mars_source_profile(**AVDEY)
        synthesis = build_mars_profile_synthesis(profile)
        self.assertEqual(
            [item.key for item in synthesis.sections],
            [spec[0] for spec in SECTION_SPECS],
        )
        self.assertEqual(
            [item.title for item in synthesis.sections],
            [spec[1] for spec in SECTION_SPECS],
        )

    def test_deterministic_repeat_of_build(self):
        profile = build_mars_source_profile(**AVDEY)
        first = build_mars_profile_synthesis(profile)
        second = build_mars_profile_synthesis(profile)
        self.assertEqual(
            [(s.key, s.fact_ids) for s in first.sections],
            [(s.key, s.fact_ids) for s in second.sections],
        )
        self.assertEqual(first.repeated_signals, second.repeated_signals)

    def test_excludes_source_only_personal_unresolved_and_has_no_score(self):
        profile = build_mars_source_profile(**AVDEY)
        synthesis = build_mars_profile_synthesis(profile)
        ids = _all_ids(synthesis)
        self.assertNotIn("mars_rx_sexual_temperament_suppression", ids)
        self.assertNotIn("mars_rx_auto_aggression", ids)
        self.assertNotIn("mars_rx_unusual_muscular_activity", ids)
        for fact_id in synthesis.unresolved_fact_ids:
            self.assertNotIn(fact_id, ids)
        src = inspect.getsource(mars_synth_module)
        self.assertNotIn("strength_score", src)
        self.assertNotIn("hard_aspected", src)
        self.assertNotIn("dominant", src)
        self.assertNotIn("REPEATED_SIGNAL_SPECS", inspect.getsource(mars_knowledge_module))
        self.assertEqual(synthesis.traceability.unclassified_fact_count, 0)
        self.assertEqual(synthesis.coverage, profile.coverage)
        self.assertEqual(synthesis.limitations, profile.limitations)

    def test_only_activated_facts_used(self):
        profile = build_mars_source_profile(**AVDEY)
        synthesis = build_mars_profile_synthesis(profile)
        for fact in synthesis.facts_by_id.values():
            self.assertTrue(fact.activated)
            self.assertFalse(fact.unresolved)
            self.assertIn(fact.scope, {"WORK_CORE", "WORK_DETAIL"})


class MarsSynthesisGoldenTests(unittest.TestCase):
    def test_avdey_layers_and_repeat_support(self):
        profile = build_mars_source_profile(**AVDEY)
        synthesis = build_mars_profile_synthesis(profile)
        by_key = _sections(synthesis)
        for key in PRIMARY_NONEMPTY_KEYS:
            self.assertGreater(by_key[key].fact_count, 0, key)
        self.assertIn("mars_capricorn_plans_then_executes", by_key["how_you_execute"].fact_ids)
        self.assertIn("mars_rx_repeated_hesitation_measure_seven_times", by_key["how_you_start"].fact_ids)
        self.assertIn("mars_rx_doing_and_redoing", by_key["work_rhythm"].fact_ids)
        self.assertIn("mars_rx_braking_inhibition", by_key["when_you_get_stuck"].fact_ids)
        self.assertIn("effort_overload", by_key["under_pressure"].repeated_signals)
        self.assertIn("mars_h6_duties_constant_overload", by_key["under_pressure"].fact_ids)
        self.assertIn(
            "mars_square_moon_l9_cluster_b_heavy_work_overwork",
            by_key["under_pressure"].fact_ids,
        )
        self.assertNotIn("mars_h6_duties_constant_overload", by_key["how_you_execute"].fact_ids)
        self.assertIn("mars_h6_workplace_conflict_pushes_line", by_key["conflict_style"].fact_ids)
        self.assertTrue(
            any(item_id.startswith("mars_opposition_sun_l9_") for item_id in _all_ids(synthesis))
        )
        self.assertTrue(
            any(item_id.startswith("mars_square_moon_l9_") for item_id in _all_ids(synthesis))
        )
        self.assertEqual(synthesis.traceability.unresolved_fact_count, 0)
        self.assertTrue(
            any("Bioastrology Mars-Moon pair source is not yet extracted." in item
                for item in synthesis.limitations)
        )

    def test_vlad_no_rx_or_l9_tense_and_bio_in_professional(self):
        profile = build_mars_source_profile(**VLAD)
        synthesis = build_mars_profile_synthesis(profile)
        ids = _all_ids(synthesis)
        self.assertFalse(any("_l9_" in fact_id for fact_id in ids))
        self.assertFalse(any(fact_id.startswith("mars_rx_") for fact_id in ids))
        self.assertEqual(synthesis.repeated_signals, ())
        professional = _sections(synthesis)["professional_associations"]
        self.assertIn("mars_mercury_bio_selling_persuasion_aptitude", professional.fact_ids)
        self.assertIn("mars_jupiter_bio_teacher_mentor_aptitude", professional.fact_ids)
        self.assertNotIn(
            "mars_mercury_bio_technical_analytical_it_engineering_aptitude",
            _sections(synthesis)["how_you_execute"].fact_ids,
        )
        self.assertIn("mars_capricorn_plans_then_executes", _sections(synthesis)["how_you_execute"].fact_ids)
        self.assertEqual(_sections(synthesis)["under_pressure"].fact_count, 0)
        self.assertTrue(
            any("no Lesson 9 source-specific interpretation pack" in item
                for item in synthesis.limitations)
        )

    def test_dzmitry_start_from_libra_no_rx_or_l9(self):
        profile = build_mars_source_profile(**DZMITRY)
        synthesis = build_mars_profile_synthesis(profile)
        ids = _all_ids(synthesis)
        self.assertFalse(any("_l9_" in fact_id for fact_id in ids))
        self.assertFalse(any(fact_id.startswith("mars_rx_") for fact_id in ids))
        start = _sections(synthesis)["how_you_start"]
        self.assertIn("mars_libra_needs_partner_or_team_to_start", start.fact_ids)
        self.assertIn("mars_libra_indecision_delayed_choice", _sections(synthesis)["when_you_get_stuck"].fact_ids)
        professional = _sections(synthesis)["professional_associations"]
        self.assertTrue(any(item_id.startswith("mars_mercury_bio_") for item_id in professional.fact_ids))
        self.assertTrue(any(item_id.startswith("mars_jupiter_bio_") for item_id in professional.fact_ids))
        self.assertEqual(synthesis.repeated_signals, ())
        self.assertEqual(_sections(synthesis)["under_pressure"].fact_count, 0)
