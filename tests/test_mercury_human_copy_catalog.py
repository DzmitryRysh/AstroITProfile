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
        self.assertEqual(len(APPROVED_RAW_FACT_IDS), 120)
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
        self.assertEqual(set(S44B_SAGITTARIUS_NEEDS_REVIEW), set(NEEDS_REVIEW_FACT_IDS))
        self.assertEqual(len(NEEDS_REVIEW_FACT_IDS), 3)
        for fact_id in S44B_SAGITTARIUS_NEEDS_REVIEW:
            with self.subTest(fact_id=fact_id):
                self.assertNotIn(fact_id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_NEEDS_REVIEW)
                self.assertFalse(entry.uses_override)
                self.assertEqual(entry.human_text, entry.canonical_text)

    def test_global_totals_after_s47b(self):
        report = build_human_copy_catalog()
        self.assertEqual(report.total_facts, 1590)
        self.assertEqual(report.approved_override_count, 139)
        self.assertEqual(report.approved_raw_count, 120)
        self.assertEqual(report.needs_review_count, 3)
        self.assertEqual(report.unreviewed_count, 1328)
        self.assertEqual(
            report.approved_override_count
            + report.approved_raw_count
            + report.needs_review_count
            + report.unreviewed_count,
            1590,
        )
        self.assertEqual(report.reviewed_count, 262)
        self.assertEqual(report.presentation_ready_count, 259)


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
        # No polarity/orb/astrology weighting fields exist on the priority key.
        sample_key = _sign_review_priority_key(ordered[0])
        self.assertEqual(len(sample_key), 4)
        self.assertIsInstance(sample_key[0], int)
        self.assertIsInstance(sample_key[1], int)
        self.assertIsInstance(sample_key[2], float)
        self.assertIsInstance(sample_key[3], str)

    def test_queue_priority_order_incomplete_signs(self):
        from app.services.mercury_human_copy_catalog import build_sign_review_queue

        queue = build_sign_review_queue()
        self.assertEqual(
            [entry.sign_name for entry in queue.incomplete_queue],
            [
                "Aquarius",
                "Pisces",
                "Scorpio",
                "Cancer",
                "Virgo",
                "Libra",
                "Aries",
                "Gemini",
            ],
        )
        completed = {entry.sign_name for entry in queue.completed_families}
        self.assertEqual(
            completed,
            {"Taurus", "Sagittarius", "Capricorn", "Leo"},
        )

    def test_suggested_batches_heaviest_lightest_partition(self):
        from app.services.mercury_human_copy_catalog import build_sign_review_queue

        queue = build_sign_review_queue()
        incomplete_keys = [entry.family_key for entry in queue.incomplete_queue]
        completed_keys = {entry.family_key for entry in queue.completed_families}
        self.assertNotIn("sign:Capricorn", incomplete_keys)
        self.assertNotIn("sign:Leo", incomplete_keys)
        self.assertIn("sign:Capricorn", completed_keys)
        self.assertIn("sign:Leo", completed_keys)
        batch_keys: list[str] = []
        for batch in queue.suggested_batches:
            self.assertGreaterEqual(len(batch.family_keys), 1)
            self.assertLessEqual(len(batch.family_keys), 2)
            for key in batch.family_keys:
                self.assertIn(key, incomplete_keys)
                self.assertNotIn(key, completed_keys)
                self.assertNotIn(key, batch_keys)
                batch_keys.append(key)
        self.assertEqual(sorted(batch_keys), sorted(incomplete_keys))
        self.assertEqual(len(batch_keys), len(set(batch_keys)))
        # Deterministic heaviest+lightest against CURRENT incomplete queue.
        remaining = list(queue.incomplete_queue)
        expected_names: list[tuple[str, ...]] = []
        expected_workloads: list[int] = []
        while remaining:
            if len(remaining) == 1:
                only = remaining.pop(0)
                expected_names.append((only.sign_name,))
                expected_workloads.append(only.unreviewed)
                break
            heavy = remaining.pop(0)
            light = remaining.pop(-1)
            expected_names.append((heavy.sign_name, light.sign_name))
            expected_workloads.append(heavy.unreviewed + light.unreviewed)
        self.assertEqual(
            [batch.sign_names for batch in queue.suggested_batches],
            expected_names,
        )
        self.assertEqual(
            [batch.unreviewed_workload for batch in queue.suggested_batches],
            expected_workloads,
        )
        by_name = {entry.sign_name: entry for entry in queue.incomplete_queue}
        expected_recommended = []
        for names in expected_names:
            expected_recommended.append(
                sum(by_name[name].review_recommended_unreviewed for name in names)
            )
        self.assertEqual(
            [batch.review_recommended_workload for batch in queue.suggested_batches],
            expected_recommended,
        )

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

    def test_needs_review_backlog_contains_sagittarius_three(self):
        from app.services.mercury_human_copy_catalog import build_sign_review_queue

        queue = build_sign_review_queue()
        backlog_ids = {item.fact_id for item in queue.needs_review_backlog}
        self.assertEqual(
            backlog_ids,
            {
                "sag_bio_impartiality_disrupted",
                "sag_bio_learnability_disrupted",
                "sag_bio_major_exile",
            },
        )
        for item in queue.needs_review_backlog:
            self.assertEqual(item.family_key, "sign:Sagittarius")
            self.assertTrue(item.canonical_text)

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
        self.assertEqual(queue.review_complete_family_count, 4)
        self.assertEqual(queue.presentation_ready_complete_family_count, 3)
        self.assertEqual(len(queue.incomplete_queue), 8)


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
        self.assertEqual(
            set(NEEDS_REVIEW_FACT_IDS),
            {
                "sag_bio_impartiality_disrupted",
                "sag_bio_learnability_disrupted",
                "sag_bio_major_exile",
            },
        )
        # Capricorn common-sense approval is ID-local; Taurus twin stays raw.
        self.assertIn("capricorn_l7_common_sense_reliance", APPROVED_RAW_FACT_IDS)
        self.assertIn("taurus_relies_on_common_sense", APPROVED_RAW_FACT_IDS)
        self.assertNotIn("capricorn_l7_common_sense_reliance", HUMAN_COPY_OVERRIDES)


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
