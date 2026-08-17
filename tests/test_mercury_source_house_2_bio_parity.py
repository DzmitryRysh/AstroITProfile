"""Tests for Mercury House 2 Bioastrology source parity (S4.21B)."""

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
    HOUSE_2,
    HOUSE_2_BIO,
    REF_H2_BIO,
    REF_H2_L7,
)
from app.services.mercury_source_profile import (
    _provenance_key,
    build_source_profile_from_factors,
    detect_repeated_signals,
)


EXPECTED_BIO_IDS: tuple[str, ...] = (
    "h2_bio_intellect_becomes_practical_applied",
    "h2_bio_intellect_oriented_toward_money",
    "h2_bio_intellect_oriented_toward_health",
    "h2_bio_favorable_earning_through_information",
    "h2_bio_two_or_three_parallel_income_sources",
    "h2_bio_intellectual_transport_profession",
    "h2_bio_consultant_qualities",
    "h2_bio_sales_qualities",
)

EXPECTED_BIO_CANONICAL: dict[str, str] = {
    "h2_bio_intellect_becomes_practical_applied": (
        "Over time, intellect may become more practical and applied."
    ),
    "h2_bio_intellect_oriented_toward_money": (
        "Over time, intellect may become more oriented toward money."
    ),
    "h2_bio_intellect_oriented_toward_health": (
        "Over time, intellect may become more oriented toward health."
    ),
    "h2_bio_favorable_earning_through_information": (
        "Favorable earning potential through information."
    ),
    "h2_bio_two_or_three_parallel_income_sources": (
        "There may be two or three parallel sources of income."
    ),
    "h2_bio_intellectual_transport_profession": (
        "Favorable association with intellectual and transport-related professions."
    ),
    "h2_bio_consultant_qualities": (
        "May support qualities associated with consulting."
    ),
    "h2_bio_sales_qualities": "May support qualities associated with sales.",
}

UNTAGGED_BIO_IDS: tuple[str, ...] = (
    "h2_bio_intellect_becomes_practical_applied",
    "h2_bio_intellect_oriented_toward_money",
    "h2_bio_intellect_oriented_toward_health",
    "h2_bio_favorable_earning_through_information",
    "h2_bio_two_or_three_parallel_income_sources",
)

FORBIDDEN_APPROXIMATE_TAGS: tuple[str, ...] = (
    "practical_thinking",
    "money_learning_motivation",
    "money_motivation",
    "financial_scheme_creation",
    "financial_mechanism_design",
    "trade_income",
    "financial_thinking",
    "money_skill",
    "health_thinking",
    "multiple_income",
    "earning",
    "persuasion",
    "advertising_income",
    "import_export_trade",
    "public_speaking_income",
    "writing_income",
)

