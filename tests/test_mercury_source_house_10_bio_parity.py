"""Tests for Mercury House 10 Bioastrology source parity (S4.29B)."""

from __future__ import annotations

import unittest
from collections import Counter

from app.schemas.mercury_work_profile import MercurySourceFactors
from app.services.mercury_human_copy import HUMAN_COPY_OVERRIDES
from app.services.mercury_human_copy_catalog import (
    APPROVED_RAW_FACT_IDS,
    NEEDS_REVIEW_FACT_IDS,
    STATUS_UNREVIEWED,
    build_catalog_entry,
    build_human_copy_catalog,
)
from app.services.mercury_source_knowledge import (
    ALL_SOURCE_FACTS,
    HOUSE_10,
    HOUSE_10_BIO,
    REF_H10,
    REF_H10_BIO,
    REPEATED_SIGNAL_SPECS,
)
from app.services.mercury_source_profile import (
    _provenance_key,
    build_source_profile_from_factors,
    detect_repeated_signals,
)


EXPECTED_BIO_IDS: tuple[str, ...] = (
    "h10_bio_communication_learning_strengthened_overall",
    "h10_bio_communication_learning_demanded_in_career",
    "h10_bio_communication_learning_demanded_in_business",
    "h10_bio_intellectual_transport_profession",
    "h10_bio_consultant_qualities",
    "h10_bio_sales_qualities",
    "h10_bio_scientist_role",
    "h10_bio_politician_role",
    "h10_bio_intellect_becomes_grounded",
    "h10_bio_intellect_becomes_conservative",
    "h10_bio_intellect_becomes_socially_conditioned",
    "h10_bio_parallel_work_business_directions",
    "h10_bio_work_with_siblings",
    "h10_bio_work_with_younger_people",
    "h10_bio_popularity_fame",
    "h10_bio_afflicted_seen_as_student",
    "h10_bio_afflicted_seen_as_servant",
)

EXPECTED_BIO_CANONICAL: dict[str, str] = {
    "h10_bio_communication_learning_strengthened_overall": (
        "Communication and learning functions may be strengthened overall."
    ),
    "h10_bio_communication_learning_demanded_in_career": (
        "Communication and learning may be especially demanded in career contexts."
    ),
    "h10_bio_communication_learning_demanded_in_business": (
        "Communication and learning may be especially demanded in business contexts."
    ),
    "h10_bio_intellectual_transport_profession": (
        "Favorable association with intellectual and transport-related professions."
    ),
    "h10_bio_consultant_qualities": (
        "May support qualities associated with consulting."
    ),
    "h10_bio_sales_qualities": "May support qualities associated with sales.",
    "h10_bio_scientist_role": (
        "May support qualities associated with a scientist role."
    ),
    "h10_bio_politician_role": (
        "May support qualities associated with a politician role."
    ),
    "h10_bio_intellect_becomes_grounded": (
        "Over time, circumstances may make the intellect more grounded and down-to-earth."
    ),
    "h10_bio_intellect_becomes_conservative": (
        "Over time, circumstances may make the intellect more conservative."
    ),
    "h10_bio_intellect_becomes_socially_conditioned": (
        "Over time, circumstances may make the intellect more socially conditioned."
    ),
    "h10_bio_parallel_work_business_directions": (
        "There may be several parallel directions in work or business."
    ),
    "h10_bio_work_with_siblings": "Work may involve siblings.",
    "h10_bio_work_with_younger_people": "Work may involve younger people.",
    "h10_bio_popularity_fame": (
        "Favorable association with popularity and public recognition."
    ),
    "h10_bio_afflicted_seen_as_student": (
        "When Mercury is afflicted, the source describes a social perception of the "
        "person only in a student role (afflicted-Mercury dependency; no house-affliction "
        "resolver is applied; not hard_aspected)."
    ),
    "h10_bio_afflicted_seen_as_servant": (
        "When Mercury is afflicted, the source describes a social perception of the "
        "person only in a servant role (afflicted-Mercury dependency; no house-affliction "
        "resolver is applied; not hard_aspected)."
    ),
}

