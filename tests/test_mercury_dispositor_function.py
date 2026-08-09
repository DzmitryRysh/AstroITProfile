import unittest

from app.schemas.mercury_work_profile import PlanetAspect
from app.services.mercury_rules import effective_dispositor_condition_state
from app.services.mercury_work_profile import synthesize_mercury_narrative


def _asp(planet: str, aspect_type: str) -> PlanetAspect:
    return PlanetAspect(planet=planet, type=aspect_type, orb_deg=1.2)


def _n(
    sign: str,
    element: str,
    *,
    major=None,
    minor=None,
    major_aspects=None,
    minor_aspects=None,
    house=None,
    mercury_aspects=None,
):
    return synthesize_mercury_narrative(
        mercury_sign=sign,
        mercury_element=element,
        mercury_motion="direct",
        mercury_house=house,
        aspects=mercury_aspects,
        major_dispositor=major,
        minor_dispositor=minor,
        major_dispositor_aspects=major_aspects,
        minor_dispositor_aspects=minor_aspects,
    )


class DispositorConditionStateTests(unittest.TestCase):
    def test_supported_when_harmonious_dominates(self):
        self.assertEqual(
            effective_dispositor_condition_state(
                [_asp("Sun", "trine"), _asp("Venus", "sextile")]
            ),
            "supported",
        )

    def test_pressured_when_tense_dominates(self):
        self.assertEqual(
            effective_dispositor_condition_state(
                [_asp("Mars", "square"), _asp("Saturn", "opposition")]
            ),
            "pressured",
        )

    def test_mixed_when_both_sides_equal(self):
        self.assertEqual(
            effective_dispositor_condition_state(
                [_asp("Sun", "trine"), _asp("Mars", "square")]
            ),
            "mixed",
        )

    def test_neutral_without_meaningful_aspects(self):
        self.assertEqual(effective_dispositor_condition_state([]), "neutral")

    def test_tense_conjunction_targets_count_as_tense(self):
        for planet in ("Mars", "Saturn", "Uranus", "Neptune", "Pluto"):
            self.assertEqual(
                effective_dispositor_condition_state([_asp(planet, "conjunction")]),
                "pressured",
                msg=planet,
            )

    def test_venus_or_jupiter_conjunction_is_not_automatically_harmonious(self):
        self.assertEqual(
            effective_dispositor_condition_state([_asp("Venus", "conjunction")]),
            "neutral",
        )
        self.assertEqual(
            effective_dispositor_condition_state([_asp("Jupiter", "conjunction")]),
            "neutral",
        )
        self.assertEqual(
            effective_dispositor_condition_state([_asp("Sun", "conjunction")]),
            "neutral",
        )


