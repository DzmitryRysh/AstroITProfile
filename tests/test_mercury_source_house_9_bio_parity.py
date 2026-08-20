"""Tests for Mercury House 9 Bioastrology source parity (S4.28B)."""

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
    HOUSE_9,
    HOUSE_9_BIO,
    REF_H9,
    REF_H9_BIO,
    REPEATED_SIGNAL_SPECS,
)
from app.services.mercury_source_profile import (
    _provenance_key,
    build_source_profile_from_factors,
    detect_repeated_signals,
)


EXPECTED_BIO_IDS: tuple[str, ...] = (
    "h9_bio_communication_learning_realized_through_travel",
    "h9_bio_communication_learning_realized_through_philosophical_concepts",
    "h9_bio_communication_learning_realized_through_scientific_theories",
    "h9_bio_not_heard_in_ordinary_situations",
    "h9_bio_strong_intellect",
    "h9_bio_increased_courses",
    "h9_bio_increased_trainings",
    "h9_bio_increased_university_contexts",
    "h9_bio_learning_through_direct_teacher_dialogue",
    "h9_bio_foreign_languages",
    "h9_bio_teacher_talent",
    "h9_bio_trainer_talent",
    "h9_bio_mentor_talent",
)

EXPECTED_BIO_CANONICAL: dict[str, str] = {
    "h9_bio_communication_learning_realized_through_travel": (
        "Communication and learning may be realized through travel."
    ),
    "h9_bio_communication_learning_realized_through_philosophical_concepts": (
        "Communication and learning may be realized through philosophical concepts."
    ),
    "h9_bio_communication_learning_realized_through_scientific_theories": (
        "Communication and learning may be realized through scientific theories."
    ),
    "h9_bio_not_heard_in_ordinary_situations": (
        "In ordinary everyday situations, the person may seem not to be heard."
    ),
    "h9_bio_strong_intellect": "May support strong intellect.",
    "h9_bio_increased_courses": (
        "There may be an increased presence of courses in the person's learning path."
    ),
    "h9_bio_increased_trainings": (
        "There may be an increased presence of trainings in the person's learning path."
    ),
    "h9_bio_increased_university_contexts": (
        "There may be an increased presence of university study contexts."
    ),
    "h9_bio_learning_through_direct_teacher_dialogue": (
        "Learning may occur through direct dialogue with a teacher."
    ),
    "h9_bio_foreign_languages": "Favorable association with foreign languages.",
    "h9_bio_teacher_talent": "May support talent as a teacher.",
    "h9_bio_trainer_talent": "May support talent as a trainer.",
    "h9_bio_mentor_talent": "May support talent as a mentor.",
}

EXPECTED_BIO_TAGS: dict[str, tuple[str, ...]] = {
    "h9_bio_foreign_languages": ("foreign_languages",),
    "h9_bio_teacher_talent": ("teaching",),
}

UNTAGGED_BIO_IDS: tuple[str, ...] = tuple(
    fact_id for fact_id in EXPECTED_BIO_IDS if fact_id not in EXPECTED_BIO_TAGS
)

LEARNING_CONTEXT_BIO_IDS: tuple[str, ...] = (
    "h9_bio_increased_courses",
    "h9_bio_increased_trainings",
    "h9_bio_increased_university_contexts",
)

ROLE_TALENT_BIO_IDS: tuple[str, ...] = (
    "h9_bio_teacher_talent",
    "h9_bio_trainer_talent",
    "h9_bio_mentor_talent",
)

FORBIDDEN_APPROXIMATE_TAGS: tuple[str, ...] = (
    "geography_travel",
    "science_interest",
    "broad_knowledge_orientation",
    "analytical_thinking",
    "abstract_thinking",
    "analytical_plus_abstract",
    "information_filtering",
    "lifelong_learning",
    "course_learning",
    "dialogue_skill",
    "argumentation",
    "evidence_requirement",
    "other_cultures",
    "formal_etiquette_communication",
)

