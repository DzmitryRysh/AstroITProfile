"""Tests for Mercury House 1 Lesson 7 source parity (S4.20B)."""

from __future__ import annotations

import unittest
from collections import Counter

from app.schemas.mercury_work_profile import MercurySourceFactors
from app.services.mercury_human_copy import HUMAN_COPY_OVERRIDES
from app.services.mercury_human_copy_catalog import (
    APPROVED_RAW_FACT_IDS,
    NEEDS_REVIEW_FACT_IDS,
    STATUS_APPROVED_OVERRIDE,
    STATUS_APPROVED_RAW,
    STATUS_UNREVIEWED,
    build_catalog_entry,
    build_human_copy_catalog,
)
from app.services.mercury_source_knowledge import (
    ALL_SOURCE_FACTS,
    HOUSE_1,
    HOUSE_1_LESSON7,
    REF_H1,
    REF_H1_L7,
)
from app.services.mercury_source_profile import (
    _provenance_key,
    build_source_profile_from_factors,
    detect_repeated_signals,
)


EXPECTED_L7_IDS: tuple[str, ...] = (
    "h1_l7_very_high_communicativeness",
    "h1_l7_quick_situational_adjustment",
    "h1_l7_appears_younger_than_age_vs_peers",
    "h1_l7_active_curiosity",
    "h1_l7_initiative_in_contacts",
    "h1_l7_talkativeness",
    "h1_l7_liveliness",
    "h1_l7_bodily_mobility",
    "h1_l7_quick_wittedness",
    "h1_l7_precise_movements",
    "h1_l7_fast_movements",
    "h1_l7_expressive_gesticulation",
    "h1_l7_teaching_association",
    "h1_l7_commerce_association",
    "h1_l7_accounting_association",
    "h1_l7_secretary_association",
    "h1_l7_scientist_association",
    "h1_l7_mathematician_association",
    "h1_l7_impression_of_fussiness",
    "h1_l7_nervousness",
    "h1_l7_restlessness",
    "h1_l7_undirected_activity",
    "h1_l7_starts_but_does_not_complete_tasks",
    "h1_l7_logic_displaces_intuition",
    "h1_l7_excessive_talkativeness",
    "h1_l7_two_facedness",
    "h1_l7_youthfulness_leads_to_lack_of_respect",
)

EXPECTED_L7_CANONICAL: dict[str, str] = {
    "h1_l7_very_high_communicativeness": "Very high communicativeness.",
    "h1_l7_quick_situational_adjustment": (
        "Quickly adjusts or restructures according to the situation."
    ),
    "h1_l7_appears_younger_than_age_vs_peers": (
        "Appears younger than one's age, especially compared with peers."
    ),
    "h1_l7_active_curiosity": "Active curiosity.",
    "h1_l7_initiative_in_contacts": "Initiative in contacts.",
    "h1_l7_talkativeness": "Talkativeness.",
    "h1_l7_liveliness": "Liveliness.",
    "h1_l7_bodily_mobility": "Bodily mobility.",
    "h1_l7_quick_wittedness": "Quick-wittedness or mental resourcefulness.",
    "h1_l7_precise_movements": "Movements are precise.",
    "h1_l7_fast_movements": "Movements are fast.",
    "h1_l7_expressive_gesticulation": "Good or expressive gesticulation.",
    "h1_l7_teaching_association": "Favorable association with teaching.",
    "h1_l7_commerce_association": "Favorable association with commerce.",
    "h1_l7_accounting_association": "Favorable association with accounting.",
    "h1_l7_secretary_association": (
        "Favorable association with working in the role of secretary."
    ),
    "h1_l7_scientist_association": (
        "Favorable association with working in the role of scientist."
    ),
    "h1_l7_mathematician_association": (
        "Favorable association with working in the role of mathematician."
    ),
    "h1_l7_impression_of_fussiness": "May give an impression of fussiness.",
    "h1_l7_nervousness": "Nervousness.",
    "h1_l7_restlessness": "Restlessness.",
    "h1_l7_undirected_activity": "Activity may lack direction.",
    "h1_l7_starts_but_does_not_complete_tasks": (
        "May take on tasks but fail to bring them to completion."
    ),
    "h1_l7_logic_displaces_intuition": "Logic may displace intuition.",
    "h1_l7_excessive_talkativeness": "Excessive talkativeness.",
    "h1_l7_two_facedness": "Two-facedness or duplicity.",
    "h1_l7_youthfulness_leads_to_lack_of_respect": (
        "Youthful appearance or quality may lead to others not taking the person "
        "seriously."
    ),
}

