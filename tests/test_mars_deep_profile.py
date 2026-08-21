"""M10.5 Phase 2A — Deep Mars source ownership backend tests."""

from __future__ import annotations

import unittest
from datetime import date, time

from app.schemas.mars_source_profile import MarsSourceProfileRequest
from app.services.mars_deep_profile import (
    build_mars_deep_profile,
    derive_presentation_lane,
    is_narrative_eligible,
    match_non_work_personal_facts,
)
from app.services.mars_profile_synthesis import (
    build_mars_profile_synthesis,
    serialize_mars_source_profile,
)
from app.services.mars_source_knowledge import ALL_MARS_SOURCE_FACTS
from app.services.mars_source_profile import build_mars_source_profile
from app.services.thinking_to_execution import build_thinking_to_execution
from app.services.contribution_profile import build_contribution_profile
from app.services.mercury_source_profile import build_mercury_source_profile
from app.schemas.mercury_source_profile import MercurySourceProfileRequest


GOLDEN = dict(
    birth_date=date(1986, 7, 14),
    birth_time=time(7, 10),
    birth_place="Simferopol, Ukraine",
)


def _internal_profile(**natal):
    return build_mars_source_profile(**natal)


def _api_profile(**natal):
    return serialize_mars_source_profile(_internal_profile(**natal))


def _deep(**natal):
    return build_mars_deep_profile(_api_profile(**natal))


class MarsH7CatalogTruthTests(unittest.TestCase):
    def test_h7_affliction_condition_is_unresolved(self):
        fact = next(
            item
            for item in ALL_MARS_SOURCE_FACTS
            if item.id == "mars_h7_affliction_early_marriage_divorce"
        )
        self.assertEqual(fact.activation_condition, "affliction_unresolved")
        self.assertTrue(fact.unresolved)
        self.assertEqual(fact.scope, "SOURCE_ONLY")


class DeepMarsOwnershipTests(unittest.TestCase):
    def test_work_facts_in_fact_ids_and_work_fact_ids(self):
        api = _api_profile(**GOLDEN)
        deep = build_mars_deep_profile(api)
        work_sign_ids = {fact.id for fact in api.sign_facts if fact.activated}
        self.assertTrue(work_sign_ids)
        self.assertTrue(work_sign_ids <= set(deep.sign.fact_ids))
        self.assertEqual(set(deep.sign.work_fact_ids), work_sign_ids)

    def test_source_only_may_appear_in_fact_ids_never_work(self):
        deep = _deep(**GOLDEN)
        # Golden Mars in House 6 → illness SOURCE_ONLY facts
        self.assertEqual(deep.house.availability, "available")
        self.assertEqual(deep.house.factor_key, "6")
        self.assertIn(
            "mars_h6_source_acute_inflammatory_illness",
            deep.house.fact_ids,
        )
        self.assertNotIn(
            "mars_h6_source_acute_inflammatory_illness",
            deep.house.work_fact_ids,
        )
        self.assertNotIn(
            "mars_h6_source_acute_inflammatory_illness",
            deep.house.narrative_eligible_fact_ids,
        )

    def test_personal_mars_visible_not_work(self):
        deep = _deep(**GOLDEN)
        self.assertEqual(deep.motion.availability, "available")
        self.assertIn(
            "mars_rx_sexual_temperament_suppression",
            deep.motion.fact_ids,
        )
        self.assertNotIn(
            "mars_rx_sexual_temperament_suppression",
            deep.motion.work_fact_ids,
        )
        self.assertNotIn(
            "mars_rx_sexual_temperament_suppression",
            deep.motion.narrative_eligible_fact_ids,
        )
        lane = next(
            ref.presentation_lane
            for ref in deep.motion.fact_refs
            if ref.fact_id == "mars_rx_sexual_temperament_suppression"
        )
        self.assertEqual(lane, "sensitive_source")

    def test_sensitive_source_not_narrative_eligible(self):
        deep = _deep(**GOLDEN)
        sensitive_ids = {
            ref.fact_id
            for block in (deep.sign, deep.house, deep.motion, *deep.aspects)
            for ref in block.fact_refs
            if ref.presentation_lane in {"sensitive_source", "source_specific"}
        }
        for fact_id in sensitive_ids:
            for block in (deep.sign, deep.house, deep.motion, *deep.aspects):
                self.assertNotIn(fact_id, block.narrative_eligible_fact_ids)
                self.assertNotIn(fact_id, block.highlight_fact_ids)

    def test_unresolved_only_in_unresolved_evidence(self):
        deep = _deep(**GOLDEN)
        # Collect any unresolved evidence across factors
        unresolved = set()
        for block in (deep.sign, deep.house, deep.motion, *deep.aspects):
            unresolved |= set(block.unresolved_evidence_ids)
            for fact_id in block.unresolved_evidence_ids:
                self.assertNotIn(fact_id, block.highlight_fact_ids)
                self.assertNotIn(fact_id, block.narrative_eligible_fact_ids)
                # May or may not be in fact_ids — Phase 2A keeps unresolved separate
                self.assertNotIn(fact_id, block.fact_ids)

        # h7 affliction is house 7 only — if golden is not H7, match helper still
        visible, unresolved_match = match_non_work_personal_facts(
            factor_type="house", factor_key="7"
        )
        ids_u = {fact.id for fact in unresolved_match}
        self.assertIn("mars_h7_affliction_early_marriage_divorce", ids_u)
        self.assertNotIn(
            "mars_h7_affliction_early_marriage_divorce",
            {fact.id for fact in visible},
        )

    def test_no_cross_factor_ownership_leak(self):
        deep = _deep(**GOLDEN)
        sign_ids = set(deep.sign.fact_ids)
        house_ids = set(deep.house.fact_ids) if deep.house.availability == "available" else set()
        motion_ids = (
            set(deep.motion.fact_ids) if deep.motion.availability == "available" else set()
        )
        self.assertFalse(sign_ids & house_ids)
        self.assertFalse(sign_ids & motion_ids)
        self.assertFalse(house_ids & motion_ids)


