import unittest

from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_rules import SIGN_UNAVAILABLE_LIMITATION
from app.services.mercury_work_profile import synthesize_mercury_narrative


def _narrative(sign: str, element: str, motion: str = "direct", mercury_house=None, aspects=None):
    return synthesize_mercury_narrative(
        mercury_sign=sign,
        mercury_element=element,
        mercury_motion=motion,
        mercury_house=mercury_house,
        aspects=aspects,
    )


def _combined_text(narrative) -> str:
    return " ".join(
        [
            narrative.thinking,
            narrative.learning,
            narrative.communication,
            narrative.team_value,
            " ".join(narrative.strengths),
            " ".join(narrative.risks),
            " ".join(narrative.possible_roles),
        ]
    )


class MercurySignInterpretationTests(unittest.TestCase):
    def test_aries_rapid_direct_challenger(self):
        n = _narrative("Aries", "fire")
        text = _combined_text(n).lower()

        self.assertIn("fast", n.thinking.lower())
        self.assertIn("immediate", n.thinking.lower())
        self.assertIn("direct", n.communication.lower())
        self.assertIn("Argument Analysis", n.strengths)
        self.assertIn("Weak-Point Detection", n.strengths)
        self.assertIn("Poor Active Listening", n.risks)
        self.assertIn("Hasty Conclusions", n.risks)
        self.assertIn("challenger", n.team_value.lower())
        self.assertIn("incident response", " ".join(n.possible_roles).lower())
        self.assertIn("impulsive / creative", n.thinking.lower())
        self.assertNotIn("house", text)
        self.assertNotIn("dispositor", text)
        self.assertNotIn("aspect", text)

    def test_gemini_connector_and_depth_risk(self):
        n = _narrative("Gemini", "air")

        self.assertIn("Fast Information Processing", n.strengths)
        self.assertIn("Negotiation", n.strengths)
        self.assertIn("Technical Explanation", n.strengths)
        self.assertIn("connector", n.team_value.lower())
        self.assertIn("Scattered Attention", n.risks)
        self.assertIn("Loss of Depth", n.risks)
        self.assertIn("logical / abstract", n.thinking.lower())
        self.assertIn("working-memory", n.thinking.lower())

    def test_virgo_precision_and_big_picture_risk(self):
        n = _narrative("Virgo", "earth")

        self.assertIn("Precision Analysis", n.strengths)
        self.assertIn("Detail Verification", n.strengths)
        self.assertIn("Debugging", n.strengths)
        self.assertIn("Losing the Big Picture", n.risks)
        self.assertIn("Excessive Detail", n.risks)
        self.assertIn("practical / applied", n.thinking.lower())
        self.assertTrue(any("qa" in role.lower() or "validation" in role.lower() for role in n.possible_roles))

    def test_sagittarius_conceptualizer_and_precision_risk(self):
        n = _narrative("Sagittarius", "fire")

        self.assertIn("Big-Picture Thinking", n.strengths)
        self.assertIn("Conceptual Thinking", n.strengths)
        self.assertIn("why", n.thinking.lower())
        self.assertIn("teach", n.learning.lower())
        self.assertIn("Detail Neglect", n.risks)
        self.assertIn("Precision Errors", n.risks)
        self.assertIn("conceptualizer", n.team_value.lower())
        self.assertIn("explorer", n.team_value.lower())

    def test_scorpio_investigation_and_criticality(self):
        n = _narrative("Scorpio", "water")

        self.assertIn("Deep Investigation", n.strengths)
        self.assertIn("Root-Cause Analysis", n.strengths)
        self.assertIn("Excessive Criticality", n.risks)
        self.assertIn("Over-investigation", n.risks)
        self.assertIn("investigator", n.team_value.lower())
        self.assertIn("emotional / image-based", n.thinking.lower())


