"""Tests for Mercury House 11 Bioastrology source parity (S4.30B)."""

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
from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS, REPEATED_SIGNAL_SPECS
from app.services.mercury_source_knowledge_b3_houses import (
    HOUSE_11,
    HOUSE_11_BIO,
    REF_H11_BIO,
    REF_H11_L7,
)
from app.services.mercury_source_profile import (
    _provenance_key,
    build_source_profile_from_factors,
    detect_repeated_signals,
)


EXPECTED_BIO_IDS: tuple[str, ...] = (
    "h11_bio_communication_learning_realized_through_internet",
    "h11_bio_communication_learning_realized_through_collectives",
    "h11_bio_communication_learning_realized_through_clubs",
    "h11_bio_communication_learning_realized_through_gatherings",
    "h11_bio_communication_learning_realized_through_forums",
    "h11_bio_intellect_becomes_scientific",
    "h11_bio_intellect_becomes_technological",
    "h11_bio_universal_intellect",
    "h11_bio_learning_oriented_toward_high_technologies",
    "h11_bio_learning_with_equals_or_peers",
    "h11_bio_learning_with_friends",
    "h11_bio_learning_in_group_or_collective",
    "h11_bio_broad_social_popularity",
    "h11_bio_many_discussed_plans",
    "h11_bio_many_discussed_projects",
)

EXPECTED_BIO_CANONICAL: dict[str, str] = {
    "h11_bio_communication_learning_realized_through_internet": (
        "Communication and learning may be realized through the Internet."
    ),
    "h11_bio_communication_learning_realized_through_collectives": (
        "Communication and learning may be realized through collectives or groups."
    ),
    "h11_bio_communication_learning_realized_through_clubs": (
        "Communication and learning may be realized through clubs."
    ),
    "h11_bio_communication_learning_realized_through_gatherings": (
        "Communication and learning may be realized through gatherings or meetings."
    ),
    "h11_bio_communication_learning_realized_through_forums": (
        "Communication and learning may be realized through forums."
    ),
    "h11_bio_intellect_becomes_scientific": (
        "Over time, the intellect may become more scientific in orientation."
    ),
    "h11_bio_intellect_becomes_technological": (
        "Over time, the intellect may become more technological in orientation."
    ),
    "h11_bio_universal_intellect": (
        "Source describes a broadly universal intellect with an ability to learn "
        "across many subjects."
    ),
    "h11_bio_learning_oriented_toward_high_technologies": (
        "Learning may be especially oriented toward high technologies."
    ),
    "h11_bio_learning_with_equals_or_peers": (
        "Learning may occur with or through equals or peers."
    ),
    "h11_bio_learning_with_friends": (
        "Learning may occur with or through friends."
    ),
    "h11_bio_learning_in_group_or_collective": (
        "Learning may occur in a group or collective setting."
    ),
    "h11_bio_broad_social_popularity": (
        "Favorable association with broad social popularity."
    ),
    "h11_bio_many_discussed_plans": (
        "There may be a large number of discussed plans."
    ),
    "h11_bio_many_discussed_projects": (
        "There may be a large number of discussed projects."
    ),
}

REALIZATION_BIO_IDS: tuple[str, ...] = (
    "h11_bio_communication_learning_realized_through_internet",
    "h11_bio_communication_learning_realized_through_collectives",
    "h11_bio_communication_learning_realized_through_clubs",
    "h11_bio_communication_learning_realized_through_gatherings",
    "h11_bio_communication_learning_realized_through_forums",
)

LEARNING_RELATION_BIO_IDS: tuple[str, ...] = (
    "h11_bio_learning_with_equals_or_peers",
    "h11_bio_learning_with_friends",
    "h11_bio_learning_in_group_or_collective",
)

FORBIDDEN_APPROXIMATE_TAGS: tuple[str, ...] = (
    "scientific_thinking_context",
    "science_interest",
    "technical_ability",
    "technical_thinking",
    "analytical_thinking",
    "research_talent",
    "universal_mind",
    "lifelong_learning",
    "quick_learning",
    "friends_as_knowledge_source",
    "groups_as_knowledge_source",
    "social_impulse_to_learning",
    "recognition_seeking",
    "prestige_orientation",
    "planning",
    "project_management",
)

