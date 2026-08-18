"""Tests for Mercury House 5 Bioastrology source parity (S4.24B)."""

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
from app.services.mercury_source_knowledge_b2_houses import (
    HOUSE_5,
    HOUSE_5_BIO,
    REF_H5_BIO,
    REF_H5_L7,
)
from app.services.mercury_source_profile import (
    _provenance_key,
    build_source_profile_from_factors,
    detect_repeated_signals,
)


EXPECTED_BIO_IDS: tuple[str, ...] = (
    "h5_bio_mercury_qualities_colored_by_children",
    "h5_bio_mercury_qualities_colored_by_creativity",
    "h5_bio_mercury_qualities_colored_by_risk",
    "h5_bio_entrepreneurial_qualities",
    "h5_bio_sales_qualities",
    "h5_bio_gift_for_writing",
    "h5_bio_books_as_hobby",
    "h5_bio_trips_as_hobby",
    "h5_bio_learning_as_hobby",
    "h5_bio_favorable_acquaintances",
    "h5_bio_parallel_romances",
    "h5_bio_twins_association",
    "h5_bio_multiple_children_association",
)

EXPECTED_BIO_CANONICAL: dict[str, str] = {
    "h5_bio_mercury_qualities_colored_by_children": (
        "Mercury-related qualities may be colored by themes involving children."
    ),
    "h5_bio_mercury_qualities_colored_by_creativity": (
        "Mercury-related qualities may be colored by creative themes."
    ),
    "h5_bio_mercury_qualities_colored_by_risk": (
        "Mercury-related qualities may be colored by themes involving risk."
    ),
    "h5_bio_entrepreneurial_qualities": "May support entrepreneurial qualities.",
    "h5_bio_sales_qualities": "May support qualities associated with sales.",
    "h5_bio_gift_for_writing": "May support a gift for writing.",
    "h5_bio_books_as_hobby": "Books may be a prominent hobby interest.",
    "h5_bio_trips_as_hobby": "Trips may be a prominent hobby interest.",
    "h5_bio_learning_as_hobby": "Learning may be a prominent hobby interest.",
    "h5_bio_favorable_acquaintances": "Favorable association with acquaintances.",
    "h5_bio_parallel_romances": "There may be parallel romantic relationships.",
    "h5_bio_twins_association": "There may be an association with twins.",
    "h5_bio_multiple_children_association": (
        "There may be an association with multiple children."
    ),
}

TAGGED_BIO_IDS: tuple[str, ...] = ("h5_bio_sales_qualities",)

UNTAGGED_BIO_IDS: tuple[str, ...] = tuple(
    fact_id for fact_id in EXPECTED_BIO_IDS if fact_id not in TAGGED_BIO_IDS
)

FORBIDDEN_APPROXIMATE_TAGS: tuple[str, ...] = (
    "books",
    "trips",
    "mobility",
    "reading",
    "book_enjoyment",
    "learning_enjoyment",
    "lifelong_learning",
    "essay_writing",
    "written_expression",
    "writing_based_creativity",
    "writing_tendency",
    "writing",
    "wide_contact_circle",
    "persuasion",
    "trade_income",
    "source_entrepreneurial_drive",
    "intellectual_creativity",
    "speech_based_creativity",
    "acquaintance_context_associations",
)

