"""Tests for Mercury House 12 Bioastrology source parity (S4.31B)."""

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
    HOUSE_12,
    HOUSE_12_BIO,
    REF_H12_BIO,
    REF_H12_L7,
)
from app.services.mercury_source_profile import (
    _provenance_key,
    build_source_profile_from_factors,
    detect_repeated_signals,
)


EXPECTED_BIO_IDS: tuple[str, ...] = (
    "h12_bio_communication_learning_hidden_from_broad_public",
    "h12_bio_circumstances_make_person_solitary",
    "h12_bio_learning_from_own_experience",
    "h12_bio_inspiration_through_dialogues_with_god",
    "h12_bio_mystic_qualities",
    "h12_bio_doctor_qualities",
    "h12_bio_psychologist_qualities",
    "h12_bio_intuitive_revelations_insights",
    "h12_bio_paradoxical_philosophical_intellect",
    "h12_bio_source_broad_intellectual_capacity",
    "h12_bio_foreign_languages",
    "h12_bio_core_strong_tense_investor_qualities",
    "h12_bio_core_strong_tense_major_manager_researcher_qualities",
    "h12_bio_afflicted_gossip",
    "h12_bio_afflicted_hate",
    "h12_bio_afflicted_traffic_accident_association",
    "h12_bio_afflicted_vascular_disease_association",
    "h12_bio_afflicted_joint_disease_association",
    "h12_bio_afflicted_lung_disease_association",
    "h12_bio_afflicted_limb_disease_association",
)

ORDINARY_BIO_IDS: tuple[str, ...] = EXPECTED_BIO_IDS[:11]
CONDITIONAL_BIO_IDS: tuple[str, ...] = EXPECTED_BIO_IDS[11:]
CORE_FAMILY_IDS: tuple[str, ...] = EXPECTED_BIO_IDS[11:13]
AFFLICTED_FAMILY_IDS: tuple[str, ...] = EXPECTED_BIO_IDS[13:]

EXPECTED_BIO_CANONICAL: dict[str, str] = {
    "h12_bio_communication_learning_hidden_from_broad_public": (
        "Communication and learning may appear hidden from the broad public."
    ),
    "h12_bio_circumstances_make_person_solitary": (
        "Circumstances may make the person more solitary."
    ),
    "h12_bio_learning_from_own_experience": (
        "Learning may occur through one's own experience."
    ),
    "h12_bio_inspiration_through_dialogues_with_god": (
        "Inspiration may come through source-described 'dialogues with God.'"
    ),
    "h12_bio_mystic_qualities": (
        "May support qualities associated with a mystic role."
    ),
    "h12_bio_doctor_qualities": (
        "May support qualities associated with a doctor role."
    ),
    "h12_bio_psychologist_qualities": (
        "May support qualities associated with a psychologist role."
    ),
    "h12_bio_intuitive_revelations_insights": (
        "May support intuitive revelations or insights."
    ),
    "h12_bio_paradoxical_philosophical_intellect": (
        "Source describes a paradoxical philosophical intellect."
    ),
    "h12_bio_source_broad_intellectual_capacity": (
        "The source describes this intellect as able to do whatever it wishes."
    ),
    "h12_bio_foreign_languages": "Favorable association with foreign languages.",
    "h12_bio_core_strong_tense_investor_qualities": (
        "When the core is strong and tense, the source associates this placement "
        "with investor qualities (core-strength/tension dependency; no House 12 "
        "core resolver is applied)."
    ),
    "h12_bio_core_strong_tense_major_manager_researcher_qualities": (
        "When the core is strong and tense, the source associates this placement "
        "with qualities of a major manager-researcher role (core-strength/tension "
        "dependency; no House 12 core resolver is applied)."
    ),
    "h12_bio_afflicted_gossip": (
        "When Mercury is afflicted, the source associates this placement with "
        "gossip (afflicted-Mercury dependency; no house-affliction resolver is "
        "applied; not hard_aspected)."
    ),
    "h12_bio_afflicted_hate": (
        "When Mercury is afflicted, the source associates this placement with "
        "hate (afflicted-Mercury dependency; no house-affliction resolver is "
        "applied; not hard_aspected)."
    ),
    "h12_bio_afflicted_traffic_accident_association": (
        "When Mercury is afflicted, the source associates this placement with "
        "traffic accidents (afflicted-Mercury dependency; no house-affliction "
        "resolver is applied; not hard_aspected)."
    ),
    "h12_bio_afflicted_vascular_disease_association": (
        "When Mercury is afflicted, the source associates this placement with "
        "diseases involving blood vessels (afflicted-Mercury dependency; "
        "no house-affliction resolver is applied; not hard_aspected)."
    ),
    "h12_bio_afflicted_joint_disease_association": (
        "When Mercury is afflicted, the source associates this placement with "
        "diseases involving joints (afflicted-Mercury dependency; no house-affliction "
        "resolver is applied; not hard_aspected)."
    ),
    "h12_bio_afflicted_lung_disease_association": (
        "When Mercury is afflicted, the source associates this placement with "
        "diseases involving lungs (afflicted-Mercury dependency; no house-affliction "
        "resolver is applied; not hard_aspected)."
    ),
    "h12_bio_afflicted_limb_disease_association": (
        "When Mercury is afflicted, the source associates this placement with "
        "diseases involving limbs (afflicted-Mercury dependency; no house-affliction "
        "resolver is applied; not hard_aspected)."
    ),
}

