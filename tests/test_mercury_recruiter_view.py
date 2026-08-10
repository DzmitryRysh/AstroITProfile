import unittest
from datetime import date, time

from collections import Counter

from app.core.app import create_app
from app.schemas.mercury_work_profile import MercuryAspect, MercuryWorkProfileRequest
from app.services.mercury_recruiter_view import build_recruiter_view
from app.services.mercury_rules import LABEL_THEME, SIGN_RULES
from app.services.mercury_work_profile import (
    build_mercury_work_profile,
    synthesize_mercury_narrative,
)

ASTRO_TERMS = ("mercury", "house", "aspect", "dispositor", "retrograde", "zodiac")
PLACE = "Miami, USA"


def _split_like_sentences(text: str) -> list[str]:
    parts = [p.strip() for p in text.replace("?", ".").replace("!", ".").split(".")]
    return [p for p in parts if p]


def _narrative(sign: str, element: str, motion: str = "direct", house=None, aspects=None):
    return synthesize_mercury_narrative(
        mercury_sign=sign,
        mercury_element=element,
        mercury_motion=motion,
        mercury_house=house,
        aspects=aspects,
    )


def _view(sign: str, element: str, motion: str = "direct", house=None, aspects=None):
    narrative = _narrative(sign, element, motion=motion, house=house, aspects=aspects)
    return build_recruiter_view(mercury_sign=sign, narrative=narrative), narrative


def _all_recruiter_text(view) -> str:
    return " ".join(
        [
            view.thinking_style,
            view.team_function,
            view.team_contribution,
            view.communication_style,
            " ".join(view.top_skills),
            " ".join(view.key_risks),
            " ".join(view.onboarding_guidance),
            " ".join(view.role_directions),
        ]
    ).lower()


class RecruiterViewSignTests(unittest.TestCase):
    def test_aries_challenger_and_haste_listening_risk(self):
        view, narrative = _view("Aries", "fire")
        self.assertIsNotNone(view)
        self.assertLessEqual(len(view.thinking_style.split(".")), 3)
        self.assertIn("fast", view.thinking_style.lower())
        self.assertEqual(view.team_function, "Challenger / Rapid Problem Solver")
        self.assertTrue(
            any("hasty" in r.lower() or "listening" in r.lower() for r in view.key_risks)
        )
        self.assertIn("Hasty Conclusions", view.key_risks)
        self.assertIn("Poor Active Listening", view.key_risks)
        self.assertTrue(narrative.thinking)
        self.assertTrue(narrative.possible_roles)

    def test_gemini_connector_and_processing_skills(self):
        view, _ = _view("Gemini", "air")
        self.assertEqual(view.team_function, "Connector / Communicator")
        self.assertIn("information", view.thinking_style.lower())
        self.assertIn("Fast Information Processing", view.top_skills)
        self.assertTrue(
            any("explanation" in s.lower() or "negotiation" in s.lower() for s in view.top_skills)
        )

    def test_virgo_precision_and_structured_onboarding(self):
        view, _ = _view("Virgo", "earth")
        self.assertEqual(view.team_function, "Precision Analyst / Validator")
        self.assertIn("detail", view.thinking_style.lower())
        self.assertTrue(
            any("precision" in s.lower() or "detail" in s.lower() for s in view.top_skills)
        )
        joined = " ".join(view.onboarding_guidance).lower()
        self.assertTrue("structur" in joined or "document" in joined or "procedure" in joined)
        self.assertTrue("verif" in joined or "checklist" in joined or "diagram" in joined)
        self.assertLessEqual(len(view.onboarding_guidance), 4)

    def test_sagittarius_conceptualizer_keeps_precision_risk(self):
        view, _ = _view("Sagittarius", "fire")
        self.assertEqual(view.team_function, "Conceptualizer / Explorer")
        self.assertIn("big-picture", view.thinking_style.lower())
        self.assertTrue(
            any("precision" in r.lower() or "detail" in r.lower() for r in view.key_risks)
        )

    def test_scorpio_investigator_label(self):
        view, _ = _view("Scorpio", "water")
        self.assertEqual(view.team_function, "Investigator / Root-Cause Analyst")

    def test_capricorn_structurer_label(self):
        view, _ = _view("Capricorn", "earth")
        self.assertEqual(view.team_function, "Structurer / Planner")

    def test_aquarius_explorer_innovator_label(self):
        view, _ = _view("Aquarius", "air")
        self.assertEqual(view.team_function, "Explorer / Innovator")


