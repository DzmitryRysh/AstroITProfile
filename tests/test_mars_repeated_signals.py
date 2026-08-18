import inspect
import unittest
from datetime import date, time

from app.services.mars_facts import MarsSourceFactors
from app.services.mars_repeated_signals import (
    MARS_REPEATED_SIGNAL_SPECS,
    detect_mars_repeated_signals,
)
from app.services.mars_source_profile import (
    MarsSourceFact,
    build_mars_source_profile,
    build_mars_source_profile_from_factors,
)
from app.services.mercury_source_knowledge import REPEATED_SIGNAL_SPECS as MERCURY_REPEAT_SPECS
from app.services import mars_repeated_signals as mars_repeat_module
from app.services import mars_source_profile as mars_profile_module
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

APPROVED_TAGS = {
    "hands_on_execution",
    "crisis_execution",
    "mood_dependent_action",
    "effort_overload",
    "action_hesitation",
}


def _fact(**kwargs) -> MarsSourceFact:
    payload = dict(
        id="mars_test",
        factor_type="sign",
        factor_key="Aries",
        text="test",
        source_reference="test",
        category="execution",
        scope="WORK_CORE",
        polarity="neutral",
        tags=(),
        activation_condition=None,
        activated=True,
        unresolved=False,
    )
    payload.update(kwargs)
    return MarsSourceFact(**payload)


class MarsRepeatSpecTests(unittest.TestCase):
    def test_specs_are_exact_approved_tags_only(self):
        tags = [spec["tag"] for spec in MARS_REPEATED_SIGNAL_SPECS]
        self.assertEqual(set(tags), APPROVED_TAGS)
        self.assertEqual(len(tags), len(set(tags)))
        for spec in MARS_REPEATED_SIGNAL_SPECS:
            self.assertEqual(spec["signal"], spec["tag"])
            self.assertEqual(spec["min_factor_keys"], 2)

    def test_does_not_import_mercury_repeat_specs(self):
        src = inspect.getsource(mars_repeat_module)
        self.assertNotIn("mercury_source_knowledge", src)
        self.assertNotIn("from app.services.mercury", src)
        mercury_tags = {spec["tag"] for spec in MERCURY_REPEAT_SPECS}
        self.assertFalse(APPROVED_TAGS & mercury_tags)
        knowledge_src = inspect.getsource(mars_knowledge_module)
        self.assertNotIn("REPEATED_SIGNAL_SPECS", knowledge_src)

    def test_no_approximate_tag_expansion_in_mars_modules(self):
        profile_src = inspect.getsource(mars_profile_module)
        self.assertNotIn("also_accept", inspect.getsource(mars_repeat_module))
        self.assertNotIn("also_accept", profile_src)


class MarsRepeatDetectionTests(unittest.TestCase):
    def test_requires_two_distinct_provenance_keys(self):
        facts = [
            _fact(
                id="mars_a",
                factor_type="sign",
                factor_key="Virgo",
                tags=("hands_on_execution",),
            ),
            _fact(
                id="mars_b",
                factor_type="house",
                factor_key="6",
                tags=("hands_on_execution",),
            ),
        ]
        signals = detect_mars_repeated_signals(facts)
        match = next(item for item in signals if item.signal == "hands_on_execution")
        self.assertEqual(match.source_count, 2)
        self.assertEqual(match.sources, ("house:6", "sign:Virgo"))
        self.assertEqual(match.fact_ids, ("mars_a", "mars_b"))

    def test_same_aspect_two_source_families_do_not_count_twice(self):
        facts = [
            _fact(
                id="mars_l9",
                factor_type="aspect",
                factor_key="opposition_Sun",
                tags=("effort_overload",),
            ),
            _fact(
                id="mars_bio",
                factor_type="aspect",
                factor_key="opposition_Sun",
                tags=("effort_overload",),
            ),
        ]
        signals = detect_mars_repeated_signals(facts)
        self.assertFalse(any(item.signal == "effort_overload" for item in signals))

    def test_unresolved_and_inactive_facts_do_not_count(self):
        facts = [
            _fact(
                id="mars_a",
                factor_type="sign",
                factor_key="Cancer",
                tags=("mood_dependent_action",),
            ),
            _fact(
                id="mars_b",
                factor_type="aspect",
                factor_key="square_Moon",
                tags=("mood_dependent_action",),
                unresolved=True,
                activated=False,
            ),
        ]
        signals = detect_mars_repeated_signals(facts)
        self.assertFalse(any(item.signal == "mood_dependent_action" for item in signals))


class MarsRepeatGoldenTests(unittest.TestCase):
    def test_avdey_effort_overload_from_house_and_moon(self):
        profile = build_mars_source_profile(**AVDEY)
        signals = {item.signal: item for item in profile.repeated_signals}
        self.assertEqual(set(signals), {"effort_overload"})
        overload = signals["effort_overload"]
        self.assertGreaterEqual(overload.source_count, 2)
        self.assertIn("house:6", overload.sources)
        self.assertIn("aspect:square_Moon", overload.sources)
        self.assertIn("mars_h6_duties_constant_overload", overload.fact_ids)
        self.assertIn(
            "mars_square_moon_l9_cluster_b_heavy_work_overwork",
            overload.fact_ids,
        )

    def test_vlad_has_no_repeats(self):
        profile = build_mars_source_profile(**VLAD)
        self.assertEqual(profile.repeated_signals, ())

    def test_dzmitry_libra_hesitation_alone_is_not_a_repeat(self):
        profile = build_mars_source_profile(**DZMITRY)
        self.assertEqual(profile.repeated_signals, ())
        hesitation_facts = [
            fact
            for fact in profile.sign_facts
            if "action_hesitation" in fact.tags
        ]
        self.assertTrue(hesitation_facts)

    def test_synthetic_scorpio_house_8_fires_crisis_execution(self):
        profile = build_mars_source_profile_from_factors(
            MarsSourceFactors(
                birth_time_known=True,
                mars_sign="Scorpio",
                mars_house=8,
            )
        )
        signals = {item.signal: item for item in profile.repeated_signals}
        self.assertIn("crisis_execution", signals)
        self.assertEqual(
            set(signals["crisis_execution"].sources),
            {"sign:Scorpio", "house:8"},
        )