PARTIAL_BIO_IDS: frozenset[str] = frozenset(
    {
        "h12_bio_communication_learning_hidden_from_broad_public",
        "h12_bio_circumstances_make_person_solitary",
    }
)
BIO_UNIQUE_IDS: frozenset[str] = frozenset(
    {
        "h12_bio_learning_from_own_experience",
        "h12_bio_inspiration_through_dialogues_with_god",
        "h12_bio_mystic_qualities",
        "h12_bio_doctor_qualities",
        "h12_bio_psychologist_qualities",
        "h12_bio_intuitive_revelations_insights",
        "h12_bio_paradoxical_philosophical_intellect",
        "h12_bio_source_broad_intellectual_capacity",
        "h12_bio_foreign_languages",
    }
)

L7_PARTIAL_NEIGHBOR_IDS: frozenset[str] = frozenset(
    {
        "h12_difficult_to_express_oneself_in_front_of_people",
        "h12_uncomfortable_to_express_oneself_in_front_of_people",
        "h12_writes_for_the_drawer",
        "h12_does_not_show_fruits_of_intellectual_creativity",
        "h12_ability_to_think_alone",
        "h12_ability_to_learn_alone",
    }
)

FORBIDDEN_APPROXIMATE_TAGS: tuple[str, ...] = (
    "insight",
    "occult_intellectual_expression",
    "unknown_domain_intellectual_expression",
    "hidden_meaning_decoding",
    "verbalizing_inexplicable",
    "solitary_thinking",
    "solitary_learning",
    "public_expression_difficulty",
    "hidden_intellectual_output",
    "gossip_based_information",
    "abstract_thinking",
    "analytical_plus_abstract",
    "nonstandard_thinking",
    "global_thinking",
    "research_talent",
    "technical_ability",
    "leadership",
    "lifelong_learning",
)

