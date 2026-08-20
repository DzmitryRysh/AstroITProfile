import inspect
import unittest
from datetime import date, time

from app.services.mars_facts import MarsAspect, MarsSourceFactors
from app.services import mars_source_knowledge as mars_knowledge_module
from app.services import mars_source_knowledge_aspects_bio as mars_bio_module
from app.services import mars_source_knowledge_aspects_l9 as mars_l9_module
from app.services import mars_source_profile as mars_profile_module
from app.services.mars_source_knowledge import (
    ALL_MARS_SOURCE_FACTS,
    BIO_MOON_NOT_EXTRACTED_LIMITATION,
    BIO_PAIR_PACKS,
    BIO_PAIR_PLANETS,
    EXPECTED_BIO_ASPECT_SOURCE_REFERENCES,
    EXPECTED_L9_ASPECT_SOURCE_REFERENCES,
    L9_ASPECT_PACKS,
    L9_TENSE_PLANETS,
    MARS_CATEGORIES,
    MARS_MAJOR_ASPECT_TYPES,
    MARS_SCOPES,
    MARS_TENSE_ASPECT_TYPES,
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

MERCURY_REPEAT_TAGS = frozenset(
    {"analytical_thinking", "technical_ability", "fast_thinking"}
)
FORBIDDEN_GLOBAL_TAGS = frozenset(
    {"hard_aspected", "afflicted_mars", "strong_mars", "weak_mars"}
)


def _work_ids(facts) -> list[str]:
    return [
        fact.id
        for fact in facts
        if fact.scope in WORK_PROFILE_SCOPES and not fact.unresolved
    ]


def _profile_with_aspect(aspect_type: str, planet: str):
    return build_mars_source_profile_from_factors(
        MarsSourceFactors(
            birth_time_known=True,
            mars_sign="Aries",
            mars_aspects=(MarsAspect(planet=planet, type=aspect_type),),
        )
    )


class MarsAspectCatalogTests(unittest.TestCase):
    def test_all_nine_lesson9_tense_families_exist(self):
        self.assertEqual(set(L9_TENSE_PLANETS), set(EXPECTED_L9_ASPECT_SOURCE_REFERENCES))
        for planet in L9_TENSE_PLANETS:
            for aspect_type in MARS_TENSE_ASPECT_TYPES:
                key = f"{aspect_type}_{planet}"
                self.assertIn(key, L9_ASPECT_PACKS, key)
                self.assertGreater(len(L9_ASPECT_PACKS[key]), 0, key)

    def test_ids_unique_and_mars_prefixed(self):
        ids = [fact.id for fact in ALL_MARS_SOURCE_FACTS]
        self.assertEqual(len(ids), len(set(ids)))
        for fact_id in ids:
            self.assertTrue(fact_id.startswith("mars_"), fact_id)

    def test_lesson9_shape_and_references(self):
        for key, pack in L9_ASPECT_PACKS.items():
            aspect_type, planet = key.split("_", 1)
            self.assertIn(aspect_type, MARS_TENSE_ASPECT_TYPES)
            self.assertIn(planet, L9_TENSE_PLANETS)
            for fact in pack:
                self.assertEqual(fact.factor_type, "aspect")
                self.assertEqual(fact.factor_key, key)
                self.assertTrue(
                    fact.id.startswith(f"mars_{aspect_type}_{planet.lower()}_l9_"),
                    fact.id,
                )
                self.assertEqual(
                    fact.source_reference,
                    EXPECTED_L9_ASPECT_SOURCE_REFERENCES[planet],
                )
                self.assertIn(fact.category, MARS_CATEGORIES)
                self.assertIn(fact.scope, MARS_SCOPES)
                self.assertFalse(MERCURY_REPEAT_TAGS & set(fact.tags), fact.id)
                self.assertFalse(FORBIDDEN_GLOBAL_TAGS & set(fact.tags), fact.id)

    def test_bio_pair_shape_and_no_moon_parity(self):
        self.assertNotIn("Moon", BIO_PAIR_PACKS)
        self.assertEqual(set(BIO_PAIR_PACKS), set(BIO_PAIR_PLANETS))
        for planet, pack in BIO_PAIR_PACKS.items():
            self.assertGreater(len(pack), 0, planet)
            for fact in pack:
                self.assertEqual(fact.factor_type, "aspect")
                self.assertEqual(fact.factor_key, f"pair_{planet}")
                self.assertTrue(fact.id.startswith(f"mars_{planet.lower()}_bio_"), fact.id)
                self.assertEqual(
                    fact.source_reference,
                    EXPECTED_BIO_ASPECT_SOURCE_REFERENCES[planet],
                )
                self.assertIn(fact.category, MARS_CATEGORIES)
                self.assertIn(fact.scope, MARS_SCOPES)
                self.assertFalse(MERCURY_REPEAT_TAGS & set(fact.tags), fact.id)
                self.assertNotIn("strategic_action", fact.tags)
                self.assertFalse(FORBIDDEN_GLOBAL_TAGS & set(fact.tags), fact.id)

    def test_no_mercury_contamination_hard_aspected_or_repeat_specs(self):
        mercury_ids = {fact.id for fact in ALL_SOURCE_FACTS}
        mars_ids = {fact.id for fact in ALL_MARS_SOURCE_FACTS}
        self.assertFalse(mars_ids & mercury_ids)
        for src in (
            inspect.getsource(mars_knowledge_module),
            inspect.getsource(mars_l9_module),
            inspect.getsource(mars_bio_module),
            inspect.getsource(mars_profile_module),
        ):
            self.assertNotIn("REPEATED_SIGNAL_SPECS", src)
            self.assertNotIn("hard_aspected", src)
            self.assertNotIn("strength_score", src)
            self.assertNotIn("afflicted_mars", src)


class MarsAspectActivationTests(unittest.TestCase):
    def test_lesson9_blockers_fire_on_square_and_opposition(self):
        for planet in L9_TENSE_PLANETS:
            for aspect_type in MARS_TENSE_ASPECT_TYPES:
                with self.subTest(planet=planet, aspect_type=aspect_type):
                    profile = _profile_with_aspect(aspect_type, planet)
                    l9_ids = _work_ids(L9_ASPECT_PACKS[f"{aspect_type}_{planet}"])
                    activated = [item.id for item in profile.aspect_facts]
                    for fact_id in l9_ids:
                        self.assertIn(fact_id, activated)
                    self.assertTrue(
                        all(
                            item.provenance_key == f"aspect:{aspect_type}_{planet}"
                            for item in profile.aspect_facts
                        )
                    )
                    self.assertIn(
                        f"aspect:{aspect_type}_{planet}",
                        profile.coverage.covered_factors,
                    )

    def test_lesson9_blockers_do_not_fire_on_trine_sextile_or_conjunction(self):
        for planet in L9_TENSE_PLANETS:
            for aspect_type in ("trine", "sextile", "conjunction"):
                with self.subTest(planet=planet, aspect_type=aspect_type):
                    profile = _profile_with_aspect(aspect_type, planet)
                    l9_ids = {
                        fact.id
                        for key, pack in L9_ASPECT_PACKS.items()
                        if key.endswith(f"_{planet}")
                        for fact in pack
                    }
                    activated = {item.id for item in profile.aspect_facts}
                    self.assertFalse(l9_ids & activated)

    def test_bio_pair_facts_activate_on_every_major_aspect(self):
        for planet in BIO_PAIR_PLANETS:
            expected = _work_ids(BIO_PAIR_PACKS[planet])
            self.assertTrue(expected, planet)
            for aspect_type in MARS_MAJOR_ASPECT_TYPES:
                with self.subTest(planet=planet, aspect_type=aspect_type):
                    profile = _profile_with_aspect(aspect_type, planet)
                    activated = [item.id for item in profile.aspect_facts]
                    for fact_id in expected:
                        self.assertIn(fact_id, activated)
                    bio_facts = [
                        item for item in profile.aspect_facts if item.id in expected
                    ]
                    self.assertTrue(
                        all(
                            item.provenance_key == f"aspect:{aspect_type}_{planet}"
                            for item in bio_facts
                        )
                    )
                    self.assertTrue(
                        all(
                            item.source_reference
                            == EXPECTED_BIO_ASPECT_SOURCE_REFERENCES[planet]
                            for item in bio_facts
                        )
                    )

    def test_lesson9_and_bio_coexist_on_same_calculated_factor(self):
        profile = _profile_with_aspect("opposition", "Sun")
        ids = {item.id for item in profile.aspect_facts}
        self.assertTrue(any(item_id.startswith("mars_opposition_sun_l9_") for item_id in ids))
        self.assertTrue(any(item_id.startswith("mars_sun_bio_") for item_id in ids))
        self.assertTrue(
            all(item.provenance_key == "aspect:opposition_Sun" for item in profile.aspect_facts)
        )
        refs = {item.source_reference for item in profile.aspect_facts}
        self.assertIn("lesson9_mars_aspect_tense_sun", refs)
        self.assertIn("bioastrology_mars_aspect_sun", refs)

    def test_conjunction_is_not_silently_tense(self):
        profile = _profile_with_aspect("conjunction", "Sun")
        ids = {item.id for item in profile.aspect_facts}
        self.assertFalse(any("_l9_" in item_id for item_id in ids))
        self.assertTrue(any(item_id.startswith("mars_sun_bio_") for item_id in ids))
        self.assertEqual(
            profile.coverage.covered_factors,
            ("sign:Aries", "aspect:conjunction_Sun"),
        )

    def test_source_only_bio_stays_out_of_work_profile(self):
        profile = _profile_with_aspect("trine", "Neptune")
        ids = {item.id for item in profile.aspect_facts}
        self.assertNotIn("mars_neptune_bio_hypnosis_extrasensory", ids)
        self.assertNotIn("mars_neptune_bio_medical_healing", ids)
        self.assertIn("mars_neptune_bio_design_aptitude", ids)

    def test_no_bio_moon_and_harmonious_moon_is_unimplemented(self):
        profile = _profile_with_aspect("trine", "Moon")
        self.assertEqual(profile.aspect_facts, ())
        self.assertIn("aspect:trine_Moon", profile.coverage.unimplemented_source_factors)
        self.assertIn(BIO_MOON_NOT_EXTRACTED_LIMITATION, profile.limitations)
        self.assertFalse(
            any("missing calculation" in item.lower() for item in profile.limitations)
        )
        self.assertFalse(
            any(fact.id.startswith("mars_moon_bio_") for fact in ALL_MARS_SOURCE_FACTS)
        )


class MarsAspectGoldenActivationTests(unittest.TestCase):
    def test_avdey_sun_opposition_and_moon_square(self):
        profile = build_mars_source_profile(**AVDEY)
        self.assertEqual(
            {(item.type, item.planet) for item in profile.calculated.mars_aspects},
            {("opposition", "Sun"), ("square", "Moon")},
        )
        ids = {item.id for item in profile.aspect_facts}
        self.assertTrue(any(item_id.startswith("mars_opposition_sun_l9_") for item_id in ids))
        self.assertTrue(any(item_id.startswith("mars_square_moon_l9_") for item_id in ids))
        self.assertTrue(any(item_id.startswith("mars_sun_bio_") for item_id in ids))
        self.assertFalse(any(item_id.startswith("mars_moon_bio_") for item_id in ids))
        sun_facts = [item for item in profile.aspect_facts if item.factor_key == "opposition_Sun"]
        moon_facts = [item for item in profile.aspect_facts if item.factor_key == "square_Moon"]
        self.assertTrue(sun_facts)
        self.assertTrue(moon_facts)
        self.assertTrue(all(item.provenance_key == "aspect:opposition_Sun" for item in sun_facts))
        self.assertTrue(all(item.provenance_key == "aspect:square_Moon" for item in moon_facts))
        self.assertIn("aspect:opposition_Sun", profile.coverage.covered_factors)
        self.assertIn("aspect:square_Moon", profile.coverage.covered_factors)
        self.assertIn(BIO_MOON_NOT_EXTRACTED_LIMITATION, profile.limitations)
        self.assertNotIn("hard_aspected", inspect.getsource(mars_profile_module))

    def test_vlad_harmonious_mercury_jupiter_bio_only(self):
        profile = build_mars_source_profile(**VLAD)
        self.assertEqual(
            {(item.type, item.planet) for item in profile.calculated.mars_aspects},
            {("trine", "Mercury"), ("sextile", "Jupiter")},
        )
        ids = {item.id for item in profile.aspect_facts}
        self.assertFalse(any("_l9_" in item_id for item_id in ids))
        self.assertTrue(any(item_id.startswith("mars_mercury_bio_") for item_id in ids))
        self.assertTrue(any(item_id.startswith("mars_jupiter_bio_") for item_id in ids))
        mercury = [item for item in profile.aspect_facts if item.factor_key == "trine_Mercury"]
        jupiter = [item for item in profile.aspect_facts if item.factor_key == "sextile_Jupiter"]
        self.assertEqual(
            [item.id for item in mercury],
            _work_ids(BIO_PAIR_PACKS["Mercury"]),
        )
        self.assertEqual(
            [item.id for item in jupiter],
            _work_ids(BIO_PAIR_PACKS["Jupiter"]),
        )
        self.assertTrue(all(item.provenance_key == "aspect:trine_Mercury" for item in mercury))
        self.assertTrue(all(item.provenance_key == "aspect:sextile_Jupiter" for item in jupiter))
        self.assertNotIn("mars_jupiter_bio_invents_strategies", {
            item.id for item in jupiter if "strategic_action" in item.tags
        })

    def test_dzmitry_harmonious_mercury_jupiter_bio_only(self):
        profile = build_mars_source_profile(**DZMITRY)
        self.assertEqual(
            {(item.type, item.planet) for item in profile.calculated.mars_aspects},
            {("sextile", "Mercury"), ("trine", "Jupiter")},
        )
        ids = {item.id for item in profile.aspect_facts}
        self.assertFalse(any("_l9_" in item_id for item_id in ids))
        self.assertTrue(any(item_id.startswith("mars_mercury_bio_") for item_id in ids))
        self.assertTrue(any(item_id.startswith("mars_jupiter_bio_") for item_id in ids))
        mercury = [item for item in profile.aspect_facts if item.factor_key == "sextile_Mercury"]
        jupiter = [item for item in profile.aspect_facts if item.factor_key == "trine_Jupiter"]
        self.assertTrue(all(item.provenance_key == "aspect:sextile_Mercury" for item in mercury))
        self.assertTrue(all(item.provenance_key == "aspect:trine_Jupiter" for item in jupiter))
        self.assertEqual(
            [item.id for item in mercury],
            _work_ids(BIO_PAIR_PACKS["Mercury"]),
        )
