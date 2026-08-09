import unittest
from datetime import date, time

from pydantic import ValidationError

from app.core.app import create_app
from app.schemas.mercury_work_profile import MercuryWorkProfileRequest
from app.schemas.profile import ProfileRequest, ProfileResponse
from app.services.astro_service import AstroService
from app.services.mercury_facts import (
    MERCURY_DISPOSITORS,
    DayProbeSnapshot,
    merge_unknown_time_probes,
)
from app.services.mercury_work_profile import build_mercury_work_profile


SIGNS = set(MERCURY_DISPOSITORS)
ELEMENTS = {"fire", "earth", "air", "water"}
MOTIONS = {"direct", "retrograde"}
ASPECT_TYPES = {"conjunction", "sextile", "square", "trine", "opposition"}

PLACE = "Miami, USA"
BIRTH_DATE = date(1990, 3, 21)
BIRTH_TIME = time(14, 30)


class MercuryWorkProfileExactTimeTests(unittest.TestCase):
    def test_exact_time_populates_mercury_facts(self):
        payload = MercuryWorkProfileRequest(
            birth_date=BIRTH_DATE,
            birth_place=PLACE,
            birth_time=BIRTH_TIME,
        )
        result = build_mercury_work_profile(payload)
        factors = result.source_factors

        self.assertEqual(result.thinking, "")
        self.assertEqual(result.learning, "")
        self.assertEqual(result.communication, "")
        self.assertEqual(result.strengths, [])
        self.assertEqual(result.risks, [])
        self.assertEqual(result.team_value, "")
        self.assertEqual(result.possible_roles, [])

        self.assertTrue(factors.birth_time_known)
        self.assertIn(factors.mercury_sign, SIGNS)
        self.assertEqual(
            factors.mercury_element,
            {
                "Aries": "fire",
                "Leo": "fire",
                "Sagittarius": "fire",
                "Taurus": "earth",
                "Virgo": "earth",
                "Capricorn": "earth",
                "Gemini": "air",
                "Libra": "air",
                "Aquarius": "air",
                "Cancer": "water",
                "Scorpio": "water",
                "Pisces": "water",
            }[factors.mercury_sign],
        )
        self.assertIsInstance(factors.mercury_longitude, float)
        self.assertIn(factors.mercury_motion, MOTIONS)
        self.assertIsInstance(factors.mercury_house, int)
        self.assertGreaterEqual(factors.mercury_house, 1)
        self.assertLessEqual(factors.mercury_house, 12)
        self.assertIsInstance(factors.house_system_used, str)
        self.assertTrue(factors.house_system_used)

        self.assertIn(factors.major_dispositor, MERCURY_DISPOSITORS[factors.mercury_sign])
        self.assertEqual(
            factors.major_dispositor,
            MERCURY_DISPOSITORS[factors.mercury_sign][0],
        )
        self.assertEqual(
            factors.minor_dispositor,
            MERCURY_DISPOSITORS[factors.mercury_sign][1],
        )
        self.assertIn(factors.major_dispositor_sign, SIGNS)
        self.assertIsInstance(factors.major_dispositor_house, int)
        if factors.minor_dispositor:
            self.assertIn(factors.minor_dispositor_sign, SIGNS)
            self.assertIsInstance(factors.minor_dispositor_house, int)

        self.assertGreaterEqual(len(factors.aspects), 1)
        for aspect in factors.aspects:
            self.assertNotEqual(aspect.planet, "Mercury")
            self.assertIn(aspect.type, ASPECT_TYPES)
            self.assertIsInstance(aspect.orb_deg, float)