FROZEN_L7_HOUSE_12: tuple[
    tuple[str, str, str, str, tuple[str, ...], str, bool], ...
] = (
    (
        "h12_mind_brightest_in_occult",
        "source_specific",
        "Mind shows itself most brightly in the occult "
        "(source-framework claim; not a scientifically validated skill).",
        "neutral",
        ("occult_intellectual_expression",),
        REF_H12_L7,
        False,
    ),
    (
        "h12_mind_brightest_in_unknown_unexplored",
        "source_specific",
        "Mind shows itself most brightly in the unknown / unexplored "
        "(source-framework claim; not a scientifically validated skill).",
        "neutral",
        ("unknown_domain_intellectual_expression",),
        REF_H12_L7,
        False,
    ),
    (
        "h12_ability_to_decipher_hidden_meanings",
        "thinking",
        "Ability to decipher hidden meanings.",
        "strength",
        ("hidden_meaning_decoding",),
        REF_H12_L7,
        False,
    ),
    (
        "h12_talent_for_putting_inexplicable_into_words",
        "communication",
        "Talent for putting the inexplicable into words "
        "(source-described expression claim; not treated as paranormal proof).",
        "strength",
        ("verbalizing_inexplicable",),
        REF_H12_L7,
        False,
    ),
    (
        "h12_many_secrets",
        "environment",
        "Many secrets.",
        "neutral",
        ("secret_heavy_context",),
        REF_H12_L7,
        False,
    ),
    (
        "h12_circumstances_require_keeping_secrets",
        "environment",
        "Circumstances require keeping secrets.",
        "neutral",
        ("secret_keeping_requirement",),
        REF_H12_L7,
        False,
    ),
    (
        "h12_ability_to_think_alone",
        "thinking",
        "Ability to think alone.",
        "strength",
        ("solitary_thinking",),
        REF_H12_L7,
        False,
    ),
    (
        "h12_ability_to_learn_alone",
        "learning",
        "Ability to learn alone.",
        "strength",
        ("solitary_learning",),
        REF_H12_L7,
        False,
    ),
    (
        "h12_learning_more_interesting_remotely",
        "learning",
        "Learning is more interesting remotely.",
        "neutral",
        ("distance_learning_preference",),
        REF_H12_L7,
        False,
    ),
    (
        "h12_learning_more_interesting_as_external_student",
        "learning",
        "Learning is more interesting as an external student / externship.",
        "neutral",
        ("external_study_preference",),
        REF_H12_L7,
        False,
    ),
    (
        "h12_talks_internally_more_than_externally",
        "communication",
        "Talks internally more often than externally.",
        "neutral",
        ("internal_dialogue_dominance",),
        REF_H12_L7,
        False,
    ),
    (
        "h12_difficult_to_express_oneself_in_front_of_people",
        "communication",
        "Difficult to express oneself in front of people.",
        "risk",
        ("public_expression_difficulty",),
        REF_H12_L7,
        False,
    ),
    (
        "h12_uncomfortable_to_express_oneself_in_front_of_people",
        "communication",
        "Uncomfortable to express oneself in front of people.",
        "risk",
        ("public_expression_discomfort",),
        REF_H12_L7,
        False,
    ),
    (
        "h12_writes_for_the_drawer",
        "communication",
        'Writes "for the drawer".',
        "neutral",
        ("private_undisplayed_writing",),
        REF_H12_L7,
        False,
    ),
    (
        "h12_does_not_show_fruits_of_intellectual_creativity",
        "communication",
        "Does not show fruits of intellectual creativity.",
        "neutral",
        ("hidden_intellectual_output",),
        REF_H12_L7,
        False,
    ),
    (
        "h12_subconscious_strongly_influences_thinking",
        "thinking",
        "Subconscious strongly influences thinking.",
        "neutral",
        ("subconscious_influence_on_thinking",),
        REF_H12_L7,
        False,
    ),
    (
        "h12_decisions_more_often_not_logical",
        "thinking",
        "Decisions are more often not logical.",
        "neutral",
        ("nonlogical_decision_tendency",),
        REF_H12_L7,
        False,
    ),
    (
        "h12_operates_with_guesses",
        "thinking",
        "Operates with guesses.",
        "neutral",
        ("guess_based_reasoning",),
        REF_H12_L7,
        False,
    ),
    (
        "h12_operates_with_gossip",
        "communication",
        "Operates with gossip.",
        "neutral",
        ("gossip_based_information",),
        REF_H12_L7,
        False,
    ),
    (
        "h12_solitude_through_internet_psychology_medicine",
        "source_specific",
        "May go into the internet, psychology, or medicine as a way of isolating / being alone "
        "(source-described solitude pathways; not a clinical diagnosis).",
        "neutral",
        ("solitude_through_internet_psychology_medicine",),
        REF_H12_L7,
        False,
    ),
)


def _house_12_facts():
    return [
        item
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "house" and item.factor_key == "12"
    ]


