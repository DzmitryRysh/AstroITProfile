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

S44B_SAGITTARIUS_APPROVED_RAW: tuple[str, ...] = (
    "sag_searches_higher_meaning_in_ordinary",
    "sag_bio_central_idea_grasping",
    "sag_bio_independent_research_learning",
    "sag_bio_learning_through_teaching",
    "sag_bio_monologue_learning",
    "sag_difficulty_theory_to_practice",
    "sag_theory_to_practice_gap_risk",
    "sag_learning_encyclopedias",
    "sag_learning_pass_knowledge_to_others",
    "sag_learning_setting_a_goal",
    "sag_learning_university_textbooks",
    "sag_teacher_like_with_siblings",
    "sag_tendency_to_attach_labels",
)

S44B_SAGITTARIUS_OVERRIDES: dict[str, str] = {
    "sag_bio_afflicted_accuracy_problems": "Accuracy problems can appear.",
    "sag_bio_afflicted_coarse_rude_communication": (
        "Communication can become coarse or rude."
    ),
    "sag_bio_afflicted_common_sense_detachment": (
        "Thinking may detach from common sense."
    ),
    "sag_bio_afflicted_dubious_philosophy_drift": (
        "May drift toward dubious or murky philosophies."
    ),
    "sag_bio_afflicted_illusions": "May become prone to illusions.",
    "sag_bio_afflicted_labeling": "May tend toward labeling others.",
    "sag_bio_afflicted_memory_problems": "Memory problems can appear.",
    "sag_bio_afflicted_practice_detachment": (
        "Religious or philosophical frameworks may detach thinking from practice."
    ),
    "sag_bio_afflicted_strange_religion_drift": (
        "May drift toward strange religions."
    ),
    "sag_bio_expert_aptitude": "May show aptitude for expert-level work.",
    "sag_bio_foreign_language_aptitude": (
        "May show aptitude for foreign languages."
    ),
    "sag_bio_humanities_aptitude": "May show aptitude for the humanities.",
    "sag_bio_pr_aptitude": "May show aptitude for PR.",
    "sag_bio_teacher_instructor_quality": (
        "May show teacher or instructor qualities."
    ),
    "sag_bio_authority_learning_motivation": (
        "Learning may be motivated by authority."
    ),
    "sag_bio_fashion_learning_motivation": (
        "Learning may be motivated by the chance to become fashionable."
    ),
    "sag_bio_status_display_learning_motivation": (
        "Learning may be motivated by the chance to display status."
    ),
    "sag_bio_universal_wisdom_learning_motivation": (
        "Learning may be motivated by a sense of touching higher or "
        "universal wisdom."
    ),
    "sag_bio_fitting_facts_under_philosophy_ideology": (
        "May fit or pull facts under a philosophy or ideology."
    ),
    "sag_calculation_errors_neglect_precision": (
        "May make calculation errors or neglect precision."
    ),
    "sag_learning_practical_life_motive": (
        "Finding a practical life motive for why the learning matters "
        "supports learning."
    ),
    "sag_lecturing_labeling_siblings": "May lecture or label siblings.",
    "sag_seeks_socially_significant_fashionable": (
        "May seek socially significant or fashionable people or themes in "
        "the environment."
    ),
    "sag_bio_occupation_associations": (
        "Occupational themes associated with this placement can include "
        "science, expertise, writing, politics, and propaganda-oriented "
        "journalism — not career assignments."
    ),
}

S44B_SAGITTARIUS_NEEDS_REVIEW: tuple[str, ...] = (
    "sag_bio_impartiality_disrupted",
    "sag_bio_learnability_disrupted",
    "sag_bio_major_exile",
)

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
        # Prefer a live needs_review ID when present (S4.4B+).
        if NEEDS_REVIEW_FACT_IDS:
            probe_id = next(iter(NEEDS_REVIEW_FACT_IDS))
            entry_needs = build_catalog_entry(by_id[probe_id])
            self.assertEqual(entry_needs.review_status, STATUS_NEEDS_REVIEW)
            self.assertFalse(entry_needs.uses_override)
            self.assertEqual(entry_needs.human_text, entry_needs.canonical_text)
        else:
            probe_id = unreviewed_id
            with unittest.mock.patch.object(
                catalog_mod,
                "NEEDS_REVIEW_FACT_IDS",
                frozenset({probe_id}),
            ):
                self.assertEqual(
                    catalog_mod.derive_review_status(probe_id), STATUS_NEEDS_REVIEW
                )
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
        self.assertTrue(set(SEED_APPROVED_RAW_EXPECTED).issubset(APPROVED_RAW_FACT_IDS))
        self.assertEqual(len(SEED_APPROVED_RAW_EXPECTED), 15)
        self.assertEqual(len(APPROVED_RAW_FACT_IDS), 338)
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
        # Fully skipped ambiguous texts: no ID approved.
        for text in ("Technical talent.", "Strong sense of humor."):
            self.assertGreaterEqual(len(by_text[text]), 2, text)
            for fact_id in by_text[text]:
                self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)
        # Common sense: each family ID decided explicitly (Taurus S4.5B, Capricorn S4.7B).
        common_sense_ids = by_text["Relies on common sense."]
        self.assertGreaterEqual(len(common_sense_ids), 2)
        self.assertIn("taurus_relies_on_common_sense", APPROVED_RAW_FACT_IDS)
        self.assertIn("capricorn_l7_common_sense_reliance", APPROVED_RAW_FACT_IDS)


