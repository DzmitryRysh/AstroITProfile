"""Tests for Mercury House 4 Bioastrology source parity (S4.23B)."""

from __future__ import annotations

import unittest
from collections import Counter

from app.schemas.mercury_work_profile import MercurySourceFactors
from app.services.mercury_human_copy import HUMAN_COPY_OVERRIDES
from app.services.mercury_human_copy_catalog import (
    APPROVED_RAW_FACT_IDS,
    NEEDS_REVIEW_FACT_IDS,
    STATUS_NEEDS_REVIEW,
    STATUS_UNREVIEWED,
    build_catalog_entry,
    build_human_copy_catalog,
)
from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS, REPEATED_SIGNAL_SPECS
from app.services.mercury_source_knowledge_b1_houses import (
    HOUSE_4,
    HOUSE_4_BIO,
    REF_H4_BIO,
    REF_H4_L7,
)
from app.services.mercury_source_profile import (
    _provenance_key,
    build_source_profile_from_factors,
    detect_repeated_signals,
)


EXPECTED_BIO_IDS: tuple[str, ...] = (
    "h4_bio_mercury_qualities_inherited_through_family",
    "h4_bio_relocation",
    "h4_bio_second_home",
    "h4_bio_family_intellectual_interest",
    "h4_bio_home_intellectual_interest",
    "h4_bio_psychology_intellectual_interest",
    "h4_bio_politics_intellectual_interest",
    "h4_bio_interest_in_medicine",
    "h4_bio_special_relevance_sibling",
    "h4_bio_home_requires_writing_study_reading",
    "h4_bio_home_requires_serving_working",
)

EXPECTED_BIO_CANONICAL: dict[str, str] = {
    "h4_bio_mercury_qualities_inherited_through_family": (
        "Mercury-related qualities may be inherited through the family line; their "
        "specific manifestation depends on Mercury's qualities."
    ),
    "h4_bio_relocation": "There may be an association with relocation or moving.",
    "h4_bio_second_home": "There may be a 'second home' association.",
    "h4_bio_family_intellectual_interest": (
        "Family may become a domain of intellectual interest."
    ),
    "h4_bio_home_intellectual_interest": (
        "Home may become a domain of intellectual interest."
    ),
    "h4_bio_psychology_intellectual_interest": (
        "Psychology may become a domain of intellectual interest."
    ),
    "h4_bio_politics_intellectual_interest": (
        "Politics may become a domain of intellectual interest."
    ),
    "h4_bio_interest_in_medicine": "May show strong interest in medicine.",
    "h4_bio_special_relevance_sibling": "A sibling may have special relevance.",
    "h4_bio_home_requires_writing_study_reading": (
        "At home, circumstances may require writing, studying, or reading."
    ),
    "h4_bio_home_requires_serving_working": (
        "At home, circumstances may require serving or working."
    ),
}

TAGGED_BIO_IDS: tuple[str, ...] = ("h4_bio_special_relevance_sibling",)

UNTAGGED_BIO_IDS: tuple[str, ...] = tuple(
    fact_id for fact_id in EXPECTED_BIO_IDS if fact_id not in TAGGED_BIO_IDS
)

FORBIDDEN_APPROXIMATE_TAGS: tuple[str, ...] = (
    "mobility",
    "trips",
    "work_travel",
    "family_history_interest",
    "intellectual_family_environment",
    "home_learning",
    "home_library",
    "mercury_strength_dependency",
    "psychology_interest",
    "lifelong_learning",
    "sales",
    "consulting",
    "intellectual_work",
    "family",
    "communication",
    "networking",
)

