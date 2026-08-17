"""API integration tests for additive Mercury profile synthesis (S3)."""

from __future__ import annotations

import unittest
from datetime import date, time

from app.api.routes.mercury_source_profile import create_mercury_source_profile
from app.schemas.mercury_source_profile import MercurySourceProfileRequest
from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_profile_synthesis import (
    DETAIL_ONLY_CATEGORIES,
    SECTION_SPECS,
    attach_mercury_profile_synthesis,
    build_mercury_profile_synthesis,
)
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
)


def _avdey_request():
    return MercurySourceProfileRequest(
        birth_date=date(1986, 7, 14),
        birth_time=time(7, 10),
        birth_place="Simferopol, Ukraine",
    )


def _vlad_request():
    return MercurySourceProfileRequest(
        birth_date=date(1986, 5, 16),
        birth_time=time(15, 0),
        birth_place="Dnipro, Ukraine",
    )


def _dzmitry_request():
    return MercurySourceProfileRequest(
        birth_date=date(1985, 11, 12),
        birth_time=time(14, 15),
        birth_place="Zhodino, Belarus",
    )


def _andrey_profile():
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


def _milka_profile():
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


class MercurySourceProfileSynthesisApiTests(unittest.TestCase):
    def test_endpoint_returns_synthesis_field(self):
        response = create_mercury_source_profile(_avdey_request())
        self.assertIsNotNone(response.synthesis)
        self.assertGreater(len(response.synthesis.strongest_patterns), 0)
        self.assertEqual(len(response.synthesis.sections), len(SECTION_SPECS))

    def test_existing_top_level_fields_remain(self):
        response = create_mercury_source_profile(_vlad_request())
        for field in (
            "calculated",
            "sign_facts",
            "house_facts",
            "motion_facts",
            "aspect_facts",
            "repeated_signals",
            "conditional_unresolved",
            "contrasting_signals",
            "coverage",
            "limitations",
        ):
            self.assertTrue(hasattr(response, field), field)
        self.assertIsNotNone(response.calculated)
        self.assertGreater(len(response.sign_facts), 0)
        self.assertIsInstance(response.repeated_signals, list)
        self.assertIsInstance(response.contrasting_signals, list)
        self.assertIsNotNone(response.coverage)

    def test_strongest_patterns_match_assembler(self):
        raw = build_mercury_source_profile(_avdey_request())
        assembled = build_mercury_profile_synthesis(raw)
        response = create_mercury_source_profile(_avdey_request())
        self.assertEqual(
            [item.signal for item in response.synthesis.strongest_patterns],
            [item.signal for item in assembled.strongest_patterns],
        )
        self.assertEqual(
            [item.signal for item in response.synthesis.strongest_patterns],
            [item.signal for item in response.repeated_signals],
        )

    def test_section_order_stable(self):
        response = create_mercury_source_profile(_dzmitry_request())
        keys = [section.key for section in response.synthesis.sections]
        self.assertEqual(keys, [spec[0] for spec in SECTION_SPECS])
        titles = [section.title for section in response.synthesis.sections]
        self.assertEqual(titles, [spec[1] for spec in SECTION_SPECS])

    def test_preview_ids_resolve_to_real_facts(self):
        response = create_mercury_source_profile(_avdey_request())
        facts = response.synthesis.facts_by_id
        for section in response.synthesis.sections:
            for fact_id in section.preview_fact_ids:
                self.assertIn(fact_id, facts)
                self.assertEqual(facts[fact_id].id, fact_id)

    def test_unresolved_and_compensation_absent_from_ordinary_previews(self):
        response = attach_mercury_profile_synthesis(_andrey_profile())
        facts = response.synthesis.facts_by_id
        for section in response.synthesis.sections:
            for fact_id in section.preview_fact_ids:
                fact = facts[fact_id]
                self.assertFalse(fact.unresolved, fact_id)
                self.assertNotIn(fact.category, DETAIL_ONLY_CATEGORIES)

    def test_conditional_facts_preserved_in_conditional_details(self):
        response = create_mercury_source_profile(_avdey_request())
        conditional_ids = {
            fact_id
            for group in response.synthesis.conditional_details
            for fact_id in group.fact_ids
        }
        unresolved_ids = {fact.id for fact in response.conditional_unresolved}
        self.assertTrue(conditional_ids)
        self.assertEqual(conditional_ids, unresolved_ids)

    def test_raw_source_arrays_still_available(self):
        response = create_mercury_source_profile(_dzmitry_request())
        self.assertGreater(len(response.sign_facts), 0)
        self.assertGreater(len(response.house_facts), 0)
        self.assertGreater(len(response.aspect_facts), 0)
        self.assertIsInstance(response.repeated_signals, list)
        self.assertIsInstance(response.contrasting_signals, list)

    def test_coverage_behavior_unchanged(self):
        with_synth = create_mercury_source_profile(_vlad_request())
        without = build_mercury_source_profile(_vlad_request())
        self.assertEqual(with_synth.coverage.status, without.coverage.status)
        self.assertEqual(with_synth.coverage.covered_factors, without.coverage.covered_factors)
        self.assertEqual(with_synth.coverage.missing_factors, without.coverage.missing_factors)

    def test_unknown_birth_time_still_works(self):
        response = attach_mercury_profile_synthesis(_milka_profile())
        self.assertFalse(response.calculated.birth_time_known)
        self.assertIsNone(response.calculated.mercury_house)
        self.assertEqual(response.house_facts, [])
        self.assertIsNotNone(response.synthesis)
        self.assertEqual(response.synthesis.strongest_patterns, [])
        nonempty = [s for s in response.synthesis.sections if s.resolved_fact_count]
        self.assertGreater(len(nonempty), 0)

    def test_output_deterministic_across_identical_requests(self):
        first = create_mercury_source_profile(_avdey_request())
        second = create_mercury_source_profile(_avdey_request())
        self.assertEqual(
            first.synthesis.model_dump(),
            second.synthesis.model_dump(),
        )
        self.assertEqual(
            [f.id for f in first.sign_facts],
            [f.id for f in second.sign_facts],
        )

    def test_build_service_without_synthesis_remains_compatible(self):
        raw = build_mercury_source_profile(_vlad_request())
        self.assertIsNone(raw.synthesis)


