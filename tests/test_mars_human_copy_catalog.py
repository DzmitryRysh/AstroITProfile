"""Tests for Mars human presentation catalog (M7)."""

from __future__ import annotations

import unittest

from app.services.mars_human_copy import HUMAN_COPY_OVERRIDES
from app.services.mars_human_copy_catalog import (
    APPROVED_RAW_FACT_IDS,
    FAMILY_BUCKETS,
    NEEDS_REVIEW_FACT_IDS,
    STATUS_APPROVED_OVERRIDE,
    STATUS_APPROVED_RAW,
    STATUS_NEEDS_REVIEW,
    STATUS_UNREVIEWED,
    HumanCopyCatalogError,
    build_human_copy_catalog,
    derive_review_status,
    validate_human_copy_registries,
)
from app.services.mars_source_knowledge import ALL_MARS_SOURCE_FACTS


class MarsHumanCopyCatalogIntegrityTests(unittest.TestCase):
    def test_catalog_contains_exactly_all_canonical_ids(self):
        report = build_human_copy_catalog()
        catalog_ids = [entry.fact_id for entry in report.entries]
        source_ids = [fact.id for fact in ALL_MARS_SOURCE_FACTS]
        self.assertEqual(len(catalog_ids), 504)
        self.assertEqual(report.total_facts, 504)
        self.assertEqual(len(catalog_ids), len(set(catalog_ids)))
        self.assertEqual(set(catalog_ids), set(source_ids))

    def test_zero_unknown_catalog_ids(self):
        catalog_ids = {fact.id for fact in ALL_MARS_SOURCE_FACTS}
        self.assertEqual(set(HUMAN_COPY_OVERRIDES) - catalog_ids, set())
        self.assertEqual(set(APPROVED_RAW_FACT_IDS) - catalog_ids, set())
        self.assertEqual(set(NEEDS_REVIEW_FACT_IDS) - catalog_ids, set())

    def test_override_and_raw_and_needs_ids_all_exist(self):
        catalog_ids = {fact.id for fact in ALL_MARS_SOURCE_FACTS}
        for fact_id in HUMAN_COPY_OVERRIDES:
            self.assertIn(fact_id, catalog_ids)
        for fact_id in APPROVED_RAW_FACT_IDS:
            self.assertIn(fact_id, catalog_ids)
        for fact_id in NEEDS_REVIEW_FACT_IDS:
            self.assertIn(fact_id, catalog_ids)

    def test_no_duplicate_review_states(self):
        override_ids = set(HUMAN_COPY_OVERRIDES)
        raw_ids = set(APPROVED_RAW_FACT_IDS)
        needs_ids = set(NEEDS_REVIEW_FACT_IDS)
        self.assertEqual(override_ids & raw_ids, set())
        self.assertEqual(override_ids & needs_ids, set())
        self.assertEqual(raw_ids & needs_ids, set())

    def test_every_fact_has_exactly_one_review_state(self):
        report = build_human_copy_catalog()
        self.assertEqual(report.unreviewed_count, 0)
        self.assertEqual(report.reviewed_count, 504)
        for entry in report.entries:
            self.assertIn(
                entry.review_status,
                {
                    STATUS_APPROVED_OVERRIDE,
                    STATUS_APPROVED_RAW,
                    STATUS_NEEDS_REVIEW,
                },
            )
            expected = derive_review_status(entry.fact_id)
            self.assertEqual(entry.review_status, expected)
            self.assertEqual(entry.uses_override, expected == STATUS_APPROVED_OVERRIDE)

    def test_validate_registries_accepts_current_state(self):
        validate_human_copy_registries()

    def test_validate_rejects_unknown_override(self):
        with self.assertRaises(HumanCopyCatalogError):
            validate_human_copy_registries(
                overrides={**HUMAN_COPY_OVERRIDES, "not_a_mars_fact": "x"}
            )

    def test_validate_rejects_overlap(self):
        sample = next(iter(HUMAN_COPY_OVERRIDES))
        with self.assertRaises(HumanCopyCatalogError):
            validate_human_copy_registries(
                approved_raw=APPROVED_RAW_FACT_IDS | {sample}
            )

    def test_family_buckets_cover_504(self):
        report = build_human_copy_catalog()
        self.assertEqual(tuple(item.bucket for item in report.buckets), FAMILY_BUCKETS)
        self.assertEqual(sum(item.total_facts for item in report.buckets), 504)
        expected = {"sign": 220, "house": 146, "motion": 10, "l9": 92, "bio": 36}
        for item in report.buckets:
            self.assertEqual(item.total_facts, expected[item.bucket], item.bucket)
            self.assertEqual(item.unreviewed, 0, item.bucket)
            self.assertEqual(item.reviewed_count, item.total_facts, item.bucket)

    def test_no_mercury_catalog_contamination(self):
        from app.services.mercury_human_copy import HUMAN_COPY_OVERRIDES as MERCURY
        from app.services.mercury_human_copy_catalog import (
            APPROVED_RAW_FACT_IDS as MERCURY_RAW,
        )

        self.assertEqual(set(HUMAN_COPY_OVERRIDES) & set(MERCURY), set())
        self.assertEqual(set(APPROVED_RAW_FACT_IDS) & set(MERCURY_RAW), set())
        self.assertTrue(all(fact_id.startswith("mars_") for fact_id in APPROVED_RAW_FACT_IDS))
        self.assertEqual(STATUS_UNREVIEWED, "unreviewed")