class House12BioCoverageTests(unittest.TestCase):
    def test_programmatic_bio_count_is_20(self):
        self.assertEqual(len(HOUSE_12_BIO), 20)
        self.assertEqual(len(EXPECTED_BIO_IDS), 20)
        self.assertEqual(tuple(item.id for item in HOUSE_12_BIO), EXPECTED_BIO_IDS)

    def test_house_12_source_counts(self):
        house_12 = _house_12_facts()
        lesson7 = [item for item in house_12 if item.source_reference == REF_H12_L7]
        bio = [item for item in house_12 if item.source_reference == REF_H12_BIO]
        self.assertEqual(len(HOUSE_12), 20)
        self.assertEqual(len(lesson7), 20)
        self.assertEqual(len(bio), 20)
        self.assertEqual(len(house_12), 40)
        self.assertEqual(len(HOUSE_12) + len(HOUSE_12_BIO), 40)

    def test_all_bio_use_bioastrology_source_reference(self):
        self.assertTrue(all(item.source_reference == REF_H12_BIO for item in HOUSE_12_BIO))
        self.assertEqual(REF_H12_BIO, "bioastrology_mercury_house_12")

    def test_all_house_12_facts_share_factor_identity(self):
        house_12 = _house_12_facts()
        self.assertEqual(len(house_12), 40)
        self.assertTrue(all(item.factor_type == "house" for item in house_12))
        self.assertTrue(all(item.factor_key == "12" for item in house_12))
        self.assertTrue(all(item.activation_condition is None for item in house_12))
        self.assertTrue(all(item.unresolved is False for item in HOUSE_12))

    def test_ordinary_and_conditional_unresolved_flags(self):
        by_id = {item.id: item for item in HOUSE_12_BIO}
        for fact_id in ORDINARY_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertFalse(by_id[fact_id].unresolved)
                self.assertIsNone(by_id[fact_id].activation_condition)
        for fact_id in CONDITIONAL_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertTrue(by_id[fact_id].unresolved)
                self.assertIsNone(by_id[fact_id].activation_condition)

    def test_ids_globally_unique(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])


class House12BioCanonicalTests(unittest.TestCase):
    def test_exact_canonical_strings_for_all_20(self):
        by_id = {item.id: item for item in HOUSE_12_BIO}
        self.assertEqual(set(by_id), set(EXPECTED_BIO_CANONICAL))
        for fact_id, canonical in EXPECTED_BIO_CANONICAL.items():
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].text, canonical)


class House12ParityClassificationTests(unittest.TestCase):
    def test_approved_bio_buckets(self):
        self.assertEqual(PARTIAL_BIO_IDS & BIO_UNIQUE_IDS, set())
        self.assertEqual(PARTIAL_BIO_IDS & set(CONDITIONAL_BIO_IDS), set())
        self.assertEqual(BIO_UNIQUE_IDS & set(CONDITIONAL_BIO_IDS), set())
        self.assertEqual(len(PARTIAL_BIO_IDS), 2)
        self.assertEqual(len(BIO_UNIQUE_IDS), 9)
        self.assertEqual(len(CONDITIONAL_BIO_IDS), 9)
        self.assertEqual(
            PARTIAL_BIO_IDS | BIO_UNIQUE_IDS | set(CONDITIONAL_BIO_IDS),
            set(EXPECTED_BIO_IDS),
        )


class House12PartialFidelityTests(unittest.TestCase):
    def test_hidden_from_public_is_not_exact_l7_expression_facts(self):
        by_id = {item.id: item for item in HOUSE_12 + HOUSE_12_BIO}
        bio = by_id["h12_bio_communication_learning_hidden_from_broad_public"]
        for l7_id in (
            "h12_difficult_to_express_oneself_in_front_of_people",
            "h12_uncomfortable_to_express_oneself_in_front_of_people",
            "h12_writes_for_the_drawer",
            "h12_does_not_show_fruits_of_intellectual_creativity",
        ):
            with self.subTest(l7_id=l7_id):
                self.assertNotEqual(bio.text, by_id[l7_id].text)
                self.assertNotEqual(bio.id, l7_id)

    def test_circumstances_solitude_is_not_ability_to_think_or_learn_alone(self):
        by_id = {item.id: item for item in HOUSE_12 + HOUSE_12_BIO}
        bio = by_id["h12_bio_circumstances_make_person_solitary"]
        think = by_id["h12_ability_to_think_alone"]
        learn = by_id["h12_ability_to_learn_alone"]
        self.assertNotEqual(bio.text, think.text)
        self.assertNotEqual(bio.text, learn.text)
        self.assertIn("circumstances", bio.text.lower())