L7_PARTIAL_NEIGHBOR_IDS: frozenset[str] = frozenset(
    {
        "h11_groups_are_sources_of_knowledge",
        "h11_friends_are_sources_of_knowledge",
        "h11_scientific_type_of_thinking_context",
        "h11_universal_mind",
    }
)

FROZEN_L7_HOUSE_11: tuple[
    tuple[str, str, str, str, tuple[str, ...], str, bool], ...
] = (
    (
        "h11_constant_social_interaction",
        "environment",
        "Constant social interaction.",
        "neutral",
        ("constant_social_interaction",),
        REF_H11_L7,
        False,
    ),
    (
        "h11_learn_yourself",
        "learning",
        "Learn yourself.",
        "strength",
        ("self_learning",),
        REF_H11_L7,
        False,
    ),
    (
        "h11_teach_others",
        "learning",
        "Teach others (House 11 social-learning context; not equated with global teaching "
        "ability).",
        "neutral",
        ("teaching_others",),
        REF_H11_L7,
        False,
    ),
    (
        "h11_friends_are_sources_of_knowledge",
        "learning",
        "Friends are sources of knowledge.",
        "strength",
        ("friends_as_knowledge_source",),
        REF_H11_L7,
        False,
    ),
    (
        "h11_groups_are_sources_of_knowledge",
        "learning",
        "Collectives / groups are sources of knowledge.",
        "strength",
        ("groups_as_knowledge_source",),
        REF_H11_L7,
        False,
    ),
    (
        "h11_social_impulse_to_study",
        "learning",
        "Friends / groups create an impulse to study.",
        "neutral",
        ("social_impulse_to_learning",),
        REF_H11_L7,
        False,
    ),
    (
        "h11_scientific_type_of_thinking_context",
        "thinking",
        "Circumstances create a scientific type / style of thinking.",
        "strength",
        ("scientific_thinking_context",),
        REF_H11_L7,
        False,
    ),
    (
        "h11_democratic_contact_regardless_of_status",
        "communication",
        "Democratic contact regardless of social status.",
        "strength",
        ("status_independent_democratic_contact",),
        REF_H11_L7,
        False,
    ),
    (
        "h11_universal_mind",
        "thinking",
        "Universal mind (source-described cognition statement).",
        "strength",
        ("universal_mind",),
        REF_H11_L7,
        False,
    ),
    (
        "h11_pioneer_inventor_reformer_associations",
        "source_specific",
        "Source associations include pioneers, inventors, and reformers; archetypal / "
        "occupation associations, not automatic professional abilities.",
        "neutral",
        ("pioneer_inventor_reformer_associations",),
        REF_H11_L7,
        False,
    ),
    (
        "h11_many_quick_acquaintances",
        "environment",
        "Many quick acquaintances.",
        "neutral",
        ("rapid_acquaintance_formation",),
        REF_H11_L7,
        False,
    ),
    (
        "h11_acquaintances_for_exchanging_advice_and_ideas",
        "communication",
        "Purpose of acquaintances: exchanging advice and ideas.",
        "neutral",
        ("advice_idea_exchange_contacts",),
        REF_H11_L7,
        False,
    ),
    (
        "h11_empty_pointless_acquaintances",
        "risk",
        "Empty / pointless acquaintances.",
        "risk",
        ("empty_contact_risk",),
        REF_H11_L7,
        False,
    ),
    (
        "h11_unpromising_acquaintances",
        "risk",
        "Unpromising acquaintances.",
        "risk",
        ("unpromising_contact_risk",),
        REF_H11_L7,
        False,
    ),
    (
        "h11_fierce_bitter_arguments",
        "risk",
        "Fierce / bitter arguments.",
        "risk",
        ("fierce_arguments",),
        REF_H11_L7,
        False,
    ),
    (
        "h11_fierce_bitter_discussions",
        "risk",
        "Fierce / bitter discussions.",
        "risk",
        ("fierce_discussions",),
        REF_H11_L7,
        False,
    ),
    (
        "h11_gossip_from_friends",
        "source_specific",
        "Gossip from friends (friend / social-environment association, not a native trait).",
        "risk",
        ("friend_gossip_risk",),
        REF_H11_L7,
        False,
    ),
    (
        "h11_lying_from_friends",
        "source_specific",
        "Lying from friends (friend / social-environment association, not a native trait).",
        "risk",
        ("friend_lying_risk",),
        REF_H11_L7,
        False,
    ),
    (
        "h11_deception_from_friends",
        "source_specific",
        "Deception from friends (friend / social-environment association, not a native trait).",
        "risk",
        ("friend_deception_risk",),
        REF_H11_L7,
        False,
    ),
    (
        "h11_meaningless_plans",
        "risk",
        "Meaningless plans.",
        "risk",
        ("meaningless_plan_risk",),
        REF_H11_L7,
        False,
    ),
    (
        "h11_meaningless_projects",
        "risk",
        "Meaningless projects.",
        "risk",
        ("meaningless_project_risk",),
        REF_H11_L7,
        False,
    ),
    (
        "h11_plans_projects_detached_from_reality",
        "risk",
        "Plans / projects detached from reality.",
        "risk",
        ("reality_detached_project_risk",),
        REF_H11_L7,
        False,
    ),
)