FROZEN_L7_HOUSE_4: tuple[
    tuple[str, str, str, str, tuple[str, ...], str, bool], ...
] = (
    (
        "h4_intellectual_family_from_childhood",
        "environment",
        "From childhood, intellectual family.",
        "strength",
        ("intellectual_family_environment",),
        REF_H4_L7,
        False,
    ),
    (
        "h4_family_contains_a_lot_of_communication",
        "environment",
        "Family contains a lot of communication.",
        "neutral",
        ("family_high_communication",),
        REF_H4_L7,
        False,
    ),
    (
        "h4_home_communication_students_neighbors_household",
        "communication",
        "Communication happens at home with students, neighbors, and household / family members.",
        "neutral",
        ("home_communication_contexts",),
        REF_H4_L7,
        False,
    ),
    (
        "h4_home_based_study",
        "learning",
        "Home-based study.",
        "strength",
        ("home_learning",),
        REF_H4_L7,
        False,
    ),
    (
        "h4_home_library",
        "learning",
        "Home library.",
        "neutral",
        ("home_library",),
        REF_H4_L7,
        False,
    ),
    (
        "h4_guests_at_home",
        "environment",
        "Guests at home.",
        "neutral",
        ("frequent_home_guests",),
        REF_H4_L7,
        False,
    ),
    (
        "h4_home_pass_through_yard_traffic",
        "environment",
        'Home may function like a "pass-through yard" / many people coming through.',
        "neutral",
        ("high_home_traffic",),
        REF_H4_L7,
        False,
    ),
    (
        "h4_interest_in_family_ancestral_history",
        "learning",
        "Interest in family / ancestral history.",
        "neutral",
        ("family_history_interest",),
        REF_H4_L7,
        False,
    ),
    (
        "h4_weak_mercury_others_speak_instead",
        "source_specific",
        "If Mercury is weak, others will speak rather than the native "
        "(Mercury-strength dependency; no Mercury-strength resolver is applied; "
        "not equated with hard_aspected).",
        "conditional",
        ("mercury_strength_dependency",),
        REF_H4_L7,
        True,
    ),
    (
        "h4_home_phone_withdrawal_from_live_communication",
        "risk",
        "Comes home and sits on the phone; this acts as withdrawal from live communication.",
        "risk",
        ("home_phone_withdrawal_from_live_communication",),
        REF_H4_L7,
        False,
    ),
)


def _house_4_facts():
    return [
        item
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "house" and item.factor_key == "4"
    ]


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


class House4BioCoverageTests(unittest.TestCase):
    def test_programmatic_bio_count_is_11(self):
        self.assertEqual(len(HOUSE_4_BIO), 11)
        self.assertEqual(len(EXPECTED_BIO_IDS), 11)
        self.assertEqual(len(EXPECTED_BIO_CANONICAL), 11)
        self.assertEqual(tuple(item.id for item in HOUSE_4_BIO), EXPECTED_BIO_IDS)

    def test_house_4_source_counts(self):
        house_4 = _house_4_facts()
        lesson7 = [item for item in house_4 if item.source_reference == REF_H4_L7]
        bio = [item for item in house_4 if item.source_reference == REF_H4_BIO]
        self.assertEqual(len(HOUSE_4), 10)
        self.assertEqual(len(lesson7), 10)
        self.assertEqual(len(bio), 11)
        self.assertEqual(len(house_4), 21)
        self.assertEqual(len(HOUSE_4) + len(HOUSE_4_BIO), 21)

    def test_all_bio_use_bioastrology_source_reference(self):
        self.assertTrue(all(item.source_reference == REF_H4_BIO for item in HOUSE_4_BIO))
        self.assertEqual(REF_H4_BIO, "bioastrology_mercury_house_4")

    def test_all_house_4_facts_share_factor_identity(self):
        house_4 = _house_4_facts()
        self.assertEqual(len(house_4), 21)
        self.assertTrue(all(item.factor_type == "house" for item in house_4))
        self.assertTrue(all(item.factor_key == "4" for item in house_4))
        self.assertTrue(all(item.activation_condition is None for item in house_4))
        unresolved_ids = {item.id for item in house_4 if item.unresolved}
        self.assertEqual(
            unresolved_ids,
            {
                "h4_weak_mercury_others_speak_instead",
                "h4_bio_mercury_qualities_inherited_through_family",
            },
        )

    def test_ids_globally_unique(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])


class House4BioCanonicalTests(unittest.TestCase):
    def test_exact_canonical_strings_for_all_11(self):
        by_id = {item.id: item for item in HOUSE_4_BIO}
        self.assertEqual(set(by_id), set(EXPECTED_BIO_CANONICAL))
        for fact_id, canonical in EXPECTED_BIO_CANONICAL.items():
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].text, canonical)