EXPECTED_BIO_TAGS: dict[str, tuple[str, ...]] = {
    "h10_bio_intellectual_transport_profession": (
        "intellectual_work",
        "transport_profession",
    ),
    "h10_bio_consultant_qualities": ("consulting",),
    "h10_bio_sales_qualities": ("sales",),
}

UNTAGGED_ORDINARY_BIO_IDS: tuple[str, ...] = tuple(
    fact_id
    for fact_id in EXPECTED_BIO_IDS
    if fact_id not in EXPECTED_BIO_TAGS
    and not fact_id.startswith("h10_bio_afflicted_")
)

AFFLICTED_BIO_IDS: tuple[str, ...] = (
    "h10_bio_afflicted_seen_as_student",
    "h10_bio_afflicted_seen_as_servant",
)

DEMAND_BIO_IDS: tuple[str, ...] = (
    "h10_bio_communication_learning_strengthened_overall",
    "h10_bio_communication_learning_demanded_in_career",
    "h10_bio_communication_learning_demanded_in_business",
)

ROLE_BIO_IDS: tuple[str, ...] = (
    "h10_bio_scientist_role",
    "h10_bio_politician_role",
)

INTELLECT_CHANGE_BIO_IDS: tuple[str, ...] = (
    "h10_bio_intellect_becomes_grounded",
    "h10_bio_intellect_becomes_conservative",
    "h10_bio_intellect_becomes_socially_conditioned",
)

WORK_CONTEXT_BIO_IDS: tuple[str, ...] = (
    "h10_bio_work_with_siblings",
    "h10_bio_work_with_younger_people",
)

FORBIDDEN_APPROXIMATE_TAGS: tuple[str, ...] = (
    "amplifier",
    "large_information_load",
    "leadership_communication",
    "science_interest",
    "research_talent",
    "analytical_thinking",
    "technical_ability",
    "persuasion",
    "leadership",
    "practical_thinking",
    "siblings",
    "teaching",
    "prestige_orientation",
    "intellectual_reputation",
    "career_change",
)

FROZEN_L7_HOUSE_10: tuple[
    tuple[str, str, str, str, tuple[str, ...], str, bool], ...
] = (
    (
        "h10_reputation_exceptional_intellect",
        "work_application",
        "Reputation of a person of exceptional intellect.",
        "strength",
        ("intellectual_reputation",),
        REF_H10,
        False,
    ),
    (
        "h10_democratic_relationship_with_leadership",
        "work_application",
        "Democratic relationship with leadership based on shared intellectual interests.",
        "strength",
        ("leadership_communication",),
        REF_H10,
        False,
    ),
    (
        "h10_mission_informing_people",
        "work_application",
        "Mission / role of informing people.",
        "strength",
        ("informing_people",),
        REF_H10,
        False,
    ),
    (
        "h10_career_requires_communication_tools",
        "work_application",
        "Career success may require mastering communication tools.",
        "neutral",
        ("leadership_communication",),
        REF_H10,
        False,
    ),
    (
        "h10_career_requires_large_information_volumes",
        "work_application",
        "Career success may require processing very large information volumes.",
        "neutral",
        ("large_information_load",),
        REF_H10,
        False,
    ),
    (
        "h10_information_load_can_be_difficult",
        "risk",
        "That information load can be difficult.",
        "risk",
        ("large_information_load",),
        REF_H10,
        False,
    ),
    (
        "h10_knowledge_for_prestige_not_curiosity",
        "risk",
        "Knowledge may be pursued for benefit / prestige / honor rather than curiosity.",
        "risk",
        ("prestige_orientation",),
        REF_H10,
        False,
    ),
    (
        "h10_many_connections_reduced_independence",
        "environment",
        "Many connections but reduced independence.",
        "risk",
        ("reduced_independence",),
        REF_H10,
        False,
    ),
    (
        "h10_frequent_change_of_work",
        "work_application",
        "Frequent change of work activity.",
        "neutral",
        ("career_change",),
        REF_H10,
        False,
    ),
    (
        "h10_may_change_professions_until_interesting_prestigious",
        "work_application",
        'May change professions until finding "interesting + prestigious".',
        "neutral",
        ("career_change", "prestige_orientation"),
        REF_H10,
        False,
    ),
    (
        "h10_interest_in_ranks",
        "work_application",
        "Interest in ranks.",
        "neutral",
        ("prestige_orientation",),
        REF_H10,
        False,
    ),
    (
        "h10_interest_in_titles",
        "work_application",
        "Interest in titles.",
        "neutral",
        ("prestige_orientation",),
        REF_H10,
        False,
    ),
    (
        "h10_interest_in_distinctions_status_markers",
        "work_application",
        "Interest in distinctions / status markers.",
        "neutral",
        ("prestige_orientation",),
        REF_H10,
        False,
    ),
)