class House12RoleDomainFidelityTests(unittest.TestCase):
    def test_mystic_qualities_are_not_occult_or_unknown_domain(self):
        by_id = {item.id: item for item in HOUSE_12 + HOUSE_12_BIO}
        mystic = by_id["h12_bio_mystic_qualities"]
        occult = by_id["h12_mind_brightest_in_occult"]
        unknown = by_id["h12_mind_brightest_in_unknown_unexplored"]
        self.assertNotEqual(mystic.text, occult.text)
        self.assertNotEqual(mystic.text, unknown.text)
        self.assertEqual(mystic.tags, ())
        self.assertNotIn("occult_intellectual_expression", mystic.tags)
        self.assertNotIn("unknown_domain_intellectual_expression", mystic.tags)


class House12ParadoxicalIntellectFidelityTests(unittest.TestCase):
    def test_paradoxical_philosophical_intellect_is_independent(self):
        by_id = {item.id: item for item in HOUSE_12 + HOUSE_12_BIO}
        bio = by_id["h12_bio_paradoxical_philosophical_intellect"]
        for l7_id in (
            "h12_mind_brightest_in_occult",
            "h12_mind_brightest_in_unknown_unexplored",
            "h12_talent_for_putting_inexplicable_into_words",
        ):
            with self.subTest(l7_id=l7_id):
                self.assertNotEqual(bio.text, by_id[l7_id].text)
        self.assertEqual(bio.tags, ())
        for tag in (
            "abstract_thinking",
            "analytical_plus_abstract",
            "nonstandard_thinking",
            "global_thinking",
        ):
            self.assertNotIn(tag, bio.tags)


class House12BroadCapacitySourceCopyTests(unittest.TestCase):
    def test_broad_capacity_preserves_able_to_do_wording(self):
        fact = next(
            item
            for item in HOUSE_12_BIO
            if item.id == "h12_bio_source_broad_intellectual_capacity"
        )
        self.assertEqual(
            fact.text,
            "The source describes this intellect as able to do whatever it wishes.",
        )
        self.assertIn("The source describes", fact.text)
        self.assertNotIn("capable of pursuing", fact.text.lower())
        self.assertNotIn("pursue", fact.text.lower())


class House12ConditionFamilyTests(unittest.TestCase):
    def test_core_family_is_unresolved_without_existing_resolvers(self):
        by_id = {item.id: item for item in HOUSE_12_BIO}
        for fact_id in CORE_FAMILY_IDS:
            with self.subTest(fact_id=fact_id):
                fact = by_id[fact_id]
                self.assertTrue(fact.unresolved)
                self.assertIsNone(fact.activation_condition)
                self.assertEqual(fact.polarity, "conditional")
                self.assertIn("strong and tense", fact.text.lower())
                self.assertNotEqual(fact.activation_condition, "creative_core_strength_unresolved")
                self.assertNotEqual(fact.activation_condition, "hard_aspected")
                self.assertNotIn("hard_aspected", fact.text)
                self.assertNotIn("creative_core_strength_unresolved", fact.text)

    def test_afflicted_family_is_unresolved_without_hard_aspected(self):
        by_id = {item.id: item for item in HOUSE_12_BIO}
        for fact_id in AFFLICTED_FAMILY_IDS:
            with self.subTest(fact_id=fact_id):
                fact = by_id[fact_id]
                self.assertTrue(fact.unresolved)
                self.assertIsNone(fact.activation_condition)
                self.assertEqual(fact.category, "source_specific")
                self.assertEqual(fact.polarity, "conditional")
                self.assertNotEqual(fact.activation_condition, "hard_aspected")
                self.assertIn("not hard_aspected", fact.text)

    def test_core_and_afflicted_families_are_disjoint(self):
        self.assertEqual(set(CORE_FAMILY_IDS) & set(AFFLICTED_FAMILY_IDS), set())
        self.assertEqual(len(CORE_FAMILY_IDS) + len(AFFLICTED_FAMILY_IDS), 9)


