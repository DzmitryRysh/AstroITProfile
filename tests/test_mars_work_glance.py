"""Presentation-only glance cards for HOW YOU WORK (M8.1)."""

from __future__ import annotations

import unittest
from datetime import date, time

from app.services.mars_profile_synthesis import (
    build_mars_profile_synthesis,
    serialize_mars_profile_synthesis,
)
from app.services.mars_source_profile import build_mars_source_profile
from app.services.mars_work_glance import (
    GLANCE_EXECUTION,
    GLANCE_PRESSURE,
    GLANCE_SLOWDOWN,
    build_mars_work_glance,
)


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

EXECUTION_TEXT = "Work tends to be deliberate and calculated, with strong focus on the task."
SLOWDOWN_TEXT = "Action may slow through internal hesitation and braking."
PRESSURE_TEXT = "Under pressure, effort may become overloaded."


def _synthesis(**kwargs):
    return build_mars_profile_synthesis(build_mars_source_profile(**kwargs))


class MarsWorkGlanceTests(unittest.TestCase):
    def test_avdey_three_cards_keep_planning_and_hesitation_apart(self):
        synthesis = _synthesis(**AVDEY)
        cards = {card.key: card for card in build_mars_work_glance(synthesis)}
        self.assertEqual(
            list(cards),
            [GLANCE_EXECUTION, GLANCE_SLOWDOWN, GLANCE_PRESSURE],
        )
        self.assertEqual(cards[GLANCE_EXECUTION].text, EXECUTION_TEXT)
        self.assertEqual(cards[GLANCE_EXECUTION].source, "template")
        self.assertEqual(cards[GLANCE_SLOWDOWN].text, SLOWDOWN_TEXT)
        self.assertEqual(cards[GLANCE_PRESSURE].text, PRESSURE_TEXT)
        self.assertEqual(cards[GLANCE_PRESSURE].repeated_signals, ("effort_overload",))
        self.assertNotIn("hesitat", cards[GLANCE_EXECUTION].text.lower())
        self.assertNotIn("plan", cards[GLANCE_SLOWDOWN].text.lower())
        self.assertNotIn("burnout", cards[GLANCE_PRESSURE].text.lower())

    def test_vlad_omits_empty_slowdown_and_pressure(self):
        synthesis = _synthesis(**VLAD)
        cards = build_mars_work_glance(synthesis)
        self.assertEqual([card.key for card in cards], [GLANCE_EXECUTION])
        self.assertEqual(cards[0].text, EXECUTION_TEXT)
        self.assertEqual(cards[0].source, "template")

    def test_dzmitry_falls_back_to_one_reviewed_observation(self):
        synthesis = _synthesis(**DZMITRY)
        cards = {card.key: card for card in build_mars_work_glance(synthesis)}
        self.assertEqual(list(cards), [GLANCE_EXECUTION, GLANCE_SLOWDOWN])
        execution = cards[GLANCE_EXECUTION]
        self.assertEqual(execution.source, "observation")
        self.assertNotEqual(execution.text, EXECUTION_TEXT)
        self.assertEqual(execution.fact_ids, ("mars_libra_ability_to_manage_people",))
        self.assertEqual(
            execution.text,
            synthesis.presentation_text_by_fact_id.get(
                "mars_libra_ability_to_manage_people",
                synthesis.facts_by_id["mars_libra_ability_to_manage_people"].text,
            ),
        )
        slowdown = cards[GLANCE_SLOWDOWN]
        self.assertEqual(slowdown.source, "observation")
        self.assertNotEqual(slowdown.text, SLOWDOWN_TEXT)
        self.assertEqual(slowdown.fact_ids, ("mars_libra_indecision_delayed_choice",))

    def test_cards_use_only_existing_facts_tags_and_repeats(self):
        for kwargs in (AVDEY, VLAD, DZMITRY):
            synthesis = _synthesis(**kwargs)
            known_tags = {tag for fact in synthesis.facts_by_id.values() for tag in fact.tags}
            known_ids = set(synthesis.facts_by_id)
            known_repeats = {item.signal for item in synthesis.repeated_signals}
            for card in build_mars_work_glance(synthesis):
                self.assertTrue(set(card.fact_ids) <= known_ids)
                self.assertTrue(set(card.tags) <= known_tags)
                self.assertTrue(set(card.repeated_signals) <= known_repeats)
                self.assertTrue(card.text)
                self.assertNotIn("score", card.text.lower())

    def test_deterministic_and_serialized_on_api_shape(self):
        synthesis = _synthesis(**AVDEY)
        first = build_mars_work_glance(synthesis)
        second = build_mars_work_glance(synthesis)
        self.assertEqual(first, second)
        payload = serialize_mars_profile_synthesis(synthesis)
        self.assertEqual(
            [card.key for card in payload.work_style_at_a_glance],
            [card.key for card in first],
        )
        self.assertEqual(payload.work_style_at_a_glance[0].text, first[0].text)

    def test_does_not_invent_obstacle_or_score_fields(self):
        synthesis = _synthesis(**AVDEY)
        by_key = {item.key: item for item in synthesis.sections}
        self.assertEqual(by_key["how_you_handle_obstacles"].fact_count, 0)
        cards = build_mars_work_glance(synthesis)
        blob = " ".join(card.text.lower() for card in cards)
        self.assertNotIn("obstacle ability", blob)
        self.assertNotIn("productivity", blob)
        self.assertFalse(hasattr(cards[0], "score"))


if __name__ == "__main__":
    unittest.main()
