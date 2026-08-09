import unittest

from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_work_profile import synthesize_mercury_narrative


def _narrative(
    sign: str,
    element: str,
    motion: str = "direct",
    mercury_house=None,
    aspects=None,
):
    return synthesize_mercury_narrative(
        mercury_sign=sign,
        mercury_element=element,
        mercury_motion=motion,
        mercury_house=mercury_house,
        aspects=aspects,
    )


def _text(n) -> str:
    return " ".join(
        [
            n.thinking,
            n.learning,
            n.communication,
            n.team_value,
            " ".join(n.strengths),
            " ".join(n.risks),
            " ".join(n.possible_roles),
        ]
    ).lower()


def _aspect(planet: str, aspect_type: str, orb=1.2) -> MercuryAspect:
    return MercuryAspect(planet=planet, type=aspect_type, orb_deg=orb)


class MercuryHouseContextTests(unittest.TestCase):
    def test_house_9_does_not_erase_aries_or_sagittarius_base(self):
        aries = _narrative("Aries", "fire", mercury_house=9)
        sag = _narrative("Sagittarius", "fire", mercury_house=9)
        aries_base = _narrative("Aries", "fire")
        sag_base = _narrative("Sagittarius", "fire")

        self.assertIn("fast", aries.thinking.lower())
        self.assertIn("challenger", aries.team_value.lower())
        self.assertIn("conceptual", aries.learning.lower() + " " + aries.thinking.lower())
        self.assertEqual(aries.possible_roles, aries_base.possible_roles)

        self.assertIn("why", sag.thinking.lower())
        self.assertIn("conceptualizer", sag.team_value.lower())
        self.assertIn("Precision Errors", sag.risks)
        self.assertIn("theory", sag.learning.lower() + " " + sag.thinking.lower())
        self.assertEqual(sag.possible_roles, sag_base.possible_roles)
        self.assertNotIn("house", _text(aries))
        self.assertNotIn("house", _text(sag))

    def test_house_8_adds_research_context_not_a_profession(self):
        base = _narrative("Gemini", "air")
        h8 = _narrative("Gemini", "air", mercury_house=8)
        text = _text(h8)

        self.assertIn("deep investigation", text)
        self.assertTrue("research" in text or "hidden" in text)
        self.assertTrue(
            "sharp" in text or "tension" in " ".join(h8.risks).lower()
        )
        self.assertEqual(h8.possible_roles, base.possible_roles)
        self.assertNotIn("Security Research", h8.possible_roles)
        self.assertIn("connector", h8.team_value.lower())
        self.assertNotIn("excellent investigator", text)

    def test_house_11_adds_collaborative_learning_context(self):
        n = _narrative("Capricorn", "earth", mercury_house=11)
        text = _text(n)
        self.assertIn("collaborative learning", " ".join(n.strengths).lower() + " " + n.learning.lower())
        self.assertTrue("team" in text or "network" in text or "idea exchange" in text)
        self.assertIn("Endless Debate", n.risks)
        self.assertIn("structure", n.thinking.lower())

    def test_unknown_birth_time_applies_no_house_narrative(self):
        no_house = _narrative("Aries", "fire", mercury_house=None)
        with_house = _narrative("Aries", "fire", mercury_house=11)
        self.assertIn("collaborative", _text(with_house))
        self.assertNotIn("collaborative", _text(no_house))
        self.assertNotIn("idea exchange", _text(no_house))
        self.assertIn("fast", no_house.thinking.lower())
        self.assertEqual(no_house.possible_roles, with_house.possible_roles)