class House12GossipConditionSeparationTests(unittest.TestCase):
    def test_unconditional_l7_gossip_is_not_afflicted_bio_gossip(self):
        by_id = {item.id: item for item in HOUSE_12 + HOUSE_12_BIO}
        l7 = by_id["h12_operates_with_gossip"]
        bio = by_id["h12_bio_afflicted_gossip"]
        self.assertFalse(l7.unresolved)
        self.assertTrue(bio.unresolved)
        self.assertNotEqual(l7.text, bio.text)
        self.assertEqual(l7.tags, ("gossip_based_information",))
        self.assertEqual(bio.tags, ())
        self.assertNotIn("gossip_based_information", bio.tags)


class House12AtomizationTests(unittest.TestCase):
    def test_first_bullet_four_atoms_remain_separate(self):
        by_id = {item.id: item for item in HOUSE_12_BIO}
        texts = {
            by_id[fact_id].text
            for fact_id in (
                "h12_bio_communication_learning_hidden_from_broad_public",
                "h12_bio_circumstances_make_person_solitary",
                "h12_bio_learning_from_own_experience",
                "h12_bio_inspiration_through_dialogues_with_god",
            )
        }
        self.assertEqual(len(texts), 4)

    def test_mystic_doctor_psychologist_remain_separate(self):
        by_id = {item.id: item for item in HOUSE_12_BIO}
        texts = {
            by_id[fact_id].text
            for fact_id in (
                "h12_bio_mystic_qualities",
                "h12_bio_doctor_qualities",
                "h12_bio_psychologist_qualities",
            )
        }
        self.assertEqual(len(texts), 3)

    def test_philosophical_style_is_separate_from_capacity_claim(self):
        by_id = {item.id: item for item in HOUSE_12_BIO}
        style = by_id["h12_bio_paradoxical_philosophical_intellect"]
        capacity = by_id["h12_bio_source_broad_intellectual_capacity"]
        self.assertNotEqual(style.text, capacity.text)

    def test_manager_researcher_remains_one_compound_role(self):
        fact = next(
            item
            for item in HOUSE_12_BIO
            if item.id == "h12_bio_core_strong_tense_major_manager_researcher_qualities"
        )
        self.assertIn("manager-researcher", fact.text.lower())
        self.assertNotIn("h12_bio_core_strong_tense_manager_qualities", {item.id for item in HOUSE_12_BIO})
        self.assertNotIn("h12_bio_core_strong_tense_researcher_qualities", {item.id for item in HOUSE_12_BIO})


class House12BioTagGuardTests(unittest.TestCase):
    def test_foreign_languages_is_the_only_bio_tag(self):
        by_id = {item.id: item for item in HOUSE_12_BIO}
        self.assertEqual(by_id["h12_bio_foreign_languages"].tags, ("foreign_languages",))
        for item in HOUSE_12_BIO:
            if item.id == "h12_bio_foreign_languages":
                continue
            with self.subTest(fact_id=item.id):
                self.assertEqual(item.tags, ())

    def test_insight_is_not_on_intuitive_revelations(self):
        fact = next(
            item
            for item in HOUSE_12_BIO
            if item.id == "h12_bio_intuitive_revelations_insights"
        )
        self.assertNotIn("insight", fact.tags)
        self.assertEqual(fact.tags, ())

    def test_no_approximate_tags_on_bio_facts(self):
        for item in HOUSE_12_BIO:
            with self.subTest(fact_id=item.id):
                for tag in FORBIDDEN_APPROXIMATE_TAGS:
                    self.assertNotIn(tag, item.tags)

    def test_no_new_repeated_signal_spec(self):
        self.assertEqual(len(REPEATED_SIGNAL_SPECS), 15)
        tags = {spec["tag"] for spec in REPEATED_SIGNAL_SPECS}
        self.assertIn("foreign_languages", tags)
        self.assertEqual(
            len([spec for spec in REPEATED_SIGNAL_SPECS if spec["tag"] == "foreign_languages"]),
            1,
        )