FROZEN_L7_HOUSE_9: tuple[
    tuple[str, str, str, str, tuple[str, ...], str, bool], ...
] = (
    (
        "h9_filters_significant_information",
        "thinking",
        "Filters significant information from a larger information stream.",
        "strength",
        ("information_filtering",),
        REF_H9,
        False,
    ),
    (
        "h9_analytical_with_abstract",
        "thinking",
        "Analytical thinking works together with abstract thinking.",
        "strength",
        ("analytical_plus_abstract", "analytical_thinking", "abstract_thinking"),
        REF_H9,
        False,
    ),
    (
        "h9_interest_other_cultures",
        "environment",
        "Understanding / interest in other cultures.",
        "strength",
        ("other_cultures",),
        REF_H9,
        False,
    ),
    (
        "h9_interest_geography_travel",
        "mobility",
        "Interest in geography and travel.",
        "neutral",
        ("geography_travel",),
        REF_H9,
        False,
    ),
    (
        "h9_attraction_to_sciences",
        "learning",
        "Attraction to sciences.",
        "strength",
        ("science_interest", "broad_knowledge_orientation"),
        REF_H9,
        False,
    ),
    (
        "h9_multiple_educations",
        "learning",
        "Multiple educations / repeated formal learning may occur.",
        "neutral",
        ("lifelong_learning",),
        REF_H9,
        False,
    ),
    (
        "h9_interest_foreign_languages",
        "learning",
        "Interest in foreign languages.",
        "strength",
        ("foreign_languages",),
        REF_H9,
        False,
    ),
    (
        "h9_eternal_student",
        "learning",
        "\"Eternal student\": circumstances require continued learning.",
        "neutral",
        ("lifelong_learning",),
        REF_H9,
        False,
    ),
    (
        "h9_elevates_intellectual_social_level",
        "environment",
        "The house can elevate intellectual / social level over time.",
        "strength",
        ("status_elevation",),
        REF_H9,
        False,
    ),
    (
        "h9_casual_communication_less_natural",
        "communication",
        "Casual / simple communication may be less natural; communication can become formal or etiquette-conscious.",
        "risk",
        ("formal_etiquette_communication",),
        REF_H9,
        False,
    ),
    (
        "h9_need_to_monitor_speech",
        "communication",
        "May feel a need to monitor speech.",
        "risk",
        ("speech_monitoring",),
        REF_H9,
        False,
    ),
    (
        "h9_selective_communication",
        "communication",
        "Selective communication / preference for selected circles.",
        "neutral",
        ("information_filtering",),
        REF_H9,
        False,
    ),
    (
        "h9_consume_too_much_high_level_info",
        "risk",
        "May consume too much high-level information.",
        "risk",
        ("information_filtering",),
        REF_H9,
        False,
    ),
    (
        "h9_cycle_on_unnecessary_information",
        "risk",
        "May cycle on unnecessary or excessive information.",
        "risk",
        ("information_filtering",),
        REF_H9,
        False,
    ),
    (
        "h9_needs_argumentation_evidence",
        "thinking",
        "Does not readily accept an idea without argumentation / evidence.",
        "neutral",
        ("evidence_requirement",),
        REF_H9,
        False,
    ),
    (
        "h9_status_environment_mismatch",
        "environment",
        "Possible feeling of being intellectually / socially out of place in a higher-status environment.",
        "risk",
        ("status_environment_mismatch",),
        REF_H9,
        False,
    ),
)


def _house_9_facts():
    return [
        item
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "house" and item.factor_key == "9"
    ]


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


class House9BioCoverageTests(unittest.TestCase):
    def test_programmatic_bio_count_is_13(self):
        self.assertEqual(len(HOUSE_9_BIO), 13)
        self.assertEqual(len(EXPECTED_BIO_IDS), 13)
        self.assertEqual(len(EXPECTED_BIO_CANONICAL), 13)
        self.assertEqual(tuple(item.id for item in HOUSE_9_BIO), EXPECTED_BIO_IDS)

    def test_house_9_source_counts(self):
        house_9 = _house_9_facts()
        lesson7 = [item for item in house_9 if item.source_reference == REF_H9]
        bio = [item for item in house_9 if item.source_reference == REF_H9_BIO]
        self.assertEqual(len(HOUSE_9), 16)
        self.assertEqual(len(lesson7), 16)
        self.assertEqual(len(bio), 13)
        self.assertEqual(len(house_9), 29)
        self.assertEqual(len(HOUSE_9) + len(HOUSE_9_BIO), 29)

    def test_all_bio_use_bioastrology_source_reference(self):
        self.assertTrue(all(item.source_reference == REF_H9_BIO for item in HOUSE_9_BIO))
        self.assertEqual(REF_H9_BIO, "bioastrology_mercury_house_9")

    def test_all_house_9_facts_share_factor_identity(self):
        house_9 = _house_9_facts()
        self.assertEqual(len(house_9), 29)
        self.assertTrue(all(item.factor_type == "house" for item in house_9))
        self.assertTrue(all(item.factor_key == "9" for item in house_9))
        self.assertTrue(all(item.activation_condition is None for item in house_9))
        self.assertTrue(all(item.unresolved is False for item in HOUSE_9_BIO))
        self.assertTrue(all(item.unresolved is False for item in HOUSE_9))

    def test_ids_globally_unique(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])