def _house_10_facts():
    return [
        item
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "house" and item.factor_key == "10"
    ]


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


class House10BioCoverageTests(unittest.TestCase):
    def test_programmatic_bio_count_is_17(self):
        self.assertEqual(len(HOUSE_10_BIO), 17)
        self.assertEqual(len(EXPECTED_BIO_IDS), 17)
        self.assertEqual(len(EXPECTED_BIO_CANONICAL), 17)
        self.assertEqual(tuple(item.id for item in HOUSE_10_BIO), EXPECTED_BIO_IDS)

    def test_house_10_source_counts(self):
        house_10 = _house_10_facts()
        lesson7 = [item for item in house_10 if item.source_reference == REF_H10]
        bio = [item for item in house_10 if item.source_reference == REF_H10_BIO]
        self.assertEqual(len(HOUSE_10), 13)
        self.assertEqual(len(lesson7), 13)
        self.assertEqual(len(bio), 17)
        self.assertEqual(len(house_10), 30)
        self.assertEqual(len(HOUSE_10) + len(HOUSE_10_BIO), 30)

    def test_all_bio_use_bioastrology_source_reference(self):
        self.assertTrue(all(item.source_reference == REF_H10_BIO for item in HOUSE_10_BIO))
        self.assertEqual(REF_H10_BIO, "bioastrology_mercury_house_10")

    def test_all_house_10_facts_share_factor_identity(self):
        house_10 = _house_10_facts()
        self.assertEqual(len(house_10), 30)
        self.assertTrue(all(item.factor_type == "house" for item in house_10))
        self.assertTrue(all(item.factor_key == "10" for item in house_10))
        self.assertTrue(all(item.activation_condition is None for item in house_10))
        self.assertTrue(all(item.unresolved is False for item in HOUSE_10))
        ordinary_bio = [item for item in HOUSE_10_BIO if not item.unresolved]
        self.assertEqual(len(ordinary_bio), 15)
        self.assertTrue(all(item.unresolved is False for item in ordinary_bio))

    def test_ids_globally_unique(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])


class House10BioCanonicalTests(unittest.TestCase):
    def test_exact_canonical_strings_for_all_17(self):
        by_id = {item.id: item for item in HOUSE_10_BIO}
        self.assertEqual(set(by_id), set(EXPECTED_BIO_CANONICAL))
        for fact_id, canonical in EXPECTED_BIO_CANONICAL.items():
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].text, canonical)


class House10PartialFidelityTests(unittest.TestCase):
    def test_career_demand_is_not_communication_tools_or_information_volumes(self):
        by_id = {item.id: item for item in HOUSE_10 + HOUSE_10_BIO}
        bio = by_id["h10_bio_communication_learning_demanded_in_career"]
        tools = by_id["h10_career_requires_communication_tools"]
        volumes = by_id["h10_career_requires_large_information_volumes"]
        self.assertNotEqual(bio.text, tools.text)
        self.assertNotEqual(bio.text, volumes.text)
        self.assertIn("demanded", bio.text.lower())
        self.assertNotIn("large_information_load", bio.tags)
        self.assertNotIn("leadership_communication", bio.tags)