class House12MedicalSafetyTests(unittest.TestCase):
    def test_four_disease_atoms_are_conditional_source_specific(self):
        by_id = {item.id: item for item in HOUSE_12_BIO}
        for fact_id, fragment in (
            ("h12_bio_afflicted_vascular_disease_association", "blood vessels"),
            ("h12_bio_afflicted_joint_disease_association", "joints"),
            ("h12_bio_afflicted_lung_disease_association", "lungs"),
            ("h12_bio_afflicted_limb_disease_association", "limbs"),
        ):
            with self.subTest(fact_id=fact_id):
                fact = by_id[fact_id]
                self.assertEqual(fact.category, "source_specific")
                self.assertEqual(fact.polarity, "conditional")
                self.assertTrue(fact.unresolved)
                self.assertEqual(fact.tags, ())
                self.assertIn(fragment, fact.text.lower())
                self.assertNotIn("diagnosis", fact.text.lower())


class House12Lesson7FrozenTests(unittest.TestCase):
    def test_existing_20_lesson7_facts_unchanged(self):
        self.assertEqual(len(HOUSE_12), 20)
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
            for item in HOUSE_12
        )
        self.assertEqual(actual, FROZEN_L7_HOUSE_12)


class House12L7OverlapAccountingTests(unittest.TestCase):
    def test_six_unique_l7_facts_are_partial_neighbors(self):
        l7_ids = {item.id for item in HOUSE_12}
        self.assertEqual(L7_PARTIAL_NEIGHBOR_IDS, L7_PARTIAL_NEIGHBOR_IDS & l7_ids)
        self.assertEqual(len(L7_PARTIAL_NEIGHBOR_IDS), 6)

    def test_fourteen_l7_facts_have_no_bio_overlap_neighbors(self):
        no_overlap = {
            item.id for item in HOUSE_12 if item.id not in L7_PARTIAL_NEIGHBOR_IDS
        }
        self.assertEqual(len(no_overlap), 14)
        self.assertEqual(len(no_overlap) + len(L7_PARTIAL_NEIGHBOR_IDS), 20)
        self.assertIn("h12_mind_brightest_in_occult", no_overlap)
        self.assertIn("h12_mind_brightest_in_unknown_unexplored", no_overlap)
        self.assertIn("h12_talent_for_putting_inexplicable_into_words", no_overlap)
        self.assertIn("h12_operates_with_gossip", no_overlap)


class House12SameHouseSourceDedupTests(unittest.TestCase):
    def test_lesson7_and_bio_share_one_provenance_key(self):
        house_12 = _house_12_facts()
        keys = {_provenance_key(item) for item in house_12}
        self.assertEqual(keys, {"house:12"})

    def test_house_12_dual_source_cannot_create_same_house_repeat(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Pisces",
                mercury_element="water",
                mercury_motion="direct",
                mercury_house=12,
                aspects=[],
            )
        )
        self.assertEqual(len(profile.house_facts), 40)
        self.assertEqual(detect_repeated_signals(profile.house_facts), [])


class House12HumanCopyInventoryConsequenceTests(unittest.TestCase):
    def test_new_bio_facts_are_unreviewed_and_not_in_registries(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        for fact_id in EXPECTED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertNotIn(fact_id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_UNREVIEWED)

    def test_house_12_family_counts_after_source_parity(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "house:12")
        self.assertEqual(family.total_facts, 40)
        self.assertEqual(family.unreviewed, 40)
        self.assertEqual(family.reviewed_count, 0)
        self.assertEqual(family.presentation_ready_count, 0)
        self.assertEqual(family.needs_review, 0)


class House12SemanticLedgerTests(unittest.TestCase):
    def test_semantic_accounting_from_implemented_facts(self):
        l7_count = len(HOUSE_12)
        bio_count = len(HOUSE_12_BIO)
        exact_overlap = 0
        partial_overlap = 2
        conditional_unresolved = 9
        unique_bio = bio_count - exact_overlap - partial_overlap - conditional_unresolved
        unique_meanings = l7_count + bio_count - exact_overlap
        self.assertEqual(l7_count, 20)
        self.assertEqual(bio_count, 20)
        self.assertEqual(exact_overlap, 0)
        self.assertEqual(partial_overlap, 2)
        self.assertEqual(unique_bio, 9)
        self.assertEqual(conditional_unresolved, 9)
        self.assertEqual(unique_meanings, 40)
        self.assertEqual(
            exact_overlap + partial_overlap + unique_bio + conditional_unresolved,
            20,
        )


if __name__ == "__main__":
    unittest.main()