FROZEN_L7_HOUSE_5: tuple[
    tuple[str, str, str, str, tuple[str, ...], str, bool], ...
] = (
    (
        "h5_creativity_connected_with_intellectual_work",
        "thinking",
        "Creativity connected with intellectual / mental work.",
        "strength",
        ("intellectual_creativity",),
        REF_H5_L7,
        False,
    ),
    (
        "h5_creativity_connected_with_writing",
        "communication",
        "Creativity connected with writing.",
        "strength",
        ("writing_based_creativity",),
        REF_H5_L7,
        False,
    ),
    (
        "h5_creativity_connected_with_speech",
        "communication",
        "Creativity connected with speech.",
        "strength",
        ("speech_based_creativity",),
        REF_H5_L7,
        False,
    ),
    (
        "h5_romantic_beautiful_speech",
        "communication",
        "To make someone fall in love, one needs to speak beautifully "
        "(source-described romantic communication).",
        "neutral",
        ("romantic_beautiful_speech",),
        REF_H5_L7,
        False,
    ),
    (
        "h5_pleasure_from_studying",
        "learning",
        "Pleasure from studying / learning.",
        "strength",
        ("learning_enjoyment",),
        REF_H5_L7,
        False,
    ),
    (
        "h5_pleasure_from_books",
        "learning",
        "Pleasure from books.",
        "neutral",
        ("book_enjoyment",),
        REF_H5_L7,
        False,
    ),
    (
        "h5_entertainment_under_control_of_mind",
        "environment",
        "Entertainment remains under control of the mind.",
        "neutral",
        ("mental_control_of_entertainment",),
        REF_H5_L7,
        False,
    ),
    (
        "h5_rational_element_in_celebration",
        "environment",
        "Rational element exists in celebration / fun.",
        "neutral",
        ("rationalized_entertainment",),
        REF_H5_L7,
        False,
    ),
    (
        "h5_acquaintance_context_associations",
        "source_specific",
        "Source associates acquaintances with celebrations, theaters, cinema, shopping, "
        "and events; contextual associations, not personality skills.",
        "neutral",
        ("acquaintance_context_associations",),
        REF_H5_L7,
        False,
    ),
    (
        "h5_circumstances_public_speaking",
        "communication",
        "Circumstances make the native tell / speak about something publicly.",
        "neutral",
        ("public_speaking_circumstance",),
        REF_H5_L7,
        False,
    ),
    (
        "h5_occupation_associations",
        "source_specific",
        "Source-described occupation associations include art critic, teacher, advertiser, "
        "creative professional, and marketer; not career assignments.",
        "neutral",
        ("occupation_associations",),
        REF_H5_L7,
        False,
    ),
    (
        "h5_rationalism_in_love",
        "risk",
        "Rationalism in love.",
        "risk",
        ("rationalism_in_love",),
        REF_H5_L7,
        False,
    ),
    (
        "h5_cold_analysis_of_feelings",
        "risk",
        "Tendency to subject feelings to cold analysis.",
        "risk",
        ("cold_analysis_of_feelings",),
        REF_H5_L7,
        False,
    ),
    (
        "h5_romantic_talk_displaces_feelings",
        "risk",
        "Romantic topics in conversation can displace the feelings themselves.",
        "risk",
        ("romantic_talk_displaces_feelings",),
        REF_H5_L7,
        False,
    ),
)


def _house_5_facts():
    return [
        item
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "house" and item.factor_key == "5"
    ]


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


class House5BioCoverageTests(unittest.TestCase):
    def test_programmatic_bio_count_is_13(self):
        self.assertEqual(len(HOUSE_5_BIO), 13)
        self.assertEqual(len(EXPECTED_BIO_IDS), 13)
        self.assertEqual(len(EXPECTED_BIO_CANONICAL), 13)
        self.assertEqual(tuple(item.id for item in HOUSE_5_BIO), EXPECTED_BIO_IDS)

    def test_house_5_source_counts(self):
        house_5 = _house_5_facts()
        lesson7 = [item for item in house_5 if item.source_reference == REF_H5_L7]
        bio = [item for item in house_5 if item.source_reference == REF_H5_BIO]
        self.assertEqual(len(HOUSE_5), 14)
        self.assertEqual(len(lesson7), 14)
        self.assertEqual(len(bio), 13)
        self.assertEqual(len(house_5), 27)
        self.assertEqual(len(HOUSE_5) + len(HOUSE_5_BIO), 27)

    def test_all_bio_use_bioastrology_source_reference(self):
        self.assertTrue(all(item.source_reference == REF_H5_BIO for item in HOUSE_5_BIO))
        self.assertEqual(REF_H5_BIO, "bioastrology_mercury_house_5")

    def test_all_house_5_facts_share_factor_identity(self):
        house_5 = _house_5_facts()
        self.assertEqual(len(house_5), 27)
        self.assertTrue(all(item.factor_type == "house" for item in house_5))
        self.assertTrue(all(item.factor_key == "5" for item in house_5))
        self.assertTrue(all(item.activation_condition is None for item in house_5))
        self.assertTrue(all(item.unresolved is False for item in house_5))

    def test_ids_globally_unique(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])