FROZEN_BIO_HOUSE_1: tuple[tuple[str, str, str, str, tuple[str, ...], str], ...] = (
    (
        "h1_strengthens_mercury_functions",
        "thinking",
        "Strengthens Mercury functions overall.",
        "strength",
        ("amplifier",),
        REF_H1,
    ),
    (
        "h1_emphasizes_mercury_sign",
        "thinking",
        "Emphasizes the Mercury sign.",
        "neutral",
        ("amplifier", "sign_emphasis"),
        REF_H1,
    ),
    (
        "h1_emphasizes_mercury_aspects",
        "thinking",
        "Emphasizes Mercury aspects.",
        "neutral",
        ("amplifier", "aspect_emphasis"),
        REF_H1,
    ),
    (
        "h1_youthful_quality",
        "communication",
        "Youthful quality.",
        "neutral",
        ("youthful",),
        REF_H1,
    ),
    (
        "h1_outward_friendliness",
        "communication",
        "Outward friendliness / openness.",
        "strength",
        ("openness",),
        REF_H1,
    ),
    (
        "h1_increased_learnability",
        "learning",
        "Increased learnability.",
        "strength",
        ("learnability",),
        REF_H1,
    ),
    (
        "h1_quickness",
        "thinking",
        "Quickness.",
        "strength",
        ("quickness",),
        REF_H1,
    ),
    (
        "h1_multitasking",
        "thinking",
        "Multitasking.",
        "strength",
        ("multitasking",),
        REF_H1,
    ),
    (
        "h1_talkative_or_writing_tendency",
        "communication",
        "Increased talkativeness and increased writing tendency.",
        "neutral",
        ("talkative", "writing_tendency"),
        REF_H1,
    ),
    (
        "h1_special_relevance_siblings",
        "environment",
        "Special relevance of siblings.",
        "neutral",
        ("siblings",),
        REF_H1,
    ),
    (
        "h1_special_relevance_car_driving",
        "mobility",
        "Special relevance of car / driving.",
        "neutral",
        ("driving_relevance", "mobility"),
        REF_H1,
    ),
    (
        "h1_eventfulness_books",
        "environment",
        "Increased eventfulness connected with books.",
        "neutral",
        ("books",),
        REF_H1,
    ),
    (
        "h1_eventfulness_trips",
        "mobility",
        "Increased eventfulness connected with trips.",
        "neutral",
        ("trips", "mobility"),
        REF_H1,
    ),
    (
        "h1_eventfulness_social_networks",
        "environment",
        "Increased eventfulness connected with social networks.",
        "neutral",
        ("social_networks",),
        REF_H1,
    ),
    (
        "h1_support_intellectual_work",
        "work_application",
        "Support for intellectual profession and transport-related profession.",
        "strength",
        ("intellectual_work", "transport_profession"),
        REF_H1,
    ),
    (
        "h1_support_consultant_qualities",
        "work_application",
        "Support for consultant qualities.",
        "strength",
        ("consulting",),
        REF_H1,
    ),
    (
        "h1_support_sales_qualities",
        "work_application",
        "Support for sales qualities.",
        "strength",
        ("sales",),
        REF_H1,
    ),
)

FORBIDDEN_SPLIT_IDS = (
    "h1_l7_starts_tasks",
    "h1_l7_does_not_complete_tasks",
)

BROAD_TAGS_FORBIDDEN_ON_L7 = (
    "fast_thinking",
    "adaptability",
    "analytical_thinking",
    "technical_ability",
    "sales",
    "teaching",
    "mobility",
    "persuasion",
    "lying",
    "deception",
)


def _house_1_facts():
    return [
        item
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "house" and item.factor_key == "1"
    ]


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