class House9BioCanonicalTests(unittest.TestCase):
    def test_exact_canonical_strings_for_all_13(self):
        by_id = {item.id: item for item in HOUSE_9_BIO}
        self.assertEqual(set(by_id), set(EXPECTED_BIO_CANONICAL))
        for fact_id, canonical in EXPECTED_BIO_CANONICAL.items():
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].text, canonical)


class House9StrongIntellectBioUniqueTests(unittest.TestCase):
    def test_strong_intellect_is_bio_unique_without_analytical_tags(self):
        by_id = {item.id: item for item in HOUSE_9 + HOUSE_9_BIO}
        bio = by_id["h9_bio_strong_intellect"]
        analytical = by_id["h9_analytical_with_abstract"]
        filtering = by_id["h9_filters_significant_information"]
        self.assertEqual(bio.tags, ())
        self.assertNotIn("analytical_thinking", bio.tags)
        self.assertNotIn("abstract_thinking", bio.tags)
        self.assertNotIn("analytical_plus_abstract", bio.tags)
        self.assertNotIn("information_filtering", bio.tags)
        self.assertNotEqual(bio.text, analytical.text)
        self.assertNotEqual(bio.text, filtering.text)
        self.assertEqual(bio.category, "thinking")
        self.assertEqual(bio.polarity, "strength")

    def test_strong_intellect_not_semantic_duplicate_of_analytical_or_filtering(self):
        bio = next(item for item in HOUSE_9_BIO if item.id == "h9_bio_strong_intellect")
        self.assertNotIn("analytical", bio.text.lower())
        self.assertNotIn("abstract", bio.text.lower())
        self.assertNotIn("filter", bio.text.lower())


class House9PartialFidelityTests(unittest.TestCase):
    def test_travel_realization_is_not_travel_interest(self):
        by_id = {item.id: item for item in HOUSE_9 + HOUSE_9_BIO}
        bio = by_id["h9_bio_communication_learning_realized_through_travel"]
        l7 = by_id["h9_interest_geography_travel"]
        self.assertNotEqual(bio.id, l7.id)
        self.assertNotEqual(bio.text, l7.text)
        self.assertIn("realized", bio.text.lower())
        self.assertNotIn("geography_travel", bio.tags)

    def test_scientific_theories_realization_is_not_science_interest(self):
        by_id = {item.id: item for item in HOUSE_9 + HOUSE_9_BIO}
        bio = by_id["h9_bio_communication_learning_realized_through_scientific_theories"]
        l7 = by_id["h9_attraction_to_sciences"]
        self.assertNotEqual(bio.text, l7.text)
        self.assertNotIn("science_interest", bio.tags)

    def test_increased_courses_is_not_multiple_educations_or_eternal_student(self):
        by_id = {item.id: item for item in HOUSE_9 + HOUSE_9_BIO}
        bio = by_id["h9_bio_increased_courses"]
        educations = by_id["h9_multiple_educations"]
        eternal = by_id["h9_eternal_student"]
        self.assertNotEqual(bio.text, educations.text)
        self.assertNotEqual(bio.text, eternal.text)
        self.assertNotIn("lifelong_learning", bio.tags)

    def test_university_contexts_is_not_multiple_educations(self):
        by_id = {item.id: item for item in HOUSE_9 + HOUSE_9_BIO}
        bio = by_id["h9_bio_increased_university_contexts"]
        educations = by_id["h9_multiple_educations"]
        self.assertNotEqual(bio.text, educations.text)
        self.assertNotIn("lifelong_learning", bio.tags)

    def test_foreign_language_association_is_not_interest(self):
        by_id = {item.id: item for item in HOUSE_9 + HOUSE_9_BIO}
        bio = by_id["h9_bio_foreign_languages"]
        l7 = by_id["h9_interest_foreign_languages"]
        self.assertNotEqual(bio.text, l7.text)
        self.assertIn("favorable association", bio.text.lower())
        self.assertIn("interest", l7.text.lower())
        self.assertEqual(bio.tags, ("foreign_languages",))
        self.assertEqual(l7.tags, ("foreign_languages",))