class House10AtomizationTests(unittest.TestCase):
    def test_overall_career_and_business_demand_atoms_remain_separate(self):
        by_id = {item.id: item for item in HOUSE_10_BIO}
        texts = {by_id[fact_id].text for fact_id in DEMAND_BIO_IDS}
        self.assertEqual(len(texts), 3)

    def test_scientist_and_politician_roles_remain_separate(self):
        by_id = {item.id: item for item in HOUSE_10_BIO}
        scientist = by_id["h10_bio_scientist_role"]
        politician = by_id["h10_bio_politician_role"]
        self.assertNotEqual(scientist.text, politician.text)

    def test_three_intellect_change_atoms_remain_separate(self):
        by_id = {item.id: item for item in HOUSE_10_BIO}
        texts = {by_id[fact_id].text for fact_id in INTELLECT_CHANGE_BIO_IDS}
        self.assertEqual(len(texts), 3)

    def test_parallel_directions_is_not_sequential_change(self):
        by_id = {item.id: item for item in HOUSE_10 + HOUSE_10_BIO}
        parallel = by_id["h10_bio_parallel_work_business_directions"]
        frequent = by_id["h10_frequent_change_of_work"]
        professions = by_id["h10_may_change_professions_until_interesting_prestigious"]
        self.assertNotEqual(parallel.text, frequent.text)
        self.assertNotEqual(parallel.text, professions.text)
        self.assertIn("parallel", parallel.text.lower())

    def test_work_with_siblings_and_younger_people_remain_separate(self):
        by_id = {item.id: item for item in HOUSE_10_BIO}
        siblings = by_id["h10_bio_work_with_siblings"]
        younger = by_id["h10_bio_work_with_younger_people"]
        self.assertNotEqual(siblings.text, younger.text)

    def test_afflicted_student_and_servant_perceptions_remain_separate(self):
        by_id = {item.id: item for item in HOUSE_10_BIO}
        student = by_id["h10_bio_afflicted_seen_as_student"]
        servant = by_id["h10_bio_afflicted_seen_as_servant"]
        self.assertNotEqual(student.text, servant.text)
        self.assertIn("student role", student.text.lower())
        self.assertIn("servant role", servant.text.lower())


class House10ServantSourceFidelityTests(unittest.TestCase):
    def test_servant_canonical_uses_servant_not_subordinate(self):
        servant = next(
            item for item in HOUSE_10_BIO if item.id == "h10_bio_afflicted_seen_as_servant"
        )
        self.assertIn("servant role", servant.text.lower())
        self.assertNotIn("subordinate", servant.text.lower())


class House10BioTagGuardTests(unittest.TestCase):
    def test_exact_tags_on_profession_role_atoms(self):
        by_id = {item.id: item for item in HOUSE_10_BIO}
        self.assertEqual(
            by_id["h10_bio_intellectual_transport_profession"].tags,
            ("intellectual_work", "transport_profession"),
        )
        self.assertEqual(by_id["h10_bio_consultant_qualities"].tags, ("consulting",))
        self.assertEqual(by_id["h10_bio_sales_qualities"].tags, ("sales",))

    def test_ordinary_bio_facts_have_no_approximate_tags(self):
        by_id = {item.id: item for item in HOUSE_10_BIO}
        for fact_id in UNTAGGED_ORDINARY_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].tags, ())
                for tag in FORBIDDEN_APPROXIMATE_TAGS:
                    self.assertNotIn(tag, by_id[fact_id].tags)

    def test_strengthened_overall_has_no_amplifier_tag(self):
        fact = next(
            item
            for item in HOUSE_10_BIO
            if item.id == "h10_bio_communication_learning_strengthened_overall"
        )
        self.assertNotIn("amplifier", fact.tags)

    def test_afflicted_atoms_have_no_tags(self):
        by_id = {item.id: item for item in HOUSE_10_BIO}
        for fact_id in AFFLICTED_BIO_IDS:
            self.assertEqual(by_id[fact_id].tags, ())

    def test_no_new_repeated_signal_spec(self):
        tags = {spec["tag"] for spec in REPEATED_SIGNAL_SPECS}
        self.assertIn("sales", tags)
        self.assertNotIn("consulting", tags)
        self.assertNotIn("intellectual_work", tags)
        self.assertNotIn("transport_profession", tags)
        sales_specs = [spec for spec in REPEATED_SIGNAL_SPECS if spec["tag"] == "sales"]
        self.assertEqual(len(sales_specs), 1)