FROZEN_L7_HOUSE_2: tuple[tuple[str, str, str, str, tuple[str, ...], str], ...] = (
    (
        "h2_profit_through_public_speaking",
        "work_application",
        "Profit may come through public speaking.",
        "strength",
        ("public_speaking_income",),
        REF_H2_L7,
    ),
    (
        "h2_profit_through_literary_text_activity",
        "work_application",
        "Profit may come through literary / text-related activity.",
        "strength",
        ("writing_income",),
        REF_H2_L7,
    ),
    (
        "h2_literary_text_work_examples",
        "source_specific",
        "Source examples within literary/text work include speechwriting, editing, and "
        "copywriting; source-described work associations, not certified skill assignments.",
        "neutral",
        ("literary_text_work_associations",),
        REF_H2_L7,
    ),
    (
        "h2_talking_genre_profession_association",
        "source_specific",
        'Source associates speaking / "talking genre" professions (source-described '
        "association, not a career assignment).",
        "neutral",
        ("talking_genre_profession_association",),
        REF_H2_L7,
    ),
    (
        "h2_trade_income_association",
        "work_application",
        "Source associates income/activity with trade.",
        "neutral",
        ("trade_income",),
        REF_H2_L7,
    ),
    (
        "h2_import_export_trade_association",
        "work_application",
        "Source especially associates trade with import-export trade.",
        "neutral",
        ("import_export_trade",),
        REF_H2_L7,
    ),
    (
        "h2_advertising_income_association",
        "work_application",
        "Source associates income/activity with advertising.",
        "neutral",
        ("advertising_income",),
        REF_H2_L7,
    ),
    (
        "h2_financial_scheme_creation",
        "work_application",
        "Maximum money can come through creating cleverly thought-out financial schemes.",
        "strength",
        ("financial_scheme_creation",),
        REF_H2_L7,
    ),
    (
        "h2_financial_mechanism_design",
        "work_application",
        "Maximum money can come through creating cleverly thought-out financial mechanisms.",
        "strength",
        ("financial_mechanism_design",),
        REF_H2_L7,
    ),
    (
        "h2_objects_attract_through_usefulness",
        "environment",
        "Objects / things attract through usefulness.",
        "neutral",
        ("usefulness_preference",),
        REF_H2_L7,
    ),
    (
        "h2_objects_attract_through_applicability",
        "environment",
        "Objects / things attract through applicability.",
        "neutral",
        ("applicability_preference",),
        REF_H2_L7,
    ),
    (
        "h2_objects_attract_through_interestingness",
        "environment",
        "Objects / things attract through interestingness.",
        "neutral",
        ("intellectual_interest_in_objects",),
        REF_H2_L7,
    ),
    (
        "h2_likes_stationery",
        "source_specific",
        "Likes stationery.",
        "neutral",
        ("likes_stationery",),
        REF_H2_L7,
    ),
    (
        "h2_likes_expensive_pens",
        "source_specific",
        "Likes expensive pens.",
        "neutral",
        ("likes_expensive_pens",),
        REF_H2_L7,
    ),
    (
        "h2_likes_notebooks",
        "source_specific",
        "Likes notebooks.",
        "neutral",
        ("likes_notebooks",),
        REF_H2_L7,
    ),
    (
        "h2_likes_writing_paper_letters",
        "source_specific",
        "Likes writing paper letters.",
        "neutral",
        ("likes_writing_paper_letters",),
        REF_H2_L7,
    ),
    (
        "h2_accumulates_collects_books",
        "source_specific",
        "Accumulates / collects books.",
        "neutral",
        ("collects_books",),
        REF_H2_L7,
    ),
    (
        "h2_money_loss_carelessness",
        "risk",
        "Source-described money-loss risk in House 2 context: carelessness / lack of caution.",
        "risk",
        ("money_loss_carelessness",),
        REF_H2_L7,
    ),
    (
        "h2_money_loss_superficiality",
        "risk",
        "Source-described money-loss risk in House 2 context: superficiality.",
        "risk",
        ("money_loss_superficiality",),
        REF_H2_L7,
    ),
    (
        "h2_money_loss_overconfidence",
        "risk",
        "Source-described money-loss risk in House 2 context: excessive self-confidence.",
        "risk",
        ("money_loss_overconfidence",),
        REF_H2_L7,
    ),
)


def _house_2_facts():
    return [
        item
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "house" and item.factor_key == "2"
    ]


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


class House2BioCoverageTests(unittest.TestCase):
    def test_programmatic_bio_count_is_8(self):
        self.assertEqual(len(HOUSE_2_BIO), 8)
        self.assertEqual(len(EXPECTED_BIO_IDS), 8)
        self.assertEqual(len(EXPECTED_BIO_CANONICAL), 8)
        self.assertEqual(tuple(item.id for item in HOUSE_2_BIO), EXPECTED_BIO_IDS)

    def test_house_2_source_counts(self):
        house_2 = _house_2_facts()
        lesson7 = [item for item in house_2 if item.source_reference == REF_H2_L7]
        bio = [item for item in house_2 if item.source_reference == REF_H2_BIO]
        self.assertEqual(len(HOUSE_2), 20)
        self.assertEqual(len(lesson7), 20)
        self.assertEqual(len(bio), 8)
        self.assertEqual(len(house_2), 28)
        self.assertEqual(len(HOUSE_2) + len(HOUSE_2_BIO), 28)

    def test_all_bio_use_bioastrology_source_reference(self):
        self.assertTrue(all(item.source_reference == REF_H2_BIO for item in HOUSE_2_BIO))
        self.assertEqual(REF_H2_BIO, "bioastrology_mercury_house_2")

    def test_all_house_2_facts_share_factor_identity(self):
        house_2 = _house_2_facts()
        self.assertEqual(len(house_2), 28)
        self.assertTrue(all(item.factor_type == "house" for item in house_2))
        self.assertTrue(all(item.factor_key == "2" for item in house_2))
        self.assertTrue(all(item.unresolved is False for item in house_2))
        self.assertTrue(all(item.activation_condition is None for item in house_2))

    def test_ids_globally_unique(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])