class SagittariusFamilyS44BTests(unittest.TestCase):
    def test_sagittarius_family_fully_reviewed(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "sign:Sagittarius")
        self.assertEqual(family.total_facts, 58)
        self.assertEqual(family.unreviewed, 0)
        self.assertEqual(family.approved_override, 42)
        self.assertEqual(family.approved_raw, 13)
        self.assertEqual(family.needs_review, 3)
        self.assertEqual(family.reviewed_count, 58)
        self.assertEqual(family.presentation_ready_count, 55)
        self.assertEqual(family.review_coverage, 1.0)
        self.assertAlmostEqual(family.presentation_ready_coverage, 55 / 58, places=6)

    def test_sagittarius_approved_raw_ids(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        self.assertEqual(len(S44B_SAGITTARIUS_APPROVED_RAW), 13)
        for fact_id in S44B_SAGITTARIUS_APPROVED_RAW:
            with self.subTest(fact_id=fact_id):
                self.assertIn(fact_id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(fact_id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_APPROVED_RAW)
                self.assertFalse(entry.uses_override)
                self.assertEqual(entry.human_text, entry.canonical_text)
                self.assertEqual(entry.canonical_text, by_id[fact_id].text)

    def test_sagittarius_new_overrides(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        self.assertEqual(len(S44B_SAGITTARIUS_OVERRIDES), 24)
        for fact_id, human in S44B_SAGITTARIUS_OVERRIDES.items():
            with self.subTest(fact_id=fact_id):
                self.assertIn(fact_id, by_id)
                self.assertEqual(HUMAN_COPY_OVERRIDES[fact_id], human)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_APPROVED_OVERRIDE)
                self.assertTrue(entry.uses_override)
                self.assertEqual(entry.human_text, human)
                self.assertEqual(entry.canonical_text, by_id[fact_id].text)
                self.assertNotEqual(entry.canonical_text, human)

        afflicted = build_catalog_entry(by_id["sag_bio_afflicted_accuracy_problems"])
        self.assertNotIn("hard_aspected", afflicted.human_text)
        self.assertNotIn("при поражении", afflicted.human_text)
        self.assertNotIn("Source affliction", afflicted.human_text)

        aptitude = build_catalog_entry(by_id["sag_bio_expert_aptitude"])
        self.assertNotIn("source-described", aptitude.human_text.lower())

        motive = build_catalog_entry(by_id["sag_bio_authority_learning_motivation"])
        self.assertEqual(motive.human_text, "Learning may be motivated by authority.")

        occupation = build_catalog_entry(by_id["sag_bio_occupation_associations"])
        self.assertIn("not career assignments", occupation.human_text)
        self.assertNotIn("recommended career", occupation.human_text.lower())
        self.assertNotIn("hiring", occupation.human_text.lower())

    def test_sagittarius_needs_review_ids(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        self.assertTrue(set(S44B_SAGITTARIUS_NEEDS_REVIEW).issubset(NEEDS_REVIEW_FACT_IDS))
        for fact_id in S44B_SAGITTARIUS_NEEDS_REVIEW:
            with self.subTest(fact_id=fact_id):
                self.assertNotIn(fact_id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_NEEDS_REVIEW)
                self.assertFalse(entry.uses_override)
                self.assertEqual(entry.human_text, entry.canonical_text)

    def test_global_totals_after_s411b(self):
        report = build_human_copy_catalog()
        self.assertEqual(report.total_facts, 1590)
        self.assertEqual(report.approved_override_count, 397)
        self.assertEqual(report.approved_raw_count, 338)
        self.assertEqual(report.needs_review_count, 19)
        self.assertEqual(report.unreviewed_count, 836)
        self.assertEqual(
            report.approved_override_count
            + report.approved_raw_count
            + report.needs_review_count
            + report.unreviewed_count,
            1590,
        )
        self.assertEqual(report.reviewed_count, 754)
        self.assertEqual(report.presentation_ready_count, 735)


class TaurusFamilyS45BTests(unittest.TestCase):
    S45B_TAURUS_APPROVED_RAW: tuple[str, ...] = (
        "taurus_harmonious_thinking",
        "taurus_unhurried_thinking",
        "taurus_bio_unhurried_thinking_communication_learning",
        "taurus_bio_productive_thinking_communication_learning",
        "taurus_relies_on_common_sense",
        "taurus_values_factual_reliability",
        "taurus_bio_beautiful_handwriting",
        "taurus_bio_beautiful_voice",
        "taurus_bio_beautiful_speech",
        "taurus_bio_practice_based_learning",
        "taurus_applying_knowledge_in_practice",
        "taurus_comfortable_learning_environment",
        "taurus_learning_needs_time_without_pressure",
        "taurus_learning_repetition_persistence",
        "taurus_may_recheck_information",
        "taurus_slow_processing_long_retention",
        "taurus_difficulty_rapidly_changing_mental_direction",
        "taurus_risk_inertia",
    )

    S45B_TAURUS_OVERRIDES: dict[str, str] = {
        "taurus_abstraction_harder_than_concrete": (
            "Abstraction can be harder than concrete or practical material."
        ),
        "taurus_bio_strong_attention": "May show increased or strong attention.",
        "taurus_bio_visual_scheme_learning": (
            "Learns best through visual schemes or diagrams."
        ),
        "taurus_slower_switching_topics": (
            "May switch more slowly between topics or tasks."
        ),
        "taurus_tangible_benefit_motivates_learning": (
            "Tangible benefit or practical motivation supports learning."
        ),
        "taurus_bio_aesthetic_learning_motivation": (
            "Learning may be motivated by material that feels beautiful or "
            "aesthetically attractive."
        ),
        "taurus_bio_money_learning_motivation": (
            "Learning may be motivated by money."
        ),
        "taurus_bio_vocal_artistic_aptitude": (
            "May show vocal or artistic aptitude."
        ),
    }

    def test_taurus_family_fully_reviewed(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "sign:Taurus")
        self.assertEqual(family.total_facts, 38)
        self.assertEqual(family.approved_override, 15)
        self.assertEqual(family.approved_raw, 23)
        self.assertEqual(family.needs_review, 0)
        self.assertEqual(family.unreviewed, 0)
        self.assertEqual(family.reviewed_count, 38)
        self.assertEqual(family.presentation_ready_count, 38)
        self.assertEqual(family.review_coverage, 1.0)
        self.assertEqual(family.presentation_ready_coverage, 1.0)

    def test_taurus_approved_raw_ids(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        self.assertEqual(len(self.S45B_TAURUS_APPROVED_RAW), 18)
        for fact_id in self.S45B_TAURUS_APPROVED_RAW:
            with self.subTest(fact_id=fact_id):
                self.assertIn(fact_id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(fact_id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_APPROVED_RAW)
                self.assertFalse(entry.uses_override)
                self.assertEqual(entry.human_text, entry.canonical_text)
                self.assertEqual(entry.canonical_text, by_id[fact_id].text)
        # Capricorn twin text was not auto-approved with Taurus; S4.7B decides it separately.
        self.assertIn("capricorn_l7_common_sense_reliance", APPROVED_RAW_FACT_IDS)
        self.assertIn("taurus_relies_on_common_sense", APPROVED_RAW_FACT_IDS)

    def test_taurus_new_overrides(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        self.assertEqual(len(self.S45B_TAURUS_OVERRIDES), 8)
        for fact_id, human in self.S45B_TAURUS_OVERRIDES.items():
            with self.subTest(fact_id=fact_id):
                self.assertIn(fact_id, by_id)
                self.assertEqual(HUMAN_COPY_OVERRIDES[fact_id], human)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_APPROVED_OVERRIDE)
                self.assertTrue(entry.uses_override)
                self.assertEqual(entry.human_text, human)
                self.assertEqual(entry.canonical_text, by_id[fact_id].text)
                self.assertNotEqual(entry.canonical_text, human)
                self.assertNotIn(" / ", human)

        aptitude = build_catalog_entry(by_id["taurus_bio_vocal_artistic_aptitude"])
        self.assertNotIn("source-described", aptitude.human_text.lower())
        motive = build_catalog_entry(by_id["taurus_bio_money_learning_motivation"])
        self.assertEqual(motive.human_text, "Learning may be motivated by money.")

    def test_taurus_no_needs_review(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "sign:Taurus")
        self.assertEqual(family.needs_review, 0)
        taurus_ids = {
            e.fact_id for e in get_family_entries(report, "sign:Taurus")
        }
        self.assertTrue(taurus_ids.isdisjoint(NEEDS_REVIEW_FACT_IDS))


class SignReviewQueueS46Tests(unittest.TestCase):
    def test_all_twelve_signs_appear_exactly_once(self):
        from app.services.mercury_human_copy_catalog import (
            SIGN_FAMILY_KEYS,
            ZODIAC_SIGN_ORDER,
            build_sign_review_queue,
        )

        queue = build_sign_review_queue()
        keys = [entry.family_key for entry in queue.all_sign_families]
        self.assertEqual(keys, list(SIGN_FAMILY_KEYS))
        self.assertEqual(len(keys), 12)
        self.assertEqual(len(set(keys)), 12)
        self.assertEqual(
            [entry.sign_name for entry in queue.all_sign_families],
            list(ZODIAC_SIGN_ORDER),
        )

    def test_taurus_and_sagittarius_completion_flags(self):
        from app.services.mercury_human_copy_catalog import build_sign_review_queue

        queue = build_sign_review_queue()
        by_key = {entry.family_key: entry for entry in queue.all_sign_families}
        taurus = by_key["sign:Taurus"]
        sag = by_key["sign:Sagittarius"]
        self.assertTrue(taurus.is_review_complete)
        self.assertTrue(taurus.is_presentation_ready_complete)
        self.assertTrue(sag.is_review_complete)
        self.assertFalse(sag.is_presentation_ready_complete)
        self.assertEqual(sag.needs_review, 3)
        self.assertEqual(sag.presentation_ready_count, 55)
        completed_keys = {entry.family_key for entry in queue.completed_families}
        self.assertIn("sign:Taurus", completed_keys)
        self.assertIn("sign:Sagittarius", completed_keys)
        incomplete_keys = {entry.family_key for entry in queue.incomplete_queue}
        self.assertNotIn("sign:Taurus", incomplete_keys)
        self.assertNotIn("sign:Sagittarius", incomplete_keys)

    def test_queue_ordering_deterministic_and_workload_based(self):
        from app.services.mercury_human_copy_catalog import (
            _sign_review_priority_key,
            build_sign_review_queue,
        )

        first = build_sign_review_queue()
        second = build_sign_review_queue()
        self.assertEqual(
            [e.family_key for e in first.incomplete_queue],
            [e.family_key for e in second.incomplete_queue],
        )
        self.assertEqual(
            [b.family_keys for b in first.suggested_batches],
            [b.family_keys for b in second.suggested_batches],
        )
        ordered = list(first.incomplete_queue)
        self.assertEqual(
            ordered,
            sorted(ordered, key=_sign_review_priority_key),
        )
        # Sign review is complete: empty incomplete queue and batches.
        self.assertEqual(ordered, [])
        self.assertEqual(list(first.suggested_batches), [])

    def test_queue_priority_order_incomplete_signs(self):
        from app.services.mercury_human_copy_catalog import build_sign_review_queue

        queue = build_sign_review_queue()
        self.assertEqual(list(queue.incomplete_queue), [])
        completed = {entry.sign_name for entry in queue.completed_families}
        self.assertEqual(
            completed,
            {
                "Taurus",
                "Sagittarius",
                "Capricorn",
                "Leo",
                "Aquarius",
                "Gemini",
                "Pisces",
                "Aries",
                "Scorpio",
                "Libra",
                "Cancer",
                "Virgo",
            },
        )

    def test_suggested_batches_heaviest_lightest_partition(self):
        from app.services.mercury_human_copy_catalog import build_sign_review_queue

        queue = build_sign_review_queue()
        incomplete_keys = [entry.family_key for entry in queue.incomplete_queue]
        completed_keys = {entry.family_key for entry in queue.completed_families}
        self.assertEqual(incomplete_keys, [])
        self.assertEqual(list(queue.suggested_batches), [])
        for sign in (
            "Capricorn",
            "Leo",
            "Aquarius",
            "Gemini",
            "Pisces",
            "Aries",
            "Scorpio",
            "Libra",
            "Cancer",
            "Virgo",
            "Taurus",
            "Sagittarius",
        ):
            self.assertIn(f"sign:{sign}", completed_keys)

    def test_pack_heaviest_lightest_and_odd_singleton(self):
        from app.services.mercury_human_copy_catalog import (
            SignReviewQueueEntry,
            _pack_sign_batches,
        )

        def entry(name: str, unreviewed: int) -> SignReviewQueueEntry:
            return SignReviewQueueEntry(
                family_key=f"sign:{name}",
                sign_name=name,
                total_facts=unreviewed,
                approved_override=0,
                approved_raw=0,
                needs_review=0,
                unreviewed=unreviewed,
                review_recommended_unreviewed=0,
                reviewed_count=0,
                presentation_ready_count=0,
                review_coverage=0.0,
                presentation_ready_coverage=0.0,
                is_review_complete=False,
                is_presentation_ready_complete=False,
                estimated_review_load=(unreviewed, 0, 0),
            )

        # Priority-sorted stand-ins: heaviest first.
        odd = (
            entry("H1", 90),
            entry("H2", 80),
            entry("M", 50),
            entry("L2", 40),
            entry("L1", 30),
        )
        batches = _pack_sign_batches(odd)
        self.assertEqual(
            [b.sign_names for b in batches],
            [("H1", "L1"), ("H2", "L2"), ("M",)],
        )
        self.assertEqual(
            [b.unreviewed_workload for b in batches],
            [120, 120, 50],
        )
        # Batching uses unreviewed workload ends only — no element/modality fields.
        even = (entry("A", 10), entry("B", 8), entry("C", 6), entry("D", 4))
        even_batches = _pack_sign_batches(even)
        self.assertEqual(
            [b.sign_names for b in even_batches],
            [("A", "D"), ("B", "C")],
        )

    def test_needs_review_backlog_contains_policy_nineteen(self):
        from app.services.mercury_human_copy_catalog import build_sign_review_queue

        queue = build_sign_review_queue()
        backlog_ids = {item.fact_id for item in queue.needs_review_backlog}
        self.assertEqual(
            backlog_ids,
            {
                "sag_bio_impartiality_disrupted",
                "sag_bio_learnability_disrupted",
                "sag_bio_major_exile",
                "aquarius_bio_afflicted_source_adhd_effect_wording",
                "aquarius_bio_source_genius_intellect_archetype",
                "aquarius_l7_source_genius_intellect_wording",
                "aquarius_l7_claircognizance",
                "gemini_bio_major_domicile_sync",
                "pisces_bio_minor_exile",
                "pisces_bio_universal_cosmic_intellect_synthesis",
                "pisces_bio_unusually_strong_intuition",
                "pisces_l7_high_intuition",
                "pisces_l7_correct_decisions_nonrational_routes",
                "pisces_l7_mystical_thinking",
                "aries_bio_source_sexual_motivation_wording",
                "scorpio_bio_source_sexual_motivation",
                "cancer_bio_depends_on_moon_sign",
                "cancer_bio_emotional_intelligence_source_claim",
                "virgo_bio_minor_domicile_near_sync",
            },
        )
        self.assertEqual(len(queue.needs_review_backlog), 19)

    def test_queue_does_not_mutate_registries_or_totals(self):
        from app.services.mercury_human_copy_catalog import (
            APPROVED_RAW_FACT_IDS,
            NEEDS_REVIEW_FACT_IDS,
            build_human_copy_catalog,
            build_sign_review_queue,
        )

        before_overrides = dict(HUMAN_COPY_OVERRIDES)
        before_raw = set(APPROVED_RAW_FACT_IDS)
        before_needs = set(NEEDS_REVIEW_FACT_IDS)
        catalog = build_human_copy_catalog()
        queue = build_sign_review_queue(catalog)
        self.assertEqual(catalog.total_facts, 1590)
        self.assertEqual(dict(HUMAN_COPY_OVERRIDES), before_overrides)
        self.assertEqual(set(APPROVED_RAW_FACT_IDS), before_raw)
        self.assertEqual(set(NEEDS_REVIEW_FACT_IDS), before_needs)
        self.assertEqual(queue.review_complete_family_count, 12)
        self.assertEqual(queue.presentation_ready_complete_family_count, 4)
        self.assertEqual(len(queue.incomplete_queue), 0)
        self.assertEqual(list(queue.suggested_batches), [])
        self.assertEqual(queue.sign_total_facts, 730)
        self.assertEqual(queue.sign_reviewed_facts, 730)
        self.assertEqual(queue.sign_unreviewed_facts, 0)
        self.assertEqual(queue.sign_presentation_ready_facts, 711)
        self.assertEqual(queue.sign_needs_review_facts, 19)


class CapricornLeoFamilyS47BTests(unittest.TestCase):
    S47B_CAPRICORN_APPROVED_RAW: tuple[str, ...] = (
        "capricorn_bio_calm_voice",
        "capricorn_bio_diploma_certificate_matters",
        "capricorn_bio_iron_argumentation",
        "capricorn_bio_learning_alone",
        "capricorn_bio_learning_long_systematic_courses",
        "capricorn_bio_learning_official_institutions",
        "capricorn_bio_learning_own_experience",
        "capricorn_bio_learning_practice",
        "capricorn_bio_logical_thinking",
        "capricorn_bio_needs_practical_usefulness_for_communication",
        "capricorn_bio_unemotional_style",
        "capricorn_l7_algorithms_help",
        "capricorn_l7_authoritative_opinion_reliance",
        "capricorn_l7_businesslike_thinking",
        "capricorn_l7_calm_speech",
        "capricorn_l7_common_sense_reliance",
        "capricorn_l7_concrete_thinking",
        "capricorn_l7_env_businesslike_siblings",
        "capricorn_l7_env_formal_communication",
        "capricorn_l7_env_limited_contact",
        "capricorn_l7_env_usefulness_selected",
        "capricorn_l7_focus_on_essence",
        "capricorn_l7_focus_on_principle",
        "capricorn_l7_formal_communication",
        "capricorn_l7_iron_logic",
        "capricorn_l7_lack_of_haste",
        "capricorn_l7_needs_sequence_of_actions",
        "capricorn_l7_needs_why_material_learned",
        "capricorn_l7_notes_help",
        "capricorn_l7_one_thing_at_a_time",
        "capricorn_l7_one_thought_at_a_time",
        "capricorn_l7_plans_help",
        "capricorn_l7_quiet_speech",
        "capricorn_l7_schedules_help",
        "capricorn_l7_schemes_help",
        "capricorn_l7_scientific_mindset",
        "capricorn_l7_speech_without_filler",
        "capricorn_l7_structure_helps",
        "capricorn_l7_structured_thinking",
        "capricorn_l7_stubbornness_in_views",
        "capricorn_l7_systems_help",
        "capricorn_l7_tables_help",
    )

    S47B_CAPRICORN_OVERRIDES: dict[str, str] = {
        "capricorn_bio_afflicted_closedness": (
            "Communication or manner may become closed."
        ),
        "capricorn_bio_afflicted_difficulty_tuning_into_others_thoughts": (
            "May have difficulty tuning into other people's thoughts."
        ),
        "capricorn_bio_afflicted_difficulty_understanding_others_thinking": (
            "May have difficulty understanding other people's thinking."
        ),
        "capricorn_bio_afflicted_duty_rule_bound_thinking": (
            'Thinking can become duty- or rule-bound ("must," "should," '
            '"proper," "obliged").'
        ),
        "capricorn_bio_afflicted_old_dogma_fixation": (
            "Thinking can fixate on old dogma."
        ),
        "capricorn_bio_afflicted_professional_vs_everyday_orientation": (
            "Professional-domain knowledge can coexist with poor orientation "
            "in everyday domains."
        ),
        "capricorn_bio_afflicted_rigid_thinking": (
            "Thinking can become rigid."
        ),
        "capricorn_bio_afflicted_severe_lack_of_imagination": (
            "Imagination may be severely limited."
        ),
        "capricorn_bio_afflicted_unsociability": "May become unsociable.",
        "capricorn_bio_clear_thinking_communication_learning": (
            "Thinking, communication, and learning are described as clear."
        ),
        "capricorn_bio_commanding_tone": "May use a commanding tone.",
        "capricorn_bio_difficult_casual_chat": (
            'Difficult to chat casually or "about life."'
        ),
        "capricorn_bio_forecasting": "Forecasting ability.",
        "capricorn_bio_logic": "Logical ability.",
        "capricorn_bio_memory": "Memory capacity.",
        "capricorn_bio_motivation_build_structure": (
            "Learning may be motivated by building structure."
        ),
        "capricorn_bio_motivation_logical_interconnections": (
            "Learning may be motivated by building logical interconnections."
        ),
        "capricorn_bio_occupation_associations": (
            "Occupational themes associated with this placement include "
            "leadership, science, and entrepreneurship; these are not career "
            "assignments."
        ),
        "capricorn_bio_planning": "Planning ability.",
        "capricorn_bio_sober_cold_style": (
            "Sober or cool communication style."
        ),
        "capricorn_bio_structured": (
            "Structured thinking, communication, and learning."
        ),
        "capricorn_bio_table_template_oriented": (
            "Oriented toward tables and templates."
        ),
        "capricorn_bio_technical_aptitude": "Technical aptitude.",
        "capricorn_l7_beautiful_voice": "May have a beautiful voice.",
        "capricorn_l7_chopped_concise_phrases": (
            "Phrases can be clipped and concise."
        ),
        "capricorn_l7_develop_fundamentality": (
            "Growth area: develop a more fundamental and well-grounded approach."
        ),
        "capricorn_l7_env_concrete_without_water": (
            "Sibling and environmental communication tends to be concrete and "
            "free of filler."
        ),
        "capricorn_l7_limited_contact": (
            "Limited contact or restrained sociability."
        ),
        "capricorn_l7_metrics_help": (
            "Clear indicators or metrics help learning."
        ),
        "capricorn_l7_rely_on_proven_experience": (
            "Growth area: rely on proven experience."
        ),
        "capricorn_l7_sarcasm_when_imagination_lacking": (
            "When imagination is lacking, humor may take a sarcastic form."
        ),
        "capricorn_l7_slow_deliberate_perception": (
            "Information perception is slow and deliberate."
        ),
        "capricorn_l7_strong_critic": "May be a strong critic.",
        "capricorn_l7_systematize": "Growth area: systematize.",
    }

    S47B_LEO_APPROVED_RAW: tuple[str, ...] = (
        "leo_l7_env_emphasizes_own_views",
        "leo_l7_env_idea_appropriation",
        "leo_l7_env_seeks_admiration",
        "leo_l7_env_seeks_recognition",
        "leo_l7_learning_bright_presentation",
        "leo_l7_learning_creative_reformulation",
        "leo_l7_learning_performing",
        "leo_l7_learning_standing_out",
        "leo_l7_monologue_communication",
        "leo_l7_monologue_thinking",
        "leo_l7_persist_in_views_while_knowing_wrong",
        "leo_l7_prepared_phrases_appearance_of_competence",
        "leo_l7_seeks_applause",
        "leo_l7_tracks_audience_effect",
        "leo_l7_transforms_others_idea_into_own",
        "leo_l7_unwillingness_to_admit_wrong",
        "leo_leadership_communication_potential",
        "leo_learns_through_impressions",
        "leo_learns_through_independent_investigation",
        "leo_may_discount_others_opinions",
        "leo_nonstandard_speech_thinking",
        "leo_playful_competition_motivates_learning",
        "leo_pr_ability",
        "leo_praise_motivates_learning",
        "leo_risk_intellectual_superficiality",
        "leo_sales_ability",
        "leo_strong_creative_quality",
        "leo_strong_debate_potential",
        "leo_strong_oratory_potential",
        "leo_thinks_from_own_position",
        "leo_visible_status_motivates_learning",
        "leo_wants_to_demonstrate_results",
    )

    S47B_LEO_OVERRIDES: dict[str, str] = {
        "leo_dialogue_difficulty": "Real two-way dialogue can be difficult.",
        "leo_expressive_visible_thinking": (
            "Thinking, communication, and learning are highly expressive and "
            "visible."
        ),
        "leo_l7_creativity": "Creative ability.",
        "leo_l7_difficulty_opinion_receptivity": (
            "May have difficulty being receptive to other people's opinions."
        ),
        "leo_l7_dignified_lordly_speech": (
            "Dignified or lordly speech style."
        ),
        "leo_l7_env_lordly_sibling_position": (
            'May take an "above" or lordly position with siblings.'
        ),
        "leo_l7_nonstandardness": "Nonstandard quality.",
        "leo_l7_self_praise_learning_motivation": (
            "Self-praise or self-encouragement can motivate learning."
        ),
        "leo_l7_verbal_escape_skill": (
            "May be able to wriggle out of situations verbally."
        ),
    }

    def test_capricorn_family_fully_reviewed(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "sign:Capricorn")
        self.assertEqual(family.total_facts, 76)
        self.assertEqual(family.approved_override, 34)
        self.assertEqual(family.approved_raw, 42)
        self.assertEqual(family.needs_review, 0)
        self.assertEqual(family.unreviewed, 0)
        self.assertEqual(family.reviewed_count, 76)
        self.assertEqual(family.presentation_ready_count, 76)
        self.assertEqual(family.review_coverage, 1.0)
        self.assertEqual(family.presentation_ready_coverage, 1.0)

    def test_leo_family_fully_reviewed(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "sign:Leo")
        self.assertEqual(family.total_facts, 56)
        self.assertEqual(family.approved_override, 24)
        self.assertEqual(family.approved_raw, 32)
        self.assertEqual(family.needs_review, 0)
        self.assertEqual(family.unreviewed, 0)
        self.assertEqual(family.reviewed_count, 56)
        self.assertEqual(family.presentation_ready_count, 56)
        self.assertEqual(family.review_coverage, 1.0)
        self.assertEqual(family.presentation_ready_coverage, 1.0)

    def test_s47b_approved_raw_and_overrides(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        self.assertEqual(len(self.S47B_CAPRICORN_APPROVED_RAW), 42)
        self.assertEqual(len(self.S47B_CAPRICORN_OVERRIDES), 34)
        self.assertEqual(len(self.S47B_LEO_APPROVED_RAW), 32)
        self.assertEqual(len(self.S47B_LEO_OVERRIDES), 9)
        for fact_id in (
            *self.S47B_CAPRICORN_APPROVED_RAW,
            *self.S47B_LEO_APPROVED_RAW,
        ):
            with self.subTest(fact_id=fact_id):
                self.assertIn(fact_id, by_id)
                self.assertIn(fact_id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(fact_id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_APPROVED_RAW)
                self.assertFalse(entry.uses_override)
                self.assertEqual(entry.human_text, entry.canonical_text)
                self.assertEqual(entry.canonical_text, by_id[fact_id].text)
        for fact_id, human in {
            **self.S47B_CAPRICORN_OVERRIDES,
            **self.S47B_LEO_OVERRIDES,
        }.items():
            with self.subTest(fact_id=fact_id):
                self.assertIn(fact_id, by_id)
                self.assertEqual(HUMAN_COPY_OVERRIDES[fact_id], human)
                self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_APPROVED_OVERRIDE)
                self.assertTrue(entry.uses_override)
                self.assertEqual(entry.human_text, human)
                self.assertEqual(entry.canonical_text, by_id[fact_id].text)
                self.assertNotEqual(entry.canonical_text, human)

    def test_s47b_four_wording_corrections(self):
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["capricorn_bio_occupation_associations"],
            "Occupational themes associated with this placement include "
            "leadership, science, and entrepreneurship; these are not career "
            "assignments.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["capricorn_l7_env_concrete_without_water"],
            "Sibling and environmental communication tends to be concrete and "
            "free of filler.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["capricorn_l7_develop_fundamentality"],
            "Growth area: develop a more fundamental and well-grounded approach.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["leo_l7_difficulty_opinion_receptivity"],
            "May have difficulty being receptive to other people's opinions.",
        )
        self.assertNotIn(
            "deafness",
            HUMAN_COPY_OVERRIDES["leo_l7_difficulty_opinion_receptivity"].lower(),
        )
        self.assertNotIn(
            "without water",
            HUMAN_COPY_OVERRIDES["capricorn_l7_env_concrete_without_water"].lower(),
        )
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        self.assertIn("without water", by_id["capricorn_l7_env_concrete_without_water"].text)
        self.assertIn("deafness", by_id["leo_l7_difficulty_opinion_receptivity"].text)
        self.assertIn("fundamentality", by_id["capricorn_l7_develop_fundamentality"].text)

    def test_s47b_no_registry_conflicts_and_needs_review_unchanged(self):
        self.assertTrue(
            set(HUMAN_COPY_OVERRIDES).isdisjoint(APPROVED_RAW_FACT_IDS)
        )
        self.assertTrue(
            set(HUMAN_COPY_OVERRIDES).isdisjoint(NEEDS_REVIEW_FACT_IDS)
        )
        self.assertTrue(
            set(APPROVED_RAW_FACT_IDS).isdisjoint(NEEDS_REVIEW_FACT_IDS)
        )
        self.assertTrue(
            {
                "sag_bio_impartiality_disrupted",
                "sag_bio_learnability_disrupted",
                "sag_bio_major_exile",
            }.issubset(NEEDS_REVIEW_FACT_IDS)
        )
        self.assertEqual(len(NEEDS_REVIEW_FACT_IDS), 19)
        # Capricorn common-sense approval is ID-local; Taurus twin stays raw.
        self.assertIn("capricorn_l7_common_sense_reliance", APPROVED_RAW_FACT_IDS)
        self.assertIn("taurus_relies_on_common_sense", APPROVED_RAW_FACT_IDS)
        self.assertNotIn("capricorn_l7_common_sense_reliance", HUMAN_COPY_OVERRIDES)


class AquariusGeminiFamilyS48BTests(unittest.TestCase):
    S48B_AQUARIUS_APPROVED_RAW: tuple[str, ...] = (
        "aquarius_bio_creative_thinking",
        "aquarius_bio_curiosity",
        "aquarius_bio_erudition",
        "aquarius_bio_extemporaneous_many_topics",
        "aquarius_bio_interest_science_fiction",
        "aquarius_bio_interest_technology",
        "aquarius_bio_knowledge_fragment_synthesis",
        "aquarius_bio_learning_audio",
        "aquarius_bio_learning_books",
        "aquarius_bio_learning_group_communication",
        "aquarius_bio_learning_lectures",
        "aquarius_bio_learning_video",
        "aquarius_l7_abstraction_ability",
        "aquarius_l7_book_learning",
        "aquarius_l7_cycles_many_options_quickly",
        "aquarius_l7_democratic_communication",
        "aquarius_l7_discussion_learning",
        "aquarius_l7_env_broad_social_circle",
        "aquarius_l7_env_friendly_siblings",
        "aquarius_l7_env_futuristic_environment",
        "aquarius_l7_env_unpredictable_siblings",
        "aquarius_l7_env_unusual_environment",
        "aquarius_l7_extemporaneous_many_topics",
        "aquarius_l7_gadgets_can_help",
        "aquarius_l7_global_thinking",
        "aquarius_l7_good_memory",
        "aquarius_l7_group_learning",
        "aquarius_l7_idealistic_thinking",
        "aquarius_l7_independent_learning",
        "aquarius_l7_independent_thinking",
        "aquarius_l7_lecture_learning",
        "aquarius_l7_planning_can_help",
        "aquarius_l7_processes_large_data_quickly",
        "aquarius_l7_spans_knowledge_areas",
        "aquarius_l7_speech_varies_with_mood",
    )

    S48B_AQUARIUS_OVERRIDES: dict[str, str] = {
        "aquarius_bio_afflicted_anomalous_rhythms": (
            "Mental activity may follow irregular or unusual rhythms."
        ),
        "aquarius_bio_afflicted_broad_fragmentary_general_knowledge": (
            "Knowledge can become broad but fragmentary."
        ),
        "aquarius_bio_afflicted_idea_waves_then_irritation_slowdown": (
            "Waves of many ideas may be followed by irritation or mental "
            "slowdown."
        ),
        "aquarius_bio_afflicted_instability_of_learning": (
            "Learning can become unstable."
        ),
        "aquarius_bio_afflicted_instability_of_thinking": (
            "Thinking can become unstable."
        ),
        "aquarius_bio_afflicted_insufficient_depth_despite_breadth": (
            "Breadth may come with insufficient depth."
        ),
        "aquarius_bio_afflicted_irregular_broken_speech_tempo": (
            "Speech tempo may become irregular or broken."
        ),
        "aquarius_bio_afflicted_loss_of_focus": "May lose focus.",
        "aquarius_bio_artistic_aptitude": "May show artistic aptitude.",
        "aquarius_bio_continual_learning_courses": (
            "Continual learning; may enjoy courses."
        ),
        "aquarius_bio_creativity": "Creative ability.",
        "aquarius_bio_forecasting": "Forecasting ability.",
        "aquarius_bio_insights": "May show insight.",
        "aquarius_bio_interest_in_future": "Interest in the future.",
        "aquarius_bio_inventor_aptitude": "May show aptitude for invention.",
        "aquarius_bio_motivation_extraordinary_new_information": (
            "Learning may be motivated by extraordinary or unusual new "
            "information."
        ),
        "aquarius_bio_motivation_fresh_information": (
            "Learning may be motivated by a constant need for fresh information."
        ),
        "aquarius_bio_motivation_natural_curiosity": (
            "Learning may be motivated by natural curiosity."
        ),
        "aquarius_bio_planning": "Planning ability.",
        "aquarius_bio_strong_firm_memory": "Strong or firm memory.",
        "aquarius_bio_technical_scientific_aptitude": (
            "May show technical or scientific aptitude."
        ),
        "aquarius_bio_uranian_freedom_equality_fraternity_coloring": (
            "Thinking, communication, and learning may be colored by themes of "
            "freedom, equality, and fraternity."
        ),
        "aquarius_l7_anomalous_mental_rhythm": (
            "Anomalous or irregular rhythm of mental activity."
        ),
        "aquarius_l7_calculator_in_the_head": (
            "May have a calculator-like way of handling mental calculations."
        ),
        "aquarius_l7_develop_concreteness_in_decisions": (
            "Growth area: make decisions more concrete and specific."
        ),
        "aquarius_l7_develop_concreteness_in_wording": (
            "Growth area: make wording more concrete and specific."
        ),
        "aquarius_l7_engage_through_genuine_interest": (
            "Growth area: engage through genuine interest."
        ),
        "aquarius_l7_gets_bored_quickly": "May get bored quickly.",
        "aquarius_l7_informal_communication": (
            "Familiar or informal communication."
        ),
        "aquarius_l7_lack_of_patience": "May show a lack of patience.",
        "aquarius_l7_lack_of_systematicity": (
            "May have difficulty staying systematic."
        ),
        "aquarius_l7_quirky_speech_manner": (
            "Quirky or unusual speech manner."
        ),
        "aquarius_l7_scattering_dispersion": (
            "Attention or interests may become scattered."
        ),
    }

    S48B_AQUARIUS_NEEDS_REVIEW: tuple[str, ...] = (
        "aquarius_bio_afflicted_source_adhd_effect_wording",
        "aquarius_bio_source_genius_intellect_archetype",
        "aquarius_l7_source_genius_intellect_wording",
        "aquarius_l7_claircognizance",
    )

    S48B_GEMINI_APPROVED_RAW: tuple[str, ...] = (
        "gemini_bio_curiosity_motivated_learning",
        "gemini_bio_demonstrative_teacher_potential",
        "gemini_bio_intellectual_multitasking",
        "gemini_bio_rationalism",
        "gemini_bio_reliance_on_facts",
        "gemini_bio_strong_memory",
        "gemini_bio_strong_student_potential",
        "gemini_l7_env_constantly_renews",
        "gemini_l7_env_contact_quantity_over_quality",
        "gemini_l7_env_sibling_easy",
        "gemini_l7_env_sibling_superficial",
        "gemini_l7_highly_contact_oriented_thinking",
        "gemini_l7_learns_easily_in_dialogue",
        "gemini_l7_logical_thinking",
        "gemini_l7_may_fail_to_see_whole",
        "gemini_l7_particular_to_general",
        "gemini_l7_quantity_may_dominate_quality",
        "gemini_l7_quick_understanding_may_cause_laziness",
        "gemini_l7_quick_understanding_may_lose_interest",
        "gemini_l7_risk_boredom_prolonged_one_subject",
        "gemini_l7_simplifies_abstractions",
        "gemini_l7_strong_commercial_ability",
        "gemini_l7_strong_negotiation_ability",
        "gemini_l7_support_books",
        "gemini_l7_support_groups",
        "gemini_l7_support_lectures",
        "gemini_l7_support_multi_person_communication",
        "gemini_l7_support_teachers",
        "gemini_l7_understands_quickly",
    )

    S48B_GEMINI_OVERRIDES: dict[str, str] = {
        "gemini_bio_afflicted_excessive_verbal_output": (
            "Communication may become excessively verbal."
        ),
        "gemini_bio_afflicted_lying": "Communication may involve lying.",
        "gemini_bio_afflicted_words_exceed_actions": (
            "Words may greatly outnumber actions."
        ),
        "gemini_bio_communicator_ability": "Communicator ability.",
        "gemini_bio_driving_ability": (
            "May show driving ability or potential."
        ),
        "gemini_bio_extraordinary_speed": (
            "Thinking, communication, and learning can be extraordinarily fast."
        ),
        "gemini_bio_foreign_language_polyglot": (
            "May show potential for foreign languages or multilingualism."
        ),
        "gemini_bio_informational_omnivorousness": (
            "May have a broad appetite for information."
        ),
        "gemini_bio_learns_from_many_sources": (
            "Learns from many kinds of sources."
        ),
        "gemini_bio_oratory_talent": (
            "May show oratory talent or potential."
        ),
        "gemini_bio_salesperson_ability": "Sales ability.",
        "gemini_bio_slight_technical_orientation": (
            "Slight technical orientation."
        ),
        "gemini_bio_writing_talent": (
            "May show writing talent or potential."
        ),
        "gemini_l7_dev_avoid_scattering": (
            "Growth area: avoid scattering across parallel tasks."
        ),
        "gemini_l7_dev_focus_one_subject": (
            "Growth area: focus on one subject."
        ),
        "gemini_l7_dev_prioritize_information": (
            "Growth area: prioritize information."
        ),
        "gemini_l7_dev_slow_down": "Growth area: slow down.",
        "gemini_l7_env_indiscriminate_acquaintances": (
            "May form acquaintances broadly and indiscriminately."
        ),
        "gemini_l7_group_listening": (
            "Can track individual people while working with a large group."
        ),
        "gemini_l7_high_working_memory_speed": (
            "Very high working-memory speed."
        ),
    }

    def test_aquarius_family_fully_reviewed(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "sign:Aquarius")
        self.assertEqual(family.total_facts, 72)
        self.assertEqual(family.approved_override, 33)
        self.assertEqual(family.approved_raw, 35)
        self.assertEqual(family.needs_review, 4)
        self.assertEqual(family.unreviewed, 0)
        self.assertEqual(family.reviewed_count, 72)
        self.assertEqual(family.presentation_ready_count, 68)
        self.assertEqual(family.review_coverage, 1.0)
        self.assertEqual(family.presentation_ready_coverage, round(68 / 72, 6))

    def test_gemini_family_fully_reviewed(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "sign:Gemini")
        self.assertEqual(family.total_facts, 50)
        self.assertEqual(family.approved_override, 20)
        self.assertEqual(family.approved_raw, 29)
        self.assertEqual(family.needs_review, 1)
        self.assertEqual(family.unreviewed, 0)
        self.assertEqual(family.reviewed_count, 50)
        self.assertEqual(family.presentation_ready_count, 49)
        self.assertEqual(family.review_coverage, 1.0)
        self.assertEqual(family.presentation_ready_coverage, 0.98)

    def test_s48b_registries_and_wording_corrections(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        self.assertEqual(len(self.S48B_AQUARIUS_APPROVED_RAW), 35)
        self.assertEqual(len(self.S48B_AQUARIUS_OVERRIDES), 33)
        self.assertEqual(len(self.S48B_AQUARIUS_NEEDS_REVIEW), 4)
        self.assertEqual(len(self.S48B_GEMINI_APPROVED_RAW), 29)
        self.assertEqual(len(self.S48B_GEMINI_OVERRIDES), 20)
        for fact_id in (
            *self.S48B_AQUARIUS_APPROVED_RAW,
            *self.S48B_GEMINI_APPROVED_RAW,
        ):
            with self.subTest(raw=fact_id):
                self.assertIn(fact_id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(fact_id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_APPROVED_RAW)
                self.assertEqual(entry.human_text, entry.canonical_text)
        for fact_id, human in {
            **self.S48B_AQUARIUS_OVERRIDES,
            **self.S48B_GEMINI_OVERRIDES,
        }.items():
            with self.subTest(override=fact_id):
                self.assertEqual(HUMAN_COPY_OVERRIDES[fact_id], human)
                self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_APPROVED_OVERRIDE)
                self.assertEqual(entry.canonical_text, by_id[fact_id].text)
                self.assertNotEqual(entry.canonical_text, human)
        for fact_id in (
            *self.S48B_AQUARIUS_NEEDS_REVIEW,
            "gemini_bio_major_domicile_sync",
        ):
            with self.subTest(needs=fact_id):
                self.assertIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                self.assertNotIn(fact_id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_NEEDS_REVIEW)
                self.assertEqual(entry.human_text, entry.canonical_text)
        # Spot-check approved wording corrections vs unchanged canonical.
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["aquarius_bio_afflicted_anomalous_rhythms"],
            "Mental activity may follow irregular or unusual rhythms.",
        )
        self.assertIn(
            "anomalous rhythms",
            by_id["aquarius_bio_afflicted_anomalous_rhythms"].text,
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["aquarius_bio_uranian_freedom_equality_fraternity_coloring"],
            "Thinking, communication, and learning may be colored by themes of "
            "freedom, equality, and fraternity.",
        )
        self.assertNotIn(
            "Mercury functions",
            HUMAN_COPY_OVERRIDES[
                "aquarius_bio_uranian_freedom_equality_fraternity_coloring"
            ],
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["gemini_bio_afflicted_words_exceed_actions"],
            "Words may greatly outnumber actions.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["gemini_bio_salesperson_ability"],
            "Sales ability.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["gemini_l7_high_working_memory_speed"],
            "Very high working-memory speed.",
        )
        self.assertTrue(
            set(HUMAN_COPY_OVERRIDES).isdisjoint(APPROVED_RAW_FACT_IDS)
        )
        self.assertTrue(
            set(HUMAN_COPY_OVERRIDES).isdisjoint(NEEDS_REVIEW_FACT_IDS)
        )
        self.assertTrue(
            set(APPROVED_RAW_FACT_IDS).isdisjoint(NEEDS_REVIEW_FACT_IDS)
        )
        self.assertEqual(len(NEEDS_REVIEW_FACT_IDS), 19)


class PiscesAriesFamilyS49BTests(unittest.TestCase):
    S49B_PISCES_APPROVED_RAW: tuple[str, ...] = (
        "pisces_bio_context_dependent_memory",
        "pisces_bio_learning_audio",
        "pisces_bio_learning_books",
        "pisces_bio_learning_flow_state",
        "pisces_bio_public_speaking_requires_preparation",
        "pisces_bio_public_speaking_requires_training",
        "pisces_bio_selective_memory",
        "pisces_l7_calm_communication",
        "pisces_l7_creative_reinterpretation_learning",
        "pisces_l7_emotional_speech",
        "pisces_l7_env_adapts_to_collective_stereotypes",
        "pisces_l7_env_avoids_polemics",
        "pisces_l7_env_possible_misunderstanding",
        "pisces_l7_env_sibling_illusions",
        "pisces_l7_env_soulful_siblings",
        "pisces_l7_harmonious_communication",
        "pisces_l7_image_based_perception",
        "pisces_l7_learning_images",
        "pisces_l7_learning_intuitive_impression",
        "pisces_l7_learning_listening",
        "pisces_l7_learning_photos",
        "pisces_l7_learning_solitude",
        "pisces_l7_learning_video",
        "pisces_l7_overall_impression_over_isolated_fact",
        "pisces_l7_speaks_through_parables",
        "pisces_l7_speaks_through_riddles",
        "pisces_l7_speech_may_lack_central_idea",
        "pisces_l7_unclear_speech",
        "pisces_l7_unconventional_learning",
    )

    S49B_PISCES_OVERRIDES: dict[str, str] = {
        "pisces_bio_afflicted_crumpled_speech": (
            "Speech may become fragmented or poorly formed."
        ),
        "pisces_bio_afflicted_information_chaos": (
            "Thinking can become contradictory and informationally chaotic."
        ),
        "pisces_bio_afflicted_lack_of_central_idea": (
            "Thinking may lack a central idea."
        ),
        "pisces_bio_afflicted_lack_of_logic": "Thinking may lack logic.",
        "pisces_bio_afflicted_lack_of_structure": (
            "Thinking may lack structure."
        ),
        "pisces_bio_afflicted_lying_distortion": (
            "Communication may involve lying or distortion."
        ),
        "pisces_bio_afflicted_mystification": (
            "Communication may involve mystification."
        ),
        "pisces_bio_afflicted_suggestibility": (
            "May become highly suggestible."
        ),
        "pisces_bio_afflicted_unclear_speech": "Speech may become unclear.",
        "pisces_bio_afflicted_words_exceed_completed_actions": (
            "Words may greatly exceed completed actions or results."
        ),
        "pisces_bio_humanities_aptitude": (
            "May show aptitude for the humanities."
        ),
        "pisces_bio_languages_aptitude": (
            "May show aptitude for languages."
        ),
        "pisces_bio_learning_emotional_psychological_attunement": (
            "Learning through emotional or psychological attunement with real "
            "people."
        ),
        "pisces_bio_learning_youtube_content_video": (
            "Learning can happen through YouTube or other video content."
        ),
        "pisces_bio_lose_grip_on_factual_reality": (
            "Thinking or learning can lose touch with factual reality."
        ),
        "pisces_bio_loses_disputes_insufficient_assertiveness": (
            "May often lose disputes because of insufficient assertiveness or "
            "forcefulness."
        ),
        "pisces_bio_lyrical_talent": "May show lyrical talent.",
        "pisces_bio_memory_range_chart_context": (
            "Memory may range from exceptional to very poor depending on chart "
            "context."
        ),
        "pisces_bio_motivation_emotional_atmosphere": (
            "Learning may be motivated by emotional atmosphere."
        ),
        "pisces_bio_motivation_kindred_people": (
            "Learning may be motivated by a sense of being among intellectually "
            "or emotionally kindred people."
        ),
        "pisces_bio_motivation_mystery": (
            "Learning may be motivated by mystery."
        ),
        "pisces_bio_motivation_mystico_psychological_engagement": (
            "Learning may be motivated by emotionally engaging mystical or "
            "psychological material."
        ),
        "pisces_bio_poetic_talent": "May show poetic talent.",
        "pisces_l7_captivity_in_illusions": (
            "May become caught in illusions."
        ),
        "pisces_l7_compressed_crumpled_speech": (
            "Speech may become compressed or disjointed."
        ),
        "pisces_l7_dev_alternate_speech_with_silence": (
            "Growth area: alternate speech flow with conscious silence."
        ),
        "pisces_l7_dev_formulate_central_idea": (
            "Growth area: formulate the central idea."
        ),
        "pisces_l7_exceptionally_strong_imagination": (
            "May show exceptionally strong imagination."
        ),
        "pisces_l7_learning_absorbing_overall_impression": (
            "Learning by absorbing or forming an overall impression."
        ),
        "pisces_l7_manipulation_susceptibility": (
            "May be susceptible to manipulation."
        ),
        "pisces_l7_nonobvious_logic": (
            "Logic may be difficult to comprehend or non-obvious."
        ),
        "pisces_l7_sensitivity_to_hidden_intonation": (
            "Sensitivity to hidden or underlying intonation."
        ),
        "pisces_l7_soulful_communication": (
            "Soulful or emotionally attuned communication."
        ),
        "pisces_l7_suggestibility": "May be suggestible.",
        "pisces_l7_words_can_diverge_from_reality": (
            "Words can diverge from reality."
        ),
    }

    S49B_PISCES_NEEDS_REVIEW: tuple[str, ...] = (
        "pisces_bio_minor_exile",
        "pisces_bio_universal_cosmic_intellect_synthesis",
        "pisces_bio_unusually_strong_intuition",
        "pisces_l7_high_intuition",
        "pisces_l7_correct_decisions_nonrational_routes",
        "pisces_l7_mystical_thinking",
    )

    S49B_ARIES_APPROVED_RAW: tuple[str, ...] = (
        "aries_bio_learns_through_disputes",
        "aries_bio_learns_through_practical_implementation",
        "aries_bio_monologue_communication",
        "aries_bio_strong_through_speed_not_depth",
        "aries_bio_strong_through_speed_not_endurance",
        "aries_bio_tends_not_to_hear_others",
        "aries_l7_communication_as_polemics",
        "aries_l7_detects_logic_weak_points",
        "aries_l7_difficult_to_reach_through_dialogue",
        "aries_l7_difficulty_hearing_others",
        "aries_l7_env_contacts_impulsive",
        "aries_l7_env_sees_opponent_in_others",
        "aries_l7_env_sibling_argumentative",
        "aries_l7_env_sibling_competitive",
        "aries_l7_fast_thinking",
        "aries_l7_hurried_thinking",
        "aries_l7_inattentive_thinking",
        "aries_l7_mediation_difficult",
        "aries_l7_ordinary_communication_becomes_argument",
        "aries_l7_perceives_interlocutors_as_opponents",
        "aries_l7_primarily_hears_self",
        "aries_l7_questioner_and_answerer",
        "aries_l7_ready_answer",
        "aries_l7_repeats_own_position",
        "aries_l7_retains_existing_formulation",
        "aries_l7_risk_haste_errors",
    )

    S49B_ARIES_OVERRIDES: dict[str, str] = {
        "aries_bio_ability_to_argue": (
            "May show an ability or tendency to argue."
        ),
        "aries_bio_engineering_ability": (
            "May show engineering ability or potential."
        ),
        "aries_bio_learns_through_trial_and_error": (
            "Learns through trial and error."
        ),
        "aries_bio_legal_ability": (
            "May show legal ability or potential."
        ),
        "aries_bio_martian_speed_coloring": (
            "Thinking, communication, and learning may be colored by speed and "
            "urgency."
        ),
        "aries_bio_motivation_challenge": (
            "Learning may be motivated by challenge."
        ),
        "aries_bio_motivation_contest_challenge": (
            "Learning may be motivated by being challenged to a fight or contest."
        ),
        "aries_bio_motivation_obstacle": (
            "Learning may be motivated by an obstacle."
        ),
        "aries_bio_oratory_ability": (
            "May show oratory ability or potential."
        ),
        "aries_bio_sales_ability": (
            "May show sales ability or potential."
        ),
        "aries_bio_technical_practicality": (
            "Thinking and learning may be practical and technically oriented."
        ),
        "aries_bio_vocal_ability": (
            "May show vocal ability or potential."
        ),
        "aries_l7_dev_listen_without_interrupting": (
            "Growth area: listen without interrupting."
        ),
        "aries_l7_dev_pause_before_forms": (
            "Growth area: pause before filling documents or forms."
        ),
        "aries_l7_dev_slow_down_before_answering": (
            "Growth area: slow down before answering."
        ),
        "aries_l7_dev_verify_dates": "Growth area: verify dates.",
        "aries_l7_dev_verify_facts": "Growth area: verify facts.",
        "aries_l7_learn_via_arguing": "Arguing supports learning.",
        "aries_l7_learn_via_competition": "Competition supports learning.",
        "aries_l7_learn_via_immediate_application": (
            "Immediate real-life application of knowledge supports learning."
        ),
        "aries_l7_learn_via_practice": "Practice supports learning.",
        "aries_l7_learn_via_proving": (
            "Trying to prove a point can support learning."
        ),
        "aries_l7_may_disregard_facts_vs_theory": (
            "May disregard facts when they do not fit an existing theory."
        ),
        "aries_l7_risk_not_hearing_other_viewpoint": (
            "May have difficulty hearing another point of view while learning."
        ),
    }

    def test_pisces_family_fully_reviewed(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "sign:Pisces")
        self.assertEqual(family.total_facts, 71)
        self.assertEqual(family.approved_override, 36)
        self.assertEqual(family.approved_raw, 29)
        self.assertEqual(family.needs_review, 6)
        self.assertEqual(family.unreviewed, 0)
        self.assertEqual(family.reviewed_count, 71)
        self.assertEqual(family.presentation_ready_count, 65)
        self.assertEqual(family.review_coverage, 1.0)
        self.assertEqual(family.presentation_ready_coverage, round(65 / 71, 6))

    def test_aries_family_fully_reviewed(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "sign:Aries")
        self.assertEqual(family.total_facts, 51)
        self.assertEqual(family.approved_override, 24)
        self.assertEqual(family.approved_raw, 26)
        self.assertEqual(family.needs_review, 1)
        self.assertEqual(family.unreviewed, 0)
        self.assertEqual(family.reviewed_count, 51)
        self.assertEqual(family.presentation_ready_count, 50)
        self.assertEqual(family.review_coverage, 1.0)
        self.assertEqual(family.presentation_ready_coverage, round(50 / 51, 6))

    def test_s49b_registries_and_wording_corrections(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        self.assertEqual(len(self.S49B_PISCES_APPROVED_RAW), 29)
        self.assertEqual(len(self.S49B_PISCES_OVERRIDES), 35)
        self.assertEqual(len(self.S49B_PISCES_NEEDS_REVIEW), 6)
        self.assertEqual(len(self.S49B_ARIES_APPROVED_RAW), 26)
        self.assertEqual(len(self.S49B_ARIES_OVERRIDES), 24)
        for fact_id in (
            *self.S49B_PISCES_APPROVED_RAW,
            *self.S49B_ARIES_APPROVED_RAW,
        ):
            with self.subTest(raw=fact_id):
                self.assertIn(fact_id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(fact_id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_APPROVED_RAW)
                self.assertEqual(entry.human_text, entry.canonical_text)
        for fact_id, human in {
            **self.S49B_PISCES_OVERRIDES,
            **self.S49B_ARIES_OVERRIDES,
        }.items():
            with self.subTest(override=fact_id):
                self.assertEqual(HUMAN_COPY_OVERRIDES[fact_id], human)
                self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_APPROVED_OVERRIDE)
                self.assertEqual(entry.canonical_text, by_id[fact_id].text)
                self.assertNotEqual(entry.canonical_text, human)
        for fact_id in (
            *self.S49B_PISCES_NEEDS_REVIEW,
            "aries_bio_source_sexual_motivation_wording",
        ):
            with self.subTest(needs=fact_id):
                self.assertIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                self.assertNotIn(fact_id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_NEEDS_REVIEW)
                self.assertEqual(entry.human_text, entry.canonical_text)
        # Limited wording corrections exact; canonical unchanged.
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["pisces_bio_afflicted_crumpled_speech"],
            "Speech may become fragmented or poorly formed.",
        )
        self.assertIn("crumpled", by_id["pisces_bio_afflicted_crumpled_speech"].text)
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["pisces_bio_afflicted_information_chaos"],
            "Thinking can become contradictory and informationally chaotic.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["pisces_bio_humanities_aptitude"],
            "May show aptitude for the humanities.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["pisces_bio_learning_youtube_content_video"],
            "Learning can happen through YouTube or other video content.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["pisces_bio_lose_grip_on_factual_reality"],
            "Thinking or learning can lose touch with factual reality.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES[
                "pisces_bio_loses_disputes_insufficient_assertiveness"
            ],
            "May often lose disputes because of insufficient assertiveness or "
            "forcefulness.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES[
                "pisces_bio_motivation_mystico_psychological_engagement"
            ],
            "Learning may be motivated by emotionally engaging mystical or "
            "psychological material.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["pisces_l7_compressed_crumpled_speech"],
            "Speech may become compressed or disjointed.",
        )
        self.assertIn("crumpled", by_id["pisces_l7_compressed_crumpled_speech"].text)
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["aries_bio_technical_practicality"],
            "Thinking and learning may be practical and technically oriented.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["aries_l7_learn_via_proving"],
            "Trying to prove a point can support learning.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["aries_l7_risk_not_hearing_other_viewpoint"],
            "May have difficulty hearing another point of view while learning.",
        )
        self.assertNotIn(
            "aries_bio_source_sexual_motivation_wording",
            HUMAN_COPY_OVERRIDES,
        )
        self.assertEqual(len(NEEDS_REVIEW_FACT_IDS), 19)
        self.assertTrue(
            set(HUMAN_COPY_OVERRIDES).isdisjoint(APPROVED_RAW_FACT_IDS)
        )
        self.assertTrue(
            set(HUMAN_COPY_OVERRIDES).isdisjoint(NEEDS_REVIEW_FACT_IDS)
        )
        self.assertTrue(
            set(APPROVED_RAW_FACT_IDS).isdisjoint(NEEDS_REVIEW_FACT_IDS)
        )


class ScorpioLibraFamilyS410BTests(unittest.TestCase):
    S410B_SCORPIO_APPROVED_RAW: tuple[str, ...] = (
        "scorpio_bio_learning_group_discussion",
        "scorpio_bio_learning_independent_research",
        "scorpio_bio_quiet_calm_voice",
        "scorpio_bio_strong_memory",
        "scorpio_l7_ability_to_see_the_essence",
        "scorpio_l7_categorical_thinking",
        "scorpio_l7_caustic_speech",
        "scorpio_l7_detective_like_thinking",
        "scorpio_l7_env_hidden_sibling_tension",
        "scorpio_l7_env_sibling_competition",
        "scorpio_l7_env_sibling_verbal_jabs",
        "scorpio_l7_expects_listener_to_infer",
        "scorpio_l7_extraction_of_nonverbal_information",
        "scorpio_l7_fast_replies",
        "scorpio_l7_high_analytical_ability",
        "scorpio_l7_independent_learning",
        "scorpio_l7_many_probing_questions",
        "scorpio_l7_maximalist_thinking",
        "scorpio_l7_research_oriented_mind",
        "scorpio_l7_says_very_little_explicitly",
        "scorpio_l7_sharp_replies",
        "scorpio_l7_sticky_memory",
        "scorpio_l7_tendency_to_dig_to_core",
        "scorpio_l7_tense_communication",
        "scorpio_l7_verbal_jabs",
        "scorpio_l7_very_deep_memory",
    )

    S410B_SCORPIO_OVERRIDES: dict[str, str] = {
        "scorpio_bio_afflicted_causticity": "Communication may become caustic.",
        "scorpio_bio_afflicted_maximalism_in_evaluations": (
            "Evaluations can become maximalist."
        ),
        "scorpio_bio_afflicted_mockery_malicious_wit": (
            "Communication may involve mockery, malicious wit, or snide remarks."
        ),
        "scorpio_bio_afflicted_quarrelsome_verbal_conflict": (
            "Communication may become quarrelsome or verbally abusive."
        ),
        "scorpio_bio_analytical_aptitude": "May show analytical aptitude.",
        "scorpio_bio_authoritative_voice_effect": (
            "Voice may have an authoritative or commanding effect."
        ),
        "scorpio_bio_critic_aptitude": "May show critic aptitude.",
        "scorpio_bio_influence_people": "May tend to influence people.",
        "scorpio_bio_intuitive_deep_thinking": (
            "Deep thinking with an intuitive quality."
        ),
        "scorpio_bio_learning_criticizing_others_ideas": (
            "Learning through criticizing or dismantling other people's ideas."
        ),
        "scorpio_bio_motivation_challenge_prove": (
            "Learning may be motivated by a challenge to prove oneself."
        ),
        "scorpio_bio_motivation_curiosity": (
            "Learning may be motivated by curiosity."
        ),
        "scorpio_bio_motivation_influence_linked_info": (
            "Learning may be motivated by information linked to the possibility "
            "of influence."
        ),
        "scorpio_bio_motivation_money": "Learning may be motivated by money.",
        "scorpio_bio_occupation_associations": (
            "Occupational themes associated with this placement include "
            "management, entrepreneurship, and psychology; these are not career "
            "assignments."
        ),
        "scorpio_bio_pluto_colored_framing": (
            "Thinking, communication, and learning may be colored by intensity, "
            "depth, and transformation themes."
        ),
        "scorpio_bio_psychological_penetration": (
            "May probe psychological material deeply."
        ),
        "scorpio_bio_researcher_aptitude": "May show researcher aptitude.",
        "scorpio_bio_speak_through_secrets": (
            "May speak through secrets, leaving others to figure things out."
        ),
        "scorpio_bio_sticky_attention": (
            "Attention can be sticky or persistent."
        ),
        "scorpio_bio_technical_aptitude": "May show technical aptitude.",
        "scorpio_l7_argument_dispute_learning": (
            "Argument or dispute can support learning."
        ),
        "scorpio_l7_asking_questions_to_expose_essence": (
            "Asking questions to expose the essence supports learning."
        ),
        "scorpio_l7_deep_concepts": "Deep concepts support learning.",
        "scorpio_l7_depth": "Depth of thinking.",
        "scorpio_l7_destroy_to_understand": (
            "May deconstruct or take apart ideas in order to understand."
        ),
        "scorpio_l7_dev_awareness_of_causticity": (
            "Growth area: become more aware of caustic communication."
        ),
        "scorpio_l7_dev_awareness_of_criticality": (
            "Growth area: become more aware of a tendency toward criticism."
        ),
        "scorpio_l7_dev_finish_explain_thought": (
            "Growth area: finish and explain a thought instead of cutting it off "
            "with hints."
        ),
        "scorpio_l7_env_manipulation_source_claim": (
            "Close-environment communication may involve a tendency toward "
            "manipulation."
        ),
        "scorpio_l7_env_transformative_role": (
            "May play a transformative role in the close environment."
        ),
        "scorpio_l7_hints": "May communicate through hints.",
        "scorpio_l7_learn_dig_to_essence": (
            "Digging to the essence supports learning."
        ),
        "scorpio_l7_practice_learning": "Practice supports learning.",
        "scorpio_l7_quiet_environment": (
            "A quiet environment supports learning."
        ),
        "scorpio_l7_risk_maximalism_in_evaluations": (
            "May show maximalism in evaluations."
        ),
        "scorpio_l7_risk_sharp_judgments": "Judgments can become sharp.",
        "scorpio_l7_sensitivity_to_intuitive_impressions": (
            "May be sensitive to intuitive impressions."
        ),
        "scorpio_l7_vulnerability_error_detection": (
            "Detecting vulnerabilities or errors supports learning."
        ),
    }

    S410B_LIBRA_APPROVED_RAW: tuple[str, ...] = (
        "libra_bio_beautiful_handwriting",
        "libra_bio_beauty_of_words",
        "libra_bio_learning_books",
        "libra_bio_learning_contrasts",
        "libra_bio_learning_dialogue",
        "libra_l7_appeal_to_fairness",
        "libra_l7_assimilation_through_discussion",
        "libra_l7_delicate_communication",
        "libra_l7_difficulty_making_decisions",
        "libra_l7_env_search_for_common_language",
        "libra_l7_env_sibling_diplomacy",
        "libra_l7_env_sibling_dispute_avoidance",
        "libra_l7_env_tendency_to_form_relationships",
        "libra_l7_evaluates_via_aesthetic_beauty",
        "libra_l7_evaluates_via_completeness",
        "libra_l7_high_receptivity",
        "libra_l7_high_speed_of_comprehension",
        "libra_l7_information_synthesis",
        "libra_l7_learning_through_contradiction_comparison",
        "libra_l7_peaceful_communication",
        "libra_l7_says_what_interlocutor_wants",
        "libra_l7_skill_with_compliments",
        "libra_l7_view_issue_from_multiple_sides",
    )

    S410B_LIBRA_OVERRIDES: dict[str, str] = {
        "libra_bio_afflicted_absence_of_conclusions": (
            "Thinking may reach no clear conclusions."
        ),
        "libra_bio_afflicted_absence_of_position": (
            "May lack a clear position."
        ),
        "libra_bio_afflicted_excessively_sugary_communication": (
            "Communication may become overly sweet or artificially positive."
        ),
        "libra_bio_afflicted_intellectual_indecision": (
            "Thinking can become intellectually indecisive."
        ),
        "libra_bio_afflicted_lying_distortion": (
            "Communication may involve lying or distortion."
        ),
        "libra_bio_communicator_aptitude": (
            "May show aptitude for communication."
        ),
        "libra_bio_compliment_skill": "May show skill with compliments.",
        "libra_bio_compromise_skill": "May show skill with compromise.",
        "libra_bio_dialogue_skill": "May show skill in dialogue.",
        "libra_bio_humanities_aptitude": (
            "May show aptitude for the humanities."
        ),
        "libra_bio_interviewer_aptitude": (
            "May show aptitude for interviewing."
        ),
        "libra_bio_learning_two_sides": (
            "Learning through two sides or two aspects of a situation."
        ),
        "libra_bio_motivation_aesthetic_environment": (
            "Learning may be motivated by an aesthetically pleasing environment."
        ),
        "libra_bio_motivation_attractive_people": (
            "Learning may be motivated by attractive or aesthetic people."
        ),
        "libra_bio_motivation_attractive_subject": (
            "Learning may be motivated by an attractive subject or material."
        ),
        "libra_bio_motivation_establish_fairness": (
            "Learning may be motivated by the possibility of establishing "
            "fairness."
        ),
        "libra_bio_motivation_possibility_to_discuss": (
            "Learning may be motivated by opportunities for discussion."
        ),
        "libra_bio_occupation_associations": (
            "Occupational themes associated with this placement include "
            "presenting, consulting, law, and politics; these are not career "
            "assignments."
        ),
        "libra_bio_salesperson_aptitude": "May show sales aptitude.",
        "libra_bio_venusian_diplomacy_aesthetic_coloring": (
            "Thinking, communication, and learning may be colored by diplomacy "
            "and aesthetic quality."
        ),
        "libra_l7_conversational_adaptation": (
            "Conversational adaptation or chameleon-like adjustment."
        ),
        "libra_l7_endless_pros_cons_weighing": (
            "May weigh pros and cons endlessly."
        ),
        "libra_l7_env_consultant_smoothing_role": (
            "May take on a consulting or conflict-smoothing role in the close "
            "environment."
        ),
        "libra_l7_env_easy_quick_contact": (
            "Contact may form easily and quickly."
        ),
        "libra_l7_reluctance_to_take_one_side": (
            "May be reluctant or afraid to take one side."
        ),
        "libra_l7_risk_avoiding_dispute": "May avoid dispute.",
        "libra_l7_risk_serving_two_masters": (
            "May try to serve two opposing sides."
        ),
        "libra_l7_support_aesthetic_environment": (
            "An aesthetic learning environment supports learning."
        ),
        "libra_l7_support_books": "Books support learning.",
        "libra_l7_support_dialogue": "Dialogue supports learning.",
        "libra_l7_support_exchange_of_opinions": (
            "Exchange of opinions supports learning."
        ),
        "libra_l7_support_lectures": "Lectures support learning.",
        "libra_l7_support_live_peer": "A live peer supports learning.",
        "libra_l7_support_live_teacher": "A live teacher supports learning.",
        "libra_l7_support_peer_collaboration": (
            "Peer collaboration on difficult problems supports learning."
        ),
    }

    def test_scorpio_family_fully_reviewed_with_integrity(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "sign:Scorpio")
        self.assertEqual(family.total_facts, 66)
        self.assertEqual(family.approved_override, 39)
        self.assertEqual(family.approved_raw, 26)
        self.assertEqual(family.needs_review, 1)
        self.assertEqual(family.unreviewed, 0)
        self.assertEqual(
            family.approved_raw + family.approved_override + family.needs_review,
            66,
        )
        self.assertEqual(family.reviewed_count, 66)
        self.assertEqual(family.presentation_ready_count, 65)
        self.assertEqual(family.review_coverage, 1.0)
        self.assertEqual(family.presentation_ready_coverage, round(65 / 66, 6))
        entry = build_catalog_entry(
            next(f for f in ALL_SOURCE_FACTS if f.id == "scorpio_l7_categorical_thinking")
        )
        self.assertEqual(entry.review_status, STATUS_APPROVED_RAW)
        self.assertIn("scorpio_l7_categorical_thinking", APPROVED_RAW_FACT_IDS)
        self.assertNotIn("scorpio_l7_categorical_thinking", HUMAN_COPY_OVERRIDES)

    def test_libra_family_fully_reviewed(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "sign:Libra")
        self.assertEqual(family.total_facts, 58)
        self.assertEqual(family.approved_override, 35)
        self.assertEqual(family.approved_raw, 23)
        self.assertEqual(family.needs_review, 0)
        self.assertEqual(family.unreviewed, 0)
        self.assertEqual(family.reviewed_count, 58)
        self.assertEqual(family.presentation_ready_count, 58)
        self.assertEqual(family.review_coverage, 1.0)
        self.assertEqual(family.presentation_ready_coverage, 1.0)

    def test_s410b_registries_and_wording_corrections(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        self.assertEqual(len(self.S410B_SCORPIO_APPROVED_RAW), 26)
        self.assertEqual(len(self.S410B_SCORPIO_OVERRIDES), 39)
        self.assertEqual(len(self.S410B_LIBRA_APPROVED_RAW), 23)
        self.assertEqual(len(self.S410B_LIBRA_OVERRIDES), 35)
        for fact_id in (
            *self.S410B_SCORPIO_APPROVED_RAW,
            *self.S410B_LIBRA_APPROVED_RAW,
        ):
            with self.subTest(raw=fact_id):
                self.assertIn(fact_id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(fact_id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_APPROVED_RAW)
                self.assertEqual(entry.human_text, entry.canonical_text)
        for fact_id, human in {
            **self.S410B_SCORPIO_OVERRIDES,
            **self.S410B_LIBRA_OVERRIDES,
        }.items():
            with self.subTest(override=fact_id):
                self.assertEqual(HUMAN_COPY_OVERRIDES[fact_id], human)
                self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_APPROVED_OVERRIDE)
                self.assertEqual(entry.canonical_text, by_id[fact_id].text)
                self.assertNotEqual(entry.canonical_text, human)
        self.assertIn("scorpio_bio_source_sexual_motivation", NEEDS_REVIEW_FACT_IDS)
        self.assertNotIn("scorpio_bio_source_sexual_motivation", HUMAN_COPY_OVERRIDES)
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["scorpio_bio_psychological_penetration"],
            "May probe psychological material deeply.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["scorpio_l7_dev_awareness_of_causticity"],
            "Growth area: become more aware of caustic communication.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["scorpio_l7_dev_awareness_of_criticality"],
            "Growth area: become more aware of a tendency toward criticism.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES[
                "libra_bio_afflicted_excessively_sugary_communication"
            ],
            "Communication may become overly sweet or artificially positive.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["libra_bio_communicator_aptitude"],
            "May show aptitude for communication.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["libra_bio_interviewer_aptitude"],
            "May show aptitude for interviewing.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["libra_bio_motivation_possibility_to_discuss"],
            "Learning may be motivated by opportunities for discussion.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["libra_l7_env_consultant_smoothing_role"],
            "May take on a consulting or conflict-smoothing role in the close "
            "environment.",
        )
        self.assertIn(
            "psychological penetration",
            by_id["scorpio_bio_psychological_penetration"].text.lower(),
        )
        self.assertEqual(len(NEEDS_REVIEW_FACT_IDS), 19)
        self.assertTrue(
            set(HUMAN_COPY_OVERRIDES).isdisjoint(APPROVED_RAW_FACT_IDS)
        )
        self.assertTrue(
            set(HUMAN_COPY_OVERRIDES).isdisjoint(NEEDS_REVIEW_FACT_IDS)
        )
        self.assertTrue(
            set(APPROVED_RAW_FACT_IDS).isdisjoint(NEEDS_REVIEW_FACT_IDS)
        )


