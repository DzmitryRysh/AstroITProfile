import inspect
import unittest
from datetime import date, time

from app.services.mars_facts import MarsSourceFactors
from app.services import mars_source_knowledge as mars_knowledge_module
from app.services import mars_source_knowledge_motion as mars_motion_module
from app.services import mars_source_profile as mars_profile_module
from app.services.mars_source_knowledge import (
    ALL_MARS_SOURCE_FACTS,
    EXPECTED_MOTION_SOURCE_REFERENCES,
    HOUSE_PACKS,
    MARS_CATEGORIES,
    MARS_SCOPES,
    MOTION_PACKS,
    SIGN_PACKS,
    SUPPORTED_MOTION_KEYS,
    WORK_PROFILE_SCOPES,
)
from app.services.mars_source_knowledge_motion import REF_RX, RETROGRADE_PACK
from app.services.mars_source_profile import (
    DIRECT_MOTION_NO_PACK_LIMITATION,
    build_mars_source_profile,
    build_mars_source_profile_from_factors,
)
from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS

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

FORBIDDEN_MOTION_TAGS = frozenset(
    {"retrograde_mars", "weak_mars", "low_energy", "procrastination"}
)
PERSONAL_RX_ID = "mars_rx_sexual_temperament_suppression"
SOURCE_ONLY_RX_IDS = frozenset(
    {
        "mars_rx_unusual_muscular_activity",
        "mars_rx_auto_aggression",
    }
)


def _work_motion_ids(motion: str) -> list[str]:
    return [
        fact.id
        for fact in MOTION_PACKS[motion]
        if fact.scope in WORK_PROFILE_SCOPES and not fact.unresolved
    ]


class MarsMotionCatalogTests(unittest.TestCase):
    def test_retrograde_pack_exists(self):
        self.assertEqual(set(MOTION_PACKS), {"retrograde"})
        self.assertEqual(SUPPORTED_MOTION_KEYS, {"retrograde"})
        self.assertGreater(len(RETROGRADE_PACK), 0)
        self.assertEqual(MOTION_PACKS["retrograde"], RETROGRADE_PACK)
        self.assertNotIn("direct", MOTION_PACKS)

    def test_ids_unique_across_sign_house_motion(self):
        ids = [fact.id for fact in ALL_MARS_SOURCE_FACTS]
        self.assertEqual(len(ids), len(set(ids)))
        for fact_id in ids:
            self.assertTrue(fact_id.startswith("mars_"), fact_id)
        sign_ids = {fact.id for pack in SIGN_PACKS.values() for fact in pack}
        house_ids = {fact.id for pack in HOUSE_PACKS.values() for fact in pack}
        motion_ids = {fact.id for pack in MOTION_PACKS.values() for fact in pack}
        self.assertFalse(sign_ids & house_ids)
        self.assertFalse(sign_ids & motion_ids)
        self.assertFalse(house_ids & motion_ids)

    def test_motion_factor_shape_and_references(self):
        motion_facts = [fact for fact in ALL_MARS_SOURCE_FACTS if fact.factor_type == "motion"]
        self.assertTrue(motion_facts)
        self.assertEqual(len(motion_facts), len(RETROGRADE_PACK))
        for fact in motion_facts:
            self.assertEqual(fact.factor_type, "motion")
            self.assertEqual(fact.factor_key, "retrograde")
            self.assertTrue(fact.id.startswith("mars_rx_"), fact.id)
            self.assertIn(fact.category, MARS_CATEGORIES)
            self.assertIn(fact.scope, MARS_SCOPES)
            self.assertEqual(fact.source_reference, REF_RX)
            self.assertEqual(
                fact.source_reference,
                EXPECTED_MOTION_SOURCE_REFERENCES[fact.factor_key],
            )
            self.assertTrue(fact.text.strip())
            self.assertFalse(FORBIDDEN_MOTION_TAGS & set(fact.tags), fact.id)

    def test_no_direct_motion_interpretation_pack(self):
        self.assertFalse(
            any(fact.factor_key == "direct" for fact in ALL_MARS_SOURCE_FACTS)
        )
        motion_src = inspect.getsource(mars_motion_module)
        self.assertNotIn("Direct Mars acts easily", motion_src)
        self.assertNotIn("Direct Mars is stronger", motion_src)
        self.assertNotIn("Direct Mars is decisive", motion_src)

    def test_no_weak_mars_or_strength_score(self):
        motion_src = inspect.getsource(mars_motion_module)
        profile_src = inspect.getsource(mars_profile_module)
        knowledge_src = inspect.getsource(mars_knowledge_module)
        self.assertNotIn("weak_mars", motion_src)
        self.assertNotIn("strength_score", motion_src)
        self.assertNotIn("strength_score", profile_src)
        self.assertNotIn("REPEATED_SIGNAL_SPECS", motion_src)
        self.assertNotIn("REPEATED_SIGNAL_SPECS", knowledge_src)
        self.assertNotIn("REPEATED_SIGNAL_SPECS", profile_src)
        self.assertNotIn("hard_aspected", motion_src)
        self.assertNotIn("hard_aspected", profile_src)
        self.assertFalse(
            any("weak mars" in fact.text.lower() for fact in RETROGRADE_PACK)
        )
        self.assertFalse(
            any("low energy" == tag for fact in RETROGRADE_PACK for tag in fact.tags)
        )

    def test_no_aspect_knowledge_or_mercury_contamination(self):
        self.assertFalse(
            any(fact.factor_type == "aspect" for fact in ALL_MARS_SOURCE_FACTS)
        )
        mercury_ids = {fact.id for fact in ALL_SOURCE_FACTS}
        mars_ids = {fact.id for fact in ALL_MARS_SOURCE_FACTS}
        self.assertFalse(mars_ids & mercury_ids)
        self.assertNotIn("ALL_SOURCE_FACTS", inspect.getsource(mars_motion_module))

    def test_personal_and_source_only_scoping(self):
        by_id = {fact.id: fact for fact in RETROGRADE_PACK}
        personal = by_id[PERSONAL_RX_ID]
        self.assertEqual(personal.scope, "PERSONAL_MARS")
        self.assertNotIn(personal.scope, WORK_PROFILE_SCOPES)
        for fact_id in SOURCE_ONLY_RX_IDS:
            self.assertEqual(by_id[fact_id].scope, "SOURCE_ONLY")
            self.assertNotIn(by_id[fact_id].scope, WORK_PROFILE_SCOPES)


