"""Presentation-only glance cards for HOW YOU THINK (M8.5)."""

from __future__ import annotations

import inspect
import unittest
from datetime import date, time

from app.schemas.mercury_source_profile import MercurySourceProfileRequest
from app.services.mercury_human_copy_catalog import (
    STATUS_APPROVED_OVERRIDE,
    STATUS_APPROVED_RAW,
    derive_review_status,
)
from app.services.mercury_profile_synthesis import (
    build_mercury_profile_synthesis,
    serialize_mercury_profile_synthesis,
)
from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS
from app.services.mercury_source_profile import build_mercury_source_profile
from app.services.mercury_think_glance import (
    GLANCE_COMMUNICATION,
    GLANCE_LEARNING,
    GLANCE_THINKING,
    GLANCE_WATCHOUT,
    MAX_GLANCE_CARDS,
    build_mercury_think_glance,
)
from app.services.person_perspective import build_person_perspective


AVDEY = dict(
    birth_date=date(1986, 7, 14),
    birth_time=time(7, 10),
    birth_place="Simferopol, Ukraine",
)
VLAD = dict(
    birth_date=date(1986, 5, 16),
    birth_time=time(15, 0),
    birth_place="Dnipro, Ukraine",
)
DZMITRY = dict(
    birth_date=date(1985, 11, 12),
    birth_time=time(14, 15),
    birth_place="Zhodino, Belarus",
)


def _synthesis(**kwargs):
    profile = build_mercury_source_profile(MercurySourceProfileRequest(**kwargs))
    return build_mercury_profile_synthesis(profile)


