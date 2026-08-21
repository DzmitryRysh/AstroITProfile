"""Semantic-boundary ownership tests for Mercury Deep Narrative (M9.5C audit)."""

from __future__ import annotations

import unittest
from datetime import date, time

from app.schemas.mercury_source_profile import MercurySourceProfileRequest
from app.services.mercury_deep_profile import build_mercury_deep_profile
from app.services.mercury_source_profile import build_mercury_source_profile


AVDEY = dict(
    birth_date=date(1986, 7, 14),
    birth_time=time(7, 10),
    birth_place="Simferopol, Ukraine",
)

AFFLICTED_LEO_IDS = (
    "leo_afflicted_extreme_stubbornness",
    "leo_afflicted_ego_interferes_with_facts",
    "leo_afflicted_lying_distortion",
    "leo_afflicted_appearance_of_competence",
    "leo_afflicted_putting_on_a_show",
    "leo_afflicted_superior_manner",
    "leo_afflicted_expecting_admiration",
)


def _avdey():
    profile = build_mercury_source_profile(MercurySourceProfileRequest(**AVDEY))
    deep = build_mercury_deep_profile(profile)
    return profile, deep


class NarrativeOwnershipBoundaryTests(unittest.TestCase):
    def test_conditional_sign_facts_remain_visible_in_source_observations(self):
        profile, deep = _avdey()
        for fact_id in AFFLICTED_LEO_IDS:
            fact = next(f for f in profile.sign_facts if f.id == fact_id)
            self.assertTrue(fact.activated)
            self.assertEqual(fact.activation_condition, "hard_aspected")
            self.assertIn(fact_id, deep.sign.fact_ids)

    def test_conditional_sign_facts_do_not_define_base_core_narrative(self):
        _, deep = _avdey()
        narrative = deep.sign.narrative
        self.assertIsNotNone(narrative)
        assert narrative is not None
        for fact_id in AFFLICTED_LEO_IDS:
            self.assertNotIn(fact_id, narrative.supporting_fact_ids)
            self.assertIn(fact_id, narrative.conditional_fact_ids)
        self.assertNotIn("extreme stubbornness", narrative.core_theme.lower())
        self.assertNotIn("extreme stubbornness", narrative.summary.lower())
        # Core theme must not be led by hard-aspect-only risk framing.
        self.assertNotIn("appearance-of-competence", narrative.core_theme.lower())

    def test_conditional_subsection_exposes_hard_aspected_activation(self):
        _, deep = _avdey()
        conditional = next(
            (
                item
                for item in deep.sign.narrative.subsections
                if item.key == "conditional"
            ),
            None,
        )
        self.assertIsNotNone(conditional)
        assert conditional is not None
        self.assertIn("hard aspects", conditional.text.lower())
        self.assertIn(
            "leo_afflicted_extreme_stubbornness",
            conditional.supporting_fact_ids,
        )

    def test_aspect_conditioned_meaning_available_for_aspect_and_integrated(self):
        _, deep = _avdey()
        pluto = next(
            block
            for block in deep.aspects
            if block.identity.factor_key == "square_Pluto"
        )
        self.assertTrue(pluto.interaction.available)
        self.assertTrue(pluto.interaction.adds)
        self.assertTrue(any(item.basis == "aspect_addition" for item in deep.integrated))
        self.assertTrue(
            any(
                "intensifies" in item.text.lower()
                or "beyond what the base" in item.text.lower()
                for item in deep.integrated
                if item.basis == "aspect_addition"
            )
        )

    def test_no_double_count_hard_aspect_effect_as_unconditional_base(self):
        """Afflicted Leo tags must not also appear as if they were base ADD themes."""
        profile, deep = _avdey()
        narrative = deep.sign.narrative
        assert narrative is not None
        # Extreme stubbornness is hard_aspected — not core support.
        self.assertNotIn(
            "leo_afflicted_extreme_stubbornness",
            narrative.supporting_fact_ids,
        )
        # Aspect ADD themes come from aspect facts, not from afflicted sign facts.
        for block in deep.aspects:
            for theme in block.interaction.adds:
                for fact_id in theme.aspect_fact_ids:
                    fact = next(
                        f
                        for f in profile.aspect_facts
                        if f.id == fact_id
                    )
                    self.assertEqual(fact.factor_type, "aspect")
                    self.assertNotEqual(fact.factor_type, "sign")

    def test_siblings_driving_are_life_context_not_watchouts(self):
        _, deep = _avdey()
        watch = next(
            (
                item
                for item in deep.house.narrative.subsections
                if item.key == "watchouts"
            ),
            None,
        )
        life = next(
            (
                item
                for item in deep.house.narrative.subsections
                if item.key == "life_context"
            ),
            None,
        )
        self.assertIsNotNone(life)
        assert life is not None
        self.assertIn("h1_special_relevance_siblings", life.supporting_fact_ids)
        self.assertIn("h1_special_relevance_car_driving", life.supporting_fact_ids)
        if watch is not None:
            self.assertNotIn("h1_special_relevance_siblings", watch.supporting_fact_ids)
            self.assertNotIn(
                "h1_special_relevance_car_driving",
                watch.supporting_fact_ids,
            )

    def test_strong_source_claims_remain_visible_and_traceable(self):
        profile, deep = _avdey()
        lying = next(f for f in profile.sign_facts if f.id == "leo_l7_lying_source_claim")
        stubborn = next(
            f
            for f in profile.sign_facts
            if f.id == "leo_afflicted_extreme_stubbornness"
        )
        self.assertTrue(lying.activated)
        self.assertTrue(stubborn.activated)
        self.assertIn("leo_l7_lying_source_claim", deep.sign.fact_ids)
        self.assertIn("leo_afflicted_extreme_stubbornness", deep.sign.fact_ids)

        narrative = deep.sign.narrative
        assert narrative is not None
        # Unconditional strong risk → Watch-outs, not core theme lead.
        watch = next(item for item in narrative.subsections if item.key == "watchouts")
        self.assertIn("leo_l7_lying_source_claim", watch.supporting_fact_ids)
        self.assertNotIn("lying", narrative.core_theme.lower())
        # Conditional strong claim → conditional subsection.
        self.assertIn(
            "leo_afflicted_extreme_stubbornness",
            narrative.conditional_fact_ids,
        )

    def test_unknown_time_behavior_unchanged(self):
        natal = dict(birth_date=AVDEY["birth_date"], birth_place=AVDEY["birth_place"])
        deep = build_mercury_deep_profile(
            build_mercury_source_profile(MercurySourceProfileRequest(**natal))
        )
        self.assertEqual(deep.house.availability, "unavailable")
        self.assertIsNone(deep.house.narrative)
        self.assertEqual(deep.house.fact_ids, [])
        self.assertIsNotNone(deep.sign.narrative)

    def test_integrated_preserves_base_vs_aspect_ownership_language(self):
        _, deep = _avdey()
        repeats = [item for item in deep.integrated if item.basis == "repeated_signal"]
        self.assertTrue(repeats)
        for item in repeats:
            has_base = any(
                key.startswith(("sign:", "house:", "motion:"))
                for key in item.provenance_keys
            )
            has_aspect = any(key.startswith("aspect:") for key in item.provenance_keys)
            if has_base and has_aspect:
                self.assertNotIn("sign:", item.text)
                self.assertNotIn("aspect:", item.text)
                self.assertNotIn("carried by", item.text.lower())
                self.assertNotIn("appears across", item.text.lower())
                self.assertNotIn("supported across", item.text.lower())


if __name__ == "__main__":
    unittest.main()