class MercuryRetrogradeModifierTests(unittest.TestCase):
    def test_retrograde_adds_without_replacing_sign(self):
        direct = _narrative("Aries", "fire", "direct")
        rx = _narrative("Aries", "fire", "retrograde")

        self.assertIn("fast", direct.thinking.lower())
        self.assertIn("fast", rx.thinking.lower())
        self.assertIn("Argument Analysis", direct.strengths)
        self.assertIn("Argument Analysis", rx.strengths)
        self.assertIn("challenger", rx.team_value.lower())
        self.assertEqual(direct.team_value, rx.team_value)
        self.assertEqual(direct.possible_roles, rx.possible_roles)

        self.assertIn("inward", rx.thinking.lower())
        self.assertIn("revisit", rx.thinking.lower())
        self.assertIn("repetition", rx.learning.lower())
        self.assertIn("written", rx.communication.lower())
        self.assertIn("Reflective Thinking", rx.strengths)
        self.assertIn("Reprocessing and Refinement", rx.strengths)
        self.assertIn("Unconventional Problem Solving", rx.strengths)
        self.assertIn("Slower Spontaneous Response", rx.risks)
        self.assertIn("Verbal Expression May Lag Behind Internal Thought", rx.risks)

        self.assertNotIn("Reflective Thinking", direct.strengths)
        self.assertNotIn("inward", direct.thinking.lower())
        self.assertNotIn("worse", rx.thinking.lower())
        self.assertNotIn("low intelligence", _combined_text(rx).lower())

    def test_unknown_motion_does_not_add_direct_bonus(self):
        known_direct = _narrative("Virgo", "earth", "direct")
        unknown_motion = _narrative("Virgo", "earth", None)

        self.assertEqual(known_direct.thinking, unknown_motion.thinking)
        self.assertEqual(known_direct.strengths, unknown_motion.strengths)
        self.assertNotIn("Reflective Thinking", unknown_motion.strengths)


class MercuryUnavailableAndUnknownTimeTests(unittest.TestCase):
    def test_missing_sign_returns_empty_interpretation(self):
        n = synthesize_mercury_narrative(
            mercury_sign=None,
            mercury_element=None,
            mercury_motion="direct",
        )
        self.assertEqual(n.thinking, "")
        self.assertEqual(n.learning, "")
        self.assertEqual(n.communication, "")
        self.assertEqual(n.strengths, [])
        self.assertEqual(n.risks, [])
        self.assertEqual(n.team_value, "")
        self.assertEqual(n.possible_roles, [])
        self.assertEqual(n.extra_limitations, [SIGN_UNAVAILABLE_LIMITATION])

    def test_unknown_time_without_houses_still_interprets_sign(self):
        factors = MercurySourceFactors(
            birth_time_known=False,
            mercury_sign="Virgo",
            mercury_element="earth",
            mercury_longitude=None,
            mercury_motion="direct",
            mercury_house=None,
            house_system_used=None,
            aspects=[MercuryAspect(planet="Saturn", type="square", orb_deg=None)],
            major_dispositor="Mercury",
            minor_dispositor=None,
            major_dispositor_sign="Virgo",
            minor_dispositor_sign=None,
            major_dispositor_house=None,
            minor_dispositor_house=None,
        )
        n = synthesize_mercury_narrative(
            mercury_sign=factors.mercury_sign,
            mercury_element=factors.mercury_element,
            mercury_motion=factors.mercury_motion,
            mercury_house=factors.mercury_house,
            aspects=factors.aspects,
        )
        self.assertTrue(n.thinking)
        self.assertIn("Precision Analysis", n.strengths)
        self.assertIn("Losing the Big Picture", n.risks)
        combined = _combined_text(n).lower()
        self.assertNotIn("house", combined)
        self.assertNotIn("saturn", combined)
        self.assertNotIn("dispositor", combined)
        self.assertIsNone(factors.mercury_house)


if __name__ == "__main__":
    unittest.main()