class DeepMarsHighlightTests(unittest.TestCase):
    def test_highlights_deterministic_and_bounded(self):
        deep_a = _deep(**GOLDEN)
        deep_b = _deep(**GOLDEN)
        self.assertEqual(
            deep_a.sign.highlight_fact_ids,
            deep_b.sign.highlight_fact_ids,
        )
        self.assertLessEqual(len(deep_a.sign.highlight_fact_ids), 5)
        for fact_id in deep_a.sign.highlight_fact_ids:
            self.assertIn(fact_id, deep_a.sign.narrative_eligible_fact_ids)


class DeepMarsAspectTests(unittest.TestCase):
    def test_complicate_empty_without_mars_contrast_catalog(self):
        deep = _deep(**GOLDEN)
        for block in deep.aspects:
            self.assertEqual(block.interaction.contrasting, [])

    def test_source_only_aspect_does_not_add(self):
        deep = _deep(**GOLDEN)
        for block in deep.aspects:
            for theme in block.interaction.adds:
                for fact_id in theme.aspect_fact_ids:
                    self.assertTrue(
                        any(
                            ref.fact_id == fact_id and ref.activated
                            for ref in block.fact_refs
                        )
                        or fact_id in block.work_fact_ids
                    )
                    self.assertNotIn(
                        fact_id,
                        {
                            ref.fact_id
                            for ref in block.fact_refs
                            if ref.scope in {"SOURCE_ONLY", "PERSONAL_MARS"}
                        },
                    )

    def test_add_and_reinforce_use_work_tags_only(self):
        deep = _deep(**GOLDEN)
        api = _api_profile(**GOLDEN)
        work_tags = {
            tag
            for fact in (
                list(api.sign_facts) + list(api.house_facts) + list(api.motion_facts)
            )
            if fact.activated
            for tag in fact.tags
        }
        for block in deep.aspects:
            for theme in block.interaction.adds:
                self.assertNotIn(theme.tag, work_tags)
            for item in block.interaction.reinforcing:
                self.assertTrue(item.aspect_fact_ids)
                self.assertTrue(item.base_fact_ids)


class DeepMarsUnknownTimeTests(unittest.TestCase):
    def test_house_unavailable_when_time_unknown(self):
        deep = _deep(
            birth_date=GOLDEN["birth_date"],
            birth_place=GOLDEN["birth_place"],
        )
        self.assertEqual(deep.house.availability, "unavailable")
        self.assertEqual(deep.house.fact_ids, [])
        self.assertEqual(deep.house.work_fact_ids, [])
        self.assertEqual(deep.house.highlight_fact_ids, [])
        self.assertFalse(deep.configuration.house_available)


class DeepMarsRegressionTests(unittest.TestCase):
    def test_work_activation_counts_unchanged(self):
        internal = _internal_profile(**GOLDEN)
        api = serialize_mars_source_profile(internal)
        # activated lists unchanged by deep attach
        self.assertEqual(len(api.sign_facts), len(internal.sign_facts))
        self.assertEqual(len(api.house_facts), len(internal.house_facts))
        self.assertEqual(len(api.motion_facts), len(internal.motion_facts))
        self.assertEqual(len(api.aspect_facts), len(internal.aspect_facts))
        self.assertTrue(all(fact.activated for fact in api.sign_facts))
        self.assertTrue(api.synthesis is not None)
        self.assertTrue(api.synthesis.deep_profile is not None)

    def test_existing_synthesis_sections_still_present(self):
        internal = _internal_profile(**GOLDEN)
        synthesis = build_mars_profile_synthesis(internal)
        self.assertTrue(synthesis.sections)
        api = serialize_mars_source_profile(internal)
        keys = [section.key for section in api.synthesis.sections]
        self.assertIn("how_you_execute", keys)

    def test_tte_and_contribution_still_build(self):
        from app.services.person_perspective import build_person_perspective

        natal = GOLDEN
        mercury = build_mercury_source_profile(
            MercurySourceProfileRequest(**natal)
        )
        mars = _internal_profile(**natal)
        person = build_person_perspective(name="Avdey", sex="male")
        tte = build_thinking_to_execution(mercury, mars, person)
        self.assertIsNotNone(tte)
        contrib = build_contribution_profile(mercury, mars, person, tte)
        self.assertIsNotNone(contrib)


class DeepMarsLaneHelpersTests(unittest.TestCase):
    def test_lane_helpers_for_catalog_defs(self):
        from app.schemas.mars_source_profile import MarsSourceFact

        sexual = next(
            item
            for item in ALL_MARS_SOURCE_FACTS
            if item.id == "mars_rx_sexual_temperament_suppression"
        )
        fact = MarsSourceFact(
            id=sexual.id,
            factor_type="motion",
            factor_key="retrograde",
            category=sexual.category,
            text=sexual.text,
            polarity=sexual.polarity,  # type: ignore[arg-type]
            scope=sexual.scope,  # type: ignore[arg-type]
            tags=[],
            source_reference=sexual.source_reference,
            activated=False,
            unresolved=False,
        )
        self.assertEqual(derive_presentation_lane(fact), "sensitive_source")
        self.assertFalse(is_narrative_eligible(fact))


if __name__ == "__main__":
    unittest.main()