class MercuryWorkProfileUnknownTimeTests(unittest.TestCase):
    def test_request_works_without_birth_time(self):
        payload = MercuryWorkProfileRequest(
            birth_date=BIRTH_DATE,
            birth_place=PLACE,
        )
        result = build_mercury_work_profile(payload)
        factors = result.source_factors

        self.assertFalse(factors.birth_time_known)
        self.assertIsNone(factors.mercury_house)
        self.assertIsNone(factors.house_system_used)
        self.assertIsNone(factors.mercury_longitude)
        self.assertIsNone(factors.major_dispositor_house)
        self.assertIsNone(factors.minor_dispositor_house)

        self.assertEqual(result.thinking, "")
        self.assertEqual(result.strengths, [])
        self.assertEqual(result.possible_roles, [])

        moon_aspects = [a for a in factors.aspects if a.planet == "Moon"]
        self.assertEqual(moon_aspects, [])
        for aspect in factors.aspects:
            self.assertIsNone(aspect.orb_deg)
            self.assertIn(aspect.type, ASPECT_TYPES)

        self.assertTrue(
            any("houses and angles omitted" in item for item in result.limitations)
        )
        self.assertTrue(
            any("Moon aspects excluded" in item for item in result.limitations)
        )
        self.assertFalse(
            any("minor dispositor" in item.lower() for item in result.limitations)
        )

        if factors.mercury_sign:
            self.assertIn(factors.mercury_sign, SIGNS)
            self.assertEqual(
                factors.major_dispositor,
                MERCURY_DISPOSITORS[factors.mercury_sign][0],
            )

    def test_merge_keeps_only_stable_facts(self):
        stable = DayProbeSnapshot(
            mercury_sign="Virgo",
            mercury_motion="direct",
            planet_signs={
                "Mercury": "Virgo",
                "Venus": "Libra",
                "Sun": "Leo",
            },
            aspect_types={"Venus": "sextile", "Saturn": "square"},
        )
        unstable_sign = DayProbeSnapshot(
            mercury_sign="Libra",
            mercury_motion="direct",
            planet_signs={
                "Mercury": "Libra",
                "Venus": "Libra",
                "Sun": "Leo",
            },
            aspect_types={"Venus": "sextile", "Mars": "trine"},
        )
        factors, limitations = merge_unknown_time_probes(
            [stable, stable, unstable_sign]
        )

        self.assertIsNone(factors.mercury_sign)
        self.assertIsNone(factors.mercury_element)
        self.assertIsNone(factors.major_dispositor)
        self.assertIsNone(factors.mercury_longitude)
        self.assertIsNone(factors.mercury_house)
        self.assertEqual(factors.mercury_motion, "direct")
        self.assertEqual(len(factors.aspects), 1)
        self.assertEqual(factors.aspects[0].planet, "Venus")
        self.assertEqual(factors.aspects[0].type, "sextile")
        self.assertIsNone(factors.aspects[0].orb_deg)
        self.assertTrue(
            any("Mercury sign is not stable" in item for item in limitations)
        )
        self.assertTrue(
            any("Mercury–Saturn aspect is not stable" in item for item in limitations)
        )
        self.assertTrue(
            any("Mercury–Mars aspect is not stable" in item for item in limitations)
        )
        self.assertTrue(
            any("Dispositor names omitted" in item for item in limitations)
        )

    def test_merge_stable_sign_and_aspect(self):
        probe_a = DayProbeSnapshot(
            mercury_sign="Scorpio",
            mercury_motion="retrograde",
            planet_signs={"Pluto": "Scorpio", "Mars": "Leo", "Sun": "Libra"},
            aspect_types={"Sun": "conjunction"},
        )
        probe_b = DayProbeSnapshot(
            mercury_sign="Scorpio",
            mercury_motion="retrograde",
            planet_signs={"Pluto": "Scorpio", "Mars": "Leo", "Sun": "Libra"},
            aspect_types={"Sun": "conjunction", "Jupiter": "square"},
        )
        probe_c = DayProbeSnapshot(
            mercury_sign="Scorpio",
            mercury_motion="retrograde",
            planet_signs={"Pluto": "Scorpio", "Mars": "Virgo", "Sun": "Libra"},
            aspect_types={"Sun": "conjunction"},
        )
        factors, limitations = merge_unknown_time_probes([probe_a, probe_b, probe_c])

        self.assertEqual(factors.mercury_sign, "Scorpio")
        self.assertEqual(factors.mercury_element, "water")
        self.assertEqual(factors.mercury_motion, "retrograde")
        self.assertEqual(factors.major_dispositor, "Pluto")
        self.assertEqual(factors.minor_dispositor, "Mars")
        self.assertEqual(factors.major_dispositor_sign, "Scorpio")
        self.assertIsNone(factors.minor_dispositor_sign)
        self.assertEqual(len(factors.aspects), 1)
        self.assertEqual(factors.aspects[0].planet, "Sun")
        self.assertEqual(factors.aspects[0].type, "conjunction")
        self.assertIsNone(factors.aspects[0].orb_deg)
        self.assertTrue(
            any("Minor dispositor (Mars) sign is not stable" in item for item in limitations)
        )
        self.assertTrue(
            any("Mercury–Jupiter aspect is not stable" in item for item in limitations)
        )
        self.assertFalse(
            any("minor dispositor is missing" in item.lower() for item in limitations)
        )


class MvpProfileUnchangedTests(unittest.TestCase):
    def test_profile_request_still_requires_birth_time(self):
        with self.assertRaises(ValidationError):
            ProfileRequest(birth_date=BIRTH_DATE, birth_place=PLACE)

    def test_existing_profile_endpoint_still_builds(self):
        payload = ProfileRequest(
            birth_date=BIRTH_DATE,
            birth_place=PLACE,
            birth_time=BIRTH_TIME,
        )
        result = AstroService().build_profile(payload)
        self.assertIsInstance(result, ProfileResponse)
        dumped = result.model_dump()
        for key in (
            "title",
            "sun_sign",
            "it_fit_score",
            "personality_style_archetype",
            "it_archetype",
            "career_axis",
            "strengths",
            "risks",
            "notes",
            "chart_type",
            "mercury_sign",
            "uranus_house",
            "house_6_sign",
            "house_10_sign",
            "house_system_used",
            "technical_mind",
        ):
            self.assertIn(key, dumped)
        self.assertIsInstance(result.it_fit_score, int)
        self.assertIsInstance(result.mercury_sign, str)

    def test_routes_include_both_profile_and_mercury(self):
        app = create_app()
        paths = {route.path for route in app.routes}
        self.assertIn("/api/v1/profile", paths)
        self.assertIn("/api/v1/mercury-work-profile", paths)


if __name__ == "__main__":
    unittest.main()