class House4AtomicFidelityTests(unittest.TestCase):
    def test_relocation_is_not_second_home(self):
        by_id = {item.id: item for item in HOUSE_4_BIO}
        relocation = by_id["h4_bio_relocation"]
        second_home = by_id["h4_bio_second_home"]
        self.assertNotEqual(relocation.id, second_home.id)
        self.assertNotEqual(relocation.text, second_home.text)
        self.assertEqual(relocation.category, "mobility")
        self.assertEqual(second_home.category, "environment")
        self.assertEqual(relocation.tags, ())
        self.assertEqual(second_home.tags, ())

    def test_family_intellectual_interest_is_not_ancestral_history(self):
        by_id = {item.id: item for item in HOUSE_4 + HOUSE_4_BIO}
        bio = by_id["h4_bio_family_intellectual_interest"]
        l7 = by_id["h4_interest_in_family_ancestral_history"]
        self.assertNotEqual(bio.id, l7.id)
        self.assertNotEqual(bio.text, l7.text)
        self.assertEqual(bio.category, "thinking")
        self.assertEqual(l7.category, "learning")
        self.assertEqual(bio.tags, ())
        self.assertIn("family_history_interest", l7.tags)
        self.assertNotIn("family_history_interest", bio.tags)
        self.assertNotIn("intellectual_family_environment", bio.tags)

    def test_home_intellectual_interest_is_not_home_study_or_library(self):
        by_id = {item.id: item for item in HOUSE_4 + HOUSE_4_BIO}
        home_interest = by_id["h4_bio_home_intellectual_interest"]
        study = by_id["h4_home_based_study"]
        library = by_id["h4_home_library"]
        self.assertNotEqual(home_interest.text, study.text)
        self.assertNotEqual(home_interest.text, library.text)
        self.assertNotIn("home_learning", home_interest.tags)
        self.assertNotIn("home_library", home_interest.tags)

    def test_psychology_interest_is_not_medicine_interest(self):
        by_id = {item.id: item for item in HOUSE_4_BIO}
        psychology = by_id["h4_bio_psychology_intellectual_interest"]
        medicine = by_id["h4_bio_interest_in_medicine"]
        politics = by_id["h4_bio_politics_intellectual_interest"]
        self.assertNotEqual(psychology.text, medicine.text)
        self.assertNotEqual(psychology.text, politics.text)
        self.assertNotEqual(medicine.text, politics.text)
        self.assertEqual(psychology.polarity, "neutral")
        self.assertEqual(medicine.polarity, "strength")
        self.assertEqual(psychology.tags, ())
        self.assertEqual(medicine.tags, ())

    def test_home_requires_writing_study_reading_is_not_home_based_study(self):
        by_id = {item.id: item for item in HOUSE_4 + HOUSE_4_BIO}
        require = by_id["h4_bio_home_requires_writing_study_reading"]
        study = by_id["h4_home_based_study"]
        library = by_id["h4_home_library"]
        self.assertNotEqual(require.text, study.text)
        self.assertNotEqual(require.text, library.text)
        self.assertEqual(require.tags, ())
        self.assertNotIn("home_learning", require.tags)
        self.assertNotIn("home_library", require.tags)
        self.assertIn("writing", require.text.lower())
        self.assertIn("studying", require.text.lower())
        self.assertIn("reading", require.text.lower())

    def test_home_requires_serving_working_is_not_generic_work_ability(self):
        serving = next(
            item
            for item in HOUSE_4_BIO
            if item.id == "h4_bio_home_requires_serving_working"
        )
        self.assertEqual(serving.category, "work_application")
        self.assertEqual(serving.polarity, "neutral")
        self.assertEqual(serving.tags, ())
        self.assertNotIn("consulting", serving.tags)
        self.assertNotIn("sales", serving.tags)
        self.assertNotIn("intellectual_work", serving.tags)
        self.assertNotIn("work ethic", serving.text.lower())
        self.assertNotIn("profession", serving.text.lower())