class House1Lesson7CoverageTests(unittest.TestCase):
    def test_programmatic_l7_count_is_27(self):
        self.assertEqual(len(HOUSE_1_LESSON7), 27)
        self.assertEqual(len(EXPECTED_L7_IDS), 27)
        self.assertEqual(len(EXPECTED_L7_CANONICAL), 27)
        self.assertEqual(tuple(item.id for item in HOUSE_1_LESSON7), EXPECTED_L7_IDS)

    def test_house_1_source_counts(self):
        house_1 = _house_1_facts()
        bio = [item for item in house_1 if item.source_reference == REF_H1]
        lesson7 = [item for item in house_1 if item.source_reference == REF_H1_L7]
        self.assertEqual(len(HOUSE_1), 17)
        self.assertEqual(len(bio), 17)
        self.assertEqual(len(lesson7), 27)
        self.assertEqual(len(house_1), 44)
        self.assertEqual(len(HOUSE_1) + len(HOUSE_1_LESSON7), 44)

    def test_all_lesson7_use_lesson7_source_reference(self):
        self.assertTrue(
            all(item.source_reference == REF_H1_L7 for item in HOUSE_1_LESSON7)
        )
        self.assertEqual(REF_H1_L7, "lesson7_mercury_house_1")

    def test_all_house_1_facts_share_factor_identity(self):
        house_1 = _house_1_facts()
        self.assertEqual(len(house_1), 44)
        self.assertTrue(all(item.factor_type == "house" for item in house_1))
        self.assertTrue(all(item.factor_key == "1" for item in house_1))
        self.assertTrue(all(item.unresolved is False for item in house_1))
        self.assertTrue(all(item.activation_condition is None for item in house_1))

    def test_ids_globally_unique(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])


class House1Lesson7CanonicalTests(unittest.TestCase):
    def test_exact_canonical_strings_for_all_27(self):
        by_id = {item.id: item for item in HOUSE_1_LESSON7}
        self.assertEqual(set(by_id), set(EXPECTED_L7_CANONICAL))
        for fact_id, canonical in EXPECTED_L7_CANONICAL.items():
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].text, canonical)

    def test_starts_but_does_not_complete_kept_relational(self):
        by_id = {item.id: item for item in HOUSE_1_LESSON7}
        fact = by_id["h1_l7_starts_but_does_not_complete_tasks"]
        self.assertEqual(
            fact.text,
            "May take on tasks but fail to bring them to completion.",
        )
        self.assertEqual(fact.category, "risk")
        self.assertEqual(fact.polarity, "risk")
        self.assertEqual(fact.tags, ())

    def test_forbidden_split_ids_do_not_exist(self):
        all_ids = {item.id for item in ALL_SOURCE_FACTS}
        for fact_id in FORBIDDEN_SPLIT_IDS:
            with self.subTest(forbidden=fact_id):
                self.assertNotIn(fact_id, all_ids)

    def test_favorable_occupation_associations(self):
        by_id = {item.id: item for item in HOUSE_1_LESSON7}
        for fact_id in (
            "h1_l7_teaching_association",
            "h1_l7_commerce_association",
            "h1_l7_accounting_association",
            "h1_l7_secretary_association",
            "h1_l7_scientist_association",
            "h1_l7_mathematician_association",
        ):
            with self.subTest(occupation=fact_id):
                fact = by_id[fact_id]
                self.assertEqual(fact.category, "source_specific")
                self.assertEqual(fact.polarity, "strength")
                self.assertTrue(fact.text.startswith("Favorable association"))
                self.assertEqual(fact.tags, ())


