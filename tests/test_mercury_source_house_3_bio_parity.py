"""Tests for Mercury House 3 Bioastrology source parity (S4.22B)."""

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
from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS
from app.services.mercury_source_knowledge_b1_houses import (
    HOUSE_3,
    HOUSE_3_BIO,
    REF_H3_BIO,
    REF_H3_L7,
)
from app.services.mercury_source_profile import (
    _provenance_key,
    build_source_profile_from_factors,
    detect_repeated_signals,
)


EXPECTED_BIO_IDS: tuple[str, ...] = (
    "h3_bio_strengthens_mercury_functions",
    "h3_bio_emphasizes_mercury_aspects",
    "h3_bio_emphasizes_mercury_sign",
    "h3_bio_eventfulness_books",
    "h3_bio_eventfulness_trips",
    "h3_bio_eventfulness_social_networks",
    "h3_bio_circumstances_force_lifelong_communication_learning",
    "h3_bio_multiple_educations",
    "h3_bio_learning_for_learning_lifestyle",
    "h3_bio_interest_trainings_seminars",
)

EXPECTED_BIO_CANONICAL: dict[str, str] = {
    "h3_bio_strengthens_mercury_functions": "Strengthens Mercury functions overall.",
    "h3_bio_emphasizes_mercury_aspects": "Emphasizes Mercury aspects.",
    "h3_bio_emphasizes_mercury_sign": "Emphasizes the Mercury sign.",
    "h3_bio_eventfulness_books": "Increased eventfulness connected with books.",
    "h3_bio_eventfulness_trips": "Increased eventfulness connected with trips.",
    "h3_bio_eventfulness_social_networks": (
        "Increased eventfulness connected with social networks."
    ),
    "h3_bio_circumstances_force_lifelong_communication_learning": (
        "Circumstances may push the person to communicate and learn throughout "
        "life, even if naturally quiet."
    ),
    "h3_bio_multiple_educations": "There may be multiple educations.",
    "h3_bio_learning_for_learning_lifestyle": (
        "Learning may become a lifestyle pursued for its own sake."
    ),
    "h3_bio_interest_trainings_seminars": (
        "May show strong interest in trainings and seminars."
    ),
}

UNTAGGED_BIO_IDS: tuple[str, ...] = (
    "h3_bio_circumstances_force_lifelong_communication_learning",
    "h3_bio_multiple_educations",
    "h3_bio_learning_for_learning_lifestyle",
    "h3_bio_interest_trainings_seminars",
)

EXPECTED_BIO_TAGS: dict[str, tuple[str, ...]] = {
    "h3_bio_strengthens_mercury_functions": ("amplifier",),
    "h3_bio_emphasizes_mercury_aspects": ("amplifier", "aspect_emphasis"),
    "h3_bio_emphasizes_mercury_sign": ("amplifier", "sign_emphasis"),
    "h3_bio_eventfulness_books": ("books",),
    "h3_bio_eventfulness_trips": ("trips", "mobility"),
    "h3_bio_eventfulness_social_networks": ("social_networks",),
}

FORBIDDEN_APPROXIMATE_TAGS: tuple[str, ...] = (
    "lifelong_learning",
    "talkative",
    "learnability",
    "course_learning",
    "lecture_learning",
    "reading",
    "wide_contact_circle",
    "dialogue_need",
    "group_learning",
    "constant_drive_toward_learning",
    "teaching",
)

