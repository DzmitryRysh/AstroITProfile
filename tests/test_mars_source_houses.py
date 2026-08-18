import inspect
import unittest
from datetime import date, time

from app.services.mars_facts import MarsSourceFactors
from app.services import mars_source_knowledge as mars_knowledge_module
from app.services import mars_source_profile as mars_profile_module
from app.services.mars_source_knowledge import (
    ALL_MARS_SOURCE_FACTS,
    EXPECTED_HOUSE_SOURCE_REFERENCES,
    HOUSE_PACKS,
    MARS_CATEGORIES,
    MARS_SCOPES,
    SUPPORTED_HOUSE_KEYS,
    WORK_PROFILE_SCOPES,
)
from app.services.mars_source_profile import (
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

HOUSE_UNRESOLVED_IDS = {
    "mars_h2_strong_harmonious_positive_budget_through_activity": "strong_harmonious_mars_unresolved",
    "mars_h3_harmonious_mars_fast_driving": "harmonious_mars_unresolved",
    "mars_h4_strong_affliction_domestic_tyranny": "strong_affliction_unresolved",
    "mars_h7_affliction_early_marriage_divorce": "affliction_unresolved",
    "mars_h12_affliction_criminal_fraud_activity": "affliction_unresolved",
}


def _work_house_ids(house: str) -> list[str]:
    return [
        fact.id
        for fact in HOUSE_PACKS[house]
        if fact.scope in WORK_PROFILE_SCOPES and not fact.unresolved
    ]


class MarsHouseCatalogTests(unittest.TestCase):
    def test_all_twelve_house_packs_exist(self):
        self.assertEqual(set(HOUSE_PACKS), {str(n) for n in range(1, 13)})
        self.assertEqual(SUPPORTED_HOUSE_KEYS, set(HOUSE_PACKS))
        for house in HOUSE_PACKS:
            self.assertGreater(len(HOUSE_PACKS[house]), 0, house)

    def test_house_fact_shape_and_references(self):
        house_facts = [fact for fact in ALL_MARS_SOURCE_FACTS if fact.factor_type == "house"]
        self.assertTrue(house_facts)
        for fact in house_facts:
            self.assertIn(fact.factor_key, SUPPORTED_HOUSE_KEYS)
            self.assertTrue(fact.id.startswith(f"mars_h{fact.factor_key}_"), fact.id)
            self.assertIn(fact.category, MARS_CATEGORIES)
            self.assertIn(fact.scope, MARS_SCOPES)
            self.assertEqual(
                fact.source_reference,
                EXPECTED_HOUSE_SOURCE_REFERENCES[fact.factor_key],
            )

    def test_unique_ids_across_signs_and_houses(self):
        ids = [fact.id for fact in ALL_MARS_SOURCE_FACTS]
        self.assertEqual(len(ids), len(set(ids)))
        for fact_id in ids:
            self.assertTrue(fact_id.startswith("mars_"), fact_id)

    def test_no_mercury_catalog_contamination(self):
        mercury_ids = {fact.id for fact in ALL_SOURCE_FACTS}
        mars_ids = {fact.id for fact in ALL_MARS_SOURCE_FACTS}
        self.assertFalse(mars_ids & mercury_ids)

    def test_no_repeat_specs_or_hard_aspected_resolver(self):
        knowledge_src = inspect.getsource(mars_knowledge_module)
        houses_src = inspect.getsource(
            __import__("app.services.mars_source_knowledge_houses", fromlist=["x"])
        )
        profile_src = inspect.getsource(mars_profile_module)
        self.assertNotIn("REPEATED_SIGNAL_SPECS", knowledge_src)
        self.assertNotIn("REPEATED_SIGNAL_SPECS", houses_src)
        self.assertNotIn("REPEATED_SIGNAL_SPECS", profile_src)
        self.assertNotIn("hard_aspected", houses_src)
        self.assertNotIn("hard_aspected", profile_src)
        self.assertFalse(
            any(fact.factor_type == "aspect" for fact in ALL_MARS_SOURCE_FACTS)
        )

    def test_unresolved_house_conditions(self):
        by_id = {fact.id: fact for fact in ALL_MARS_SOURCE_FACTS}
        for fact_id, condition in HOUSE_UNRESOLVED_IDS.items():
            fact = by_id[fact_id]
            self.assertTrue(fact.unresolved, fact_id)
            self.assertEqual(fact.activation_condition, condition)
            self.assertEqual(fact.factor_type, "house")


class MarsHouseActivationTests(unittest.TestCase):
    def test_exact_house_activation_no_leakage(self):
        for house in SUPPORTED_HOUSE_KEYS:
            with self.subTest(house=house):
                profile = build_mars_source_profile_from_factors(
                    MarsSourceFactors(
                        birth_time_known=True,
                        mars_sign="Aries",
                        mars_house=int(house),
                    )
                )
                self.assertEqual({item.factor_key for item in profile.house_facts}, {house})
                self.assertEqual(
                    [item.id for item in profile.house_facts],
                    _work_house_ids(house),
                )
                self.assertTrue(all(item.activated for item in profile.house_facts))
                self.assertTrue(all(item.provenance_key == f"house:{house}" for item in profile.house_facts))
                self.assertEqual(profile.motion_facts, ())
                self.assertEqual(profile.aspect_facts, ())

    def test_unresolved_house_facts_do_not_ordinary_activate(self):
        profile = build_mars_source_profile_from_factors(
            MarsSourceFactors(birth_time_known=True, mars_sign="Aries", mars_house=2)
        )
        activated = {item.id for item in profile.house_facts}
        unresolved = {item.id for item in profile.conditional_unresolved}
        self.assertNotIn(
            "mars_h2_strong_harmonious_positive_budget_through_activity", activated
        )
        self.assertIn(
            "mars_h2_strong_harmonious_positive_budget_through_activity", unresolved
        )
        self.assertTrue(
            all(item.activated is False for item in profile.conditional_unresolved)
        )

    def test_unknown_time_does_not_activate_house_source(self):
        profile = build_mars_source_profile(
            birth_date=AVDEY["birth_date"],
            birth_place=AVDEY["birth_place"],
            birth_time=None,
        )
        self.assertFalse(profile.calculated.birth_time_known)
        self.assertIsNone(profile.calculated.mars_house)
        self.assertEqual(profile.house_facts, ())
        self.assertEqual(profile.calculated.mars_sign, "Capricorn")
        self.assertTrue(profile.sign_facts)
        self.assertNotIn("house:6", profile.coverage.covered_factors)
        self.assertTrue(
            any(
                "House source layer unavailable because birth time is unknown." in item
                for item in profile.limitations
            )
        )
        self.assertFalse(
            any("Mars house source missing" in item for item in profile.limitations)
        )
        self.assertFalse(
            any("house source knowledge is not implemented yet" in item
                for item in profile.limitations)
        )


class MarsHouseGoldenActivationTests(unittest.TestCase):
    def test_avdey_capricorn_house_6(self):
        profile = build_mars_source_profile(**AVDEY)
        self.assertEqual(profile.calculated.mars_sign, "Capricorn")
        self.assertEqual(profile.calculated.mars_house, 6)
        self.assertEqual({item.factor_key for item in profile.sign_facts}, {"Capricorn"})
        self.assertEqual({item.factor_key for item in profile.house_facts}, {"6"})
        self.assertEqual(
            [item.id for item in profile.house_facts],
            _work_house_ids("6"),
        )
        self.assertIn("mars_h6_difficult_task_tolerance", {
            item.id for item in profile.house_facts
        })
        self.assertNotIn("mars_h4_high_activity_in_home_life", {
            item.id for item in profile.house_facts
        })
        self.assertEqual(
            profile.coverage.covered_factors,
            ("sign:Capricorn", "house:6", "motion:retrograde"),
        )

    def test_vlad_capricorn_house_4(self):
        profile = build_mars_source_profile(**VLAD)
        self.assertEqual(profile.calculated.mars_sign, "Capricorn")
        self.assertEqual(profile.calculated.mars_house, 4)
        self.assertEqual({item.factor_key for item in profile.house_facts}, {"4"})
        self.assertEqual(
            [item.id for item in profile.house_facts],
            _work_house_ids("4"),
        )
        self.assertNotIn("mars_h6_difficult_task_tolerance", {
            item.id for item in profile.house_facts
        })

    def test_dzmitry_libra_house_7(self):
        profile = build_mars_source_profile(**DZMITRY)
        self.assertEqual(profile.calculated.mars_sign, "Libra")
        self.assertEqual(profile.calculated.mars_house, 7)
        self.assertEqual({item.factor_key for item in profile.sign_facts}, {"Libra"})
        self.assertEqual({item.factor_key for item in profile.house_facts}, {"7"})
        self.assertEqual(
            [item.id for item in profile.house_facts],
            _work_house_ids("7"),
        )
        self.assertNotIn("mars_h6_difficult_task_tolerance", {
            item.id for item in profile.house_facts
        })
        self.assertNotIn(
            "mars_h7_affliction_early_marriage_divorce",
            {item.id for item in profile.house_facts},
        )