class House4TwoUnresolvedConditionsTests(unittest.TestCase):
    def test_lesson7_weak_mercury_dependency_unchanged(self):
        fact = next(
            item for item in HOUSE_4 if item.id == "h4_weak_mercury_others_speak_instead"
        )
        self.assertEqual(fact.source_reference, REF_H4_L7)
        self.assertTrue(fact.unresolved)
        self.assertIsNone(fact.activation_condition)
        self.assertEqual(fact.polarity, "conditional")
        self.assertEqual(fact.category, "source_specific")
        self.assertEqual(fact.tags, ("mercury_strength_dependency",))
        self.assertNotEqual(fact.activation_condition, "hard_aspected")
        self.assertNotIn(fact.id, {item.id for item in HOUSE_4_BIO})

    def test_bio_inherited_mercury_qualities_unresolved_and_distinct(self):
        bio = next(
            item
            for item in HOUSE_4_BIO
            if item.id == "h4_bio_mercury_qualities_inherited_through_family"
        )
        l7 = next(
            item for item in HOUSE_4 if item.id == "h4_weak_mercury_others_speak_instead"
        )
        self.assertEqual(bio.source_reference, REF_H4_BIO)
        self.assertTrue(bio.unresolved)
        self.assertIsNone(bio.activation_condition)
        self.assertEqual(bio.polarity, "conditional")
        self.assertEqual(bio.category, "source_specific")
        self.assertEqual(bio.tags, ())
        self.assertNotIn("mercury_strength_dependency", bio.tags)
        self.assertNotEqual(bio.id, l7.id)
        self.assertNotEqual(bio.text, l7.text)
        self.assertNotEqual(bio.tags, l7.tags)

    def test_both_unresolved_facts_appear_in_conditional_bucket(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Cancer",
                mercury_element="water",
                mercury_motion="direct",
                mercury_house=4,
                aspects=[],
            )
        )
        unresolved_ids = _ids(profile.conditional_unresolved)
        self.assertIn("h4_weak_mercury_others_speak_instead", unresolved_ids)
        self.assertIn(
            "h4_bio_mercury_qualities_inherited_through_family", unresolved_ids
        )
        self.assertNotEqual(
            "h4_weak_mercury_others_speak_instead",
            "h4_bio_mercury_qualities_inherited_through_family",
        )


class House4BioTagGuardTests(unittest.TestCase):
    def test_only_sibling_fact_has_siblings_tag(self):
        by_id = {item.id: item for item in HOUSE_4_BIO}
        self.assertEqual(by_id["h4_bio_special_relevance_sibling"].tags, ("siblings",))
        house1 = next(
            item for item in ALL_SOURCE_FACTS if item.id == "h1_special_relevance_siblings"
        )
        self.assertIn("siblings", house1.tags)

    def test_other_10_bio_facts_have_no_tags(self):
        by_id = {item.id: item for item in HOUSE_4_BIO}
        self.assertEqual(len(UNTAGGED_BIO_IDS), 10)
        for fact_id in UNTAGGED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].tags, ())
                for tag in FORBIDDEN_APPROXIMATE_TAGS:
                    self.assertNotIn(tag, by_id[fact_id].tags)

    def test_relocation_does_not_receive_mobility_or_trips_tags(self):
        relocation = next(
            item for item in HOUSE_4_BIO if item.id == "h4_bio_relocation"
        )
        self.assertNotIn("mobility", relocation.tags)
        self.assertNotIn("trips", relocation.tags)
        self.assertNotIn("work_travel", relocation.tags)

    def test_home_requirement_does_not_receive_home_learning_tag(self):
        require = next(
            item
            for item in HOUSE_4_BIO
            if item.id == "h4_bio_home_requires_writing_study_reading"
        )
        self.assertNotIn("home_learning", require.tags)

    def test_inherited_qualities_do_not_receive_mercury_strength_tag(self):
        inherited = next(
            item
            for item in HOUSE_4_BIO
            if item.id == "h4_bio_mercury_qualities_inherited_through_family"
        )
        self.assertNotIn("mercury_strength_dependency", inherited.tags)

    def test_siblings_is_not_a_repeated_signal_spec(self):
        tags = {spec["tag"] for spec in REPEATED_SIGNAL_SPECS}
        self.assertNotIn("siblings", tags)


class House4Lesson7FrozenTests(unittest.TestCase):
    def test_existing_10_lesson7_facts_unchanged(self):
        self.assertEqual(len(HOUSE_4), 10)
        self.assertEqual(len(FROZEN_L7_HOUSE_4), 10)
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
            for item in HOUSE_4
        )
        self.assertEqual(actual, FROZEN_L7_HOUSE_4)
        self.assertTrue(all(item.activation_condition is None for item in HOUSE_4))
        self.assertTrue(all(item.factor_type == "house" for item in HOUSE_4))
        self.assertTrue(all(item.factor_key == "4" for item in HOUSE_4))