class House2BioCanonicalTests(unittest.TestCase):
    def test_exact_canonical_strings_for_all_8(self):
        by_id = {item.id: item for item in HOUSE_2_BIO}
        self.assertEqual(set(by_id), set(EXPECTED_BIO_CANONICAL))
        for fact_id, canonical in EXPECTED_BIO_CANONICAL.items():
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].text, canonical)

    def test_three_intellect_facts_remain_distinct(self):
        by_id = {item.id: item for item in HOUSE_2_BIO}
        practical = by_id["h2_bio_intellect_becomes_practical_applied"]
        money = by_id["h2_bio_intellect_oriented_toward_money"]
        health = by_id["h2_bio_intellect_oriented_toward_health"]
        texts = {practical.text, money.text, health.text}
        self.assertEqual(len(texts), 3)
        self.assertEqual(practical.category, "thinking")
        self.assertEqual(money.category, "thinking")
        self.assertEqual(health.category, "thinking")
        self.assertEqual(practical.polarity, "neutral")
        self.assertEqual(money.polarity, "neutral")
        self.assertEqual(health.polarity, "neutral")


class House2AtomicFidelityTests(unittest.TestCase):
    def test_earning_through_information_is_not_public_speaking_or_writing_income(self):
        by_id = {item.id: item for item in HOUSE_2 + HOUSE_2_BIO}
        info = by_id["h2_bio_favorable_earning_through_information"]
        speaking = by_id["h2_profit_through_public_speaking"]
        writing = by_id["h2_profit_through_literary_text_activity"]
        self.assertNotEqual(info.text, speaking.text)
        self.assertNotEqual(info.text, writing.text)
        self.assertNotIn("public_speaking_income", info.tags)
        self.assertNotIn("writing_income", info.tags)
        self.assertEqual(info.tags, ())
        self.assertIn("information", info.text.lower())
        self.assertIn("favorable", info.text.lower())

    def test_parallel_income_sources_are_not_trade_income(self):
        by_id = {item.id: item for item in HOUSE_2 + HOUSE_2_BIO}
        parallel = by_id["h2_bio_two_or_three_parallel_income_sources"]
        trade = by_id["h2_trade_income_association"]
        self.assertNotEqual(parallel.text, trade.text)
        self.assertNotIn("trade_income", parallel.tags)
        self.assertIn("two or three", parallel.text.lower())
        self.assertIn("parallel", parallel.text.lower())

    def test_sales_qualities_are_not_trade_income(self):
        by_id = {item.id: item for item in HOUSE_2 + HOUSE_2_BIO}
        sales = by_id["h2_bio_sales_qualities"]
        trade = by_id["h2_trade_income_association"]
        self.assertNotEqual(sales.text, trade.text)
        self.assertIn("sales", sales.tags)
        self.assertNotIn("sales", trade.tags)
        self.assertNotIn("trade_income", sales.tags)
        self.assertNotIn("persuasion", sales.tags)
        self.assertNotIn("advertising_income", sales.tags)

    def test_transport_profession_is_not_import_export_trade(self):
        by_id = {item.id: item for item in HOUSE_2 + HOUSE_2_BIO}
        transport = by_id["h2_bio_intellectual_transport_profession"]
        import_export = by_id["h2_import_export_trade_association"]
        self.assertNotEqual(transport.text, import_export.text)
        self.assertIn("transport_profession", transport.tags)
        self.assertNotIn("import_export_trade", transport.tags)
        self.assertNotIn("transport_profession", import_export.tags)


class House2BioTagGuardTests(unittest.TestCase):
    def test_intellectual_transport_profession_tags(self):
        fact = next(
            item
            for item in HOUSE_2_BIO
            if item.id == "h2_bio_intellectual_transport_profession"
        )
        self.assertEqual(fact.tags, ("intellectual_work", "transport_profession"))

    def test_consultant_qualities_has_consulting_tag(self):
        fact = next(
            item for item in HOUSE_2_BIO if item.id == "h2_bio_consultant_qualities"
        )
        self.assertEqual(fact.tags, ("consulting",))

    def test_sales_qualities_has_sales_tag(self):
        fact = next(item for item in HOUSE_2_BIO if item.id == "h2_bio_sales_qualities")
        self.assertEqual(fact.tags, ("sales",))

    def test_first_five_bio_facts_have_no_tags(self):
        by_id = {item.id: item for item in HOUSE_2_BIO}
        for fact_id in UNTAGGED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].tags, ())
                for tag in FORBIDDEN_APPROXIMATE_TAGS:
                    self.assertNotIn(tag, by_id[fact_id].tags)


