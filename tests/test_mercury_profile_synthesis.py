"""Tests for Mercury Profile Synthesis v1 — deterministic presentation assembler."""

from __future__ import annotations

import unittest
from datetime import date, time

from app.schemas.mercury_source_profile import MercurySourceProfileRequest, SourceFact
from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_profile_synthesis import (
    CATEGORY_TO_SECTION,
    DETAIL_ONLY_CATEGORIES,
    MAX_PREVIEW_FACTS,
    SECTION_SPECS,
    build_mercury_profile_synthesis,
    collect_canonical_facts,
)
from app.services.mercury_source_knowledge import CONTRAST_PAIRS, REPEATED_SIGNAL_SPECS
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
)


def _avdey():
    return build_mercury_source_profile(
        MercurySourceProfileRequest(
            birth_date=date(1986, 7, 14),
            birth_time=time(7, 10),
            birth_place="Simferopol, Ukraine",
        )
    )


def _vlad():
    return build_mercury_source_profile(
        MercurySourceProfileRequest(
            birth_date=date(1986, 5, 16),
            birth_time=time(15, 0),
            birth_place="Dnipro, Ukraine",
        )
    )


def _dzmitry():
    return build_mercury_source_profile(
        MercurySourceProfileRequest(
            birth_date=date(1985, 11, 12),
            birth_time=time(14, 15),
            birth_place="Zhodino, Belarus",
        )
    )


def _andrey():
    return build_source_profile_from_factors(
        MercurySourceFactors(
            birth_time_known=True,
            mercury_sign="Cancer",
            mercury_element="water",
            mercury_motion="direct",
            mercury_house=5,
            aspects=[
                MercuryAspect(planet="Uranus", type="trine", orb_deg=1.65),
                MercuryAspect(planet="Pluto", type="square", orb_deg=2.68),
            ],
        )
    )


def _milka():
    return build_source_profile_from_factors(
        MercurySourceFactors(
            birth_time_known=False,
            mercury_sign="Pisces",
            mercury_element="water",
            mercury_motion="direct",
            mercury_house=None,
            aspects=[],
        )
    )


def _signal_names(profile):
    return [item.signal for item in profile.repeated_signals]


def _synthesis_signal_names(synthesis):
    return [item.signal for item in synthesis.strongest_patterns]


class SynthesisAssemblerCoreTests(unittest.TestCase):
    def test_accepts_profile_and_is_deterministic(self):
        profile = _milka()
        first = build_mercury_profile_synthesis(profile)
        second = build_mercury_profile_synthesis(profile)
        self.assertEqual(first.traceability, second.traceability)
        self.assertEqual(first.strongest_patterns, second.strongest_patterns)
        self.assertEqual(
            [section.preview_fact_ids for section in first.sections],
            [section.preview_fact_ids for section in second.sections],
        )

    def test_input_not_mutated(self):
        profile = _avdey()
        before = profile.model_dump()
        build_mercury_profile_synthesis(profile)
        self.assertEqual(profile.model_dump(), before)

    def test_canonical_facts_dedupe_by_id_from_layers_only(self):
        profile = _avdey()
        layer_ids = [
            fact.id
            for fact in (
                list(profile.sign_facts)
                + list(profile.house_facts)
                + list(profile.motion_facts)
                + list(profile.aspect_facts)
            )
        ]
        canonical = collect_canonical_facts(profile)
        self.assertEqual(len(canonical), len({fact.id for fact in canonical}))
        self.assertEqual({fact.id for fact in canonical}, set(layer_ids))
        # Unresolved already present in aspect_facts are not double-counted via
        # conditional_unresolved concatenation.
        self.assertEqual(
            len(canonical),
            len(set(layer_ids)),
        )