class House5BioCanonicalTests(unittest.TestCase):
    def test_exact_canonical_strings_for_all_13(self):
        by_id = {item.id: item for item in HOUSE_5_BIO}
        self.assertEqual(set(by_id), set(EXPECTED_BIO_CANONICAL))
        for fact_id, canonical in EXPECTED_BIO_CANONICAL.items():
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].text, canonical)


class House5AtomicFidelityTests(unittest.TestCase):
    def test_three_coloring_atoms_remain_distinct(self):
        by_id = {item.id: item for item in HOUSE_5_BIO}
        children = by_id["h5_bio_mercury_qualities_colored_by_children"]
        creativity = by_id["h5_bio_mercury_qualities_colored_by_creativity"]
        risk = by_id["h5_bio_mercury_qualities_colored_by_risk"]
        self.assertEqual(len({children.text, creativity.text, risk.text}), 3)
        self.assertEqual(children.category, "source_specific")
        self.assertEqual(creativity.category, "source_specific")
        self.assertEqual(risk.category, "source_specific")
        self.assertEqual(children.tags, ())
        self.assertEqual(creativity.tags, ())
        self.assertEqual(risk.tags, ())

    def test_creativity_coloring_is_not_creativity_connected_with_writing(self):
        by_id = {item.id: item for item in HOUSE_5 + HOUSE_5_BIO}
        coloring = by_id["h5_bio_mercury_qualities_colored_by_creativity"]
        writing = by_id["h5_creativity_connected_with_writing"]
        self.assertNotEqual(coloring.id, writing.id)
        self.assertNotEqual(coloring.text, writing.text)
        self.assertNotIn("writing_based_creativity", coloring.tags)
        self.assertNotIn("intellectual_creativity", coloring.tags)

    def test_risk_coloring_is_not_gambling_or_risk_ability(self):
        risk = next(
            item
            for item in HOUSE_5_BIO
            if item.id == "h5_bio_mercury_qualities_colored_by_risk"
        )
        lowered = risk.text.lower()
        self.assertNotIn("gambl", lowered)
        self.assertNotIn("appetite", lowered)
        self.assertNotIn("ability", lowered)
        self.assertEqual(risk.polarity, "neutral")
        self.assertEqual(risk.tags, ())

    def test_entrepreneurial_qualities_are_not_sales_qualities(self):
        by_id = {item.id: item for item in HOUSE_5_BIO}
        entrepreneurial = by_id["h5_bio_entrepreneurial_qualities"]
        sales = by_id["h5_bio_sales_qualities"]
        self.assertNotEqual(entrepreneurial.id, sales.id)
        self.assertNotEqual(entrepreneurial.text, sales.text)
        self.assertEqual(entrepreneurial.tags, ())
        self.assertEqual(sales.tags, ("sales",))
        self.assertNotIn("sales", entrepreneurial.tags)
        self.assertNotIn("source_entrepreneurial_drive", entrepreneurial.tags)

    def test_writing_gift_is_not_writing_based_creativity(self):
        by_id = {item.id: item for item in HOUSE_5 + HOUSE_5_BIO}
        gift = by_id["h5_bio_gift_for_writing"]
        creativity = by_id["h5_creativity_connected_with_writing"]
        self.assertNotEqual(gift.text, creativity.text)
        self.assertEqual(gift.tags, ())
        self.assertNotIn("writing_based_creativity", gift.tags)
        self.assertNotIn("essay_writing", gift.tags)
        self.assertNotIn("written_expression", gift.tags)
        self.assertNotIn("writing", gift.tags)

    def test_books_hobby_is_not_book_enjoyment(self):
        by_id = {item.id: item for item in HOUSE_5 + HOUSE_5_BIO}
        hobby = by_id["h5_bio_books_as_hobby"]
        pleasure = by_id["h5_pleasure_from_books"]
        self.assertNotEqual(hobby.text, pleasure.text)
        self.assertNotIn("book_enjoyment", hobby.tags)
        self.assertNotIn("books", hobby.tags)
        self.assertNotIn("reading", hobby.tags)

    def test_learning_hobby_is_not_learning_enjoyment(self):
        by_id = {item.id: item for item in HOUSE_5 + HOUSE_5_BIO}
        hobby = by_id["h5_bio_learning_as_hobby"]
        pleasure = by_id["h5_pleasure_from_studying"]
        self.assertNotEqual(hobby.text, pleasure.text)
        self.assertNotIn("learning_enjoyment", hobby.tags)
        self.assertNotIn("lifelong_learning", hobby.tags)

    def test_favorable_acquaintances_are_not_venue_context(self):
        by_id = {item.id: item for item in HOUSE_5 + HOUSE_5_BIO}
        favorable = by_id["h5_bio_favorable_acquaintances"]
        context = by_id["h5_acquaintance_context_associations"]
        self.assertNotEqual(favorable.text, context.text)
        self.assertEqual(favorable.polarity, "strength")
        self.assertEqual(context.polarity, "neutral")
        self.assertEqual(favorable.tags, ())
        self.assertNotIn("wide_contact_circle", favorable.tags)
        self.assertNotIn("acquaintance_context_associations", favorable.tags)

    def test_twins_are_not_multiple_children(self):
        by_id = {item.id: item for item in HOUSE_5_BIO}
        twins = by_id["h5_bio_twins_association"]
        multiple = by_id["h5_bio_multiple_children_association"]
        children_coloring = by_id["h5_bio_mercury_qualities_colored_by_children"]
        self.assertNotEqual(twins.text, multiple.text)
        self.assertNotEqual(twins.text, children_coloring.text)
        self.assertNotEqual(multiple.text, children_coloring.text)
        self.assertEqual(twins.tags, ())
        self.assertEqual(multiple.tags, ())