class House2Lesson7FrozenTests(unittest.TestCase):
    def test_existing_20_lesson7_facts_unchanged(self):
        self.assertEqual(len(HOUSE_2), 20)
        self.assertEqual(len(FROZEN_L7_HOUSE_2), 20)
        actual = tuple(
            (
                item.id,
                item.category,
                item.text,
                item.polarity,
                item.tags,
                item.source_reference,
            )
            for item in HOUSE_2
        )
        self.assertEqual(actual, FROZEN_L7_HOUSE_2)
        self.assertTrue(all(item.activation_condition is None for item in HOUSE_2))
        self.assertTrue(all(item.unresolved is False for item in HOUSE_2))
        self.assertTrue(all(item.factor_type == "house" for item in HOUSE_2))
        self.assertTrue(all(item.factor_key == "2" for item in HOUSE_2))


class House2SameHouseSourceDedupTests(unittest.TestCase):
    def test_lesson7_and_bio_share_one_provenance_key(self):
        house_2 = _house_2_facts()
        keys = {_provenance_key(item) for item in house_2}
        self.assertEqual(keys, {"house:2"})
        for item in HOUSE_2 + HOUSE_2_BIO:
            with self.subTest(fact_id=item.id):
                self.assertEqual(_provenance_key(item), "house:2")

    def test_house_2_dual_source_cannot_create_repeat_alone(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign=None,
                mercury_element=None,
                mercury_motion="direct",
                mercury_house=2,
                aspects=[],
            )
        )
        self.assertEqual(len(profile.house_facts), 28)
        self.assertTrue(all(item.factor_key == "2" for item in profile.house_facts))
        self.assertIn("h2_profit_through_public_speaking", _ids(profile.house_facts))
        self.assertIn("h2_bio_sales_qualities", _ids(profile.house_facts))
        repeats = detect_repeated_signals(profile.house_facts)
        self.assertEqual(repeats, [])
        sales_facts = [item for item in profile.house_facts if "sales" in item.tags]
        sales_keys = {_provenance_key(item) for item in sales_facts}
        self.assertTrue(sales_keys.issubset({"house:2"}))


class House2HumanCopyInventoryConsequenceTests(unittest.TestCase):
    def test_new_bio_facts_are_unreviewed_and_not_in_registries(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        for fact_id in EXPECTED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertNotIn(fact_id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_UNREVIEWED)

    def test_house_2_family_counts_after_source_parity(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "house:2")
        self.assertEqual(family.total_facts, 28)
        self.assertEqual(family.approved_override, 19)
        self.assertEqual(family.approved_raw, 1)
        self.assertEqual(family.needs_review, 0)
        self.assertEqual(family.unreviewed, 8)
        self.assertEqual(family.reviewed_count, 20)
        self.assertEqual(family.presentation_ready_count, 20)

    def test_existing_lesson7_human_copy_decisions_unchanged(self):
        l7_ids = {item.id for item in HOUSE_2}
        self.assertEqual(len(l7_ids), 20)
        raw_id = "h2_profit_through_public_speaking"
        self.assertIn(raw_id, APPROVED_RAW_FACT_IDS)
        self.assertNotIn(raw_id, HUMAN_COPY_OVERRIDES)
        self.assertNotIn(raw_id, NEEDS_REVIEW_FACT_IDS)
        override_ids = l7_ids - {raw_id}
        self.assertEqual(len(override_ids), 19)
        for fact_id in override_ids:
            with self.subTest(l7_id=fact_id):
                self.assertIn(fact_id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)


class House2SemanticLedgerTests(unittest.TestCase):
    def test_semantic_accounting_from_implemented_facts(self):
        l7_count = len(HOUSE_2)
        bio_count = len(HOUSE_2_BIO)
        exact_overlap = 0
        partial_overlap = 0
        unique_bio = bio_count - exact_overlap - partial_overlap
        unique_meanings = l7_count + unique_bio
        self.assertEqual(l7_count, 20)
        self.assertEqual(bio_count, 8)
        self.assertEqual(unique_bio, 8)
        self.assertEqual(unique_meanings, 28)
        self.assertEqual(l7_count + bio_count, 28)


if __name__ == "__main__":
    unittest.main()
