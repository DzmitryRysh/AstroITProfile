import inspect
import unittest
from datetime import date, time

from app.services.astro_calc import SIGNS
from app.services.mars_facts import MarsSourceFactors
from app.services import mars_source_knowledge as mars_knowledge_module
from app.services import mars_source_profile as mars_profile_module
from app.services.mars_source_knowledge import (
    ALL_MARS_SOURCE_FACTS,
    EXPECTED_SIGN_SOURCE_REFERENCES,
    MARS_CATEGORIES,
    MARS_SCOPES,
    SIGN_PACKS,
    SUPPORTED_SIGN_KEYS,
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

WEAK_NEPTUNE_IDS = frozenset(
    {
        "mars_pisces_weak_neptune_chaos_wasted_effort",
        "mars_pisces_weak_neptune_grounding_recommendation",
    }
)
AQUARIUS_SOURCE_ONLY_ID = "mars_aquarius_source_democracy_liberalism_irresponsibility"


def _sign_keys(facts) -> set[str]:
    return {item.factor_key for item in facts}


class MarsSignCatalogTests(unittest.TestCase):
    def test_all_twelve_sign_packs_exist(self):
        self.assertEqual(set(SIGN_PACKS), set(SIGNS))
        self.assertEqual(SUPPORTED_SIGN_KEYS, set(SIGNS))
        for sign in SIGNS:
            self.assertGreater(len(SIGN_PACKS[sign]), 0, sign)

    def test_fact_ids_unique_and_mars_prefixed(self):
        ids = [fact.id for fact in ALL_MARS_SOURCE_FACTS]
        self.assertEqual(len(ids), len(set(ids)))
        for fact_id in ids:
            self.assertTrue(fact_id.startswith("mars_"), fact_id)

    def test_factor_type_key_category_scope_and_references(self):
        for fact in ALL_MARS_SOURCE_FACTS:
            self.assertIn(fact.factor_type, {"sign", "house"})
            self.assertIn(fact.category, MARS_CATEGORIES)
            self.assertIn(fact.scope, MARS_SCOPES)
            self.assertTrue(fact.text.strip())
            if fact.factor_type == "sign":
                self.assertIn(fact.factor_key, SIGNS)
                self.assertEqual(
                    fact.source_reference,
                    EXPECTED_SIGN_SOURCE_REFERENCES[fact.factor_key],
                )

    def test_no_mercury_catalog_contamination(self):
        mercury_ids = {fact.id for fact in ALL_SOURCE_FACTS}
        mars_ids = {fact.id for fact in ALL_MARS_SOURCE_FACTS}
        self.assertFalse(mars_ids & mercury_ids)
        self.assertNotIn("ALL_SOURCE_FACTS", inspect.getsource(mars_knowledge_module))

    def test_no_repeated_signal_specs_or_strength_score(self):
        knowledge_src = inspect.getsource(mars_knowledge_module)
        profile_src = inspect.getsource(mars_profile_module)
        self.assertNotIn("REPEATED_SIGNAL_SPECS", knowledge_src)
        self.assertNotIn("REPEATED_SIGNAL_SPECS", profile_src)
        self.assertNotIn("strength_score", knowledge_src)
        self.assertNotIn("hard_aspected", profile_src)

    def test_no_motion_or_aspect_knowledge_facts(self):
        types = {fact.factor_type for fact in ALL_MARS_SOURCE_FACTS}
        self.assertEqual(types, {"sign", "house"})

    def test_weak_neptune_facts_are_unresolved(self):
        by_id = {fact.id: fact for fact in ALL_MARS_SOURCE_FACTS}
        for fact_id in WEAK_NEPTUNE_IDS:
            fact = by_id[fact_id]
            self.assertTrue(fact.unresolved)
            self.assertEqual(fact.activation_condition, "neptune_strength_unresolved")
            self.assertEqual(fact.factor_key, "Pisces")

    def test_aquarius_political_statement_is_source_only(self):
        fact = next(
            item for item in ALL_MARS_SOURCE_FACTS if item.id == AQUARIUS_SOURCE_ONLY_ID
        )
        self.assertEqual(fact.scope, "SOURCE_ONLY")
        self.assertNotIn(fact.scope, WORK_PROFILE_SCOPES)


class MarsSignActivationTests(unittest.TestCase):
    def test_activation_selects_exactly_one_sign_family(self):
        for sign in SIGNS:
            with self.subTest(sign=sign):
                profile = build_mars_source_profile_from_factors(
                    MarsSourceFactors(birth_time_known=True, mars_sign=sign)
                )
                self.assertEqual(_sign_keys(profile.sign_facts), {sign})
                self.assertTrue(all(item.activated for item in profile.sign_facts))
                self.assertTrue(all(item.unresolved is False for item in profile.sign_facts))
                self.assertTrue(
                    all(item.scope in WORK_PROFILE_SCOPES for item in profile.sign_facts)
                )
                expected_work = [
                    fact
                    for fact in SIGN_PACKS[sign]
                    if fact.scope in WORK_PROFILE_SCOPES and not fact.unresolved
                ]
                self.assertEqual(
                    [item.id for item in profile.sign_facts],
                    [fact.id for fact in expected_work],
                )
                self.assertEqual(profile.house_facts, ())
                self.assertEqual(profile.motion_facts, ())
                self.assertEqual(profile.aspect_facts, ())

    def test_pisces_weak_neptune_facts_are_not_ordinary_activation(self):
        profile = build_mars_source_profile_from_factors(
            MarsSourceFactors(birth_time_known=True, mars_sign="Pisces")
        )
        activated_ids = {item.id for item in profile.sign_facts}
        unresolved_ids = {item.id for item in profile.conditional_unresolved}
        self.assertFalse(WEAK_NEPTUNE_IDS & activated_ids)
        self.assertEqual(unresolved_ids, set(WEAK_NEPTUNE_IDS))
        self.assertTrue(
            all(item.activated is False for item in profile.conditional_unresolved)
        )
        self.assertTrue(all(item.unresolved for item in profile.conditional_unresolved))

    def test_aquarius_source_only_fact_does_not_enter_work_profile(self):
        profile = build_mars_source_profile_from_factors(
            MarsSourceFactors(birth_time_known=True, mars_sign="Aquarius")
        )
        self.assertNotIn(
            AQUARIUS_SOURCE_ONLY_ID, {item.id for item in profile.sign_facts}
        )

    def test_unimplemented_layers_are_source_gaps_not_missing_calculation(self):
        profile = build_mars_source_profile_from_factors(
            MarsSourceFactors(
                birth_time_known=True,
                mars_sign="Aries",
                mars_house=1,
                mars_motion="retrograde",
            )
        )
        self.assertEqual(profile.coverage.covered_factors, ("sign:Aries", "house:1"))
        self.assertNotIn("house:1", profile.coverage.unimplemented_source_factors)
        self.assertIn("motion:retrograde", profile.coverage.unimplemented_source_factors)
        self.assertEqual(profile.coverage.status, "partial")
        self.assertFalse(
            any("house source knowledge is not implemented yet" in item
                for item in profile.limitations)
        )
        self.assertFalse(
            any("missing calculation" in item.lower() for item in profile.limitations)
        )


class MarsSignGoldenActivationTests(unittest.TestCase):
    def test_avdey_activates_only_capricorn(self):
        profile = build_mars_source_profile(**AVDEY)
        self.assertEqual(profile.calculated.mars_sign, "Capricorn")
        self.assertEqual(_sign_keys(profile.sign_facts), {"Capricorn"})
        self.assertEqual(len(profile.sign_facts), len([
            fact for fact in SIGN_PACKS["Capricorn"]
            if fact.scope in WORK_PROFILE_SCOPES and not fact.unresolved
        ]))
        self.assertIn("mars_capricorn_plans_then_executes", {
            item.id for item in profile.sign_facts
        })
        self.assertEqual(profile.motion_facts, ())
        self.assertEqual(profile.aspect_facts, ())
        self.assertEqual(profile.coverage.covered_factors, ("sign:Capricorn", "house:6"))
        self.assertNotIn("house:6", profile.coverage.unimplemented_source_factors)
        self.assertIn("motion:retrograde", profile.coverage.unimplemented_source_factors)
        self.assertIn(
            "aspect:opposition_Sun", profile.coverage.unimplemented_source_factors
        )
        self.assertIn("aspect:square_Moon", profile.coverage.unimplemented_source_factors)
        self.assertTrue(all(item.provenance_key == "sign:Capricorn" for item in profile.sign_facts))

    def test_vlad_activates_same_capricorn_pack(self):
        profile = build_mars_source_profile(**VLAD)
        self.assertEqual(profile.calculated.mars_sign, "Capricorn")
        self.assertEqual(_sign_keys(profile.sign_facts), {"Capricorn"})
        avdey = build_mars_source_profile(**AVDEY)
        self.assertEqual(
            [item.id for item in profile.sign_facts],
            [item.id for item in avdey.sign_facts],
        )

    def test_dzmitry_activates_only_libra(self):
        profile = build_mars_source_profile(**DZMITRY)
        self.assertEqual(profile.calculated.mars_sign, "Libra")
        self.assertEqual(_sign_keys(profile.sign_facts), {"Libra"})
        self.assertIn("mars_libra_needs_partner_or_team_to_start", {
            item.id for item in profile.sign_facts
        })
        self.assertNotIn("mars_capricorn_plans_then_executes", {
            item.id for item in profile.sign_facts
        })
        self.assertEqual(profile.coverage.covered_factors, ("sign:Libra", "house:7"))
        self.assertNotIn("house:7", profile.coverage.unimplemented_source_factors)
        self.assertNotIn("motion:retrograde", profile.coverage.unimplemented_source_factors)
