import unittest
from datetime import date, time

from app.schemas.mercury_work_profile import (
    DispositorCondition,
    MercuryWorkProfileRequest,
    PlanetAspect,
)
from app.services.mercury_facts import (
    DayProbeSnapshot,
    merge_unknown_time_probes,
    summarize_dispositor_condition,
)
from app.services.mercury_work_profile import (
    build_mercury_work_profile,
    synthesize_mercury_narrative,
)


PLACE = "Miami, USA"
ARIES_DATE = date(1990, 3, 21)
GEMINI_DATE = date(1990, 6, 15)
TAURUS_DATE = date(1977, 5, 5)
BIRTH_TIME = time(14, 30)


def _narrative_fields(result) -> dict:
    return {
        "thinking": result.thinking,
        "learning": result.learning,
        "communication": result.communication,
        "strengths": result.strengths,
        "risks": result.risks,
        "team_value": result.team_value,
        "possible_roles": result.possible_roles,
    }


class DispositorConditionSummaryTests(unittest.TestCase):
    def test_counts_split_harmonious_tense_and_conjunction(self):
        aspects = [
            PlanetAspect(planet="Sun", type="trine", orb_deg=1.0),
            PlanetAspect(planet="Venus", type="sextile", orb_deg=2.0),
            PlanetAspect(planet="Mars", type="square", orb_deg=1.5),
            PlanetAspect(planet="Saturn", type="opposition", orb_deg=3.0),
            PlanetAspect(planet="Mercury", type="conjunction", orb_deg=0.8),
        ]
        condition = summarize_dispositor_condition(aspects)
        self.assertEqual(condition.harmonious_aspect_count, 2)
        self.assertEqual(condition.tense_aspect_count, 2)
        self.assertEqual(condition.conjunction_count, 1)
        self.assertEqual(
            set(condition.model_dump()),
            {"harmonious_aspect_count", "tense_aspect_count", "conjunction_count"},
        )
        dumped = condition.model_dump()
        self.assertNotIn("rating", dumped)
        self.assertNotIn("quality", dumped)
        self.assertNotIn("good", dumped)
        self.assertNotIn("bad", dumped)


class DispositorExactTimeFactTests(unittest.TestCase):
    def test_major_and_minor_dispositor_aspects_for_aries(self):
        result = build_mercury_work_profile(
            MercuryWorkProfileRequest(
                birth_date=ARIES_DATE,
                birth_place=PLACE,
                birth_time=BIRTH_TIME,
            )
        )
        factors = result.source_factors
        self.assertEqual(factors.mercury_sign, "Aries")
        self.assertEqual(factors.major_dispositor, "Mars")
        self.assertEqual(factors.minor_dispositor, "Pluto")
        self.assertTrue(factors.major_dispositor_aspects)
        self.assertTrue(factors.minor_dispositor_aspects)
        self.assertIsInstance(factors.major_dispositor_condition, DispositorCondition)
        self.assertIsInstance(factors.minor_dispositor_condition, DispositorCondition)

        for aspect in factors.major_dispositor_aspects:
            self.assertNotEqual(aspect.planet, "Mars")
            self.assertIn(aspect.type, {"conjunction", "sextile", "square", "trine", "opposition"})
            self.assertIsInstance(aspect.orb_deg, float)
        for aspect in factors.minor_dispositor_aspects:
            self.assertNotEqual(aspect.planet, "Pluto")
            self.assertIsInstance(aspect.orb_deg, float)

        major_cond = factors.major_dispositor_condition
        recomputed = summarize_dispositor_condition(factors.major_dispositor_aspects)
        self.assertEqual(major_cond, recomputed)
        self.assertEqual(
            major_cond.harmonious_aspect_count
            + major_cond.tense_aspect_count
            + major_cond.conjunction_count,
            len(factors.major_dispositor_aspects),
        )

    def test_single_dispositor_has_empty_minor_condition_and_no_limitation(self):
        result = build_mercury_work_profile(
            MercuryWorkProfileRequest(
                birth_date=TAURUS_DATE,
                birth_place=PLACE,
                birth_time=BIRTH_TIME,
            )
        )
        factors = result.source_factors
        self.assertEqual(factors.mercury_sign, "Taurus")
        self.assertEqual(factors.major_dispositor, "Venus")
        self.assertIsNone(factors.minor_dispositor)
        self.assertTrue(factors.major_dispositor_aspects)
        self.assertEqual(factors.minor_dispositor_aspects, [])
        self.assertIsInstance(factors.major_dispositor_condition, DispositorCondition)
        self.assertIsNone(factors.minor_dispositor_condition)
        self.assertFalse(
            any("minor dispositor" in item.lower() for item in result.limitations)
        )

    def test_mercury_self_dispositor_skips_self_aspect(self):
        result = build_mercury_work_profile(
            MercuryWorkProfileRequest(
                birth_date=GEMINI_DATE,
                birth_place=PLACE,
                birth_time=BIRTH_TIME,
            )
        )
        factors = result.source_factors
        self.assertEqual(factors.mercury_sign, "Gemini")
        self.assertEqual(factors.major_dispositor, "Mercury")
        self.assertIsNone(factors.minor_dispositor)
        self.assertEqual(factors.minor_dispositor_aspects, [])
        self.assertIsNone(factors.minor_dispositor_condition)
        self.assertNotIn("Mercury", [a.planet for a in factors.major_dispositor_aspects])
        self.assertNotIn("Mercury", [a.planet for a in factors.aspects])
        for aspect in factors.major_dispositor_aspects:
            self.assertIsInstance(aspect.orb_deg, float)

    def test_dispositor_facts_do_not_change_narrative(self):
        result = build_mercury_work_profile(
            MercuryWorkProfileRequest(
                birth_date=ARIES_DATE,
                birth_place=PLACE,
                birth_time=BIRTH_TIME,
            )
        )
        expected = synthesize_mercury_narrative(
            mercury_sign=result.source_factors.mercury_sign,
            mercury_element=result.source_factors.mercury_element,
            mercury_motion=result.source_factors.mercury_motion,
            mercury_house=result.source_factors.mercury_house,
            aspects=result.source_factors.aspects,
            major_dispositor=result.source_factors.major_dispositor,
            minor_dispositor=result.source_factors.minor_dispositor,
            major_dispositor_aspects=result.source_factors.major_dispositor_aspects,
            minor_dispositor_aspects=result.source_factors.minor_dispositor_aspects,
        )
        self.assertEqual(result.thinking, expected.thinking)
        self.assertEqual(result.learning, expected.learning)
        self.assertEqual(result.communication, expected.communication)
        self.assertEqual(result.strengths, expected.strengths)
        self.assertEqual(result.risks, expected.risks)
        self.assertEqual(result.team_value, expected.team_value)
        self.assertEqual(result.possible_roles, expected.possible_roles)
        combined = " ".join(
            [
                result.thinking,
                result.learning,
                result.communication,
                result.team_value,
            ]
        ).lower()
        self.assertNotIn("dispositor", combined)
        self.assertNotIn("harmonious_aspect_count", combined)