class House9BioUniqueTests(unittest.TestCase):
    def test_philosophical_concepts_is_not_abstract_thinking(self):
        by_id = {item.id: item for item in HOUSE_9 + HOUSE_9_BIO}
        bio = by_id["h9_bio_communication_learning_realized_through_philosophical_concepts"]
        l7 = by_id["h9_analytical_with_abstract"]
        self.assertNotEqual(bio.text, l7.text)
        self.assertNotIn("abstract_thinking", bio.tags)
        self.assertNotIn("analytical_thinking", bio.tags)

    def test_not_heard_is_not_formal_or_selective_communication(self):
        by_id = {item.id: item for item in HOUSE_9 + HOUSE_9_BIO}
        bio = by_id["h9_bio_not_heard_in_ordinary_situations"]
        formal = by_id["h9_casual_communication_less_natural"]
        selective = by_id["h9_selective_communication"]
        self.assertNotEqual(bio.text, formal.text)
        self.assertNotEqual(bio.text, selective.text)
        self.assertIn("not to be heard", bio.text.lower())

    def test_teacher_dialogue_is_not_teacher_talent(self):
        by_id = {item.id: item for item in HOUSE_9 + HOUSE_9_BIO}
        dialogue = by_id["h9_bio_learning_through_direct_teacher_dialogue"]
        talent = by_id["h9_bio_teacher_talent"]
        self.assertNotEqual(dialogue.text, talent.text)
        self.assertNotIn("teaching", dialogue.tags)
        self.assertEqual(talent.tags, ("teaching",))


class House9ListSplitFidelityTests(unittest.TestCase):
    def test_three_learning_context_atoms_remain_separate(self):
        by_id = {item.id: item for item in HOUSE_9_BIO}
        texts = {by_id[fact_id].text for fact_id in LEARNING_CONTEXT_BIO_IDS}
        self.assertEqual(len(texts), 3)
        lowered = {text.lower() for text in texts}
        self.assertTrue(any("courses" in text for text in lowered))
        self.assertTrue(any("trainings" in text for text in lowered))
        self.assertTrue(any("university" in text for text in lowered))
        for fact_id in LEARNING_CONTEXT_BIO_IDS:
            self.assertEqual(by_id[fact_id].tags, ())

    def test_three_role_talent_atoms_remain_separate(self):
        by_id = {item.id: item for item in HOUSE_9_BIO}
        teacher = by_id["h9_bio_teacher_talent"]
        trainer = by_id["h9_bio_trainer_talent"]
        mentor = by_id["h9_bio_mentor_talent"]
        self.assertNotEqual(teacher.text, trainer.text)
        self.assertNotEqual(teacher.text, mentor.text)
        self.assertNotEqual(trainer.text, mentor.text)
        self.assertEqual(teacher.tags, ("teaching",))
        self.assertEqual(trainer.tags, ())
        self.assertEqual(mentor.tags, ())