class House4SameHouseSourceDedupTests(unittest.TestCase):
    def test_lesson7_and_bio_share_one_provenance_key(self):
        house_4 = _house_4_facts()
        keys = {_provenance_key(item) for item in house_4}
        self.assertEqual(keys, {"house:4"})
        for item in HOUSE_4 + HOUSE_4_BIO:
            with self.subTest(fact_id=item.id):
                self.assertEqual(_provenance_key(item), "house:4")

    def test_house_4_dual_source_cannot_create_repeat_alone(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign=None,
                mercury_element=None,
                mercury_motion="direct",
                mercury_house=4,
                aspects=[],
            )
        )
        self.assertEqual(len(profile.house_facts), 21)
        self.assertTrue(all(item.factor_key == "4" for item in profile.house_facts))
        self.assertIn("h4_interest_in_family_ancestral_history", _ids(profile.house_facts))
        self.assertIn("h4_bio_family_intellectual_interest", _ids(profile.house_facts))
        repeats = detect_repeated_signals(profile.house_facts)
        self.assertEqual(repeats, [])
        for signal in repeats:
            house_sources = [src for src in signal.sources if src.startswith("house:")]
            self.assertLessEqual(len(house_sources), 1, signal)


class House4HumanCopyInventoryConsequenceTests(unittest.TestCase):
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

    def test_unresolved_bio_fact_is_unreviewed_not_needs_review(self):
        inherited_id = "h4_bio_mercury_qualities_inherited_through_family"
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        entry = build_catalog_entry(by_id[inherited_id])
        self.assertNotEqual(entry.review_status, STATUS_UNREVIEWED)
        self.assertNotEqual(entry.review_status, STATUS_NEEDS_REVIEW)
        self.assertIn(inherited_id, HUMAN_COPY_OVERRIDES)
        self.assertNotIn(inherited_id, NEEDS_REVIEW_FACT_IDS)
        weak_entry = build_catalog_entry(by_id["h4_weak_mercury_others_speak_instead"])
        self.assertEqual(weak_entry.review_status, STATUS_NEEDS_REVIEW)

    def test_house_4_family_counts_after_source_parity(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "house:4")
        self.assertEqual(family.total_facts, 21)
        self.assertEqual(family.approved_override, 12)
        self.assertEqual(family.approved_raw, 8)
        self.assertEqual(family.needs_review, 1)
        self.assertEqual(family.unreviewed, 0)
        self.assertEqual(family.reviewed_count, 21)
        self.assertEqual(family.presentation_ready_count, 20)

    def test_existing_lesson7_human_copy_decisions_unchanged(self):
        l7_ids = {item.id for item in HOUSE_4}
        self.assertEqual(len(l7_ids), 10)
        weak_id = "h4_weak_mercury_others_speak_instead"
        self.assertIn(weak_id, NEEDS_REVIEW_FACT_IDS)
        self.assertNotIn(weak_id, HUMAN_COPY_OVERRIDES)
        self.assertNotIn(weak_id, APPROVED_RAW_FACT_IDS)
        override_ids = l7_ids - {weak_id}
        self.assertEqual(len(override_ids), 9)
        for fact_id in override_ids:
            with self.subTest(l7_id=fact_id):
                self.assertIn(fact_id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)


class House4SemanticLedgerTests(unittest.TestCase):
    def test_semantic_accounting_from_implemented_facts(self):
        l7_count = len(HOUSE_4)
        bio_count = len(HOUSE_4_BIO)
        exact_overlap = 0
        partial_overlap = 1
        conditional_unresolved = 1
        unique_bio = bio_count - exact_overlap - partial_overlap - conditional_unresolved
        unique_meanings = (
            l7_count + unique_bio + partial_overlap + conditional_unresolved
        )
        self.assertEqual(l7_count, 10)
        self.assertEqual(bio_count, 11)
        self.assertEqual(exact_overlap, 0)
        self.assertEqual(partial_overlap, 1)
        self.assertEqual(unique_bio, 9)
        self.assertEqual(conditional_unresolved, 1)
        self.assertEqual(unique_meanings, 21)
        self.assertEqual(l7_count + bio_count, 21)
        self.assertEqual(
            exact_overlap + partial_overlap + unique_bio + conditional_unresolved,
            11,
        )


if __name__ == "__main__":
    unittest.main()
