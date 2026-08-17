"""Tests for Mercury human presentation catalog (S4.3)."""

from __future__ import annotations

import unittest
import unittest.mock

from app.schemas.mercury_source_profile import SourceFact
from app.services.mercury_human_copy import HUMAN_COPY_OVERRIDES, get_human_fact_text
from app.services.mercury_human_copy_audit import detect_audit_reasons
import app.services.mercury_human_copy_catalog as catalog_mod
from app.services.mercury_human_copy_catalog import (
    APPROVED_RAW_FACT_IDS,
    NEEDS_REVIEW_FACT_IDS,
    STATUS_APPROVED_OVERRIDE,
    STATUS_APPROVED_RAW,
    STATUS_NEEDS_REVIEW,
    STATUS_UNREVIEWED,
    HumanCopyCatalogError,
    build_catalog_entry,
    build_human_copy_catalog,
    derive_review_status,
    get_family_entries,
    least_reviewed_families,
    validate_human_copy_registries,
)
from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS


SEED_APPROVED_RAW_EXPECTED: dict[str, str] = {
    "pluto_sq_strong_persuasiveness": "Strong persuasiveness.",
    "pluto_sq_powerful_words": "Powerful words.",
    "pluto_sq_debate_ability": "Debate ability.",
    "taurus_productive_thinking": "Productive thinking.",
    "taurus_thorough_thinking": "Thorough thinking.",
    "taurus_measured_orderly_speech": "Measured, orderly speech.",
    "taurus_clearly_structured_speech": "Speech tends to be clearly structured.",
    "taurus_thinks_before_speaking": "Tends to think before speaking.",
    "jupiter_sx_analysis_connects_with_synthesis": "Analysis connects with synthesis.",
    "uranus_cj_genius_potential": "Genius potential.",
    "uranus_cj_freshness_of_mind": "Freshness of mind.",
    "uranus_cj_openness_of_mind": "Openness of mind.",
    "uranus_cj_spontaneous_creativity": "Spontaneous creativity.",
    "mars_tr_persuasive": "Persuasive.",
    "jupiter_sx_oratory_and_persuasion": "Oratory and persuasion.",
}

SKIPPED_AMBIGUOUS_SEED_TEXTS: tuple[str, ...] = (
    "Technical talent.",
    "Strong sense of humor.",
    "Relies on common sense.",
)