class RecruiterViewModifierTests(unittest.TestCase):
    def test_retrograde_onboarding_includes_processing_time(self):
        view, _ = _view("Virgo", "earth", motion="retrograde")
        joined = " ".join(view.onboarding_guidance).lower()
        self.assertTrue("revisit" in joined or "reprocess" in joined)
        self.assertTrue("written" in joined or "verbal" in joined)
        self.assertLessEqual(len(view.onboarding_guidance), 5)

    def test_gemini_house_8_keeps_base_and_probing_modifier(self):
        view, _ = _view("Gemini", "air", house=8)
        comm = view.communication_style.lower()
        self.assertTrue(
            "quickly" in comm or "connect" in comm or "explain" in comm,
            comm,
        )
        self.assertTrue("probing" in comm or "sharp" in comm, comm)
        self.assertIn("information", view.thinking_style.lower())
        self.assertEqual(view.team_function, "Connector / Communicator")
        self.assertIn("connect", view.team_contribution.lower())

    def test_aries_house_9_synthesizes_team_contribution(self):
        view, _ = _view("Aries", "fire", house=9)
        text = view.team_contribution
        lower = text.lower()
        self.assertIn("challenge", lower)
        self.assertTrue("conceptual" in lower or "knowledge synthesis" in lower)
        self.assertNotRegex(text, r"(?i)\buseful\b.*\buseful\b")
        self.assertNotRegex(text, r"(?i)\bcan be useful\b.*\buseful\b")
        self.assertLessEqual(len(_split_like_sentences(text)), 2)
        self.assertEqual(view.team_function, "Challenger / Rapid Problem Solver")

    def test_gemini_tense_saturn_keeps_fast_identity_and_guarded_expression(self):
        view, _ = _view(
            "Gemini",
            "air",
            aspects=[MercuryAspect(planet="Saturn", type="square", orb_deg=2.0)],
        )
        text = view.communication_style.lower()
        self.assertTrue("quickly" in text or "connect" in text or "information" in text)
        self.assertTrue("guarded" in text or "self-censor" in text)
        self.assertIn("information", view.thinking_style.lower())

    def test_gemini_tense_saturn_exposes_communication_inhibition_risk(self):
        view, _ = _view(
            "Gemini",
            "air",
            aspects=[MercuryAspect(planet="Saturn", type="square", orb_deg=2.0)],
        )
        self.assertIn("Communication Inhibition", view.key_risks)
        gemini_risks = set(SIGN_RULES["Gemini"].risks)
        self.assertGreaterEqual(sum(1 for item in view.key_risks if item in gemini_risks), 2)
        self.assertLessEqual(len(view.key_risks), 4)

    def test_gemini_baseline_keeps_normal_risk_set(self):
        view, _ = _view("Gemini", "air")
        self.assertNotIn("Communication Inhibition", view.key_risks)
        self.assertEqual(
            view.key_risks,
            [
                "Information Overload",
                "Scattered Attention",
                "Loss of Depth",
                "Boredom With One Long Topic",
            ],
        )

    def test_aries_tense_mars_keeps_direct_base_and_conflict_pressure(self):
        view, _ = _view(
            "Aries",
            "fire",
            aspects=[MercuryAspect(planet="Mars", type="square", orb_deg=1.5)],
        )
        comm = view.communication_style.lower()
        self.assertIn("direct", comm)
        self.assertTrue(
            "interrupt" in comm or "argumentative" in comm or "listening" in comm
            or "attentive" in comm,
            comm,
        )
        risks = " ".join(view.key_risks).lower()
        self.assertIn("hasty", risks)
        self.assertIn("listening", risks)
        self.assertIn("conflict", risks)
        themes = [LABEL_THEME[item] for item in view.key_risks if item in LABEL_THEME]
        counts = Counter(themes)
        for theme in ("haste", "listening", "conflict"):
            self.assertLessEqual(counts[theme], 1, view.key_risks)

    def test_supported_aspect_skill_can_enter_without_replacing_identity(self):
        view, _ = _view(
            "Gemini",
            "air",
            aspects=[MercuryAspect(planet="Venus", type="trine", orb_deg=2.0)],
        )
        self.assertIn("Fast Information Processing", view.top_skills)
        self.assertIn("Diplomatic Communication", view.top_skills)
        gemini_skills = set(SIGN_RULES["Gemini"].strengths)
        self.assertGreaterEqual(sum(1 for item in view.top_skills if item in gemini_skills), 3)
        self.assertLessEqual(len(view.top_skills), 5)

    def test_skill_and_risk_limits_hold_with_modifiers(self):
        view, _ = _view(
            "Gemini",
            "air",
            house=8,
            aspects=[MercuryAspect(planet="Saturn", type="square", orb_deg=2.0)],
        )
        self.assertLessEqual(len(view.top_skills), 5)
        self.assertLessEqual(len(view.key_risks), 4)

    def test_libra_baseline_dedupes_indecision_theme(self):
        view, _ = _view("Libra", "air")
        hesitation = {
            "Indecision",
            "Endless Weighing of Alternatives",
            "Difficulty Taking a Firm Position",
        }
        self.assertLessEqual(sum(1 for item in view.key_risks if item in hesitation), 1)
        self.assertIn("Indecision", view.key_risks)
        self.assertLessEqual(len(view.key_risks), 4)

    def test_libra_neptune_keeps_verification_risks(self):
        view, _ = _view(
            "Libra",
            "air",
            aspects=[MercuryAspect(planet="Neptune", type="square", orb_deg=2.0)],
        )
        self.assertIn("Mental Fog", view.key_risks)
        self.assertIn("Fact-Assumption Confusion", view.key_risks)
        libra_risks = set(SIGN_RULES["Libra"].risks)
        self.assertGreaterEqual(sum(1 for item in view.key_risks if item in libra_risks), 1)
        self.assertLessEqual(len(view.key_risks), 4)

    def test_libra_house_9_neptune_keeps_identity_and_modifier_skill(self):
        view, _ = _view(
            "Libra",
            "air",
            house=9,
            aspects=[MercuryAspect(planet="Neptune", type="square", orb_deg=2.0)],
        )
        libra_risks = set(SIGN_RULES["Libra"].risks)
        self.assertGreaterEqual(sum(1 for item in view.key_risks if item in libra_risks), 1)
        self.assertTrue(
            "Mental Fog" in view.key_risks or "Fact-Assumption Confusion" in view.key_risks
        )
        libra_skills = set(SIGN_RULES["Libra"].strengths)
        self.assertGreaterEqual(sum(1 for item in view.top_skills if item in libra_skills), 2)
        self.assertTrue(
            any(
                item
                in {
                    "Conceptual Learning",
                    "Theory Integration",
                    "Knowledge Filtering",
                    "Imaginative Association",
                }
                for item in view.top_skills
            )
        )
        self.assertLessEqual(len(view.top_skills), 5)
        self.assertLessEqual(len(view.key_risks), 4)

    def test_team_contribution_avoids_duplicated_useful_leads(self):
        for sign, element, house in (
            ("Aries", "fire", 9),
            ("Gemini", "air", 8),
            ("Virgo", "earth", 6),
            ("Sagittarius", "fire", 11),
        ):
            view, _ = _view(sign, element, house=house)
            text = view.team_contribution
            self.assertNotRegex(
                text,
                r"(?i)\b(?:can be )?useful\b.*\buseful\b",
                msg=f"{sign} house {house}: {text}",
            )


