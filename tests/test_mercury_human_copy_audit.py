"""Tests for Mercury human-copy readability audit (S4.1)."""

from __future__ import annotations

import unittest

from app.services.mercury_human_copy import HUMAN_COPY_OVERRIDES
from app.services.mercury_human_copy_audit import (
    DEVELOPMENT_FOCUS_PREFIX,
    OVERLY_LONG_MIN_CHARS,
    REASON_CYRILLIC_SOURCE_NOTE,
    REASON_OVERLY_LONG,
    REASON_PARENTHETICAL_HEAVY,
    REASON_QUOTED_LITERALISM,
    REASON_REPEATED_EDITORIAL_PREFIX,
    REASON_SLASH_HEAVY,
    REASON_TECHNICAL_SCAFFOLDING,
    REASON_TRANSLATION_ARTIFACT,
    SLASH_HEAVY_MIN_COUNT,
    audit_source_fact,
    build_golden_resolved_section_fact_ids,
    detect_audit_reasons,
    inventory_development_focus,
    run_human_copy_audit,
)
from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS, SourceFactDef


def _def(
    fact_id: str,
    text: str,
    *,
    polarity: str = "neutral",
    category: str = "communication",
) -> SourceFactDef:
    return SourceFactDef(
        id=fact_id,
        factor_type="aspect",
        factor_key="Pluto_square",
        category=category,
        text=text,
        polarity=polarity,
        tags=(),
        source_reference="test",
    )


class DetectAuditReasonsTests(unittest.TestCase):
    def test_technical_scaffolding_detection(self):
        text = (
            "Source affliction tendency (activated via project hard_aspected "
            "proxy for 'x'): superior manner."
        )
        reasons = detect_audit_reasons(text)
        self.assertIn(REASON_TECHNICAL_SCAFFOLDING, reasons)

    def test_cyrillic_detection(self):
        text = "activated via project hard_aspected proxy for 'при поражении'"
        reasons = detect_audit_reasons(text)
        self.assertIn(REASON_CYRILLIC_SOURCE_NOTE, reasons)

    def test_slash_heavy_detection(self):
        self.assertEqual(SLASH_HEAVY_MIN_COUNT, 2)
        self.assertNotIn(
            REASON_SLASH_HEAVY,
            detect_audit_reasons("poisonous / venomous quality."),
        )
        self.assertIn(
            REASON_SLASH_HEAVY,
            detect_audit_reasons("Tendency to destroy / dig / defeat through speech."),
        )

    def test_repeated_editorial_prefix_detection(self):
        self.assertIn(
            REASON_REPEATED_EDITORIAL_PREFIX,
            detect_audit_reasons("Development focus: learn to hear opinions."),
        )
        self.assertIn(
            REASON_REPEATED_EDITORIAL_PREFIX,
            detect_audit_reasons(
                "Source affliction tendency (activated via project): x."
            ),
        )

    def test_long_text_detection(self):
        short = "Strong persuasiveness."
        long = "A" * OVERLY_LONG_MIN_CHARS
        self.assertNotIn(REASON_OVERLY_LONG, detect_audit_reasons(short))
        self.assertIn(REASON_OVERLY_LONG, detect_audit_reasons(long))

    def test_parenthetical_heavy_detection(self):
        light = "Ability (sometimes) to speak."
        heavy = (
            "Claim (activated via project hard_aspected proxy for condition "
            "resolution pathway detail) remains."
        )
        self.assertNotIn(REASON_PARENTHETICAL_HEAVY, detect_audit_reasons(light))
        self.assertIn(REASON_PARENTHETICAL_HEAVY, detect_audit_reasons(heavy))

    def test_quoted_literalism_and_translation_artifact(self):
        quoted = 'Development focus: appearance / "dust in eyes".'
        reasons = detect_audit_reasons(quoted)
        self.assertIn(REASON_QUOTED_LITERALISM, reasons)
        artifact = "Speech may be used to justify / whiten oneself."
        self.assertIn(
            REASON_TRANSLATION_ARTIFACT,
            detect_audit_reasons(artifact),
        )

    def test_ordinary_concise_facts_not_flagged(self):
        clean = [
            "Strong persuasiveness.",
            "Powerful words.",
            "Debate ability.",
            "Technical talent.",
            "Ability to find strong arguments.",
            "Strong sense of humor.",
        ]
        for text in clean:
            with self.subTest(text=text):
                self.assertEqual(detect_audit_reasons(text), ())

    def test_risk_polarity_alone_does_not_create_candidate(self):
        fact = _def(
            "risk_only_clean",
            "Toxic conflictual atmosphere around communication.",
            polarity="risk",
        )
        # May or may not flag for mechanical reasons; polarity itself is ignored.
        # This concise risk line has no slash-heavy / scaffolding / Cyrillic.
        self.assertEqual(detect_audit_reasons(fact.text), ())
        self.assertIsNone(audit_source_fact(fact, exposure_by_profile={}))