class CatalogIntegrityTests(unittest.TestCase):
    def test_catalog_contains_exactly_all_canonical_ids(self):
        report = build_human_copy_catalog()
        catalog_ids = [entry.fact_id for entry in report.entries]
        source_ids = [fact.id for fact in ALL_SOURCE_FACTS]
        self.assertEqual(len(catalog_ids), 1590)
        self.assertEqual(report.total_facts, 1590)
        self.assertEqual(len(catalog_ids), len(set(catalog_ids)))
        self.assertEqual(set(catalog_ids), set(source_ids))

    def test_overrides_derive_approved_override(self):
        report = build_human_copy_catalog()
        by_id = {entry.fact_id: entry for entry in report.entries}
        for fact_id, human in HUMAN_COPY_OVERRIDES.items():
            entry = by_id[fact_id]
            self.assertEqual(entry.review_status, STATUS_APPROVED_OVERRIDE)
            self.assertTrue(entry.uses_override)
            self.assertEqual(entry.human_text, human)
            self.assertEqual(entry.canonical_text, next(f for f in ALL_SOURCE_FACTS if f.id == fact_id).text)
            self.assertNotEqual(entry.canonical_text, entry.human_text)

    def test_approved_raw_and_needs_review_and_unreviewed_semantics(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        sample_raw = next(iter(APPROVED_RAW_FACT_IDS))
        entry_raw = build_catalog_entry(by_id[sample_raw])
        self.assertEqual(entry_raw.review_status, STATUS_APPROVED_RAW)
        self.assertFalse(entry_raw.uses_override)
        self.assertEqual(entry_raw.human_text, entry_raw.canonical_text)

        # needs_review empty in S4.3; simulate derivation path.
        self.assertEqual(NEEDS_REVIEW_FACT_IDS, frozenset())
        self.assertEqual(derive_review_status("nonexistent_unreviewed_id"), STATUS_UNREVIEWED)

        unreviewed_id = next(
            fact.id
            for fact in ALL_SOURCE_FACTS
            if fact.id not in HUMAN_COPY_OVERRIDES
            and fact.id not in APPROVED_RAW_FACT_IDS
            and fact.id not in NEEDS_REVIEW_FACT_IDS
        )
        entry_unreviewed = build_catalog_entry(by_id[unreviewed_id])
        self.assertEqual(entry_unreviewed.review_status, STATUS_UNREVIEWED)
        self.assertEqual(entry_unreviewed.human_text, entry_unreviewed.canonical_text)

        # needs_review: canonical fallback text, status remains needs_review (not ready).
        probe_id = unreviewed_id
        with unittest.mock.patch.object(
            catalog_mod,
            "NEEDS_REVIEW_FACT_IDS",
            frozenset({probe_id}),
        ):
            self.assertEqual(catalog_mod.derive_review_status(probe_id), STATUS_NEEDS_REVIEW)
            entry_needs = catalog_mod.build_catalog_entry(by_id[probe_id])
            self.assertEqual(entry_needs.review_status, STATUS_NEEDS_REVIEW)
            self.assertFalse(entry_needs.uses_override)
            self.assertEqual(entry_needs.human_text, entry_needs.canonical_text)

    def test_audit_does_not_auto_decide_status(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        clean = by_id["pluto_sq_strong_persuasiveness"]
        self.assertEqual(detect_audit_reasons(clean.text), ())
        # Seeded approved_raw is an explicit decision, not automatic from clean audit.
        self.assertEqual(derive_review_status(clean.id), STATUS_APPROVED_RAW)

        # Find an audit-flagged unreviewed fact.
        flagged = next(
            fact
            for fact in ALL_SOURCE_FACTS
            if detect_audit_reasons(fact.text)
            and fact.id not in HUMAN_COPY_OVERRIDES
            and fact.id not in APPROVED_RAW_FACT_IDS
            and fact.id not in NEEDS_REVIEW_FACT_IDS
        )
        entry = build_catalog_entry(flagged)
        self.assertTrue(entry.review_recommended)
        self.assertEqual(entry.review_status, STATUS_UNREVIEWED)
        self.assertNotEqual(entry.review_status, STATUS_NEEDS_REVIEW)


class RegistryValidationTests(unittest.TestCase):
    def test_conflict_and_unknown_ids_fail(self):
        with self.assertRaises(HumanCopyCatalogError):
            validate_human_copy_registries(
                overrides={"unknown_override_id": "x"},
                approved_raw=frozenset(),
                needs_review=frozenset(),
            )
        with self.assertRaises(HumanCopyCatalogError):
            validate_human_copy_registries(
                overrides={},
                approved_raw=frozenset({"unknown_raw_id"}),
                needs_review=frozenset(),
            )
        with self.assertRaises(HumanCopyCatalogError):
            validate_human_copy_registries(
                overrides={},
                approved_raw=frozenset(),
                needs_review=frozenset({"unknown_needs_id"}),
            )
        sample_override = next(iter(HUMAN_COPY_OVERRIDES))
        with self.assertRaises(HumanCopyCatalogError):
            validate_human_copy_registries(
                overrides=HUMAN_COPY_OVERRIDES,
                approved_raw=frozenset({sample_override}),
                needs_review=frozenset(),
            )
        with self.assertRaises(HumanCopyCatalogError):
            validate_human_copy_registries(
                overrides=HUMAN_COPY_OVERRIDES,
                approved_raw=frozenset(),
                needs_review=frozenset({sample_override}),
            )
        sample_raw = next(iter(APPROVED_RAW_FACT_IDS))
        with self.assertRaises(HumanCopyCatalogError):
            validate_human_copy_registries(
                overrides={},
                approved_raw=frozenset({sample_raw}),
                needs_review=frozenset({sample_raw}),
            )

    def test_live_registries_are_consistent(self):
        validate_human_copy_registries()
        report = build_human_copy_catalog()
        self.assertEqual(report.approved_override_count, len(HUMAN_COPY_OVERRIDES))
        self.assertEqual(report.approved_raw_count, len(APPROVED_RAW_FACT_IDS))
        self.assertEqual(report.needs_review_count, len(NEEDS_REVIEW_FACT_IDS))


class CoverageAndFamilyTests(unittest.TestCase):
    def test_coverage_math_and_family_sums(self):
        report = build_human_copy_catalog()
        self.assertEqual(
            report.reviewed_count,
            report.approved_override_count
            + report.approved_raw_count
            + report.needs_review_count,
        )
        self.assertEqual(
            report.presentation_ready_count,
            report.approved_override_count + report.approved_raw_count,
        )
        self.assertEqual(
            report.approved_override_count
            + report.approved_raw_count
            + report.needs_review_count
            + report.unreviewed_count,
            report.total_facts,
        )
        family_total = sum(family.total_facts for family in report.families)
        self.assertEqual(family_total, report.total_facts)
        for family in report.families:
            self.assertEqual(
                family.approved_override
                + family.approved_raw
                + family.needs_review
                + family.unreviewed,
                family.total_facts,
            )
            self.assertEqual(
                family.reviewed_count,
                family.approved_override + family.approved_raw + family.needs_review,
            )
            self.assertEqual(
                family.presentation_ready_count,
                family.approved_override + family.approved_raw,
            )

    def test_no_alias_double_count(self):
        report = build_human_copy_catalog()
        self.assertEqual(report.total_facts, len(ALL_SOURCE_FACTS))
        self.assertEqual(len({entry.fact_id for entry in report.entries}), 1590)

    def test_deterministic_order(self):
        first = build_human_copy_catalog()
        second = build_human_copy_catalog()
        self.assertEqual(
            [entry.fact_id for entry in first.entries],
            [entry.fact_id for entry in second.entries],
        )
        self.assertEqual(
            [family.family_key for family in first.families],
            [family.family_key for family in second.families],
        )
        self.assertEqual(
            [f.family_key for f in least_reviewed_families(first, limit=10)],
            [f.family_key for f in least_reviewed_families(second, limit=10)],
        )

    def test_family_lookup(self):
        report = build_human_copy_catalog()
        sag = get_family_entries(report, "sign:Sagittarius")
        self.assertTrue(sag)
        self.assertTrue(all(entry.family_key == "sign:Sagittarius" for entry in sag))
        self.assertEqual([e.fact_id for e in sag], sorted(e.fact_id for e in sag))


class SeedApprovedRawTests(unittest.TestCase):
    def test_seeded_approved_raw_ids(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        self.assertEqual(set(SEED_APPROVED_RAW_EXPECTED), set(APPROVED_RAW_FACT_IDS))
        self.assertEqual(len(APPROVED_RAW_FACT_IDS), 15)
        for fact_id, expected_text in SEED_APPROVED_RAW_EXPECTED.items():
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].text, expected_text)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_APPROVED_RAW)
                self.assertFalse(entry.uses_override)
                self.assertEqual(entry.human_text, expected_text)

    def test_ambiguous_seed_texts_were_skipped(self):
        by_text = {}
        for fact in ALL_SOURCE_FACTS:
            by_text.setdefault(fact.text, []).append(fact.id)
        for text in SKIPPED_AMBIGUOUS_SEED_TEXTS:
            self.assertGreaterEqual(len(by_text[text]), 2, text)
            for fact_id in by_text[text]:
                self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)