class House1Lesson7TagGuardTests(unittest.TestCase):
    def test_talkativeness_neutral_has_talkative_tag_only(self):
        fact = next(item for item in HOUSE_1_LESSON7 if item.id == "h1_l7_talkativeness")
        self.assertEqual(fact.tags, ("talkative",))
        self.assertEqual(fact.polarity, "neutral")
        self.assertEqual(fact.category, "communication")

    def test_excessive_talkativeness_has_no_talkative_tag(self):
        fact = next(
            item for item in HOUSE_1_LESSON7 if item.id == "h1_l7_excessive_talkativeness"
        )
        self.assertNotIn("talkative", fact.tags)
        self.assertEqual(fact.tags, ())
        self.assertEqual(fact.category, "risk")
        self.assertEqual(fact.polarity, "risk")

    def test_commerce_has_no_sales_tag(self):
        fact = next(
            item for item in HOUSE_1_LESSON7 if item.id == "h1_l7_commerce_association"
        )
        self.assertNotIn("sales", fact.tags)
        self.assertEqual(fact.tags, ())

    def test_teaching_association_has_no_teaching_tag(self):
        fact = next(
            item for item in HOUSE_1_LESSON7 if item.id == "h1_l7_teaching_association"
        )
        self.assertNotIn("teaching", fact.tags)
        self.assertEqual(fact.tags, ())

    def test_scientist_has_no_analytical_or_scientific_thinking_tag(self):
        fact = next(
            item for item in HOUSE_1_LESSON7 if item.id == "h1_l7_scientist_association"
        )
        self.assertNotIn("analytical_thinking", fact.tags)
        self.assertNotIn("scientific_thinking", fact.tags)
        self.assertEqual(fact.tags, ())

    def test_bodily_mobility_has_no_travel_mobility_tag(self):
        fact = next(item for item in HOUSE_1_LESSON7 if item.id == "h1_l7_bodily_mobility")
        self.assertNotIn("mobility", fact.tags)
        self.assertEqual(fact.tags, ())
        self.assertEqual(fact.category, "source_specific")

    def test_quick_wittedness_has_no_fast_thinking_tag(self):
        fact = next(item for item in HOUSE_1_LESSON7 if item.id == "h1_l7_quick_wittedness")
        self.assertNotIn("fast_thinking", fact.tags)
        self.assertNotIn("analytical_thinking", fact.tags)
        self.assertNotIn("technical_ability", fact.tags)
        self.assertEqual(fact.tags, ())

    def test_no_approximate_broad_tags_on_any_l7_fact(self):
        for item in HOUSE_1_LESSON7:
            with self.subTest(fact_id=item.id):
                for tag in BROAD_TAGS_FORBIDDEN_ON_L7:
                    if item.id == "h1_l7_talkativeness" and tag == "talkative":
                        continue
                    self.assertNotIn(tag, item.tags)
                if item.id != "h1_l7_talkativeness":
                    self.assertEqual(item.tags, ())

    def test_quick_situational_adjustment_has_no_adaptability_or_fast_thinking(self):
        fact = next(
            item
            for item in HOUSE_1_LESSON7
            if item.id == "h1_l7_quick_situational_adjustment"
        )
        self.assertNotIn("fast_thinking", fact.tags)
        self.assertNotIn("adaptability", fact.tags)
        self.assertEqual(fact.tags, ())


class House1BioFrozenTests(unittest.TestCase):
    def test_existing_17_bio_facts_unchanged(self):
        self.assertEqual(len(HOUSE_1), 17)
        self.assertEqual(len(FROZEN_BIO_HOUSE_1), 17)
        actual = tuple(
            (
                item.id,
                item.category,
                item.text,
                item.polarity,
                item.tags,
                item.source_reference,
            )
            for item in HOUSE_1
        )
        self.assertEqual(actual, FROZEN_BIO_HOUSE_1)
        self.assertTrue(all(item.activation_condition is None for item in HOUSE_1))
        self.assertTrue(all(item.unresolved is False for item in HOUSE_1))
        self.assertTrue(all(item.factor_type == "house" for item in HOUSE_1))
        self.assertTrue(all(item.factor_key == "1" for item in HOUSE_1))