def _house_11_facts():
    return [
        item
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "house" and item.factor_key == "11"
    ]


class House11BioCoverageTests(unittest.TestCase):
    def test_programmatic_bio_count_is_15(self):
        self.assertEqual(len(HOUSE_11_BIO), 15)
        self.assertEqual(len(EXPECTED_BIO_IDS), 15)
        self.assertEqual(tuple(item.id for item in HOUSE_11_BIO), EXPECTED_BIO_IDS)

    def test_house_11_source_counts(self):
        house_11 = _house_11_facts()
        lesson7 = [item for item in house_11 if item.source_reference == REF_H11_L7]
        bio = [item for item in house_11 if item.source_reference == REF_H11_BIO]
        self.assertEqual(len(HOUSE_11), 22)
        self.assertEqual(len(lesson7), 22)
        self.assertEqual(len(bio), 15)
        self.assertEqual(len(house_11), 37)
        self.assertEqual(len(HOUSE_11) + len(HOUSE_11_BIO), 37)

    def test_all_bio_use_bioastrology_source_reference(self):
        self.assertTrue(all(item.source_reference == REF_H11_BIO for item in HOUSE_11_BIO))
        self.assertEqual(REF_H11_BIO, "bioastrology_mercury_house_11")

    def test_all_house_11_facts_share_factor_identity(self):
        house_11 = _house_11_facts()
        self.assertEqual(len(house_11), 37)
        self.assertTrue(all(item.factor_type == "house" for item in house_11))
        self.assertTrue(all(item.factor_key == "11" for item in house_11))
        self.assertTrue(all(item.activation_condition is None for item in house_11))
        self.assertTrue(all(item.unresolved is False for item in HOUSE_11))
        self.assertTrue(all(item.unresolved is False for item in HOUSE_11_BIO))

    def test_ids_globally_unique(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])


class House11BioCanonicalTests(unittest.TestCase):
    def test_exact_canonical_strings_for_all_15(self):
        by_id = {item.id: item for item in HOUSE_11_BIO}
        self.assertEqual(set(by_id), set(EXPECTED_BIO_CANONICAL))
        for fact_id, canonical in EXPECTED_BIO_CANONICAL.items():
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].text, canonical)