class RuntimeRegressionTests(unittest.TestCase):
    def test_human_ui_fallback_unchanged(self):
        # Override path.
        override_id = "pluto_sq_conflictual_communication"
        raw = next(f for f in ALL_SOURCE_FACTS if f.id == override_id).text
        fact = SourceFact(
            id=override_id,
            factor_type="aspect",
            factor_key="square_Pluto",
            category="communication",
            text=raw,
            polarity="risk",
            tags=[],
            source_reference="test",
            activated=True,
            unresolved=False,
        )
        self.assertEqual(get_human_fact_text(fact), HUMAN_COPY_OVERRIDES[override_id])
        self.assertEqual(fact.text, raw)

        # Approved raw still falls back to canonical text at runtime.
        raw_id = "pluto_sq_strong_persuasiveness"
        raw_text = next(f for f in ALL_SOURCE_FACTS if f.id == raw_id).text
        raw_fact = SourceFact(
            id=raw_id,
            factor_type="aspect",
            factor_key="square_Pluto",
            category="communication",
            text=raw_text,
            polarity="strength",
            tags=[],
            source_reference="test",
            activated=True,
            unresolved=False,
        )
        self.assertEqual(get_human_fact_text(raw_fact), raw_text)
        self.assertNotIn(raw_id, HUMAN_COPY_OVERRIDES)


if __name__ == "__main__":
    unittest.main()