class MercuryThinkGlanceTests(unittest.TestCase):
    def test_glance_is_not_repeat_only(self):
        synthesis = _synthesis(**DZMITRY)
        cards = build_mercury_think_glance(synthesis)
        self.assertGreaterEqual(len(cards), 3)
        repeat_only = all(
            card.fact_ids
            and all(
                fact_id in {
                    fid
                    for signal in synthesis.strongest_patterns
                    for fid in signal.fact_ids
                }
                for fact_id in card.fact_ids
            )
            for card in cards
        )
        self.assertFalse(repeat_only)

    def test_dzmitry_sign_baseline_and_recurring_signals_remain_separate(self):
        synthesis = _synthesis(**DZMITRY)
        cards = {card.key: card for card in build_mercury_think_glance(synthesis)}
        self.assertEqual(
            list(cards),
            [GLANCE_THINKING, GLANCE_COMMUNICATION, GLANCE_LEARNING, GLANCE_WATCHOUT],
        )
        self.assertEqual(cards[GLANCE_THINKING].fact_ids, ("sag_thinks_in_categories_globally",))
        self.assertEqual(
            cards[GLANCE_COMMUNICATION].fact_ids,
            ("sag_speaks_like_preacher_agitator_philosopher",),
        )
        self.assertEqual(
            cards[GLANCE_LEARNING].fact_ids,
            ("sag_learning_pass_knowledge_to_others",),
        )
        self.assertEqual(
            cards[GLANCE_WATCHOUT].fact_ids,
            ("sag_calculation_errors_neglect_precision",),
        )
        repeats = [item.signal for item in synthesis.strongest_patterns]
        self.assertEqual(repeats, ["persuasion", "foreign_languages", "teaching"])
        glance_ids = {fact_id for card in cards.values() for fact_id in card.fact_ids}
        self.assertNotIn("mars_tr_persuasive", glance_ids)
        self.assertNotIn("jupiter_sx_native_and_foreign_languages", glance_ids)

    def test_baseline_sign_can_enter_without_repeat(self):
        synthesis = _synthesis(**DZMITRY)
        thinking = next(card for card in build_mercury_think_glance(synthesis) if card.key == GLANCE_THINKING)
        fact = synthesis.facts_by_id[thinking.fact_ids[0]]
        self.assertEqual(fact.factor_type, "sign")
        self.assertNotIn(fact.id, synthesis.strongest_patterns[0].fact_ids)

    def test_max_four_glance_cards(self):
        for kwargs in (AVDEY, VLAD, DZMITRY):
            cards = build_mercury_think_glance(_synthesis(**kwargs))
            self.assertLessEqual(len(cards), MAX_GLANCE_CARDS)

    def test_deterministic_and_serialized_on_api_shape(self):
        synthesis = _synthesis(**DZMITRY)
        first = build_mercury_think_glance(synthesis)
        second = build_mercury_think_glance(synthesis)
        self.assertEqual(first, second)
        payload = serialize_mercury_profile_synthesis(synthesis)
        self.assertEqual(
            [card.key for card in payload.thinking_at_a_glance],
            [card.key for card in first],
        )

    def test_reviewed_human_copy_only(self):
        synthesis = _synthesis(**DZMITRY)
        for card in build_mercury_think_glance(synthesis):
            for fact_id in card.fact_ids:
                status = derive_review_status(fact_id)
                self.assertIn(status, {STATUS_APPROVED_OVERRIDE, STATUS_APPROVED_RAW})

    def test_no_detail_only_categories(self):
        synthesis = _synthesis(**DZMITRY)
        for card in build_mercury_think_glance(synthesis):
            for fact_id in card.fact_ids:
                fact = synthesis.facts_by_id[fact_id]
                self.assertNotIn(fact.category, {"source_specific", "compensation", "secondary_gain"})

    def test_avdey_keeps_core_style_before_repeats(self):
        synthesis = _synthesis(**AVDEY)
        cards = build_mercury_think_glance(synthesis)
        keys = [card.key for card in cards]
        self.assertIn(GLANCE_THINKING, keys)
        thinking = next(card for card in cards if card.key == GLANCE_THINKING)
        fact = synthesis.facts_by_id[thinking.fact_ids[0]]
        self.assertEqual(fact.factor_type, "sign")
        repeats = {item.signal for item in synthesis.strongest_patterns}
        self.assertTrue({"analytical_thinking", "technical_ability", "debate"}.issubset(repeats))

    def test_vlad_keeps_core_style_before_repeats(self):
        synthesis = _synthesis(**VLAD)
        cards = build_mercury_think_glance(synthesis)
        thinking = next(card for card in cards if card.key == GLANCE_THINKING)
        fact = synthesis.facts_by_id[thinking.fact_ids[0]]
        self.assertEqual(fact.factor_type, "sign")
        self.assertEqual(thinking.fact_ids[0], "taurus_productive_thinking")
        repeats = {item.signal for item in synthesis.strongest_patterns}
        self.assertTrue({"analytical_thinking", "foreign_languages", "teaching"}.issubset(repeats))

    def test_cards_use_only_existing_facts_and_tags(self):
        known_tags = {tag for fact in ALL_SOURCE_FACTS for tag in fact.tags}
        for kwargs in (AVDEY, VLAD, DZMITRY):
            synthesis = _synthesis(**kwargs)
            known_ids = set(synthesis.facts_by_id)
            for card in build_mercury_think_glance(synthesis):
                self.assertTrue(set(card.fact_ids) <= known_ids)
                self.assertTrue(set(card.tags) <= known_tags)
                self.assertTrue(card.text)
                self.assertNotIn("score", card.text.lower())

    def test_no_knowledge_or_synthesis_semantic_change(self):
        src = inspect.getsource(build_mercury_think_glance)
        self.assertNotIn("ALL_SOURCE_FACTS", src)
        self.assertNotIn("REPEATED_SIGNAL_SPECS", src)
        self.assertNotIn("HUMAN_COPY_OVERRIDES[", src)

    def test_person_perspective_preserved(self):
        from app.services.mercury_think_glance import render_mercury_glance_text
        from app.services.person_perspective import PERSPECTIVE_SELF

        synthesis = _synthesis(**DZMITRY)
        watchout = next(
            card for card in build_mercury_think_glance(synthesis) if card.key == GLANCE_WATCHOUT
        )
        self_text = render_mercury_glance_text(
            watchout,
            build_person_perspective(name="Dzmitry", sex="male", perspective=PERSPECTIVE_SELF),
        )
        self.assertTrue(self_text.lower().startswith("you "))
        recruiter_text = render_mercury_glance_text(
            watchout,
            build_person_perspective(name="Dzmitry", sex="male"),
        )
        self.assertIn("may", recruiter_text.lower())
        self.assertNotIn("you may", recruiter_text.lower())


if __name__ == "__main__":
    unittest.main()