class RecruiterViewContractTests(unittest.TestCase):
    def test_unknown_birth_time_still_builds_without_house_wording(self):
        result = build_mercury_work_profile(
            MercuryWorkProfileRequest(birth_date=date(1990, 3, 21), birth_place=PLACE)
        )
        self.assertIsNotNone(result.recruiter_view)
        self.assertFalse(result.source_factors.birth_time_known)
        self.assertIsNone(result.source_factors.mercury_house)
        self.assertNotIn("house", _all_recruiter_text(result.recruiter_view))
        self.assertTrue(result.thinking)
        self.assertTrue(result.source_factors.mercury_sign)

    def test_missing_sign_returns_null_recruiter_view(self):
        narrative = synthesize_mercury_narrative(
            mercury_sign=None,
            mercury_element=None,
            mercury_motion="direct",
        )
        self.assertIsNone(build_recruiter_view(mercury_sign=None, narrative=narrative))

    def test_skill_risk_role_limits(self):
        view, narrative = _view("Gemini", "air")
        self.assertLessEqual(len(view.top_skills), 5)
        self.assertLessEqual(len(view.key_risks), 4)
        self.assertLessEqual(len(view.role_directions), 5)
        self.assertGreaterEqual(len(view.top_skills), 1)
        self.assertGreaterEqual(len(view.key_risks), 1)
        self.assertEqual(view.role_directions, narrative.possible_roles[:5])

    def test_no_astrology_terminology_in_recruiter_view(self):
        for sign, element in (
            ("Aries", "fire"),
            ("Gemini", "air"),
            ("Virgo", "earth"),
            ("Sagittarius", "fire"),
            ("Scorpio", "water"),
            ("Capricorn", "earth"),
            ("Aquarius", "air"),
        ):
            view, _ = _view(sign, element, motion="retrograde", house=9)
            text = _all_recruiter_text(view)
            for term in ASTRO_TERMS:
                self.assertNotIn(term, text.split(), msg=f"{sign} contains {term}")

    def test_legacy_profile_route_still_loads(self):
        app = create_app()
        paths = {getattr(route, "path", None) for route in app.routes}
        self.assertIn("/api/v1/profile", paths)
        self.assertIn("/api/v1/mercury-work-profile", paths)


if __name__ == "__main__":
    unittest.main()