class House11AtomizationTests(unittest.TestCase):
    def test_five_realization_context_atoms_remain_separate(self):
        by_id = {item.id: item for item in HOUSE_11_BIO}
        texts = {by_id[fact_id].text for fact_id in REALIZATION_BIO_IDS}
        self.assertEqual(len(texts), 5)

    def test_collective_realization_is_distinct_from_group_learning(self):
        by_id = {item.id: item for item in HOUSE_11_BIO}
        realization = by_id["h11_bio_communication_learning_realized_through_collectives"]
        learning = by_id["h11_bio_learning_in_group_or_collective"]
        self.assertNotEqual(realization.text, learning.text)
        self.assertIn("realized", realization.text.lower())
        self.assertIn("setting", learning.text.lower())

    def test_scientific_and_technological_intellect_remain_separate(self):
        by_id = {item.id: item for item in HOUSE_11_BIO}
        scientific = by_id["h11_bio_intellect_becomes_scientific"]
        technological = by_id["h11_bio_intellect_becomes_technological"]
        self.assertNotEqual(scientific.text, technological.text)

    def test_universal_intellect_is_distinct_from_high_technology_learning(self):
        by_id = {item.id: item for item in HOUSE_11_BIO}
        universal = by_id["h11_bio_universal_intellect"]
        high_tech = by_id["h11_bio_learning_oriented_toward_high_technologies"]
        self.assertNotEqual(universal.text, high_tech.text)

    def test_three_learning_relation_atoms_remain_separate(self):
        by_id = {item.id: item for item in HOUSE_11_BIO}
        texts = {by_id[fact_id].text for fact_id in LEARNING_RELATION_BIO_IDS}
        self.assertEqual(len(texts), 3)

    def test_discussed_plans_and_projects_remain_separate(self):
        by_id = {item.id: item for item in HOUSE_11_BIO}
        plans = by_id["h11_bio_many_discussed_plans"]
        projects = by_id["h11_bio_many_discussed_projects"]
        self.assertNotEqual(plans.text, projects.text)
        self.assertIn("discussed", plans.text.lower())
        self.assertIn("discussed", projects.text.lower())


class House11EqualsPeersSourceFidelityTests(unittest.TestCase):
    def test_equals_or_peers_without_intellectual_qualifier(self):
        fact = next(
            item
            for item in HOUSE_11_BIO
            if item.id == "h11_bio_learning_with_equals_or_peers"
        )
        self.assertIn("equals or peers", fact.text.lower())
        self.assertNotIn("intellectual equals", fact.text.lower())
        self.assertNotIn("intellectual peers", fact.text.lower())


class House11PartialFidelityTests(unittest.TestCase):
    def test_collective_realization_is_not_groups_as_knowledge_source(self):
        by_id = {item.id: item for item in HOUSE_11 + HOUSE_11_BIO}
        bio = by_id["h11_bio_communication_learning_realized_through_collectives"]
        l7 = by_id["h11_groups_are_sources_of_knowledge"]
        self.assertNotEqual(bio.text, l7.text)
        self.assertNotIn("groups_as_knowledge_source", bio.tags)

    def test_scientific_intellect_is_not_scientific_thinking_context(self):
        by_id = {item.id: item for item in HOUSE_11 + HOUSE_11_BIO}
        bio = by_id["h11_bio_intellect_becomes_scientific"]
        l7 = by_id["h11_scientific_type_of_thinking_context"]
        self.assertNotEqual(bio.text, l7.text)
        self.assertNotIn("scientific_thinking_context", bio.tags)

    def test_universal_intellect_is_not_universal_mind(self):
        by_id = {item.id: item for item in HOUSE_11 + HOUSE_11_BIO}
        bio = by_id["h11_bio_universal_intellect"]
        l7 = by_id["h11_universal_mind"]
        self.assertNotEqual(bio.text, l7.text)
        self.assertNotIn("universal_mind", bio.tags)

    def test_learning_with_friends_is_not_friends_as_knowledge_source(self):
        by_id = {item.id: item for item in HOUSE_11 + HOUSE_11_BIO}
        bio = by_id["h11_bio_learning_with_friends"]
        l7 = by_id["h11_friends_are_sources_of_knowledge"]
        self.assertNotEqual(bio.text, l7.text)
        self.assertNotIn("friends_as_knowledge_source", bio.tags)

    def test_group_learning_is_not_groups_as_knowledge_source(self):
        by_id = {item.id: item for item in HOUSE_11 + HOUSE_11_BIO}
        bio = by_id["h11_bio_learning_in_group_or_collective"]
        l7 = by_id["h11_groups_are_sources_of_knowledge"]
        self.assertNotEqual(bio.text, l7.text)
        self.assertNotIn("groups_as_knowledge_source", bio.tags)


