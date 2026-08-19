"""API integration tests for Mars HOW YOU WORK source profile (M8)."""

from __future__ import annotations

import unittest
from datetime import date, time

from app.api.routes.mars_source_profile import create_mars_source_profile
from app.core.app import create_app
from app.schemas.mars_source_profile import MarsSourceProfileRequest, MarsSourceProfileResponse
from app.services.mars_facts import compute_mars_source_factors
from app.services.mars_human_copy import HUMAN_COPY_OVERRIDES
from app.services.mars_profile_synthesis import (
    SECTION_SPECS,
    build_mars_profile_synthesis,
    serialize_mars_source_profile,
)
from app.services.mars_source_profile import build_mars_source_profile


def _avdey_request():
    return MarsSourceProfileRequest(
        birth_date=date(1986, 7, 14),
        birth_time=time(7, 10),
        birth_place="Simferopol, Ukraine",
    )


def _vlad_request():
    return MarsSourceProfileRequest(
        birth_date=date(1986, 5, 16),
        birth_time=time(15, 0),
        birth_place="Dnipro, Ukraine",
    )


def _dzmitry_request():
    return MarsSourceProfileRequest(
        birth_date=date(1985, 11, 12),
        birth_time=time(14, 15),
        birth_place="Zhodino, Belarus",
    )


def _unknown_time_request():
    return MarsSourceProfileRequest(
        birth_date=date(1986, 7, 14),
        birth_time=None,
        birth_place="Simferopol, Ukraine",
    )


FORBIDDEN_SCOPES = {"SOURCE_ONLY", "PERSONAL_MARS"}
FORBIDDEN_PRODUCT_KEYS = (
    "strength_score",
    "mars_strength",
    "hard_aspected",
    "hire",
    "reject",
    "ranking",
    "job_fit",
    "productivity_score",
)