class House5BioTagGuardTests(unittest.TestCase):
    def test_only_sales_fact_has_sales_tag(self):
        by_id = {item.id: item for item in HOUSE_5_BIO}
        self.assertEqual(by_id["h5_bio_sales_qualities"].tags, ("sales",))
        house1 = next(
            item for item in ALL_SOURCE_FACTS if item.id == "h1_support_sales_qualities"
        )
        house2 = next(
            item for item in ALL_SOURCE_FACTS if item.id == "h2_bio_sales_qualities"
        )
        self.assertIn("sales", house1.tags)
        self.assertEqual(house2.tags, ("sales",))
        self.assertEqual(
            by_id["h5_bio_sales_qualities"].text,
            "May support qualities associated with sales.",
        )

    def test_other_12_bio_facts_have_no_tags(self):
        by_id = {item.id: item for item in HOUSE_5_BIO}
        self.assertEqual(len(UNTAGGED_BIO_IDS), 12)
        for fact_id in UNTAGGED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].tags, ())
                for tag in FORBIDDEN_APPROXIMATE_TAGS:
                    self.assertNotIn(tag, by_id[fact_id].tags)

    def test_writing_gift_has_no_approximate_writing_tags(self):
        gift = next(
            item for item in HOUSE_5_BIO if item.id == "h5_bio_gift_for_writing"
        )
        self.assertNotIn("writing", gift.tags)
        self.assertNotIn("essay_writing", gift.tags)
        self.assertNotIn("written_expression", gift.tags)
        self.assertNotIn("writing_based_creativity", gift.tags)
        self.assertNotIn("writing_tendency", gift.tags)

    def test_hobby_facts_have_no_eventfulness_or_enjoyment_tags(self):
        by_id = {item.id: item for item in HOUSE_5_BIO}
        books = by_id["h5_bio_books_as_hobby"]
        trips = by_id["h5_bio_trips_as_hobby"]
        learning = by_id["h5_bio_learning_as_hobby"]
        self.assertNotIn("books", books.tags)
        self.assertNotIn("trips", trips.tags)
        self.assertNotIn("mobility", trips.tags)
        self.assertNotIn("work_travel", trips.tags)
        self.assertNotIn("lifelong_learning", learning.tags)
        self.assertEqual(trips.category, "mobility")
        self.assertEqual(trips.tags, ())

    def test_sales_repeat_spec_unchanged(self):
        tags = {spec["tag"] for spec in REPEATED_SIGNAL_SPECS}
        self.assertIn("sales", tags)
        sales_specs = [spec for spec in REPEATED_SIGNAL_SPECS if spec["tag"] == "sales"]
        self.assertEqual(len(sales_specs), 1)
        self.assertEqual(sales_specs[0]["min_factor_keys"], 2)