class MarsMotionActivationTests(unittest.TestCase):
    def test_retrograde_activates_work_pack_only(self):
        profile = build_mars_source_profile_from_factors(
            MarsSourceFactors(
                birth_time_known=True,
                mars_sign="Aries",
                mars_house=1,
                mars_motion="retrograde",
            )
        )
        self.assertEqual(
            [item.id for item in profile.motion_facts],
            _work_motion_ids("retrograde"),
        )
        self.assertTrue(all(item.activated for item in profile.motion_facts))
        self.assertTrue(all(item.factor_type == "motion" for item in profile.motion_facts))
        self.assertTrue(all(item.factor_key == "retrograde" for item in profile.motion_facts))
        self.assertTrue(
            all(item.provenance_key == "motion:retrograde" for item in profile.motion_facts)
        )
        self.assertTrue(
            all(item.scope in WORK_PROFILE_SCOPES for item in profile.motion_facts)
        )
        activated_ids = {item.id for item in profile.motion_facts}
        self.assertNotIn(PERSONAL_RX_ID, activated_ids)
        self.assertFalse(SOURCE_ONLY_RX_IDS & activated_ids)
        self.assertEqual(profile.aspect_facts, ())
        self.assertIn("motion:retrograde", profile.coverage.covered_factors)
        self.assertNotIn("motion:retrograde", profile.coverage.unimplemented_source_factors)

    def test_direct_motion_does_not_receive_invented_facts(self):
        profile = build_mars_source_profile_from_factors(
            MarsSourceFactors(
                birth_time_known=True,
                mars_sign="Aries",
                mars_house=1,
                mars_motion="direct",
            )
        )
        self.assertEqual(profile.calculated.mars_motion, "direct")
        self.assertEqual(profile.motion_facts, ())
        self.assertNotIn("motion:direct", profile.coverage.covered_factors)
        self.assertNotIn("motion:direct", profile.coverage.unimplemented_source_factors)
        self.assertNotIn("motion:retrograde", profile.coverage.covered_factors)
        self.assertIn(DIRECT_MOTION_NO_PACK_LIMITATION, profile.limitations)
        self.assertFalse(
            any("missing calculation" in item.lower() for item in profile.limitations)
        )
        self.assertFalse(
            any("not implemented yet" in item and "motion" in item for item in profile.limitations)
        )


class MarsMotionGoldenActivationTests(unittest.TestCase):
    def test_avdey_activates_sign_house_and_rx(self):
        profile = build_mars_source_profile(**AVDEY)
        self.assertEqual(profile.calculated.mars_sign, "Capricorn")
        self.assertEqual(profile.calculated.mars_house, 6)
        self.assertEqual(profile.calculated.mars_motion, "retrograde")
        self.assertEqual({item.factor_key for item in profile.sign_facts}, {"Capricorn"})
        self.assertEqual({item.factor_key for item in profile.house_facts}, {"6"})
        self.assertEqual(
            [item.id for item in profile.motion_facts],
            _work_motion_ids("retrograde"),
        )
        self.assertIn("mars_rx_braking_inhibition", {item.id for item in profile.motion_facts})
        self.assertNotIn(PERSONAL_RX_ID, {item.id for item in profile.motion_facts})
        self.assertEqual(
            profile.coverage.covered_factors,
            ("sign:Capricorn", "house:6", "motion:retrograde"),
        )
        self.assertTrue(
            all(item.startswith("aspect:") for item in profile.coverage.unimplemented_source_factors)
        )
        self.assertEqual(profile.aspect_facts, ())
        self.assertNotIn(DIRECT_MOTION_NO_PACK_LIMITATION, profile.limitations)

    def test_vlad_does_not_activate_rx(self):
        profile = build_mars_source_profile(**VLAD)
        self.assertEqual(profile.calculated.mars_motion, "direct")
        self.assertEqual(profile.motion_facts, ())
        self.assertNotIn("motion:retrograde", profile.coverage.covered_factors)
        self.assertNotIn("motion:direct", profile.coverage.covered_factors)
        self.assertNotIn("motion:retrograde", profile.coverage.unimplemented_source_factors)
        self.assertIn(DIRECT_MOTION_NO_PACK_LIMITATION, profile.limitations)
        self.assertTrue(profile.sign_facts)
        self.assertTrue(profile.house_facts)

    def test_dzmitry_does_not_activate_rx(self):
        profile = build_mars_source_profile(**DZMITRY)
        self.assertEqual(profile.calculated.mars_motion, "direct")
        self.assertEqual(profile.motion_facts, ())
        self.assertNotIn("motion:retrograde", profile.coverage.covered_factors)
        self.assertNotIn("motion:direct", profile.coverage.covered_factors)
        self.assertIn(DIRECT_MOTION_NO_PACK_LIMITATION, profile.limitations)
        self.assertEqual(profile.coverage.covered_factors, ("sign:Libra", "house:7"))