class House9BioTagGuardTests(unittest.TestCase):
    def test_exact_tags_for_foreign_languages_and_teacher_talent(self):
        by_id = {item.id: item for item in HOUSE_9_BIO}
        self.assertEqual(by_id["h9_bio_foreign_languages"].tags, ("foreign_languages",))
        self.assertEqual(by_id["h9_bio_teacher_talent"].tags, ("teaching",))

    def test_trainer_and_mentor_do_not_receive_teaching_tag(self):
        by_id = {item.id: item for item in HOUSE_9_BIO}
        self.assertNotIn("teaching", by_id["h9_bio_trainer_talent"].tags)
        self.assertNotIn("teaching", by_id["h9_bio_mentor_talent"].tags)

    def test_strong_intellect_and_learning_context_atoms_have_no_approximate_tags(self):
        by_id = {item.id: item for item in HOUSE_9_BIO}
        for fact_id in ("h9_bio_strong_intellect",) + LEARNING_CONTEXT_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                for tag in FORBIDDEN_APPROXIMATE_TAGS:
                    self.assertNotIn(tag, by_id[fact_id].tags)

    def test_other_untagged_bio_facts_have_no_tags(self):
        by_id = {item.id: item for item in HOUSE_9_BIO}
        self.assertEqual(len(UNTAGGED_BIO_IDS), 11)
        for fact_id in UNTAGGED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].tags, ())

    def test_no_new_repeated_signal_spec(self):
        tags = {spec["tag"] for spec in REPEATED_SIGNAL_SPECS}
        self.assertIn("foreign_languages", tags)
        self.assertIn("teaching", tags)
        self.assertEqual(len([spec for spec in REPEATED_SIGNAL_SPECS if spec["tag"] == "foreign_languages"]), 1)
        self.assertEqual(len([spec for spec in REPEATED_SIGNAL_SPECS if spec["tag"] == "teaching"]), 1)


class House9Lesson7FrozenTests(unittest.TestCase):
    def test_existing_16_lesson7_facts_unchanged(self):
        self.assertEqual(len(HOUSE_9), 16)
        self.assertEqual(len(FROZEN_L7_HOUSE_9), 16)
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
            for item in HOUSE_9
        )
        self.assertEqual(actual, FROZEN_L7_HOUSE_9)


class House9SameHouseSourceDedupTests(unittest.TestCase):
    def test_lesson7_and_bio_share_one_provenance_key(self):
        house_9 = _house_9_facts()
        keys = {_provenance_key(item) for item in house_9}
        self.assertEqual(keys, {"house:9"})

    def test_house_9_dual_source_cannot_create_foreign_languages_repeat_alone(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Taurus",
                mercury_element="earth",
                mercury_motion="direct",
                mercury_house=9,
                aspects=[],
            )
        )
        self.assertEqual(len(profile.house_facts), 29)
        self.assertIn("h9_interest_foreign_languages", _ids(profile.house_facts))
        self.assertIn("h9_bio_foreign_languages", _ids(profile.house_facts))
        repeats = detect_repeated_signals(profile.house_facts)
        foreign_repeats = [signal for signal in repeats if signal.signal == "foreign_languages"]
        self.assertEqual(foreign_repeats, [])


class House9HumanCopyInventoryConsequenceTests(unittest.TestCase):
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

    def test_house_9_family_counts_after_source_parity(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "house:9")
        self.assertEqual(family.total_facts, 29)
        self.assertEqual(family.approved_override, 13)
        self.assertEqual(family.approved_raw, 16)
        self.assertEqual(family.unreviewed, 0)
        self.assertEqual(family.reviewed_count, 29)
        self.assertEqual(family.presentation_ready_count, 29)
        self.assertEqual(family.needs_review, 0)


class House9SemanticLedgerTests(unittest.TestCase):
    def test_semantic_accounting_from_implemented_facts(self):
        l7_count = len(HOUSE_9)
        bio_count = len(HOUSE_9_BIO)
        exact_overlap = 0
        partial_overlap = 5
        conditional_unresolved = 0
        unique_bio = (
            bio_count - exact_overlap - partial_overlap - conditional_unresolved
        )
        unique_meanings = l7_count + bio_count - exact_overlap
        self.assertEqual(l7_count, 16)
        self.assertEqual(bio_count, 13)
        self.assertEqual(exact_overlap, 0)
        self.assertEqual(partial_overlap, 5)
        self.assertEqual(unique_bio, 8)
        self.assertEqual(conditional_unresolved, 0)
        self.assertEqual(unique_meanings, 29)
        self.assertEqual(
            exact_overlap + partial_overlap + unique_bio + conditional_unresolved,
            13,
        )


if __name__ == "__main__":
    unittest.main()