class House1RepeatSafetyTests(unittest.TestCase):
    def test_bio_and_lesson7_share_one_provenance_key(self):
        house_1 = _house_1_facts()
        keys = {_provenance_key(item) for item in house_1}
        self.assertEqual(keys, {"house:1"})
        bio = next(item for item in HOUSE_1 if item.id == "h1_talkative_or_writing_tendency")
        l7 = next(item for item in HOUSE_1_LESSON7 if item.id == "h1_l7_talkativeness")
        self.assertEqual(_provenance_key(bio), "house:1")
        self.assertEqual(_provenance_key(l7), "house:1")
        self.assertIn("talkative", bio.tags)
        self.assertIn("talkative", l7.tags)

    def test_house_1_dual_source_cannot_create_repeat_alone(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign=None,
                mercury_element=None,
                mercury_motion="direct",
                mercury_house=1,
                aspects=[],
            )
        )
        self.assertEqual(len(profile.house_facts), 44)
        self.assertTrue(all(item.factor_key == "1" for item in profile.house_facts))
        self.assertIn("h1_talkative_or_writing_tendency", _ids(profile.house_facts))
        self.assertIn("h1_l7_talkativeness", _ids(profile.house_facts))
        repeats = detect_repeated_signals(profile.house_facts)
        self.assertEqual(repeats, [])
        for signal in repeats:
            house_sources = [src for src in signal.sources if src.startswith("house:")]
            self.assertLessEqual(len(house_sources), 1, signal)


class House1HumanCopyInventoryConsequenceTests(unittest.TestCase):
    L7_APPROVED_RAW: tuple[str, ...] = (
        "h1_l7_impression_of_fussiness",
        "h1_l7_undirected_activity",
        "h1_l7_starts_but_does_not_complete_tasks",
        "h1_l7_logic_displaces_intuition",
        "h1_l7_youthfulness_leads_to_lack_of_respect",
    )

    def test_new_l7_facts_are_reviewed_and_ready(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        raw_ids = set(self.L7_APPROVED_RAW)
        for fact_id in EXPECTED_L7_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertNotEqual(entry.review_status, STATUS_UNREVIEWED)
                if fact_id in raw_ids:
                    self.assertIn(fact_id, APPROVED_RAW_FACT_IDS)
                    self.assertNotIn(fact_id, HUMAN_COPY_OVERRIDES)
                    self.assertEqual(entry.review_status, STATUS_APPROVED_RAW)
                    self.assertEqual(entry.human_text, by_id[fact_id].text)
                else:
                    self.assertIn(fact_id, HUMAN_COPY_OVERRIDES)
                    self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)
                    self.assertEqual(entry.review_status, STATUS_APPROVED_OVERRIDE)

    def test_house_1_family_counts_after_l7_human_copy(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "house:1")
        self.assertEqual(family.total_facts, 44)
        self.assertEqual(family.approved_override, 39)
        self.assertEqual(family.approved_raw, 5)
        self.assertEqual(family.needs_review, 0)
        self.assertEqual(family.unreviewed, 0)
        self.assertEqual(family.reviewed_count, 44)
        self.assertEqual(family.presentation_ready_count, 44)

    def test_existing_bio_human_copy_decisions_unchanged(self):
        bio_ids = {item.id for item in HOUSE_1}
        self.assertEqual(len(bio_ids), 17)
        for fact_id in bio_ids:
            with self.subTest(bio_id=fact_id):
                self.assertIn(fact_id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)


class House1SemanticLedgerTests(unittest.TestCase):
    def test_semantic_accounting_from_implemented_facts(self):
        bio_count = len(HOUSE_1)
        l7_count = len(HOUSE_1_LESSON7)
        exact_overlap = 1  # talkativeness
        partial_overlap = 1  # youthful quality vs age/peer comparison
        unique_l7 = l7_count - exact_overlap - partial_overlap
        unique_meanings = bio_count + unique_l7 + partial_overlap
        self.assertEqual(bio_count, 17)
        self.assertEqual(l7_count, 27)
        self.assertEqual(unique_l7, 25)
        self.assertEqual(unique_meanings, 43)
        self.assertEqual(bio_count + l7_count, 44)
        self.assertEqual(
            {item.id for item in HOUSE_1 if "talkative" in item.tags},
            {"h1_talkative_or_writing_tendency"},
        )
        self.assertEqual(
            {item.id for item in HOUSE_1_LESSON7 if "talkative" in item.tags},
            {"h1_l7_talkativeness"},
        )


if __name__ == "__main__":
    unittest.main()
