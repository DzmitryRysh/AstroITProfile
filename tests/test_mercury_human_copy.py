"""Tests for Mercury human presentation copy layer (S4.0)."""

from __future__ import annotations

import unittest

from app.schemas.mercury_source_profile import SourceFact
from app.services.mercury_human_copy import (
    HUMAN_COPY_OVERRIDES,
    get_human_fact_text,
    presentation_overrides_for_facts,
)
from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS


def _fact(
    fact_id: str,
    text: str,
    *,
    polarity: str = "neutral",
    tags: list[str] | None = None,
) -> SourceFact:
    return SourceFact(
        id=fact_id,
        factor_type="aspect",
        factor_key="Pluto_square",
        category="communication",
        text=text,
        polarity=polarity,
        tags=tags or [],
        source_reference="test",
        activated=True,
        unresolved=False,
    )


class HumanCopyModuleTests(unittest.TestCase):
    def test_curated_id_returns_human_text(self):
        fact = _fact(
            "pluto_sq_conflictual_communication",
            "Toxic conflictual atmosphere around communication.",
            polarity="risk",
        )
        self.assertEqual(
            get_human_fact_text(fact),
            "Communication can become highly conflictual and toxic.",
        )

    def test_unmapped_fact_returns_raw_text(self):
        fact = _fact("some_unmapped_fact", "Strong persuasiveness.")
        self.assertEqual(get_human_fact_text(fact), "Strong persuasiveness.")

    def test_unknown_id_cannot_silently_invent_copy(self):
        self.assertNotIn("invented_fact_id", HUMAN_COPY_OVERRIDES)
        fact = _fact("invented_fact_id", "Canonical raw wording.")
        self.assertEqual(get_human_fact_text(fact), "Canonical raw wording.")

    def test_raw_source_fact_text_unchanged(self):
        raw = "Toxic conflictual atmosphere around communication."
        fact = _fact("pluto_sq_conflictual_communication", raw, polarity="risk")
        _ = get_human_fact_text(fact)
        self.assertEqual(fact.text, raw)

    def test_override_mapping_uses_stable_ids(self):
        for key in HUMAN_COPY_OVERRIDES:
            self.assertIsInstance(key, str)
            self.assertTrue(key)
            self.assertNotIn(" ", key)

    def test_duplicate_override_ids_impossible(self):
        # Dict construction already dedupes; assert uniqueness of keys explicitly.
        keys = list(HUMAN_COPY_OVERRIDES.keys())
        self.assertEqual(len(keys), len(set(keys)))

    def test_every_curated_override_id_exists_in_canonical_knowledge(self):
        catalog_ids = {fact.id for fact in ALL_SOURCE_FACTS}
        missing = sorted(set(HUMAN_COPY_OVERRIDES) - catalog_ids)
        self.assertEqual(missing, [])

    def test_no_blank_human_copy(self):
        for fact_id, text in HUMAN_COPY_OVERRIDES.items():
            self.assertTrue(text.strip(), fact_id)

    def test_presentation_overrides_only_for_present_facts(self):
        mapped = _fact(
            "pluto_sq_words_can_hurt",
            "Words can strongly hurt / have high resonance.",
            polarity="risk",
        )
        unmapped = _fact("unmapped_x", "Strong persuasiveness.")
        result = presentation_overrides_for_facts([mapped, unmapped])
        self.assertEqual(
            result,
            {
                "pluto_sq_words_can_hurt": (
                    "Words can have strong impact and can hurt deeply."
                )
            },
        )
        self.assertNotIn("unmapped_x", result)

    def test_pilot_override_count(self):
        # S4.0 (11) + S4.2 golden-exposure batch (25).
        self.assertEqual(len(HUMAN_COPY_OVERRIDES), 36)

    def test_s42_override_ids_exist_and_raw_text_unchanged(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        s42_ids = [
            "pluto_sq_core_conflict",
            "leo_afflicted_lying_distortion",
            "leo_afflicted_appearance_of_competence",
            "leo_afflicted_ego_interferes_with_facts",
            "leo_afflicted_extreme_stubbornness",
            "leo_afflicted_putting_on_a_show",
            "taurus_bio_afflicted_cognitive_sluggishness",
            "taurus_bio_afflicted_reduced_muted_intuition",
            "taurus_bio_afflicted_weak_abstract_thinking",
            "cancer_bio_afflicted_disregard_for_facts",
            "cancer_bio_afflicted_everyday_momentary_thinking",
            "cancer_bio_afflicted_habit_bound_momentary_reasoning",
            "cancer_bio_afflicted_losing_central_meaning",
            "cancer_bio_afflicted_losing_the_thread",
            "cancer_bio_afflicted_scatter_distractibility",
            "cancer_bio_afflicted_thinking_trapped_by_habits",
            "cancer_bio_afflicted_thinking_trapped_by_outdated_beliefs",
            "cancer_bio_afflicted_loss_of_focus",
            "leo_l7_throwing_dust_in_eyes",
            "leo_l7_lying_source_claim",
            "leo_l7_dev_creative_vision",
            "leo_l7_dev_creativity",
            "leo_l7_dev_hear_others_opinions",
            "uranus_cj_adhd_like_attention_scatter",
            "pisces_l7_dev_distinguish_own_vs_suggested",
        ]
        self.assertEqual(len(s42_ids), 25)
        for fact_id in s42_ids:
            with self.subTest(fact_id=fact_id):
                self.assertIn(fact_id, by_id)
                self.assertIn(fact_id, HUMAN_COPY_OVERRIDES)
                human = HUMAN_COPY_OVERRIDES[fact_id]
                self.assertTrue(human.strip())
                raw = by_id[fact_id].text
                self.assertNotEqual(raw, human)
                fact = _fact(fact_id, raw)
                self.assertEqual(get_human_fact_text(fact), human)
                self.assertEqual(fact.text, raw)

    def test_technical_proxy_and_cyrillic_absent_from_human_display(self):
        scaffolding_ids = [
            "leo_afflicted_lying_distortion",
            "leo_afflicted_putting_on_a_show",
            "taurus_bio_afflicted_cognitive_sluggishness",
            "cancer_bio_afflicted_loss_of_focus",
        ]
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        for fact_id in scaffolding_ids:
            raw = by_id[fact_id].text
            human = get_human_fact_text(_fact(fact_id, raw))
            self.assertIn("hard_aspected proxy", raw)
            self.assertIn("при поражении", raw)
            self.assertNotIn("hard_aspected", human)
            self.assertNotIn("при поражении", human)
            self.assertNotIn("Source affliction tendency", human)
            self.assertNotIn("activated via project", human)

    def test_sensitive_lying_claims_are_tendencies_not_accusations(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        for fact_id in ("leo_l7_lying_source_claim", "leo_afflicted_lying_distortion"):
            human = get_human_fact_text(_fact(fact_id, by_id[fact_id].text)).lower()
            self.assertNotIn("this person lies", human)
            self.assertNotIn("they deceive", human)
            self.assertNotIn("they are dishonest", human)
            self.assertTrue(
                "may" in human or "can" in human or "tendency" in human,
                human,
            )

    def test_development_focus_growth_area_copy(self):
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["leo_l7_dev_hear_others_opinions"],
            "Growth area: listen more carefully to other people's perspectives.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["leo_l7_dev_creative_vision"],
            "Growth area: develop a broader creative vision.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["leo_l7_dev_creativity"],
            "Growth area: strengthen creative expression.",
        )


if __name__ == "__main__":
    unittest.main()
