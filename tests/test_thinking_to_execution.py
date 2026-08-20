"""Deterministic Thinking → Execution bridge (M9)."""

from __future__ import annotations

import inspect
import unittest
from datetime import date, time
from unittest.mock import patch

from app.api.routes.thinking_to_execution import create_thinking_to_execution
from app.core.app import create_app
from app.schemas.mercury_source_profile import MercurySourceProfileRequest
from app.schemas.mercury_work_profile import MercurySourceFactors
from app.schemas.thinking_to_execution import ThinkingToExecutionRequest
from app.services.mars_facts import MarsSourceFactors
from app.services.mars_source_knowledge import ALL_MARS_SOURCE_FACTS
from app.services.mars_source_profile import (
    build_mars_source_profile,
    build_mars_source_profile_from_factors,
)
from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
)
from app.services.person_perspective import build_person_perspective
from app.services import thinking_to_execution as tte
from app.services.mercury_human_copy_catalog import (
    APPROVED_RAW_FACT_IDS,
    STATUS_APPROVED_OVERRIDE,
    STATUS_APPROVED_RAW,
    STATUS_UNREVIEWED,
    derive_review_status,
)
from app.services.mercury_human_copy import HUMAN_COPY_OVERRIDES
from app.services.mars_human_copy_catalog import derive_review_status as mars_review_status
from app.services.thinking_to_execution import (
    CROSS_PATTERN_SPECS,
    EXCLUDED_MARS_SCOPES,
    build_thinking_to_execution,
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


def _mercury(**kwargs):
    return build_mercury_source_profile(MercurySourceProfileRequest(**kwargs))


def _mars(**kwargs):
    return build_mars_source_profile(**kwargs)


def _bridge(person_kwargs, natal):
    person = build_person_perspective(**person_kwargs)
    return build_thinking_to_execution(_mercury(**natal), _mars(**natal), person)


class ThinkingToExecutionRegistryTests(unittest.TestCase):
    def test_registry_uses_only_existing_tags(self):
        mercury_tags = {tag for fact in ALL_SOURCE_FACTS for tag in fact.tags}
        mars_tags = {tag for fact in ALL_MARS_SOURCE_FACTS for tag in fact.tags}
        seen_ids = []
        for spec in CROSS_PATTERN_SPECS:
            seen_ids.append(spec.id)
            self.assertIn(spec.mercury_semantic, mercury_tags)
            self.assertIn(spec.mars_semantic, mars_tags)
            self.assertIn(spec.kind, {"reinforcement", "friction", "contrast"})
        self.assertEqual(len(seen_ids), len(set(seen_ids)))
        self.assertNotIn("technical_ability", [spec.mercury_semantic for spec in CROSS_PATTERN_SPECS])

    def test_does_not_merge_fact_lists_or_rerun_repeat_detection(self):
        src = inspect.getsource(tte)
        self.assertNotIn("detect_mars_repeated_signals", src)
        self.assertNotIn("REPEATED_SIGNAL_SPECS", src)
        self.assertNotIn("mercury_facts + mars_facts", src)
        self.assertNotIn("mars_facts + mercury_facts", src)
        self.assertIn("_active_mercury_facts", src)
        self.assertIn("_active_mars_facts", src)

    def test_no_new_astrology_or_hiring_language(self):
        templates = " ".join(spec.presentation_template for spec in CROSS_PATTERN_SPECS).lower()
        self.assertNotIn("overthinking", templates)
        self.assertNotIn("technical worker", templates)
        self.assertNotIn("leadership", templates)
        self.assertNotIn("productivity", templates)
        self.assertNotIn("strategist", templates)
        self.assertNotIn("score", templates)
        self.assertNotIn("ranking", templates)
        self.assertNotIn("hiring", templates)
        self.assertNotIn("avdey", templates)
        self.assertNotIn("score", tte.WHY_TEMPLATE.lower())
        analysis = next(spec for spec in CROSS_PATTERN_SPECS if spec.id == "analysis_slower_commitment")
        speed = next(spec for spec in CROSS_PATTERN_SPECS if spec.id == "fast_processing_slower_commitment")
        self.assertNotIn("clear analysis", analysis.title.lower())
        self.assertNotIn("clearly", analysis.presentation_template.lower())
        self.assertNotIn("fast processing", speed.title.lower())
        self.assertNotIn("process quickly", speed.presentation_template.lower())


class ThinkingToExecutionProfileTests(unittest.TestCase):
    def test_avdey_reviewed_analytical_facts_feed_evidence_backed_bridges(self):
        mercury = _mercury(**AVDEY)
        mars = _mars(**AVDEY)
        result = build_thinking_to_execution(
            mercury,
            mars,
            build_person_perspective(name="Avdey", sex="male"),
        )
        analytical_ids = {
            fact.id
            for bucket in (mercury.sign_facts, mercury.house_facts, mercury.motion_facts, mercury.aspect_facts)
            for fact in bucket
            if fact.activated and not fact.unresolved and "analytical_thinking" in (fact.tags or [])
        }
        self.assertEqual(
            analytical_ids,
            {"saturn_tr_analytical_ability", "pluto_sq_analytical_ability"},
        )
        for fact_id in analytical_ids:
            self.assertIn(
                derive_review_status(fact_id),
                {STATUS_APPROVED_RAW, STATUS_APPROVED_OVERRIDE},
            )
        self.assertEqual(
            [item.id for item in result.patterns],
            [
                "analysis_to_deliberate_execution",
                "analysis_slower_commitment",
                "analysis_to_practical_execution",
            ],
        )
        self.assertEqual(
            result.overview_pattern_ids,
            [
                "analysis_to_deliberate_execution",
                "analysis_slower_commitment",
            ],
        )
        self.assertNotIn(
            "analysis_to_practical_execution",
            result.overview_pattern_ids,
        )
        self.assertNotIn("technical_ability", [item.mercury_semantic for item in result.patterns])

    def test_overview_prefers_kind_diversity_and_caps_at_two(self):
        result = _bridge({"name": "Avdey", "sex": "male"}, AVDEY)
        self.assertEqual(len(result.overview_pattern_ids), 2)
        self.assertLessEqual(len(result.overview_pattern_ids), tte.OVERVIEW_BRIDGE_LIMIT)
        overview = [
            item
            for item in result.patterns
            if item.id in result.overview_pattern_ids
        ]
        kinds = {item.kind for item in overview}
        self.assertEqual(kinds, {"reinforcement", "friction"})
        self.assertEqual(len(result.patterns), 3)
        self.assertIn("analysis_to_practical_execution", [item.id for item in result.patterns])

    def test_vlad_gets_only_evidence_backed_pattern(self):
        result = _bridge({"name": "Vlad", "sex": "male"}, VLAD)
        self.assertEqual(
            [item.id for item in result.patterns],
            ["analysis_to_deliberate_execution"],
        )
        self.assertEqual(
            result.overview_pattern_ids,
            ["analysis_to_deliberate_execution"],
        )

    def test_dzmitry_does_not_receive_invented_pairs(self):
        result = _bridge({"name": "Dzmitry", "sex": "male"}, DZMITRY)
        ids = [item.id for item in result.patterns]
        self.assertEqual(
            ids,
            ["analysis_slower_commitment", "fast_processing_slower_commitment"],
        )
        self.assertEqual(
            result.overview_pattern_ids,
            [
                "analysis_slower_commitment",
                "fast_processing_slower_commitment",
            ],
        )
        self.assertNotIn("analysis_to_deliberate_execution", ids)
        self.assertNotIn("fast_processing_to_fast_action", ids)

    def test_two_mercury_support_facts_are_presentation_ready(self):
        for fact_id in (
            "mars_tr_thinking_more_analytical",
            "mars_tr_thinking_faster",
        ):
            self.assertIn(fact_id, APPROVED_RAW_FACT_IDS)
            self.assertEqual(derive_review_status(fact_id), STATUS_APPROVED_RAW)
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        self.assertEqual(
            by_id["mars_tr_thinking_more_analytical"].text,
            "Thinking becomes more analytical.",
        )
        self.assertEqual(by_id["mars_tr_thinking_faster"].text, "Thinking becomes faster.")
        self.assertEqual(
            by_id["mars_tr_thinking_more_analytical"].tags,
            ("analytical_thinking",),
        )
        self.assertEqual(by_id["mars_tr_thinking_faster"].tags, ("fast_thinking",))

    def test_dzmitry_bridges_use_exact_semantics_not_inflated_wording(self):
        result = _bridge({"name": "Dzmitry", "sex": "male"}, DZMITRY)
        by_id = {item.id: item for item in result.patterns}
        analysis = by_id["analysis_slower_commitment"]
        self.assertEqual(analysis.title, "More analytical thinking → Slower commitment")
        self.assertEqual(analysis.mercury_semantic, "analytical_thinking")
        self.assertEqual(analysis.mars_semantic, "action_hesitation")
        self.assertEqual(analysis.mercury_support, ["mars_tr_thinking_more_analytical"])
        self.assertEqual(analysis.mars_support, ["mars_libra_indecision_delayed_choice"])
        self.assertEqual(
            analysis.presentation_text,
            "Dzmitry's thinking may become more analytical while still "
            "taking more time to commit to action.",
        )
        self.assertNotIn("clear", analysis.presentation_text.lower())
        speed = by_id["fast_processing_slower_commitment"]
        self.assertEqual(speed.title, "Faster thinking → Slower commitment")
        self.assertEqual(speed.mercury_semantic, "fast_thinking")
        self.assertEqual(speed.mars_semantic, "action_hesitation")
        self.assertEqual(speed.mercury_support, ["mars_tr_thinking_faster"])
        self.assertNotIn("conjunction_Uranus", " ".join(speed.mercury_provenance))
        self.assertNotIn("fast processing", speed.title.lower())
        self.assertNotIn("process", speed.presentation_text.lower())
        self.assertEqual(
            speed.presentation_text,
            "Dzmitry's thinking may move faster while still hesitating "
            "before fully committing to action.",
        )

    def test_unreviewed_support_does_not_render_or_fallback(self):
        real = tte.mercury_review_status

        def fake_status(fact_id: str) -> str:
            if fact_id in {
                "mars_tr_thinking_more_analytical",
                "mars_tr_thinking_faster",
            }:
                return STATUS_UNREVIEWED
            return real(fact_id)

        with patch.object(tte, "mercury_review_status", fake_status):
            result = _bridge({"name": "Dzmitry", "sex": "male"}, DZMITRY)
        ids = [item.id for item in result.patterns]
        self.assertNotIn("analysis_slower_commitment", ids)
        self.assertNotIn("fast_processing_slower_commitment", ids)
        self.assertEqual(result.patterns, [])

    def test_zero_pattern_result_is_valid_and_has_no_fallback_prose(self):
        mercury = build_source_profile_from_factors(
            MercurySourceFactors(birth_time_known=False)
        )
        mars = build_mars_source_profile_from_factors(
            MarsSourceFactors(birth_time_known=False)
        )
        result = build_thinking_to_execution(
            mercury,
            mars,
            build_person_perspective(name="Sam"),
        )
        self.assertEqual(result.patterns, [])

    def test_fast_thinking_fast_start_requires_both_exact_tags(self):
        mercury = build_source_profile_from_factors(
            MercurySourceFactors(birth_time_known=False, mercury_sign="Aries")
        )
        mars = build_mars_source_profile_from_factors(
            MarsSourceFactors(birth_time_known=False, mars_sign="Aries")
        )
        result = build_thinking_to_execution(
            mercury,
            mars,
            build_person_perspective(name="Alex", sex="male"),
        )
        ids = [item.id for item in result.patterns]
        self.assertIn("fast_processing_to_fast_action", ids)
        self.assertNotIn("analysis_to_deliberate_execution", ids)

    def test_deterministic_and_female_self_unknown_perspectives(self):
        first = _bridge({"name": "Dzmitry", "sex": "male"}, DZMITRY)
        second = _bridge({"name": "Dzmitry", "sex": "male"}, DZMITRY)
        self.assertEqual(first.model_dump(), second.model_dump())
        female = _bridge({"name": "Nadia", "sex": "female"}, DZMITRY)
        self.assertTrue(any("Nadia" in item.presentation_text for item in female.patterns))
        self.assertFalse(any(" he " in item.presentation_text.lower() for item in female.patterns))
        unknown = _bridge({"name": "Dzmitry"}, DZMITRY)
        self.assertFalse(any(item.presentation_text.startswith("He ") for item in unknown.patterns))
        self_view = _bridge({"name": "", "perspective": "self"}, DZMITRY)
        self.assertTrue(any(item.presentation_text.startswith("Your ") or item.presentation_text.startswith("You ") for item in self_view.patterns))
        self.assertFalse(any("Dzmitry" in item.presentation_text for item in self_view.patterns))

    def test_api_returns_namespaced_dzmitry_bridge(self):
        app = create_app()
        paths = {getattr(route, "path", None) for route in app.routes}
        self.assertIn("/api/v1/thinking-to-execution", paths)
        response = create_thinking_to_execution(
            ThinkingToExecutionRequest(
                birth_date=DZMITRY["birth_date"],
                birth_time=DZMITRY["birth_time"],
                birth_place=DZMITRY["birth_place"],
                display_name="Dzmitry",
                sex="male",
            )
        )
        self.assertEqual(len(response.patterns), 2)
        self.assertTrue(all(item.mercury_provenance[0].startswith("mercury:") for item in response.patterns))
        self.assertTrue(all("sextile_Mars" in " ".join(item.mercury_provenance) for item in response.patterns))
        self.assertFalse(any("conjunction_Uranus" in " ".join(item.mercury_provenance) for item in response.patterns))
        blob = response.model_dump_json().lower()
        self.assertNotIn("hire", blob)
        self.assertNotIn("ranking", blob)
        self.assertNotIn("score", blob)
        self.assertNotIn("clear analysis", blob)
        self.assertNotIn("fast processing", blob)


BRIDGE_ELIGIBLE_MERCURY_RAW = frozenset(
    {
        "saturn_tr_analytical_ability",
        "pluto_sq_analytical_ability",
        "pluto_harm_analytical_quality",
    }
)
BRIDGE_ELIGIBLE_MERCURY_OVERRIDE = frozenset(
    {
        "plu_cj_analytical_thinking",
        "plu_opp_analytical_thinking",
    }
)


class BridgeEligibleFactAuditTests(unittest.TestCase):
    def test_bridge_eligible_mercury_facts_all_reviewed(self):
        merc_tags = {spec.mercury_semantic for spec in CROSS_PATTERN_SPECS}
        mars_tags = {spec.mars_semantic for spec in CROSS_PATTERN_SPECS}
        eligible_mercury = [
            fact
            for fact in ALL_SOURCE_FACTS
            if any(tag in merc_tags for tag in (fact.tags or ()))
        ]
        eligible_mars = [
            fact
            for fact in ALL_MARS_SOURCE_FACTS
            if any(tag in mars_tags for tag in (fact.tags or ()))
        ]
        reviewable_mercury = [fact for fact in eligible_mercury if not fact.unresolved]
        unreviewed_mercury = [
            fact.id
            for fact in reviewable_mercury
            if derive_review_status(fact.id) == STATUS_UNREVIEWED
        ]
        self.assertEqual(unreviewed_mercury, [])
        self.assertEqual(len(reviewable_mercury), 13)
        self.assertEqual(
            [fact.id for fact in eligible_mercury if fact.unresolved],
            ["saturn_sq_branch_mercury_analytical_qualities"],
        )
        for fact_id in BRIDGE_ELIGIBLE_MERCURY_RAW:
            self.assertIn(fact_id, APPROVED_RAW_FACT_IDS)
            self.assertEqual(derive_review_status(fact_id), STATUS_APPROVED_RAW)
        for fact_id in BRIDGE_ELIGIBLE_MERCURY_OVERRIDE:
            self.assertIn(fact_id, HUMAN_COPY_OVERRIDES)
            self.assertEqual(derive_review_status(fact_id), STATUS_APPROVED_OVERRIDE)
        for fact in eligible_mars:
            if fact.scope in EXCLUDED_MARS_SCOPES:
                continue
            self.assertIn(
                mars_review_status(fact.id),
                {STATUS_APPROVED_RAW, STATUS_APPROVED_OVERRIDE},
            )

    def test_m93_review_did_not_touch_unrelated_facts(self):
        reviewed_in_m93 = BRIDGE_ELIGIBLE_MERCURY_RAW | BRIDGE_ELIGIBLE_MERCURY_OVERRIDE
        unrelated_unreviewed = {
            fact.id
            for fact in ALL_SOURCE_FACTS
            if fact.id not in reviewed_in_m93
            and derive_review_status(fact.id) == STATUS_UNREVIEWED
        }
        self.assertGreater(len(unrelated_unreviewed), 600)


if __name__ == "__main__":
    unittest.main()
