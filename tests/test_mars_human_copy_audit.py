"""Tests for Mars human-copy readability audit (M7)."""

from __future__ import annotations

import unittest

from app.services.mars_human_copy import HUMAN_COPY_OVERRIDES
from app.services.mars_human_copy_audit import (
    OVERLY_LONG_MIN_CHARS,
    REASON_COMPETENCE_INFLATION,
    REASON_DETERMINISTIC_ACCUSATION,
    REASON_OVERLY_LONG,
    REASON_SLASH_HEAVY,
    REASON_TECHNICAL_SCAFFOLDING,
    SLASH_HEAVY_MIN_COUNT,
    detect_audit_reasons,
    run_human_copy_audit,
)
from app.services.mars_source_knowledge import ALL_MARS_SOURCE_FACTS


class MarsDetectAuditReasonsTests(unittest.TestCase):
    def test_technical_scaffolding_detection(self):
        self.assertIn(
            REASON_TECHNICAL_SCAFFOLDING,
            detect_audit_reasons("Source describes a compensation pattern."),
        )

    def test_slash_heavy_detection(self):
        self.assertEqual(SLASH_HEAVY_MIN_COUNT, 2)
        self.assertNotIn(REASON_SLASH_HEAVY, detect_audit_reasons("Anger / irritation."))
        self.assertIn(
            REASON_SLASH_HEAVY,
            detect_audit_reasons("Tactlessness / impatience / criticism."),
        )

    def test_long_text_detection(self):
        self.assertNotIn(REASON_OVERLY_LONG, detect_audit_reasons("Indecision."))
        self.assertIn(REASON_OVERLY_LONG, detect_audit_reasons("A" * OVERLY_LONG_MIN_CHARS))

    def test_accusation_and_competence_inflation(self):
        self.assertIn(
            REASON_DETERMINISTIC_ACCUSATION,
            detect_audit_reasons("You are violent in conflict."),
        )
        self.assertIn(
            REASON_COMPETENCE_INFLATION,
            detect_audit_reasons("Would be good at surgery."),
        )
        self.assertNotIn(
            REASON_COMPETENCE_INFLATION,
            detect_audit_reasons(
                "The source associates this pairing with technical, analytical, "
                "or IT-engineering aptitude."
            ),
        )
        self.assertNotIn(
            REASON_DETERMINISTIC_ACCUSATION,
            detect_audit_reasons("Conflict may become unusually intense."),
        )

    def test_ordinary_work_copy_not_flagged(self):
        clean = [
            "May prefer to plan before acting.",
            "Starting itself may not be the main problem.",
            "May revisit or redo actions before moving forward.",
        ]
        for text in clean:
            with self.subTest(text=text):
                self.assertEqual(detect_audit_reasons(text), ())


class MarsHumanCopyAuditReportTests(unittest.TestCase):
    def test_audit_covers_all_facts_and_no_missing_overrides(self):
        report = run_human_copy_audit(include_golden_exposure=False)
        self.assertEqual(report.total_source_facts, 504)
        self.assertEqual(report.human_override_count, len(HUMAN_COPY_OVERRIDES))
        self.assertEqual(report.override_ids_missing_from_catalog, ())

    def test_no_accusation_or_competence_inflation_in_display_copy(self):
        report = run_human_copy_audit(include_golden_exposure=False)
        bad = [
            candidate.fact_id
            for candidate in report.candidates
            if REASON_DETERMINISTIC_ACCUSATION in candidate.reasons
            or REASON_COMPETENCE_INFLATION in candidate.reasons
        ]
        self.assertEqual(bad, [])

    def test_goldens_do_not_expose_source_only_or_personal(self):
        report = run_human_copy_audit(include_golden_exposure=True)
        exposed = {
            candidate.fact_id: candidate.golden_profiles
            for candidate in report.candidates
            if candidate.golden_exposure_count
        }
        forbidden = {
            fact.id
            for fact in ALL_MARS_SOURCE_FACTS
            if fact.scope in {"SOURCE_ONLY", "PERSONAL_MARS"}
        }
        self.assertEqual(set(exposed) & forbidden, set())