class DispositorUnknownTimeFactTests(unittest.TestCase):
    def test_unknown_time_live_request_keeps_conservative_facts(self):
        result = build_mercury_work_profile(
            MercuryWorkProfileRequest(birth_date=ARIES_DATE, birth_place=PLACE)
        )
        factors = result.source_factors
        self.assertFalse(factors.birth_time_known)
        self.assertIsNone(factors.major_dispositor_house)
        self.assertIsNone(factors.minor_dispositor_house)
        self.assertFalse(any(a.planet == "Moon" for a in factors.major_dispositor_aspects))
        self.assertFalse(any(a.planet == "Moon" for a in factors.minor_dispositor_aspects))
        for aspect in factors.major_dispositor_aspects + factors.minor_dispositor_aspects:
            self.assertIsNone(aspect.orb_deg)
        if factors.minor_dispositor is None:
            self.assertEqual(factors.minor_dispositor_aspects, [])
            self.assertIsNone(factors.minor_dispositor_condition)
        self.assertFalse(
            any("minor dispositor" in item.lower() for item in result.limitations)
        )

    def test_unknown_time_only_stable_dispositor_aspect_types_survive(self):
        base_signs = {"Pluto": "Scorpio", "Mars": "Leo", "Sun": "Libra", "Mercury": "Scorpio"}
        probe_a = DayProbeSnapshot(
            mercury_sign="Scorpio",
            mercury_motion="direct",
            planet_signs=base_signs,
            aspect_types={"Sun": "conjunction"},
            planet_aspect_types={
                "Pluto": {"Sun": "trine", "Mars": "square", "Venus": "sextile"},
                "Mars": {"Sun": "sextile", "Venus": "conjunction"},
            },
        )
        probe_b = DayProbeSnapshot(
            mercury_sign="Scorpio",
            mercury_motion="direct",
            planet_signs=base_signs,
            aspect_types={"Sun": "conjunction"},
            planet_aspect_types={
                "Pluto": {"Sun": "trine", "Jupiter": "square", "Venus": "sextile"},
                "Mars": {"Sun": "trine", "Venus": "conjunction"},
            },
        )
        probe_c = DayProbeSnapshot(
            mercury_sign="Scorpio",
            mercury_motion="direct",
            planet_signs={**base_signs, "Mars": "Virgo"},
            aspect_types={"Sun": "conjunction"},
            planet_aspect_types={
                "Pluto": {"Sun": "trine", "Venus": "sextile"},
                "Mars": {"Venus": "conjunction"},
            },
        )
        factors, limitations = merge_unknown_time_probes([probe_a, probe_b, probe_c])

        self.assertEqual(factors.major_dispositor, "Pluto")
        self.assertEqual(factors.minor_dispositor, "Mars")
        self.assertIsNone(factors.major_dispositor_house)
        self.assertIsNone(factors.minor_dispositor_house)
        self.assertEqual(
            [(a.planet, a.type, a.orb_deg) for a in factors.major_dispositor_aspects],
            [("Sun", "trine", None), ("Venus", "sextile", None)],
        )
        self.assertEqual(
            [(a.planet, a.type, a.orb_deg) for a in factors.minor_dispositor_aspects],
            [("Venus", "conjunction", None)],
        )
        self.assertFalse(any(a.planet == "Moon" for a in factors.major_dispositor_aspects))
        self.assertEqual(factors.major_dispositor_condition.harmonious_aspect_count, 2)
        self.assertEqual(factors.major_dispositor_condition.tense_aspect_count, 0)
        self.assertEqual(factors.major_dispositor_condition.conjunction_count, 0)
        self.assertEqual(factors.minor_dispositor_condition.conjunction_count, 1)
        self.assertIsNone(factors.minor_dispositor_sign)
        self.assertTrue(any("Major dispositor (Pluto)–Mars" in item for item in limitations))
        self.assertTrue(any("Major dispositor (Pluto)–Jupiter" in item for item in limitations))
        self.assertTrue(any("Minor dispositor (Mars)–Sun" in item for item in limitations))


if __name__ == "__main__":
    unittest.main()