class MarsSourceProfileApiContractTests(unittest.TestCase):
    def test_endpoint_exists(self):
        app = create_app()
        paths = {getattr(route, "path", None) for route in app.routes}
        self.assertIn("/api/v1/mars-source-profile", paths)
        self.assertIn("/api/v1/mercury-source-profile", paths)

    def test_valid_request_returns_profile_response(self):
        response = create_mars_source_profile(_avdey_request())
        self.assertIsInstance(response, MarsSourceProfileResponse)
        self.assertIsNotNone(response.calculated)
        self.assertIsNotNone(response.synthesis)
        self.assertEqual(response.calculated.mars_sign, "Capricorn")

    def test_mars_factors_match_engine(self):
        response = create_mars_source_profile(_avdey_request())
        engine = compute_mars_source_factors(
            birth_date=date(1986, 7, 14),
            birth_time=time(7, 10),
            birth_place="Simferopol, Ukraine",
        )
        self.assertEqual(response.calculated.mars_sign, engine.mars_sign)
        self.assertEqual(response.calculated.mars_house, engine.mars_house)
        self.assertEqual(response.calculated.mars_motion, engine.mars_motion)
        self.assertEqual(response.calculated.birth_time_known, engine.birth_time_known)
        self.assertEqual(
            [(item.planet, item.type, item.orb_deg) for item in response.calculated.aspects],
            [(item.planet, item.type, item.orb_deg) for item in engine.mars_aspects],
        )
        self.assertEqual(response.calculated.mars_sign, "Capricorn")
        self.assertEqual(response.calculated.mars_house, 6)
        self.assertEqual(response.calculated.mars_motion, "retrograde")

    def test_synthesis_sections_deterministic(self):
        first = create_mars_source_profile(_avdey_request())
        second = create_mars_source_profile(_avdey_request())
        self.assertEqual(
            first.synthesis.model_dump(),
            second.synthesis.model_dump(),
        )
        self.assertEqual(
            [section.key for section in first.synthesis.sections],
            [spec[0] for spec in SECTION_SPECS],
        )
        self.assertEqual(
            [section.title for section in first.synthesis.sections],
            [spec[1] for spec in SECTION_SPECS],
        )
        raw = build_mars_source_profile(
            birth_date=date(1986, 7, 14),
            birth_time=time(7, 10),
            birth_place="Simferopol, Ukraine",
        )
        assembled = build_mars_profile_synthesis(raw)
        self.assertEqual(
            [section.fact_ids for section in first.synthesis.sections],
            [list(section.fact_ids) for section in assembled.sections],
        )

    def test_presentation_text_uses_human_copy_layer(self):
        response = create_mars_source_profile(_avdey_request())
        synthesis = response.synthesis
        self.assertIsNotNone(synthesis)
        hesitate_id = "mars_rx_repeated_hesitation_measure_seven_times"
        raw = synthesis.facts_by_id[hesitate_id].text
        human = synthesis.presentation_text_by_fact_id[hesitate_id]
        self.assertEqual(human, HUMAN_COPY_OVERRIDES[hesitate_id])
        self.assertNotEqual(raw, human)
        self.assertIn("hesitation", human.lower())
        for fact_id, text in synthesis.presentation_text_by_fact_id.items():
            self.assertEqual(text, HUMAN_COPY_OVERRIDES[fact_id])
            self.assertEqual(
                synthesis.facts_by_id[fact_id].text,
                next(
                    item.text
                    for item in (
                        *response.sign_facts,
                        *response.house_facts,
                        *response.motion_facts,
                        *response.aspect_facts,
                    )
                    if item.id == fact_id
                ),
            )
        plain = next(
            fact_id
            for fact_id in synthesis.facts_by_id
            if fact_id not in HUMAN_COPY_OVERRIDES
        )
        self.assertNotIn(plain, synthesis.presentation_text_by_fact_id)

    def test_repeated_signals_serialized_with_provenance(self):
        response = create_mars_source_profile(_avdey_request())
        raw = build_mars_source_profile(
            birth_date=date(1986, 7, 14),
            birth_time=time(7, 10),
            birth_place="Simferopol, Ukraine",
        )
        self.assertEqual(
            [item.signal for item in response.repeated_signals],
            [item.signal for item in raw.repeated_signals],
        )
        self.assertEqual(
            [item.signal for item in response.synthesis.repeated_signals],
            [item.signal for item in response.repeated_signals],
        )
        overload = next(
            item for item in response.repeated_signals if item.signal == "effort_overload"
        )
        self.assertGreaterEqual(overload.source_count, 2)
        self.assertIn("house:6", overload.sources)
        self.assertTrue(any(item.startswith("aspect:") for item in overload.sources))
        self.assertTrue(overload.fact_ids)
        pressure = next(
            section
            for section in response.synthesis.sections
            if section.key == "under_pressure"
        )
        self.assertIn("effort_overload", pressure.repeated_signals)

    def test_evidence_provenance_survives(self):
        response = create_mars_source_profile(_avdey_request())
        fact = response.synthesis.facts_by_id["mars_capricorn_plans_then_executes"]
        self.assertEqual(fact.factor_type, "sign")
        self.assertEqual(fact.factor_key, "Capricorn")
        self.assertTrue(fact.source_reference)
        self.assertTrue(fact.category)
        execute = next(
            section
            for section in response.synthesis.sections
            if section.key == "how_you_execute"
        )
        self.assertIn("mars_capricorn_plans_then_executes", execute.fact_ids)
        self.assertTrue(execute.factor_keys)
        self.assertEqual(execute.preview_fact_ids, execute.fact_ids[:3])

    def test_source_only_and_personal_mars_excluded(self):
        response = create_mars_source_profile(_avdey_request())
        all_facts = (
            list(response.sign_facts)
            + list(response.house_facts)
            + list(response.motion_facts)
            + list(response.aspect_facts)
            + list(response.synthesis.facts_by_id.values())
        )
        ids = {fact.id for fact in all_facts} | set(response.synthesis.facts_by_id)
        self.assertNotIn("mars_rx_auto_aggression", ids)
        self.assertNotIn("mars_rx_sexual_temperament_suppression", ids)
        self.assertNotIn("mars_rx_unusual_muscular_activity", ids)
        self.assertNotIn(
            "mars_aquarius_source_democracy_liberalism_irresponsibility", ids
        )
        for fact in all_facts:
            self.assertNotIn(fact.scope, FORBIDDEN_SCOPES)
        self.assertNotIn(
            "mars_rx_auto_aggression", response.synthesis.presentation_text_by_fact_id
        )

    def test_unknown_time_omits_house_layer(self):
        response = create_mars_source_profile(_unknown_time_request())
        self.assertFalse(response.calculated.birth_time_known)
        self.assertIsNone(response.calculated.mars_house)
        self.assertEqual(response.house_facts, [])
        self.assertTrue(
            any("House source layer unavailable" in item for item in response.limitations)
        )
        house_sections = [
            section.fact_ids
            for section in response.synthesis.sections
            for fact_id in section.fact_ids
            if fact_id.startswith("mars_h")
        ]
        self.assertEqual(house_sections, [])

    def test_limitations_serialized(self):
        vlad = create_mars_source_profile(_vlad_request())
        self.assertTrue(
            any("no Lesson 9 source-specific interpretation pack" in item for item in vlad.limitations)
        )
        self.assertEqual(vlad.synthesis.limitations, vlad.limitations)
        avdey = create_mars_source_profile(_avdey_request())
        self.assertTrue(
            any("Bioastrology Mars-Moon pair source is not yet extracted." in item for item in avdey.limitations)
        )

    def test_no_score_rank_or_hiring_recommendation(self):
        dumped = create_mars_source_profile(_avdey_request()).model_dump()
        blob = str(dumped).lower()
        for key in FORBIDDEN_PRODUCT_KEYS:
            self.assertNotIn(key, dumped)
            self.assertNotIn("hire/reject", blob)
        self.assertNotIn("best role", blob)
        self.assertNotIn("job fit", blob)
        self.assertNotIn("candidate suitability", blob)

    def test_sun_completion_not_rewritten_as_start_problem(self):
        response = create_mars_source_profile(_avdey_request())
        start = response.synthesis.presentation_text_by_fact_id.get(
            "mars_opposition_sun_l9_start_not_main_problem",
            response.synthesis.facts_by_id["mars_opposition_sun_l9_start_not_main_problem"].text,
        )
        self.assertIn("starting itself may not be the main problem", start.lower())
        self.assertNotIn("difficulty starting", start.lower())

    def test_vlad_dzmitry_no_rx_or_l9_and_bio_source_bounded(self):
        for request in (_vlad_request(), _dzmitry_request()):
            response = create_mars_source_profile(request)
            ids = set(response.synthesis.facts_by_id)
            self.assertFalse(any(item.startswith("mars_rx_") for item in ids))
            self.assertFalse(any("_l9_" in item for item in ids))
            self.assertEqual(response.repeated_signals, [])
            tech = response.synthesis.presentation_text_by_fact_id[
                "mars_mercury_bio_technical_analytical_it_engineering_aptitude"
            ]
            self.assertIn("The source associates this pairing with", tech)
            self.assertNotIn("Strong technical skills", tech)
            self.assertEqual(response.calculated.mars_motion, "direct")

    def test_serialize_matches_route(self):
        raw = build_mars_source_profile(
            birth_date=date(1985, 11, 12),
            birth_time=time(14, 15),
            birth_place="Zhodino, Belarus",
        )
        serialized = serialize_mars_source_profile(raw)
        routed = create_mars_source_profile(_dzmitry_request())
        self.assertEqual(serialized.model_dump(), routed.model_dump())
        self.assertEqual(routed.calculated.mars_sign, "Libra")
        self.assertEqual(routed.calculated.mars_house, 7)