class CancerVirgoFamilyS411BTests(unittest.TestCase):
    S411B_CANCER_APPROVED_RAW: tuple[str, ...] = (
        "cancer_bio_also_accepts_books",
        "cancer_bio_attachment_to_classics_opinions",
        "cancer_bio_attachment_to_parents_opinions",
        "cancer_bio_image_based_emotional_memory",
        "cancer_bio_learns_through_audio",
        "cancer_bio_learns_through_impressions",
        "cancer_bio_learns_through_lectures",
        "cancer_bio_learns_through_video",
        "cancer_bio_living_image_in_web_of_facts",
        "cancer_bio_may_lose_debates_lacking_force",
        "cancer_bio_speech_may_be_unstable",
        "cancer_l7_deep_associative_connections",
        "cancer_l7_env_authorities_important",
        "cancer_l7_env_emotional_attachment_siblings",
        "cancer_l7_env_traditions_important",
        "cancer_l7_excellent_imagination",
        "cancer_l7_good_improvisation",
        "cancer_l7_intuitive_args_hard_to_explain",
        "cancer_l7_learning_through_authorities",
        "cancer_l7_learning_through_traditions",
        "cancer_l7_mind_attached_to_past",
        "cancer_l7_need_emotional_feedback",
        "cancer_l7_risk_difficulty_concentrating",
        "cancer_l7_risk_emotionality_interferes_learning",
        "cancer_l7_risk_mental_drifting",
        "cancer_l7_sensitivity_to_dialogue_atmosphere",
        "cancer_l7_speech_can_become_tangled",
        "cancer_l7_speech_expresses_emotion",
        "cancer_l7_sticky_memory_emotions",
        "cancer_l7_sticky_memory_images",
        "cancer_l7_sticky_memory_smells",
        "cancer_l7_thought_hard_to_express",
    )

    S411B_CANCER_FROZEN_OVERRIDES: tuple[str, ...] = (
        "cancer_bio_afflicted_disregard_for_facts",
        "cancer_bio_afflicted_everyday_momentary_thinking",
        "cancer_bio_afflicted_habit_bound_momentary_reasoning",
        "cancer_bio_afflicted_losing_central_meaning",
        "cancer_bio_afflicted_losing_the_thread",
        "cancer_bio_afflicted_scatter_distractibility",
        "cancer_bio_afflicted_thinking_trapped_by_habits",
        "cancer_bio_afflicted_thinking_trapped_by_outdated_beliefs",
        "cancer_bio_afflicted_loss_of_focus",
    )

    S411B_CANCER_NEW_OVERRIDES: dict[str, str] = {
        "cancer_bio_can_be_hurt_in_communication": (
            "May be hurt or offended in communication."
        ),
        "cancer_bio_can_be_knocked_off_balance_in_speech": (
            "May be knocked off balance or confused in speech."
        ),
        "cancer_bio_communication_colored_by_emotionality": (
            "Communication may be colored by emotionality."
        ),
        "cancer_bio_depth_substantive_nature": "May show depth and substance.",
        "cancer_bio_humanities_aptitude": (
            "May show aptitude for the humanities."
        ),
        "cancer_bio_learning_colored_by_emotionality": (
            "Learning may be colored by emotionality."
        ),
        "cancer_bio_learns_around_familiar_people": (
            "Learns well around familiar or close people."
        ),
        "cancer_bio_motivation_comfortable_environment": (
            "Learning may be motivated by a comfortable environment."
        ),
        "cancer_bio_motivation_familiar_group": (
            "Learning may be motivated by a familiar group."
        ),
        "cancer_bio_motivation_favorite_teacher": (
            "Learning may be motivated when facts are connected to a favorite "
            "or respected teacher."
        ),
        "cancer_bio_motivation_strong_emotion": (
            "Learning may be motivated by strong emotion."
        ),
        "cancer_bio_motivation_tradition": (
            "Learning may be motivated by tradition."
        ),
        "cancer_bio_notice_rhyme": "May notice rhyme.",
        "cancer_bio_notice_subtext": "May notice subtext.",
        "cancer_bio_psychologically_dissect_texts": (
            "May analyze texts from a psychological perspective."
        ),
        "cancer_bio_see_hidden_meaning": "May see hidden meaning.",
        "cancer_bio_storyteller_talent": (
            "May show storyteller talent or potential."
        ),
        "cancer_bio_thinking_colored_by_emotionality": (
            "Thinking may be colored by emotionality."
        ),
        "cancer_bio_writer_association": (
            "May show writing aptitude or potential."
        ),
        "cancer_l7_arguments_arise_intuitively": (
            "Arguments may arise intuitively."
        ),
        "cancer_l7_dev_avoid_stuck_in_details": (
            "Growth area: avoid getting stuck in details."
        ),
        "cancer_l7_dev_retain_central_idea": (
            "Growth area: retain the central idea."
        ),
        "cancer_l7_dev_separate_emotion_from_argument": (
            "Growth area: separate emotion from rational argument."
        ),
        "cancer_l7_dev_structured_speech_training": (
            "Growth area: practice structuring speech."
        ),
        "cancer_l7_dev_subjectivity_risk": "Subjectivity can become a risk.",
        "cancer_l7_env_narrow_pleasant_circle": (
            "May keep a narrow circle of people found pleasant."
        ),
        "cancer_l7_env_possible_social_withdrawal": (
            "May withdraw socially in connection with sensitivity or "
            "vulnerability."
        ),
        "cancer_l7_learn_comfortable_environment": (
            "A comfortable, gentle environment supports learning."
        ),
        "cancer_l7_learn_small_segments": (
            "Dividing information into small pieces or segments supports "
            "learning."
        ),
        "cancer_l7_searches_for_roots": (
            "May search for the roots or origin of an idea."
        ),
        "cancer_l7_viewpoint_depends_on_tastes": (
            "Viewpoint may depend on tastes, views, or habits."
        ),
    }

    S411B_CANCER_NEEDS_REVIEW: tuple[str, ...] = (
        "cancer_bio_depends_on_moon_sign",
        "cancer_bio_emotional_intelligence_source_claim",
    )

    S411B_VIRGO_APPROVED_RAW: tuple[str, ...] = (
        "virgo_bio_deliberately_correct_speech",
        "virgo_bio_grounded_thinking",
        "virgo_bio_independent_analysis_learning",
        "virgo_bio_learning_on_the_fly",
        "virgo_bio_strong_attention",
        "virgo_bio_strong_erudition",
        "virgo_l7_analytical_thinking",
        "virgo_l7_dispersion_into_small_details",
        "virgo_l7_env_limited_social_circle",
        "virgo_l7_env_low_emotionality_siblings",
        "virgo_l7_limited_contact_circle",
        "virgo_l7_practical_learning",
        "virgo_l7_precision_of_formulations",
        "virgo_l7_selective_thinking",
        "virgo_l7_strong_tactical_thinking",
        "virgo_l7_strongest_logic_after_preparation",
        "virgo_l7_tendency_to_clarify_details",
        "virgo_l7_weaker_strategic_overview",
    )

    S411B_VIRGO_OVERRIDES: dict[str, str] = {
        "virgo_bio_afflicted_cannot_see_forest_for_trees": (
            "May lose sight of the forest for the trees."
        ),
        "virgo_bio_afflicted_collecting_facts_without_central_idea": (
            "May collect facts without a central idea."
        ),
        "virgo_bio_afflicted_collecting_facts_without_conclusion": (
            "May collect facts without reaching a conclusion."
        ),
        "virgo_bio_afflicted_pettiness": (
            "Thinking or communication may become petty."
        ),
        "virgo_bio_afflicted_tediousness": (
            "Thinking or communication may become tedious."
        ),
        "virgo_bio_high_mastery_of_words": (
            "May show potential for very high mastery of words."
        ),
        "virgo_bio_legal_aptitude": "May show legal aptitude.",
        "virgo_bio_less_accumulation_for_its_own_sake": (
            "Learning merely for the sake of accumulating knowledge is "
            "described as less characteristic."
        ),
        "virgo_bio_literary_aptitude": "May show literary aptitude.",
        "virgo_bio_motivation_curiosity": (
            "Learning may be motivated by curiosity."
        ),
        "virgo_bio_motivation_practical_usefulness": (
            "Learning may be motivated by practical usefulness."
        ),
        "virgo_bio_occupation_associations": (
            "Occupational themes associated with this placement include "
            "writers, scientists, officials, and backstage negotiators; "
            "these are not career assignments."
        ),
        "virgo_bio_skill_operating_facts": (
            "May be skilled at working with facts."
        ),
        "virgo_bio_somewhat_dry_thinking_learning": (
            "Thinking and learning may be somewhat dry."
        ),
        "virgo_bio_speech_lacks_expressive_zest": (
            "Speech may lack expressive flair."
        ),
        "virgo_bio_sticky_strong_memory": "Sticky or strong memory.",
        "virgo_bio_strongly_articulated_wording": (
            "Strongly articulated or stamped wording."
        ),
        "virgo_bio_technical_aptitude": "May show technical aptitude.",
        "virgo_bio_writing_aptitude": "May show writing aptitude.",
        "virgo_l7_dev_avoid_micromanagement": (
            "Growth area: avoid micromanagement."
        ),
        "virgo_l7_dev_build_schemes": "Growth area: build schemes.",
        "virgo_l7_dev_construct_methodology": (
            "Growth area: develop a methodology."
        ),
        "virgo_l7_dev_put_each_detail_in_place": (
            "Growth area: put each detail into its place."
        ),
        "virgo_l7_dev_remove_unnecessary": (
            "Growth area: remove unnecessary elements."
        ),
        "virgo_l7_diary_recording_tendency": (
            "May have a tendency to keep a diary or records."
        ),
        "virgo_l7_emotionally_cool": (
            "May be emotionally cool or not easily moved by emotion."
        ),
        "virgo_l7_env_connections_from_duty": (
            "May maintain connections from duty or propriety."
        ),
        "virgo_l7_env_practical_sibling_communication": (
            "Practical or useful communication with siblings."
        ),
        "virgo_l7_fixation_on_everyday_details": (
            "May fixate on everyday or routine details."
        ),
        "virgo_l7_learning_algorithms": "Algorithms support learning.",
        "virgo_l7_learning_compile_others_opinions": (
            "Compiling other people's opinions supports learning."
        ),
        "virgo_l7_learning_notes": "Notes support learning.",
        "virgo_l7_learning_schemes": "Schemes support learning.",
        "virgo_l7_learning_tables": "Tables support learning.",
        "virgo_l7_observation_keeping": "May keep observations.",
        "virgo_l7_proper_intonation": "Proper or correct intonation.",
        "virgo_l7_risk_losing_whole_picture": (
            "May lose the whole picture because of details."
        ),
        "virgo_l7_risk_routine_fixation": "May become fixated on routine.",
        "virgo_l7_selects_significant_arguments": (
            "May identify or select significant arguments."
        ),
        "virgo_l7_simple_direct_communication": (
            "Simple or direct communication style."
        ),
        "virgo_l7_statistics_tracking": "May track statistics.",
    }

    def test_cancer_family_fully_reviewed(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "sign:Cancer")
        self.assertEqual(family.total_facts, 74)
        self.assertEqual(family.approved_override, 40)
        self.assertEqual(family.approved_raw, 32)
        self.assertEqual(family.needs_review, 2)
        self.assertEqual(family.unreviewed, 0)
        self.assertEqual(family.reviewed_count, 74)
        self.assertEqual(family.presentation_ready_count, 72)
        self.assertEqual(family.review_coverage, 1.0)
        self.assertEqual(family.presentation_ready_coverage, round(72 / 74, 6))

    def test_virgo_family_fully_reviewed(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "sign:Virgo")
        self.assertEqual(family.total_facts, 60)
        self.assertEqual(family.approved_override, 41)
        self.assertEqual(family.approved_raw, 18)
        self.assertEqual(family.needs_review, 1)
        self.assertEqual(family.unreviewed, 0)
        self.assertEqual(family.reviewed_count, 60)
        self.assertEqual(family.presentation_ready_count, 59)
        self.assertEqual(family.review_coverage, 1.0)
        self.assertEqual(family.presentation_ready_coverage, round(59 / 60, 6))

    def test_sign_layer_complete_after_s411b(self):
        from app.services.mercury_human_copy_catalog import build_sign_review_queue

        queue = build_sign_review_queue()
        self.assertEqual(queue.review_complete_family_count, 12)
        self.assertEqual(queue.presentation_ready_complete_family_count, 4)
        self.assertEqual(list(queue.incomplete_queue), [])
        self.assertEqual(list(queue.suggested_batches), [])
        self.assertEqual(queue.sign_total_facts, 730)
        self.assertEqual(queue.sign_reviewed_facts, 730)
        self.assertEqual(queue.sign_unreviewed_facts, 0)
        self.assertEqual(queue.sign_presentation_ready_facts, 711)
        self.assertEqual(queue.sign_needs_review_facts, 19)
        ready_complete = {
            e.sign_name
            for e in queue.all_sign_families
            if e.is_presentation_ready_complete
        }
        self.assertEqual(ready_complete, {"Taurus", "Capricorn", "Leo", "Libra"})

    def test_s411b_registries_and_wording_corrections(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        self.assertEqual(len(self.S411B_CANCER_APPROVED_RAW), 32)
        self.assertEqual(len(self.S411B_CANCER_NEW_OVERRIDES), 31)
        self.assertEqual(len(self.S411B_CANCER_FROZEN_OVERRIDES), 9)
        self.assertEqual(len(self.S411B_VIRGO_APPROVED_RAW), 18)
        self.assertEqual(len(self.S411B_VIRGO_OVERRIDES), 41)
        for fact_id in (
            *self.S411B_CANCER_APPROVED_RAW,
            *self.S411B_VIRGO_APPROVED_RAW,
        ):
            with self.subTest(raw=fact_id):
                self.assertIn(fact_id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(fact_id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_APPROVED_RAW)
                self.assertEqual(entry.human_text, entry.canonical_text)
        for fact_id, human in {
            **self.S411B_CANCER_NEW_OVERRIDES,
            **self.S411B_VIRGO_OVERRIDES,
        }.items():
            with self.subTest(override=fact_id):
                self.assertEqual(HUMAN_COPY_OVERRIDES[fact_id], human)
                self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_APPROVED_OVERRIDE)
                self.assertEqual(entry.canonical_text, by_id[fact_id].text)
                self.assertNotEqual(entry.canonical_text, human)
        for fact_id in self.S411B_CANCER_FROZEN_OVERRIDES:
            with self.subTest(frozen=fact_id):
                self.assertIn(fact_id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
        for fact_id in (
            *self.S411B_CANCER_NEEDS_REVIEW,
            "virgo_bio_minor_domicile_near_sync",
        ):
            with self.subTest(needs=fact_id):
                self.assertIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                self.assertNotIn(fact_id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_NEEDS_REVIEW)
                self.assertEqual(entry.human_text, entry.canonical_text)
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["cancer_bio_depth_substantive_nature"],
            "May show depth and substance.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["cancer_bio_motivation_favorite_teacher"],
            "Learning may be motivated when facts are connected to a favorite "
            "or respected teacher.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["cancer_bio_psychologically_dissect_texts"],
            "May analyze texts from a psychological perspective.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["cancer_l7_dev_structured_speech_training"],
            "Growth area: practice structuring speech.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["cancer_l7_learn_comfortable_environment"],
            "A comfortable, gentle environment supports learning.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["virgo_bio_less_accumulation_for_its_own_sake"],
            "Learning merely for the sake of accumulating knowledge is "
            "described as less characteristic.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["virgo_bio_skill_operating_facts"],
            "May be skilled at working with facts.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["virgo_bio_speech_lacks_expressive_zest"],
            "Speech may lack expressive flair.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["virgo_l7_diary_recording_tendency"],
            "May have a tendency to keep a diary or records.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["virgo_l7_emotionally_cool"],
            "May be emotionally cool or not easily moved by emotion.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["virgo_l7_dev_construct_methodology"],
            "Growth area: develop a methodology.",
        )
        # Sticky emotional memories stay approved_raw (not generic strong_memory).
        for sticky_id in (
            "cancer_l7_sticky_memory_emotions",
            "cancer_l7_sticky_memory_images",
            "cancer_l7_sticky_memory_smells",
        ):
            self.assertIn(sticky_id, APPROVED_RAW_FACT_IDS)
            self.assertNotIn(sticky_id, HUMAN_COPY_OVERRIDES)
        self.assertIn("Gemini", by_id["virgo_bio_less_accumulation_for_its_own_sake"].text)
        self.assertEqual(len(NEEDS_REVIEW_FACT_IDS), 19)
        self.assertEqual(len(HUMAN_COPY_OVERRIDES), 397)
        self.assertEqual(len(APPROVED_RAW_FACT_IDS), 338)
        self.assertTrue(
            set(HUMAN_COPY_OVERRIDES).isdisjoint(APPROVED_RAW_FACT_IDS)
        )
        self.assertTrue(
            set(HUMAN_COPY_OVERRIDES).isdisjoint(NEEDS_REVIEW_FACT_IDS)
        )
        self.assertTrue(
            set(APPROVED_RAW_FACT_IDS).isdisjoint(NEEDS_REVIEW_FACT_IDS)
        )


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