class House10ConditionalSafetyTests(unittest.TestCase):
    def test_afflicted_atoms_are_unresolved_without_hard_aspected(self):
        by_id = {item.id: item for item in HOUSE_10_BIO}
        for fact_id in AFFLICTED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                fact = by_id[fact_id]
                self.assertEqual(fact.category, "source_specific")
                self.assertEqual(fact.polarity, "conditional")
                self.assertIsNone(fact.activation_condition)
                self.assertNotEqual(fact.activation_condition, "hard_aspected")
                self.assertTrue(fact.unresolved)
                self.assertIn("not hard_aspected", fact.text)


class House10Lesson7FrozenTests(unittest.TestCase):
    def test_existing_13_lesson7_facts_unchanged(self):
        self.assertEqual(len(HOUSE_10), 13)
        self.assertEqual(len(FROZEN_L7_HOUSE_10), 13)
        actual = tuple(
            (
                item.id,
                item.category,
                item.text,
                item.polarity,
                item.tags,
                item.source_reference,
                item.unresolved,
            )
            for item in HOUSE_10
        )
        self.assertEqual(actual, FROZEN_L7_HOUSE_10)


class House10SameHouseSourceDedupTests(unittest.TestCase):
    def test_lesson7_and_bio_share_one_provenance_key(self):
        house_10 = _house_10_facts()
        keys = {_provenance_key(item) for item in house_10}
        self.assertEqual(keys, {"house:10"})

    def test_house_10_tagged_bio_facts_do_not_create_same_house_repeats(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Sagittarius",
                mercury_element="fire",
                mercury_motion="direct",
                mercury_house=10,
                aspects=[],
            )
        )
        self.assertEqual(len(profile.house_facts), 30)
        repeats = detect_repeated_signals(profile.house_facts)
        self.assertEqual(repeats, [])


class House10HumanCopyInventoryConsequenceTests(unittest.TestCase):
    def test_new_bio_facts_are_unreviewed_and_not_in_registries(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        for fact_id in EXPECTED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertNotIn(fact_id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_UNREVIEWED)

    def test_house_10_family_counts_after_source_parity(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "house:10")
        self.assertEqual(family.total_facts, 30)
        self.assertEqual(family.unreviewed, 30)
        self.assertEqual(family.reviewed_count, 0)
        self.assertEqual(family.presentation_ready_count, 0)
        self.assertEqual(family.needs_review, 0)


class House10SemanticLedgerTests(unittest.TestCase):
    def test_semantic_accounting_from_implemented_facts(self):
        l7_count = len(HOUSE_10)
        bio_count = len(HOUSE_10_BIO)
        exact_overlap = 0
        partial_overlap = 1
        conditional_unresolved = 2
        unique_bio = bio_count - exact_overlap - partial_overlap - conditional_unresolved
        unique_meanings = l7_count + bio_count - exact_overlap
        self.assertEqual(l7_count, 13)
        self.assertEqual(bio_count, 17)
        self.assertEqual(exact_overlap, 0)
        self.assertEqual(partial_overlap, 1)
        self.assertEqual(unique_bio, 14)
        self.assertEqual(conditional_unresolved, 2)
        self.assertEqual(unique_meanings, 30)
        self.assertEqual(
            exact_overlap + partial_overlap + unique_bio + conditional_unresolved,
            17,
        )


class House10PopularityDistinctTests(unittest.TestCase):
    def test_popularity_is_not_exceptional_intellect_reputation(self):
        by_id = {item.id: item for item in HOUSE_10 + HOUSE_10_BIO}
        bio = by_id["h10_bio_popularity_fame"]
        l7 = by_id["h10_reputation_exceptional_intellect"]
        self.assertNotEqual(bio.text, l7.text)
        self.assertNotIn("intellectual_reputation", bio.tags)
        self.assertNotIn("prestige_orientation", bio.tags)


if __name__ == "__main__":
    unittest.main()