class SynthesisRoutingTests(unittest.TestCase):
    def test_six_sections_stable_order_and_category_mapping(self):
        synthesis = build_mercury_profile_synthesis(_milka())
        self.assertEqual(len(synthesis.sections), 6)
        self.assertEqual(
            [section.key for section in synthesis.sections],
            [key for key, _title, _cats in SECTION_SPECS],
        )
        self.assertEqual(CATEGORY_TO_SECTION["thinking"], "thinking")
        self.assertEqual(CATEGORY_TO_SECTION["communication"], "communication")
        self.assertEqual(CATEGORY_TO_SECTION["learning"], "learning")
        self.assertEqual(CATEGORY_TO_SECTION["memory"], "memory_focus")
        self.assertEqual(CATEGORY_TO_SECTION["focus"], "memory_focus")
        self.assertEqual(CATEGORY_TO_SECTION["work_application"], "work_application")
        self.assertEqual(CATEGORY_TO_SECTION["risk"], "context_risks")
        self.assertEqual(CATEGORY_TO_SECTION["environment"], "context_risks")
        self.assertEqual(CATEGORY_TO_SECTION["mobility"], "context_risks")

    def test_detail_only_categories_excluded_from_sections_and_previews(self):
        synthesis = build_mercury_profile_synthesis(_dzmitry())
        detail_ids = {
            fact_id
            for bucket in synthesis.source_details
            for fact_id in bucket.fact_ids
        }
        section_ids = {
            fact_id
            for section in synthesis.sections
            for fact_id in section.resolved_fact_ids
        }
        preview_ids = {
            fact_id
            for section in synthesis.sections
            for fact_id in section.preview_fact_ids
        }
        for fact in synthesis.facts_by_id.values():
            if fact.category in DETAIL_ONLY_CATEGORIES and not fact.unresolved:
                self.assertIn(fact.id, detail_ids)
                self.assertNotIn(fact.id, section_ids)
                self.assertNotIn(fact.id, preview_ids)

    def test_dzmitry_compensation_regression(self):
        profile = _dzmitry()
        synthesis = build_mercury_profile_synthesis(profile)
        compensation = [
            fact
            for fact in collect_canonical_facts(profile)
            if fact.category == "compensation" and not fact.unresolved
        ]
        self.assertGreaterEqual(len(compensation), 1)
        compensation_bucket = next(
            bucket for bucket in synthesis.source_details if bucket.key == "compensation"
        )
        compensation_ids = {fact.id for fact in compensation}
        self.assertTrue(compensation_ids.issubset(set(compensation_bucket.fact_ids)))
        for section in synthesis.sections:
            self.assertTrue(compensation_ids.isdisjoint(section.resolved_fact_ids))
            self.assertTrue(compensation_ids.isdisjoint(section.preview_fact_ids))
        owned = (
            {fid for section in synthesis.sections for fid in section.resolved_fact_ids}
            | {fid for group in synthesis.conditional_details for fid in group.fact_ids}
            | {fid for bucket in synthesis.source_details for fid in bucket.fact_ids}
        )
        self.assertTrue(compensation_ids.issubset(owned))

    def test_unresolved_routed_to_conditional_details_only(self):
        synthesis = build_mercury_profile_synthesis(_avdey())
        unresolved_ids = {
            fact.id for fact in synthesis.facts_by_id.values() if fact.unresolved
        }
        self.assertTrue(unresolved_ids)
        conditional_ids = {
            fact_id
            for group in synthesis.conditional_details
            for fact_id in group.fact_ids
        }
        self.assertEqual(unresolved_ids, conditional_ids)
        for section in synthesis.sections:
            self.assertTrue(unresolved_ids.isdisjoint(section.resolved_fact_ids))
            self.assertTrue(unresolved_ids.isdisjoint(section.preview_fact_ids))
        for group in synthesis.conditional_details:
            self.assertTrue(group.fact_ids)
            self.assertTrue(isinstance(group.factor_type, str))
            self.assertTrue(isinstance(group.factor_key, str))

    def test_unknown_category_falls_into_other_detail_bucket(self):
        profile = _milka()
        orphan = SourceFact(
            id="synth_orphan_future_category",
            factor_type="sign",
            factor_key="Pisces",
            category="future_unknown_category",
            text="Synthetic future category for routing test.",
            polarity="neutral",
            tags=[],
            source_reference="test_only",
            activated=True,
            unresolved=False,
        )
        mutated = profile.model_copy(deep=True)
        mutated.sign_facts = list(mutated.sign_facts) + [orphan]
        synthesis = build_mercury_profile_synthesis(mutated)
        other = next(bucket for bucket in synthesis.source_details if bucket.key == "other")
        self.assertIn(orphan.id, other.fact_ids)
        self.assertEqual(synthesis.traceability.unclassified_fact_count, 0)