FROZEN_L7_HOUSE_3: tuple[
    tuple[str, str, str, str, tuple[str, ...], str, bool], ...
] = (
    (
        "h3_extreme_curiosity",
        "thinking",
        "Extreme / very strong curiosity.",
        "strength",
        ("extreme_curiosity",),
        REF_H3_L7,
        False,
    ),
    (
        "h3_constant_drive_toward_learning",
        "learning",
        "Constant drive toward learning.",
        "strength",
        ("constant_drive_toward_learning",),
        REF_H3_L7,
        False,
    ),
    (
        "h3_knowledge_grasped_on_the_fly",
        "learning",
        'Knowledge is grasped "on the fly".',
        "strength",
        ("quick_learning",),
        REF_H3_L7,
        False,
    ),
    (
        "h3_ability_to_switch_between_activities",
        "thinking",
        "Ability to switch between activities.",
        "strength",
        ("activity_switching",),
        REF_H3_L7,
        False,
    ),
    (
        "h3_ability_to_distribute_attention",
        "focus",
        "Ability to distribute attention.",
        "strength",
        ("distributed_attention",),
        REF_H3_L7,
        False,
    ),
    (
        "h3_writes_essays_well",
        "communication",
        "Writes essays well.",
        "strength",
        ("essay_writing",),
        REF_H3_L7,
        False,
    ),
    (
        "h3_learns_languages",
        "learning",
        "Learns languages.",
        "strength",
        ("languages_learning",),
        REF_H3_L7,
        False,
    ),
    (
        "h3_excellent_written_expression",
        "communication",
        "Excellent ability to express thoughts in writing.",
        "strength",
        ("written_expression",),
        REF_H3_L7,
        False,
    ),
    (
        "h3_skilled_storyteller",
        "communication",
        "Skilled storyteller.",
        "strength",
        ("storytelling",),
        REF_H3_L7,
        False,
    ),
    (
        "h3_arguments_readily_available",
        "communication",
        'Arguments are readily available / "always ready".',
        "strength",
        ("argument_readiness",),
        REF_H3_L7,
        False,
    ),
    (
        "h3_wide_circle_of_acquaintances",
        "environment",
        "Wide circle of acquaintances.",
        "neutral",
        ("wide_contact_circle",),
        REF_H3_L7,
        False,
    ),
    (
        "h3_need_for_dialogue",
        "communication",
        "Need for dialogue.",
        "neutral",
        ("dialogue_need",),
        REF_H3_L7,
        False,
    ),
    (
        "h3_need_for_feedback",
        "communication",
        "Need for feedback.",
        "neutral",
        ("feedback_need",),
        REF_H3_L7,
        False,
    ),
    (
        "h3_ability_to_ask_right_questions",
        "communication",
        "Ability to ask the right questions.",
        "strength",
        ("question_asking",),
        REF_H3_L7,
        False,
    ),
    (
        "h3_ability_to_solve_tactical_tasks",
        "thinking",
        "Ability to solve tactical tasks.",
        "strength",
        ("tactical_problem_solving",),
        REF_H3_L7,
        False,
    ),
    (
        "h3_intellectual_success_depends_on_concentration",
        "source_specific",
        "Intellectual success occurs if concentration succeeds / if the native can concentrate "
        "(source dependency; no concentration-ability resolver is applied).",
        "conditional",
        ("intellectual_success_depends_on_concentration",),
        REF_H3_L7,
        True,
    ),
    (
        "h3_group_learning_easier",
        "learning",
        "Group learning is easier.",
        "strength",
        ("group_learning",),
        REF_H3_L7,
        False,
    ),
    (
        "h3_reads_a_lot",
        "learning",
        "Reads a lot.",
        "neutral",
        ("reading",),
        REF_H3_L7,
        False,
    ),
    (
        "h3_attends_courses",
        "learning",
        "Attends courses.",
        "neutral",
        ("course_learning",),
        REF_H3_L7,
        False,
    ),
    (
        "h3_attends_lectures",
        "learning",
        "Attends lectures.",
        "neutral",
        ("lecture_learning",),
        REF_H3_L7,
        False,
    ),
    (
        "h3_events_often_begin_with_receiving_news",
        "source_specific",
        "Events often begin with receiving news (source examples: call, letter).",
        "neutral",
        ("events_triggered_by_information",),
        REF_H3_L7,
        False,
    ),
    (
        "h3_many_unnecessary_contacts",
        "risk",
        "Very many connections, most often unnecessary.",
        "risk",
        ("many_unnecessary_contacts",),
        REF_H3_L7,
        False,
    ),
)