class MercuryHumanPresentationApiTests(unittest.TestCase):
    def test_presentation_map_additive_raw_intact(self):
        from app.services.mercury_human_copy import HUMAN_COPY_OVERRIDES

        response = create_mercury_source_profile(_avdey_request())
        synthesis = response.synthesis
        self.assertIsNotNone(synthesis)

        conflict_id = "pluto_sq_conflictual_communication"
        raw = "Toxic conflictual atmosphere around communication."
        human = "Communication can become highly conflictual and toxic."
        self.assertEqual(synthesis.facts_by_id[conflict_id].text, raw)
        self.assertEqual(synthesis.presentation_text_by_fact_id[conflict_id], human)

        for fact_id, text in synthesis.presentation_text_by_fact_id.items():
            self.assertEqual(text, HUMAN_COPY_OVERRIDES[fact_id])
            self.assertNotEqual(synthesis.facts_by_id[fact_id].text, text)

        # Unoverridden facts are omitted from the presentation map.
        plain = next(
            fid
            for fid, fact in synthesis.facts_by_id.items()
            if fid not in HUMAN_COPY_OVERRIDES
        )
        self.assertNotIn(plain, synthesis.presentation_text_by_fact_id)

        # Structural invariants unchanged vs raw build.
        raw_profile = build_mercury_source_profile(_avdey_request())
        self.assertEqual(
            [s.signal for s in response.repeated_signals],
            [s.signal for s in raw_profile.repeated_signals],
        )
        self.assertEqual(
            [(c.tag_a, c.tag_b) for c in response.contrasting_signals],
            [(c.tag_a, c.tag_b) for c in raw_profile.contrasting_signals],
        )
        self.assertEqual(response.coverage.status, raw_profile.coverage.status)
        self.assertEqual(
            synthesis.traceability.total_fact_count,
            len(synthesis.facts_by_id),
        )
        unresolved = {f.id for f in synthesis.facts_by_id.values() if f.unresolved}
        conditional = {
            fid
            for group in synthesis.conditional_details
            for fid in group.fact_ids
        }
        self.assertEqual(unresolved, conditional)


class MercurySynthesisProductAuditTests(unittest.TestCase):
    """UI-oriented stats for the five golden profiles (report helpers)."""

    @staticmethod
    def _ui_stats(profile):
        synthesis = profile.synthesis
        nonempty_sections = [
            section for section in synthesis.sections if section.resolved_fact_count
        ]
        preview_count = sum(len(section.preview_fact_ids) for section in nonempty_sections)
        leak_ids = []
        for section in nonempty_sections:
            for fact_id in section.preview_fact_ids:
                fact = synthesis.facts_by_id[fact_id]
                if fact.unresolved or fact.category in DETAIL_ONLY_CATEGORIES:
                    leak_ids.append(fact_id)
        return {
            "patterns": len(synthesis.strongest_patterns),
            "sections": len(nonempty_sections),
            "preview_facts": preview_count,
            "resolved_tensions": len(synthesis.resolved_tensions),
            "conditional_tensions": len(synthesis.conditional_tensions),
            "conditional_groups": len(synthesis.conditional_details),
            "detail_only_leak": leak_ids,
            "source_details_keys": [bucket.key for bucket in synthesis.source_details],
        }

    def test_five_profile_ui_stats_and_no_detail_leak(self):
        profiles = {
            "avdey": create_mercury_source_profile(_avdey_request()),
            "vlad": create_mercury_source_profile(_vlad_request()),
            "dzmitry": create_mercury_source_profile(_dzmitry_request()),
            "andrey": attach_mercury_profile_synthesis(_andrey_profile()),
            "milka": attach_mercury_profile_synthesis(_milka_profile()),
        }
        stats = {name: self._ui_stats(profile) for name, profile in profiles.items()}

        self.assertEqual(stats["milka"]["patterns"], 0)
        self.assertGreater(stats["milka"]["sections"], 0)
        self.assertGreater(stats["avdey"]["patterns"], 0)
        for name, item in stats.items():
            self.assertEqual(item["detail_only_leak"], [], name)
            # Compensation / source_specific must not appear in section previews.
            for section in profiles[name].synthesis.sections:
                for fact_id in section.preview_fact_ids:
                    fact = profiles[name].synthesis.facts_by_id[fact_id]
                    self.assertNotIn(fact.category, DETAIL_ONLY_CATEGORIES, name)


if __name__ == "__main__":
    unittest.main()