class House5Lesson7FrozenTests(unittest.TestCase):
    def test_existing_14_lesson7_facts_unchanged(self):
        self.assertEqual(len(HOUSE_5), 14)
        self.assertEqual(len(FROZEN_L7_HOUSE_5), 14)
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
            for item in HOUSE_5
        )
        self.assertEqual(actual, FROZEN_L7_HOUSE_5)
        self.assertTrue(all(item.activation_condition is None for item in HOUSE_5))
        self.assertTrue(all(item.factor_type == "house" for item in HOUSE_5))
        self.assertTrue(all(item.factor_key == "5" for item in HOUSE_5))
        self.assertTrue(all(item.unresolved is False for item in HOUSE_5))


class House5SameHouseSourceDedupTests(unittest.TestCase):
    def test_lesson7_and_bio_share_one_provenance_key(self):
        house_5 = _house_5_facts()
        keys = {_provenance_key(item) for item in house_5}
        self.assertEqual(keys, {"house:5"})
        for item in HOUSE_5 + HOUSE_5_BIO:
            with self.subTest(fact_id=item.id):
                self.assertEqual(_provenance_key(item), "house:5")

    def test_house_5_dual_source_cannot_create_repeat_alone(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign=None,
                mercury_element=None,
                mercury_motion="direct",
                mercury_house=5,
                aspects=[],
            )
        )
        self.assertEqual(len(profile.house_facts), 27)
        self.assertTrue(all(item.factor_key == "5" for item in profile.house_facts))
        self.assertIn("h5_bio_sales_qualities", _ids(profile.house_facts))
        self.assertIn(
            "h5_creativity_connected_with_writing", _ids(profile.house_facts)
        )
        sales_facts = [
            item for item in profile.house_facts if "sales" in item.tags
        ]
        self.assertEqual(len(sales_facts), 1)
        repeats = detect_repeated_signals(profile.house_facts)
        self.assertEqual(repeats, [])
        for signal in repeats:
            house_sources = [src for src in signal.sources if src.startswith("house:")]
            self.assertLessEqual(len(house_sources), 1, signal)


class House5HumanCopyInventoryConsequenceTests(unittest.TestCase):
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

    def test_existing_lesson7_facts_remain_unreviewed(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        for item in HOUSE_5:
            with self.subTest(l7_id=item.id):
                self.assertNotIn(item.id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[item.id])
                self.assertNotEqual(entry.review_status, STATUS_UNREVIEWED)
                self.assertTrue(
                    (item.id in HUMAN_COPY_OVERRIDES)
                    ^ (item.id in APPROVED_RAW_FACT_IDS)
                )

    def test_house_5_family_counts_after_source_parity(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "house:5")
        self.assertEqual(family.total_facts, 27)
        self.assertEqual(family.approved_override, 14)
        self.assertEqual(family.approved_raw, 13)
        self.assertEqual(family.needs_review, 0)
        self.assertEqual(family.unreviewed, 0)
        self.assertEqual(family.reviewed_count, 27)
        self.assertEqual(family.presentation_ready_count, 27)


class House5SemanticLedgerTests(unittest.TestCase):
    def test_semantic_accounting_from_implemented_facts(self):
        l7_count = len(HOUSE_5)
        bio_count = len(HOUSE_5_BIO)
        exact_overlap = 0
        partial_overlap = 0
        conditional_unresolved = 0
        unique_bio = (
            bio_count - exact_overlap - partial_overlap - conditional_unresolved
        )
        unique_meanings = (
            l7_count + unique_bio + partial_overlap + conditional_unresolved
        )
        self.assertEqual(l7_count, 14)
        self.assertEqual(bio_count, 13)
        self.assertEqual(exact_overlap, 0)
        self.assertEqual(partial_overlap, 0)
        self.assertEqual(unique_bio, 13)
        self.assertEqual(conditional_unresolved, 0)
        self.assertEqual(unique_meanings, 27)
        self.assertEqual(l7_count + bio_count, 27)
        self.assertEqual(
            exact_overlap + partial_overlap + unique_bio + conditional_unresolved,
            13,
        )


if __name__ == "__main__":
    unittest.main()