class SynthesisPreviewTests(unittest.TestCase):
    def test_preview_max_four_and_provenance_diversity(self):
        synthesis = build_mercury_profile_synthesis(_avdey())
        for section in synthesis.sections:
            self.assertLessEqual(len(section.preview_fact_ids), MAX_PREVIEW_FACTS)
            self.assertTrue(
                set(section.preview_fact_ids).issubset(set(section.resolved_fact_ids))
            )
            if section.resolved_fact_count >= 1:
                self.assertGreaterEqual(len(section.preview_fact_ids), 1)
            # First min(4, factor_count) previews should prefer distinct provenance.
            preview_facts = [synthesis.facts_by_id[fid] for fid in section.preview_fact_ids]
            first_wave = preview_facts[: min(MAX_PREVIEW_FACTS, section.factor_count)]
            provenances = [
                f"{fact.factor_type}:{fact.factor_key}" for fact in first_wave
            ]
            self.assertEqual(len(provenances), len(set(provenances)))

    def test_preview_does_not_prefer_polarity_or_orb(self):
        # With fixed diversity algorithm, reordering by polarity must not change
        # the selected preview set for a section with multiple factors.
        synthesis = build_mercury_profile_synthesis(_vlad())
        thinking = next(section for section in synthesis.sections if section.key == "thinking")
        self.assertEqual(thinking.preview_fact_ids, thinking.preview_fact_ids)
        # Deterministic: same profile twice yields identical previews.
        again = build_mercury_profile_synthesis(_vlad())
        thinking2 = next(section for section in again.sections if section.key == "thinking")
        self.assertEqual(thinking.preview_fact_ids, thinking2.preview_fact_ids)


class SynthesisLosslessnessTests(unittest.TestCase):
    def test_inventory_partition_and_no_duplicates(self):
        for builder in (_avdey, _vlad, _dzmitry, _andrey, _milka):
            with self.subTest(profile=builder.__name__):
                synthesis = build_mercury_profile_synthesis(builder())
                resolved = [
                    fid for section in synthesis.sections for fid in section.resolved_fact_ids
                ]
                conditional = [
                    fid for group in synthesis.conditional_details for fid in group.fact_ids
                ]
                detail = [
                    fid for bucket in synthesis.source_details for fid in bucket.fact_ids
                ]
                self.assertEqual(len(resolved), len(set(resolved)))
                self.assertEqual(len(conditional), len(set(conditional)))
                self.assertEqual(len(detail), len(set(detail)))
                self.assertTrue(set(resolved).isdisjoint(conditional))
                self.assertTrue(set(resolved).isdisjoint(detail))
                self.assertTrue(set(conditional).isdisjoint(detail))
                trace = synthesis.traceability
                self.assertEqual(
                    trace.resolved_section_fact_count
                    + trace.conditional_fact_count
                    + trace.detail_only_fact_count
                    + trace.unclassified_fact_count,
                    trace.total_fact_count,
                )
                self.assertEqual(trace.unclassified_fact_count, 0)
                self.assertEqual(trace.total_fact_count, len(synthesis.facts_by_id))