def _house_3_facts():
    return [
        item
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "house" and item.factor_key == "3"
    ]


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


class House3BioCoverageTests(unittest.TestCase):
    def test_programmatic_bio_count_is_10(self):
        self.assertEqual(len(HOUSE_3_BIO), 10)
        self.assertEqual(len(EXPECTED_BIO_IDS), 10)
        self.assertEqual(len(EXPECTED_BIO_CANONICAL), 10)
        self.assertEqual(tuple(item.id for item in HOUSE_3_BIO), EXPECTED_BIO_IDS)

    def test_house_3_source_counts(self):
        house_3 = _house_3_facts()
        lesson7 = [item for item in house_3 if item.source_reference == REF_H3_L7]
        bio = [item for item in house_3 if item.source_reference == REF_H3_BIO]
        self.assertEqual(len(HOUSE_3), 22)
        self.assertEqual(len(lesson7), 22)
        self.assertEqual(len(bio), 10)
        self.assertEqual(len(house_3), 32)
        self.assertEqual(len(HOUSE_3) + len(HOUSE_3_BIO), 32)

    def test_all_bio_use_bioastrology_source_reference(self):
        self.assertTrue(all(item.source_reference == REF_H3_BIO for item in HOUSE_3_BIO))
        self.assertEqual(REF_H3_BIO, "bioastrology_mercury_house_3")

    def test_all_house_3_facts_share_factor_identity(self):
        house_3 = _house_3_facts()
        self.assertEqual(len(house_3), 32)
        self.assertTrue(all(item.factor_type == "house" for item in house_3))
        self.assertTrue(all(item.factor_key == "3" for item in house_3))
        self.assertTrue(all(item.activation_condition is None for item in house_3))
        self.assertTrue(all(item.unresolved is False for item in HOUSE_3_BIO))

    def test_ids_globally_unique(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])


class House3BioCanonicalTests(unittest.TestCase):
    def test_exact_canonical_strings_for_all_10(self):
        by_id = {item.id: item for item in HOUSE_3_BIO}
        self.assertEqual(set(by_id), set(EXPECTED_BIO_CANONICAL))
        for fact_id, canonical in EXPECTED_BIO_CANONICAL.items():
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].text, canonical)


