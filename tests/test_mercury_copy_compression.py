"""M9.5D — Human copy compression tests for Mercury Deep Narrative."""

from __future__ import annotations

import re
import unittest
from datetime import date, time

from app.schemas.mercury_source_profile import MercurySourceProfileRequest
from app.services.mercury_deep_narrative import DEBUG_PHRASE_MARKERS, tag_phrase
from app.services.mercury_deep_profile import build_mercury_deep_profile
from app.services.mercury_source_profile import build_mercury_source_profile


AVDEY = dict(
    birth_date=date(1986, 7, 14),
    birth_time=time(7, 10),
    birth_place="Simferopol, Ukraine",
)

RAW_KEY_RE = re.compile(r"(sign:|house:|motion:|aspect:)")


def _avdey_deep():
    profile = build_mercury_source_profile(MercurySourceProfileRequest(**AVDEY))
    return profile, build_mercury_deep_profile(profile)


class MercuryCopyCompressionTests(unittest.TestCase):
    def test_summary_subsections_do_not_repeat_dominant_summary_theme(self):
        _, deep = _avdey_deep()
        narrative = deep.sign.narrative
        self.assertIsNotNone(narrative)
        assert narrative is not None
        summary_l = narrative.summary.lower()
        # Summary should be a single integrated sentence, not pasted subsections.
        self.assertNotIn("thinking tends toward", summary_l)
        self.assertNotIn("communication tends toward", summary_l)
        for sub in narrative.subsections:
            if sub.key not in {"thinking", "communication", "learning"}:
                continue
            # Subsection text should not restate the whole summary phrase block.
            overlap_tokens = [
                token
                for token in ("presentation-oriented communication",)
                if token in summary_l and token in sub.text.lower()
            ]
            if sub.key == "communication":
                self.assertEqual(
                    overlap_tokens,
                    [],
                    msg="Communication subsection restates summary theme",
                )

    def test_source_facts_remain_intact(self):
        profile, deep = _avdey_deep()
        self.assertEqual(
            set(deep.sign.fact_ids),
            {fact.id for fact in profile.sign_facts if fact.activated},
        )
        self.assertIn("leo_l7_lying_source_claim", deep.sign.fact_ids)
        self.assertIn("leo_afflicted_extreme_stubbornness", deep.sign.fact_ids)
        self.assertIn("h1_special_relevance_siblings", deep.house.fact_ids)

    def test_aspect_paragraph_does_not_enumerate_full_add_list(self):
        _, deep = _avdey_deep()
        pluto = next(
            block
            for block in deep.aspects
            if block.identity.factor_key == "square_Pluto"
        )
        statement = (pluto.interaction.statement or "").lower()
        labels = [item.label.lower() for item in pluto.interaction.adds if item.label]
        self.assertGreaterEqual(len(labels), 4)
        echoed = sum(1 for label in labels if label in statement)
        self.assertLess(echoed, len(labels))
        self.assertNotIn("among other themes", statement)
        # Structured detail still lists all ADD themes.
        self.assertEqual(len(pluto.interaction.adds), len(labels))

    def test_human_labels_contain_no_raw_machine_keys(self):
        _, deep = _avdey_deep()
        for block in deep.aspects:
            for item in block.interaction.adds:
                self.assertFalse(item.label.endswith("_"))
                self.assertNotIn("_", item.label.replace(" ", ""))
                self.assertNotRegex(item.label, RAW_KEY_RE)
            statement = block.interaction.statement or ""
            self.assertNotRegex(statement, RAW_KEY_RE)
            self.assertNotIn(" vs ", statement.lower())

    def test_integrated_primary_text_has_no_provenance_debug_phrasing(self):
        _, deep = _avdey_deep()
        self.assertTrue(deep.integrated)
        self.assertLessEqual(len(deep.integrated), 4)
        for item in deep.integrated:
            lowered = item.text.lower()
            for marker in DEBUG_PHRASE_MARKERS:
                self.assertNotIn(marker, lowered)
            self.assertNotRegex(item.text, RAW_KEY_RE)
            self.assertTrue(item.supporting_fact_ids)
            self.assertTrue(item.provenance_keys)

    def test_every_human_sentence_remains_traceable(self):
        _, deep = _avdey_deep()
        for block in (deep.sign, deep.house, deep.motion):
            if not block.narrative:
                continue
            self.assertTrue(block.narrative.supporting_fact_ids)
            for sub in block.narrative.subsections:
                self.assertTrue(sub.supporting_fact_ids)
        for block in deep.aspects:
            if block.interaction.available:
                self.assertTrue(block.interaction.supporting_fact_ids)
                self.assertTrue(block.interaction.statement)
        for item in deep.integrated:
            self.assertTrue(item.supporting_fact_ids)

    def test_conditional_ownership_unchanged(self):
        _, deep = _avdey_deep()
        narrative = deep.sign.narrative
        assert narrative is not None
        self.assertIn(
            "leo_afflicted_extreme_stubbornness",
            narrative.conditional_fact_ids,
        )
        self.assertNotIn(
            "leo_afflicted_extreme_stubbornness",
            narrative.supporting_fact_ids,
        )
        conditional = next(
            item for item in narrative.subsections if item.key == "conditional"
        )
        self.assertIn("hard aspects", conditional.text.lower())

    def test_unknown_time_behavior_unchanged(self):
        natal = dict(birth_date=AVDEY["birth_date"], birth_place=AVDEY["birth_place"])
        deep = build_mercury_deep_profile(
            build_mercury_source_profile(MercurySourceProfileRequest(**natal))
        )
        self.assertEqual(deep.house.availability, "unavailable")
        self.assertIsNone(deep.house.narrative)
        self.assertEqual(deep.house.fact_ids, [])

    def test_idea_appropriation_humanized(self):
        self.assertIn("adopting", tag_phrase("idea_appropriation"))
        self.assertNotEqual(tag_phrase("idea_appropriation"), "idea appropriation")

    def test_awkward_presentation_labels_humanized(self):
        self.assertEqual(tag_phrase("dust_in_eyes"), "misleading impression risk")
        self.assertEqual(
            tag_phrase("lordly_sibling_position"),
            "a dominant role among siblings",
        )
        self.assertNotIn("dust in the eyes", tag_phrase("dust_in_eyes"))
        self.assertNotIn("lordly", tag_phrase("lordly_sibling_position"))


if __name__ == "__main__":
    unittest.main()