class House11BioTagGuardTests(unittest.TestCase):
    def test_all_fifteen_bio_facts_have_no_tags(self):
        for item in HOUSE_11_BIO:
            with self.subTest(fact_id=item.id):
                self.assertEqual(item.tags, ())

    def test_no_approximate_tags_on_any_bio_fact(self):
        for item in HOUSE_11_BIO:
            with self.subTest(fact_id=item.id):
                for tag in FORBIDDEN_APPROXIMATE_TAGS:
                    self.assertNotIn(tag, item.tags)

    def test_no_new_repeated_signal_spec(self):
        before = len(REPEATED_SIGNAL_SPECS)
        self.assertEqual(before, 15)


class House11Lesson7FrozenTests(unittest.TestCase):
    def test_existing_22_lesson7_facts_unchanged(self):
        self.assertEqual(len(HOUSE_11), 22)
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
            for item in HOUSE_11
        )
        self.assertEqual(actual, FROZEN_L7_HOUSE_11)


class House11L7OverlapAccountingTests(unittest.TestCase):
    def test_four_unique_l7_facts_are_partial_neighbors(self):
        l7_ids = {item.id for item in HOUSE_11}
        self.assertEqual(L7_PARTIAL_NEIGHBOR_IDS, L7_PARTIAL_NEIGHBOR_IDS & l7_ids)
        self.assertEqual(len(L7_PARTIAL_NEIGHBOR_IDS), 4)

    def test_eighteen_l7_facts_have_no_bio_overlap_neighbors(self):
        no_overlap = {
            item.id for item in HOUSE_11 if item.id not in L7_PARTIAL_NEIGHBOR_IDS
        }
        self.assertEqual(len(no_overlap), 18)
        self.assertEqual(len(no_overlap) + len(L7_PARTIAL_NEIGHBOR_IDS), 22)


class House11SameHouseSourceDedupTests(unittest.TestCase):
    def test_lesson7_and_bio_share_one_provenance_key(self):
        house_11 = _house_11_facts()
        keys = {_provenance_key(item) for item in house_11}
        self.assertEqual(keys, {"house:11"})

    def test_house_11_dual_source_cannot_create_same_house_repeat(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Virgo",
                mercury_element="earth",
                mercury_motion="direct",
                mercury_house=11,
                aspects=[],
            )
        )
        self.assertEqual(len(profile.house_facts), 37)
        self.assertEqual(detect_repeated_signals(profile.house_facts), [])


class House11HumanCopyInventoryConsequenceTests(unittest.TestCase):
    def test_new_bio_facts_are_unreviewed_and_not_in_registries(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        for fact_id in EXPECTED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertNotEqual(entry.review_status, STATUS_UNREVIEWED)
                self.assertTrue(
                    (fact_id in HUMAN_COPY_OVERRIDES)
                    ^ (fact_id in APPROVED_RAW_FACT_IDS)
                )

    def test_house_11_family_counts_after_source_parity(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "house:11")
        self.assertEqual(family.total_facts, 37)
        self.assertEqual(family.approved_override, 22)
        self.assertEqual(family.approved_raw, 15)
        self.assertEqual(family.unreviewed, 0)
        self.assertEqual(family.reviewed_count, 37)
        self.assertEqual(family.presentation_ready_count, 37)
        self.assertEqual(family.needs_review, 0)


class House11SemanticLedgerTests(unittest.TestCase):
    def test_semantic_accounting_from_implemented_facts(self):
        l7_count = len(HOUSE_11)
        bio_count = len(HOUSE_11_BIO)
        exact_overlap = 0
        partial_overlap = 5
        conditional_unresolved = 0
        unique_bio = bio_count - exact_overlap - partial_overlap - conditional_unresolved
        unique_meanings = l7_count + bio_count - exact_overlap
        self.assertEqual(l7_count, 22)
        self.assertEqual(bio_count, 15)
        self.assertEqual(exact_overlap, 0)
        self.assertEqual(partial_overlap, 5)
        self.assertEqual(unique_bio, 10)
        self.assertEqual(conditional_unresolved, 0)
        self.assertEqual(unique_meanings, 37)
        self.assertEqual(
            exact_overlap + partial_overlap + unique_bio + conditional_unresolved,
            15,
        )


if __name__ == "__main__":
    unittest.main()