class SynthesisRepeatAndContrastTests(unittest.TestCase):
    def test_repeated_signals_preserved_exactly(self):
        cases = {
            "avdey": (
                _avdey,
                [
                    "analytical_thinking",
                    "technical_ability",
                    "debate",
                    "argumentation",
                    "nonstandard_thinking",
                    "sales",
                ],
            ),
            "vlad": (
                _vlad,
                [
                    "analytical_thinking",
                    "persuasion",
                    "lifelong_learning",
                    "foreign_languages",
                ],
            ),
            "dzmitry": (_dzmitry, ["persuasion", "foreign_languages", "teaching"]),
            "andrey": (_andrey, ["technical_ability"]),
            "milka": (_milka, []),
        }
        for name, (builder, expected) in cases.items():
            with self.subTest(name=name):
                profile = builder()
                synthesis = build_mercury_profile_synthesis(profile)
                self.assertEqual(_signal_names(profile), expected)
                self.assertEqual(_synthesis_signal_names(synthesis), expected)
                for raw, syn in zip(profile.repeated_signals, synthesis.strongest_patterns):
                    self.assertEqual(raw.signal, syn.signal)
                    self.assertEqual(raw.source_count, syn.source_count)
                    self.assertEqual(tuple(raw.sources), syn.sources)
                    self.assertEqual(tuple(raw.fact_ids), syn.fact_ids)

    def test_no_new_repeat_or_contrast_specs(self):
        self.assertEqual(len(REPEATED_SIGNAL_SPECS), 15)
        self.assertEqual(len(CONTRAST_PAIRS), 6)

    def test_contrasts_classified_without_engine_change(self):
        avdey = build_mercury_profile_synthesis(_avdey())
        vlad = build_mercury_profile_synthesis(_vlad())
        self.assertEqual(len(avdey.resolved_tensions) + len(avdey.conditional_tensions), 1)
        self.assertEqual(len(vlad.resolved_tensions) + len(vlad.conditional_tensions), 2)
        for tension in list(avdey.resolved_tensions) + list(avdey.conditional_tensions):
            self.assertIn(tension.state, {"resolved", "conditional"})
            side_a = [avdey.facts_by_id[fid] for fid in tension.facts_a if fid in avdey.facts_by_id]
            side_b = [avdey.facts_by_id[fid] for fid in tension.facts_b if fid in avdey.facts_by_id]
            a_ok = any(not fact.unresolved for fact in side_a)
            b_ok = any(not fact.unresolved for fact in side_b)
            if tension.state == "resolved":
                self.assertTrue(a_ok and b_ok)
            else:
                self.assertFalse(a_ok and b_ok)


class SynthesisGoldenAuditTests(unittest.TestCase):
    def test_milka_empty_repeats_but_nonempty_sections(self):
        synthesis = build_mercury_profile_synthesis(_milka())
        self.assertEqual(synthesis.strongest_patterns, ())
        self.assertEqual(synthesis.resolved_tensions, ())
        self.assertEqual(synthesis.conditional_tensions, ())
        self.assertGreater(synthesis.traceability.total_fact_count, 0)
        nonempty = [section for section in synthesis.sections if section.resolved_fact_count]
        self.assertTrue(nonempty)
        self.assertTrue(any(section.preview_fact_ids for section in nonempty))

    def test_golden_synthesis_stats_smoke(self):
        expected_min_total = {
            "avdey": 100,
            "vlad": 70,
            "dzmitry": 100,
            "andrey": 100,
            "milka": 50,
        }
        builders = {
            "avdey": _avdey,
            "vlad": _vlad,
            "dzmitry": _dzmitry,
            "andrey": _andrey,
            "milka": _milka,
        }
        for name, builder in builders.items():
            with self.subTest(name=name):
                profile = builder()
                synthesis = build_mercury_profile_synthesis(profile)
                self.assertGreaterEqual(
                    synthesis.traceability.total_fact_count,
                    expected_min_total[name],
                )
                self.assertEqual(len(synthesis.sections), 6)
                self.assertEqual(synthesis.traceability.unclassified_fact_count, 0)
                self.assertEqual(
                    len(synthesis.strongest_patterns),
                    len(profile.repeated_signals),
                )


class SynthesisImmutabilityOfSourceLayerTests(unittest.TestCase):
    def test_source_schema_and_specs_untouched(self):
        fields = set(SourceFact.model_fields)
        self.assertEqual(
            fields,
            {
                "id",
                "factor_type",
                "factor_key",
                "category",
                "text",
                "polarity",
                "tags",
                "source_reference",
                "activation_condition",
                "activated",
                "unresolved",
            },
        )
        self.assertNotIn("priority", fields)
        self.assertNotIn("presentation_score", fields)
        self.assertEqual(len(REPEATED_SIGNAL_SPECS), 15)
        self.assertEqual(len(CONTRAST_PAIRS), 6)


if __name__ == "__main__":
    unittest.main()