class HumanOverrideAndCatalogTests(unittest.TestCase):
    def test_human_override_exists_uses_real_overrides(self):
        fact = next(
            f for f in ALL_SOURCE_FACTS if f.id == "leo_afflicted_superior_manner"
        )
        candidate = audit_source_fact(fact, exposure_by_profile={})
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertTrue(candidate.human_override_exists)
        self.assertIn(fact.id, HUMAN_COPY_OVERRIDES)

    def test_all_override_ids_exist_in_catalog(self):
        catalog_ids = {fact.id for fact in ALL_SOURCE_FACTS}
        missing = sorted(set(HUMAN_COPY_OVERRIDES) - catalog_ids)
        self.assertEqual(missing, [])
        report = run_human_copy_audit(include_golden_exposure=False)
        self.assertEqual(report.override_ids_missing_from_catalog, ())
        self.assertEqual(report.human_override_count, len(HUMAN_COPY_OVERRIDES))


class OrderingAndStabilityTests(unittest.TestCase):
    def test_deterministic_ordering_and_stable_rerun(self):
        first = run_human_copy_audit()
        second = run_human_copy_audit()
        self.assertEqual(
            [c.fact_id for c in first.candidates],
            [c.fact_id for c in second.candidates],
        )
        self.assertEqual(
            [c.fact_id for c in first.still_raw_by_presentation_review_priority],
            [c.fact_id for c in second.still_raw_by_presentation_review_priority],
        )
        self.assertEqual(first.reason_counts, second.reason_counts)
        # Still-raw first in overall candidate ordering.
        if first.candidates_still_raw and first.candidates_already_overridden:
            first_raw = first.candidates_still_raw[0].fact_id
            first_over = first.candidates_already_overridden[0].fact_id
            ids = [c.fact_id for c in first.candidates]
            self.assertLess(ids.index(first_raw), ids.index(first_over))

    def test_development_focus_inventory_deterministic(self):
        a = inventory_development_focus()
        b = inventory_development_focus()
        self.assertEqual([item.fact_id for item in a], [item.fact_id for item in b])
        self.assertTrue(all(item.source_text.startswith(DEVELOPMENT_FOCUS_PREFIX) for item in a))
        self.assertEqual(
            [item.fact_id for item in a],
            sorted(item.fact_id for item in a),
        )