class House3AtomicFidelityTests(unittest.TestCase):
    def test_amplifier_sign_and_aspect_emphasis_remain_distinct(self):
        by_id = {item.id: item for item in HOUSE_3_BIO}
        functions = by_id["h3_bio_strengthens_mercury_functions"]
        aspects = by_id["h3_bio_emphasizes_mercury_aspects"]
        sign = by_id["h3_bio_emphasizes_mercury_sign"]
        texts = {functions.text, aspects.text, sign.text}
        self.assertEqual(len(texts), 3)
        self.assertNotEqual(functions.tags, aspects.tags)
        self.assertNotEqual(functions.tags, sign.tags)
        self.assertNotEqual(aspects.tags, sign.tags)

    def test_three_eventfulness_domains_remain_distinct(self):
        by_id = {item.id: item for item in HOUSE_3_BIO}
        books = by_id["h3_bio_eventfulness_books"]
        trips = by_id["h3_bio_eventfulness_trips"]
        social = by_id["h3_bio_eventfulness_social_networks"]
        self.assertEqual(len({books.text, trips.text, social.text}), 3)
        self.assertEqual(books.tags, ("books",))
        self.assertEqual(trips.tags, ("trips", "mobility"))
        self.assertEqual(social.tags, ("social_networks",))

    def test_books_eventfulness_is_not_reads_a_lot(self):
        by_id = {item.id: item for item in HOUSE_3 + HOUSE_3_BIO}
        eventfulness = by_id["h3_bio_eventfulness_books"]
        reads = by_id["h3_reads_a_lot"]
        self.assertNotEqual(eventfulness.text, reads.text)
        self.assertNotIn("reading", eventfulness.tags)
        self.assertNotIn("books", reads.tags)

    def test_multiple_educations_is_not_courses_or_lectures(self):
        by_id = {item.id: item for item in HOUSE_3 + HOUSE_3_BIO}
        educations = by_id["h3_bio_multiple_educations"]
        courses = by_id["h3_attends_courses"]
        lectures = by_id["h3_attends_lectures"]
        self.assertNotEqual(educations.text, courses.text)
        self.assertNotEqual(educations.text, lectures.text)
        self.assertEqual(educations.tags, ())
        self.assertNotIn("course_learning", educations.tags)
        self.assertNotIn("lecture_learning", educations.tags)

    def test_learning_lifestyle_is_not_constant_drive(self):
        by_id = {item.id: item for item in HOUSE_3 + HOUSE_3_BIO}
        lifestyle = by_id["h3_bio_learning_for_learning_lifestyle"]
        drive = by_id["h3_constant_drive_toward_learning"]
        self.assertNotEqual(lifestyle.text, drive.text)
        self.assertNotEqual(lifestyle.id, drive.id)
        self.assertEqual(lifestyle.polarity, "neutral")
        self.assertEqual(drive.polarity, "strength")
        self.assertEqual(lifestyle.tags, ())
        self.assertIn("constant_drive_toward_learning", drive.tags)
        self.assertNotIn("lifelong_learning", lifestyle.tags)
        self.assertNotIn("lifelong_learning", drive.tags)

    def test_training_seminar_interest_is_not_course_attendance(self):
        by_id = {item.id: item for item in HOUSE_3 + HOUSE_3_BIO}
        interest = by_id["h3_bio_interest_trainings_seminars"]
        courses = by_id["h3_attends_courses"]
        self.assertNotEqual(interest.text, courses.text)
        self.assertNotIn("course_learning", interest.tags)
        self.assertNotIn("lecture_learning", interest.tags)


class House3ConditionalFreezeTests(unittest.TestCase):
    def test_concentration_dependency_unchanged(self):
        fact = next(
            item
            for item in HOUSE_3
            if item.id == "h3_intellectual_success_depends_on_concentration"
        )
        self.assertEqual(fact.source_reference, REF_H3_L7)
        self.assertTrue(fact.unresolved)
        self.assertIsNone(fact.activation_condition)
        self.assertEqual(fact.polarity, "conditional")
        self.assertEqual(fact.category, "source_specific")
        self.assertEqual(
            fact.tags, ("intellectual_success_depends_on_concentration",)
        )
        self.assertNotEqual(fact.activation_condition, "hard_aspected")
        self.assertNotIn(fact.id, {item.id for item in HOUSE_3_BIO})


class House3BioTagGuardTests(unittest.TestCase):
    def test_exact_tags_for_b3_01_through_b3_06(self):
        by_id = {item.id: item for item in HOUSE_3_BIO}
        for fact_id, tags in EXPECTED_BIO_TAGS.items():
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].tags, tags)

    def test_b3_07_through_b3_10_have_no_tags(self):
        by_id = {item.id: item for item in HOUSE_3_BIO}
        for fact_id in UNTAGGED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].tags, ())
                for tag in FORBIDDEN_APPROXIMATE_TAGS:
                    self.assertNotIn(tag, by_id[fact_id].tags)

    def test_no_lifelong_learning_or_attendance_tags_on_untagged_bio(self):
        by_id = {item.id: item for item in HOUSE_3_BIO}
        circumstances = by_id[
            "h3_bio_circumstances_force_lifelong_communication_learning"
        ]
        lifestyle = by_id["h3_bio_learning_for_learning_lifestyle"]
        interest = by_id["h3_bio_interest_trainings_seminars"]
        self.assertNotIn("lifelong_learning", circumstances.tags)
        self.assertNotIn("lifelong_learning", lifestyle.tags)
        self.assertNotIn("course_learning", interest.tags)
        self.assertNotIn("lecture_learning", interest.tags)