class MercuryAspectModifierTests(unittest.TestCase):
    def test_gemini_tense_saturn_keeps_fast_baseline_and_guards_speech(self):
        n = _narrative("Gemini", "air", aspects=[_aspect("Saturn", "square")])
        text = _text(n)
        self.assertIn("working-memory", n.thinking.lower())
        self.assertIn("Fast Information Processing", n.strengths)
        self.assertIn("connector", n.team_value.lower())
        self.assertIn("guarded", n.communication.lower())
        self.assertIn("Communication Inhibition", n.risks)
        self.assertNotIn("erase", text)
        self.assertIn("information-oriented", n.communication.lower())

    def test_aries_tense_mars_strengthens_haste_without_duplicate_risks(self):
        base = _narrative("Aries", "fire")
        n = _narrative("Aries", "fire", aspects=[_aspect("Mars", "square")])
        self.assertIn("immediate response under pressure", n.thinking.lower())
        self.assertIn("Hasty Conclusions", n.risks)
        self.assertIn("Poor Active Listening", n.risks)
        self.assertIn("Conflict Escalation", n.risks)
        self.assertNotIn("Hasty Action", n.risks)
        self.assertNotIn("Poor Listening Under Pressure", n.risks)
        self.assertNotIn("Conflict-Prone Communication", n.risks)
        self.assertLessEqual(len(n.risks), len(base.risks) + 2)
        self.assertIn("challenger", n.team_value.lower())
        self.assertEqual(n.possible_roles, base.possible_roles)

    def test_harmonious_venus_adds_diplomatic_communication(self):
        n = _narrative("Aries", "fire", aspects=[_aspect("Venus", "trine")])
        self.assertIn("Diplomatic Communication", n.strengths)
        self.assertIn("Tactful Expression", n.strengths)
        self.assertIn("tact", n.communication.lower())
        self.assertIn("fast", n.thinking.lower())

    def test_harmonious_mars_adds_thought_to_action_strengths(self):
        n = _narrative("Virgo", "earth", aspects=[_aspect("Mars", "sextile")])
        self.assertIn("Fast Analytical Response", n.strengths)
        self.assertIn("Thought-to-Action Execution", n.strengths)
        self.assertIn("Persuasive Direct Communication", n.strengths)
        self.assertIn("Precision Analysis", n.strengths)

    def test_tense_jupiter_adds_overload_scope_message_risks(self):
        n = _narrative("Taurus", "earth", aspects=[_aspect("Jupiter", "opposition")])
        self.assertIn("Information Overload", n.risks)
        self.assertIn("Scope Inflation", n.risks)
        self.assertIn("Loss of Core Message", n.risks)
        self.assertIn("deliberate", n.thinking.lower())

    def test_tense_uranus_adds_insight_and_fragmented_attention(self):
        n = _narrative("Capricorn", "earth", aspects=[_aspect("Uranus", "conjunction")])
        self.assertIn("Non-Linear Problem Solving", n.strengths)
        self.assertIn("Unexpected Insight", n.strengths)
        self.assertIn("Fragmented Attention", n.risks)
        self.assertIn("Mental Overstimulation", n.risks)
        self.assertNotIn("adhd", _text(n))
        self.assertIn("structured", n.thinking.lower())

    def test_tense_neptune_adds_verification_risk_without_mystical_wording(self):
        n = _narrative("Virgo", "earth", aspects=[_aspect("Neptune", "square")])
        text = _text(n)
        self.assertIn("Fact-Assumption Confusion", n.risks)
        self.assertIn("Mental Fog", n.risks)
        self.assertIn("verification", text)
        self.assertNotIn("occult", text)
        self.assertNotIn("psychic", text)
        self.assertNotIn("medical", text)
        self.assertNotIn("diagnos", text)
        self.assertIn("Precision Analysis", n.strengths)

    def test_tense_pluto_adds_deep_investigation_and_over_fixation(self):
        n = _narrative("Taurus", "earth", aspects=[_aspect("Pluto", "opposition")])
        self.assertIn("Deep Investigation", n.strengths)
        self.assertIn("Over-Fixation", n.risks)
        self.assertIn("Suspicion Bias", n.risks)
        self.assertIn("Mental Pressure", n.risks)
        self.assertIn("grounded", n.thinking.lower())

    def test_unsupported_trine_pluto_does_not_change_narrative(self):
        base = _narrative("Taurus", "earth")
        unsupported = _narrative(
            "Taurus",
            "earth",
            aspects=[_aspect("Pluto", "trine")],
        )
        self.assertEqual(unsupported.thinking, base.thinking)
        self.assertEqual(unsupported.learning, base.learning)
        self.assertEqual(unsupported.communication, base.communication)
        self.assertEqual(unsupported.strengths, base.strengths)
        self.assertEqual(unsupported.risks, base.risks)
        self.assertEqual(unsupported.team_value, base.team_value)
        self.assertEqual(unsupported.possible_roles, base.possible_roles)

    def test_dispositor_presence_does_not_alter_narrative(self):
        shared = dict(
            birth_time_known=True,
            mercury_sign="Aries",
            mercury_element="fire",
            mercury_longitude=10.0,
            mercury_motion="direct",
            mercury_house=9,
            house_system_used="P",
            aspects=[_aspect("Venus", "sextile")],
        )
        a = MercurySourceFactors(
            **shared,
            major_dispositor="Mars",
            minor_dispositor="Pluto",
            major_dispositor_sign="Aquarius",
            minor_dispositor_sign="Scorpio",
            major_dispositor_house=6,
            minor_dispositor_house=4,
        )
        b = MercurySourceFactors(
            **shared,
            major_dispositor="Venus",
            minor_dispositor="Saturn",
            major_dispositor_sign="Taurus",
            minor_dispositor_sign="Capricorn",
            major_dispositor_house=2,
            minor_dispositor_house=10,
        )
        na = synthesize_mercury_narrative(
            mercury_sign=a.mercury_sign,
            mercury_element=a.mercury_element,
            mercury_motion=a.mercury_motion,
            mercury_house=a.mercury_house,
            aspects=a.aspects,
        )
        nb = synthesize_mercury_narrative(
            mercury_sign=b.mercury_sign,
            mercury_element=b.mercury_element,
            mercury_motion=b.mercury_motion,
            mercury_house=b.mercury_house,
            aspects=b.aspects,
        )
        self.assertEqual(na.thinking, nb.thinking)
        self.assertEqual(na.strengths, nb.strengths)
        self.assertEqual(na.risks, nb.risks)
        self.assertEqual(na.team_value, nb.team_value)
        self.assertNotIn("dispositor", _text(na))
        self.assertIn("mars", a.major_dispositor.lower())
        self.assertIn("venus", b.major_dispositor.lower())


if __name__ == "__main__":
    unittest.main()