class GoldenExposureTests(unittest.TestCase):
    def test_golden_exposure_based_on_resolved_section_ids(self):
        exposure = build_golden_resolved_section_fact_ids()
        self.assertEqual(set(exposure), {"Avdey", "Vlad", "Dzmitry", "Andrey", "Milka"})
        # Known Avdey Leo afflicted fact is a resolved section member when activated.
        avdey_ids = exposure["Avdey"]
        self.assertIn("leo_afflicted_superior_manner", avdey_ids)
        report = run_human_copy_audit(exposure_by_profile=exposure)
        candidate = next(
            c for c in report.candidates if c.fact_id == "leo_afflicted_superior_manner"
        )
        self.assertIn("Avdey", candidate.golden_profiles)
        self.assertGreaterEqual(candidate.golden_exposure_count, 1)
        # Exposure only from resolved section IDs, not inventing unknown profiles.
        for c in report.candidates:
            self.assertTrue(
                set(c.golden_profiles).issubset(
                    {"Avdey", "Vlad", "Dzmitry", "Andrey", "Milka"}
                )
            )
            self.assertEqual(c.golden_exposure_count, len(c.golden_profiles))

    def test_audit_does_not_change_golden_profile_structure(self):
        from datetime import date, time

        from app.schemas.mercury_source_profile import MercurySourceProfileRequest
        from app.services.mercury_source_profile import build_mercury_source_profile

        before = build_mercury_source_profile(
            MercurySourceProfileRequest(
                birth_date=date(1986, 7, 14),
                birth_time=time(7, 10),
                birth_place="Simferopol, Ukraine",
            )
        )
        _ = run_human_copy_audit()
        after = build_mercury_source_profile(
            MercurySourceProfileRequest(
                birth_date=date(1986, 7, 14),
                birth_time=time(7, 10),
                birth_place="Simferopol, Ukraine",
            )
        )
        self.assertEqual(before.calculated, after.calculated)
        self.assertEqual(
            [f.id for f in before.sign_facts],
            [f.id for f in after.sign_facts],
        )
        self.assertEqual(
            [s.signal for s in before.repeated_signals],
            [s.signal for s in after.repeated_signals],
        )
        self.assertEqual(
            [(c.tag_a, c.tag_b) for c in before.contrasting_signals],
            [(c.tag_a, c.tag_b) for c in after.contrasting_signals],
        )
        self.assertEqual(before.coverage.status, after.coverage.status)


class FullAuditSmokeTests(unittest.TestCase):
    def test_full_audit_counts_coherent(self):
        report = run_human_copy_audit()
        self.assertEqual(report.total_source_facts, len(ALL_SOURCE_FACTS))
        self.assertEqual(report.human_override_count, len(HUMAN_COPY_OVERRIDES))
        self.assertEqual(report.human_override_count, 504)
        self.assertEqual(
            len(report.candidates),
            len(report.candidates_already_overridden)
            + len(report.candidates_still_raw),
        )
        self.assertEqual(
            report.candidates_still_raw,
            report.still_raw_by_presentation_review_priority,
        )
        # Overrides that are audit candidates should be counted as overridden.
        overridden_ids = {c.fact_id for c in report.candidates_already_overridden}
        for fact_id in HUMAN_COPY_OVERRIDES:
            fact = next(f for f in ALL_SOURCE_FACTS if f.id == fact_id)
            reasons = detect_audit_reasons(fact.text)
            if reasons:
                self.assertIn(fact_id, overridden_ids)


class GoldenExposureHumanCopyAuditRegressionTests(unittest.TestCase):
    def test_s42_reduces_golden_exposed_raw_candidates(self):
        report = run_human_copy_audit()
        by_profile = {name: 0 for name in ("Avdey", "Vlad", "Dzmitry", "Andrey", "Milka")}
        for candidate in report.candidates_still_raw:
            for name in candidate.golden_profiles:
                by_profile[name] += 1
        # Pre-S4.2 baselines were Avdey 13 / Vlad 3 / Dzmitry 4 / Andrey 18 / Milka 4.
        self.assertLess(by_profile["Avdey"], 13)
        self.assertLess(by_profile["Vlad"], 3)
        self.assertLess(by_profile["Dzmitry"], 4)
        self.assertLess(by_profile["Andrey"], 18)
        self.assertLess(by_profile["Milka"], 4)
        # Development-focus Avdey growth overrides are no longer still-raw.
        still_raw_ids = {c.fact_id for c in report.candidates_still_raw}
        for fact_id in (
            "leo_l7_dev_creative_vision",
            "leo_l7_dev_creativity",
            "leo_l7_dev_hear_others_opinions",
            "leo_afflicted_lying_distortion",
            "pluto_sq_core_conflict",
        ):
            self.assertNotIn(fact_id, still_raw_ids)
        # Candidate detection itself still flags the underlying mechanical reasons.
        from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS

        by_id = {f.id: f for f in ALL_SOURCE_FACTS}
        reasons = detect_audit_reasons(by_id["leo_afflicted_lying_distortion"].text)
        self.assertIn(REASON_TECHNICAL_SCAFFOLDING, reasons)
        self.assertIn(REASON_CYRILLIC_SOURCE_NOTE, reasons)


if __name__ == "__main__":
    unittest.main()