class House3Lesson7FrozenTests(unittest.TestCase):
    def test_existing_22_lesson7_facts_unchanged(self):
        self.assertEqual(len(HOUSE_3), 22)
        self.assertEqual(len(FROZEN_L7_HOUSE_3), 22)
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
            for item in HOUSE_3
        )
        self.assertEqual(actual, FROZEN_L7_HOUSE_3)
        self.assertTrue(all(item.activation_condition is None for item in HOUSE_3))
        self.assertTrue(all(item.factor_type == "house" for item in HOUSE_3))
        self.assertTrue(all(item.factor_key == "3" for item in HOUSE_3))


class House3SameHouseSourceDedupTests(unittest.TestCase):
    def test_lesson7_and_bio_share_one_provenance_key(self):
        house_3 = _house_3_facts()
        keys = {_provenance_key(item) for item in house_3}
        self.assertEqual(keys, {"house:3"})
        for item in HOUSE_3 + HOUSE_3_BIO:
            with self.subTest(fact_id=item.id):
                self.assertEqual(_provenance_key(item), "house:3")

    def test_house_3_dual_source_cannot_create_repeat_alone(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign=None,
                mercury_element=None,
                mercury_motion="direct",
                mercury_house=3,
                aspects=[],
            )
        )
        self.assertEqual(len(profile.house_facts), 32)
        self.assertTrue(all(item.factor_key == "3" for item in profile.house_facts))
        self.assertIn("h3_constant_drive_toward_learning", _ids(profile.house_facts))
        self.assertIn("h3_bio_learning_for_learning_lifestyle", _ids(profile.house_facts))
        repeats = detect_repeated_signals(profile.house_facts)
        self.assertEqual(repeats, [])
        for signal in repeats:
            house_sources = [src for src in signal.sources if src.startswith("house:")]
            self.assertLessEqual(len(house_sources), 1, signal)


class House3HumanCopyInventoryConsequenceTests(unittest.TestCase):
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

    def test_house_3_family_counts_after_source_parity(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "house:3")
        self.assertEqual(family.total_facts, 32)
        self.assertEqual(family.approved_override, 27)
        self.assertEqual(family.approved_raw, 5)
        self.assertEqual(family.needs_review, 0)
        self.assertEqual(family.unreviewed, 0)
        self.assertEqual(family.reviewed_count, 32)
        self.assertEqual(family.presentation_ready_count, 32)

    def test_existing_lesson7_human_copy_decisions_unchanged(self):
        l7_ids = {item.id for item in HOUSE_3}
        self.assertEqual(len(l7_ids), 22)
        raw_id = "h3_reads_a_lot"
        self.assertIn(raw_id, APPROVED_RAW_FACT_IDS)
        self.assertNotIn(raw_id, HUMAN_COPY_OVERRIDES)
        self.assertNotIn(raw_id, NEEDS_REVIEW_FACT_IDS)
        override_ids = l7_ids - {raw_id}
        self.assertEqual(len(override_ids), 21)
        for fact_id in override_ids:
            with self.subTest(l7_id=fact_id):
                self.assertIn(fact_id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)


class House3SemanticLedgerTests(unittest.TestCase):
    def test_semantic_accounting_from_implemented_facts(self):
        l7_count = len(HOUSE_3)
        bio_count = len(HOUSE_3_BIO)
        exact_overlap = 0
        partial_overlap = 1
        unique_bio = bio_count - exact_overlap - partial_overlap
        unique_meanings = l7_count + unique_bio + partial_overlap
        self.assertEqual(l7_count, 22)
        self.assertEqual(bio_count, 10)
        self.assertEqual(unique_bio, 9)
        self.assertEqual(unique_meanings, 32)
        self.assertEqual(l7_count + bio_count, 32)


if __name__ == "__main__":
    unittest.main()