class DispositorFunctionSynthesisTests(unittest.TestCase):
    def test_sagittarius_jupiter_adds_meaning_expansion_modifier(self):
        n = _n(
            "Sagittarius",
            "fire",
            major="Jupiter",
            major_aspects=[_asp("Sun", "trine"), _asp("Venus", "sextile")],
        )
        text = n.thinking.lower()
        self.assertIn("why", text)
        self.assertIn("meaning", text)
        self.assertTrue("expand" in text or "expansion" in text or "transmitting knowledge" in text)
        self.assertIn("conceptualizer", n.team_value.lower())
        self.assertNotIn("Action-Oriented Thinking", n.strengths)
        self.assertEqual(n.strengths.count("Big-Picture Thinking"), 1)
        self.assertEqual(n.strengths.count("Conceptual Thinking"), 1)
        self.assertNotIn("Meaning-Oriented Thinking", n.strengths)
        self.assertNotIn("Knowledge Transfer", n.strengths)

    def test_sagittarius_jupiter_major_neptune_minor_stays_subordinate(self):
        n = _n(
            "Sagittarius",
            "fire",
            major="Jupiter",
            minor="Neptune",
            major_aspects=[_asp("Sun", "trine")],
            minor_aspects=[_asp("Venus", "sextile")],
        )
        thinking = n.thinking
        self.assertIn("meaning", thinking.lower())
        self.assertTrue(
            "imaginative" in thinking.lower() or "associative" in thinking.lower()
        )
        self.assertLess(thinking.lower().find("meaning"), thinking.lower().find("secondary"))
        jupiter_span = thinking.lower().find("secondary") - thinking.lower().find("meaning")
        self.assertGreater(jupiter_span, 20)
        self.assertNotIn("half jupiter", thinking.lower())
        self.assertNotIn("half neptune", thinking.lower())

    def test_aries_mars_reinforces_action_without_duplicate_labels(self):
        base = _n("Aries", "fire")
        n = _n("Aries", "fire", major="Mars", major_aspects=[_asp("Sun", "trine")])
        self.assertIn("action", n.thinking.lower())
        self.assertIn("Rapid Problem Response", n.strengths)
        self.assertNotIn("Action-Oriented Thinking", n.strengths)
        self.assertNotIn("Decisive Problem Response", n.strengths)
        self.assertNotIn("Premature Action Bias", n.risks)
        self.assertIn("Hasty Conclusions", n.risks)
        self.assertEqual(n.possible_roles, base.possible_roles)
        self.assertIn("challenger", n.team_value.lower())

    def test_scorpio_pluto_reinforces_depth_without_duplication(self):
        n = _n("Scorpio", "water", major="Pluto", major_aspects=[_asp("Sun", "trine")])
        self.assertIn("depth", n.thinking.lower())
        self.assertTrue(
            "root-cause" in n.thinking.lower()
            or "investigation" in n.thinking.lower()
            or "investigative" in n.thinking.lower()
        )
        self.assertIn("Deep Investigation", n.strengths)
        self.assertNotIn("Investigative Depth", n.strengths)
        self.assertIn("Over-investigation", n.risks)
        self.assertNotIn("Over-Control or Over-Investigation", n.risks)

    def test_capricorn_saturn_reinforces_structure_without_duplicate_labels(self):
        n = _n("Capricorn", "earth", major="Saturn", major_aspects=[_asp("Sun", "trine")])
        self.assertIn("structure", n.thinking.lower())
        self.assertIn("Structured Reasoning", n.strengths)
        self.assertNotIn("Structured Thinking", n.strengths)
        self.assertIn("Rigidity", n.risks)
        self.assertNotIn("Cognitive Rigidity", n.risks)
        self.assertIn("Discipline", n.strengths)

    def test_gemini_self_dispositor_adds_no_second_layer(self):
        base = _n("Gemini", "air")
        n = _n("Gemini", "air", major="Mercury", major_aspects=[_asp("Sun", "trine")])
        self.assertEqual(n.thinking, base.thinking)
        self.assertEqual(n.learning, base.learning)
        self.assertEqual(n.communication, base.communication)
        self.assertEqual(n.strengths, base.strengths)
        self.assertEqual(n.risks, base.risks)
        self.assertEqual(n.team_value, base.team_value)
        self.assertEqual(n.possible_roles, base.possible_roles)
        self.assertNotIn("deeper routing", n.thinking.lower())

    def test_supported_condition_wording(self):
        n = _n(
            "Taurus",
            "earth",
            major="Jupiter",
            major_aspects=[_asp("Sun", "trine"), _asp("Venus", "sextile")],
        )
        self.assertEqual(
            effective_dispositor_condition_state([_asp("Sun", "trine"), _asp("Venus", "sextile")]),
            "supported",
        )
        self.assertIn("meaning", n.thinking.lower())
        self.assertIn("favors", n.thinking.lower())
        self.assertNotIn("harder to regulate", n.thinking.lower())
        self.assertNotIn("good planet", n.thinking.lower())
        self.assertNotIn("strong planet", n.thinking.lower())

    def test_pressured_condition_adds_regulation_language(self):
        n = _n(
            "Sagittarius",
            "fire",
            major="Jupiter",
            major_aspects=[_asp("Mars", "square"), _asp("Saturn", "opposition")],
        )
        self.assertIn("harder to regulate", n.thinking.lower())
        self.assertIn("over-expansion", n.thinking.lower())
        self.assertIn("why", n.thinking.lower())
        self.assertIn("Precision Errors", n.risks)
        self.assertLessEqual(n.risks.count("Over-expansion"), 1)
        self.assertNotIn("bad planet", n.thinking.lower())
        self.assertNotIn("weak planet", n.thinking.lower())

    def test_mixed_condition_keeps_both_sides(self):
        n = _n(
            "Taurus",
            "earth",
            major="Jupiter",
            major_aspects=[_asp("Sun", "trine"), _asp("Mars", "square")],
        )
        text = n.thinking.lower()
        self.assertIn("meaning", text)
        self.assertTrue("mixed" in text or "both" in text or "grounding" in text)
        self.assertNotIn("good planet", text)

    def test_neutral_condition_avoids_invented_judgment(self):
        n = _n("Taurus", "earth", major="Jupiter", major_aspects=[])
        text = n.thinking.lower()
        self.assertIn("meaning", text)
        self.assertNotIn("favors", text)
        self.assertNotIn("harder to regulate", text)
        self.assertNotIn("good", text)
        self.assertNotIn("bad", text)
        self.assertNotIn("strong planet", text)

    def test_possible_roles_unchanged_by_dispositor_logic(self):
        base = _n("Sagittarius", "fire")
        n = _n(
            "Sagittarius",
            "fire",
            major="Jupiter",
            minor="Neptune",
            major_aspects=[_asp("Sun", "trine")],
            minor_aspects=[_asp("Mars", "square")],
        )
        self.assertEqual(n.possible_roles, base.possible_roles)


if __name__ == "__main__":
    unittest.main()
