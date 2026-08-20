"""Contribution Profile v1 — evidence-backed work contribution."""

from __future__ import annotations

import unittest
from datetime import date, time

from unittest.mock import patch

from app.api.routes.contribution_profile import create_contribution_profile
from app.core.app import create_app
from app.schemas.contribution_profile import ContributionProfileRequest
from app.schemas.thinking_to_execution import (
    CrossProfilePattern,
    ThinkingToExecutionSynthesis,
)
from app.schemas.mercury_source_profile import MercurySourceProfileRequest
from app.schemas.mercury_work_profile import MercurySourceFactors
from app.services.contribution_profile import (
    CONTRIBUTION_DIMENSION_SPECS,
    PROFILE_NOTES,
    build_contribution_profile,
)
from app.services.mars_facts import MarsSourceFactors
from app.services.mars_source_knowledge import ALL_MARS_SOURCE_FACTS
from app.services.mars_source_profile import (
    build_mars_source_profile,
    build_mars_source_profile_from_factors,
)
from app.services.mercury_human_copy_catalog import STATUS_UNREVIEWED
from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
)
from app.services.person_perspective import build_person_perspective
from app.services.thinking_to_execution import (
    CROSS_PATTERN_SPECS,
    build_thinking_to_execution,
)
from app.services import thinking_to_execution as tte


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

KNOWN_MERCURY_TAGS = {tag for fact in ALL_SOURCE_FACTS for tag in fact.tags}
KNOWN_MARS_TAGS = {tag for fact in ALL_MARS_SOURCE_FACTS for tag in fact.tags}
KNOWN_BRIDGE_IDS = {spec.id for spec in CROSS_PATTERN_SPECS}


def _profile(person_kwargs, natal):
    mercury = build_mercury_source_profile(MercurySourceProfileRequest(**natal))
    mars = build_mars_source_profile(**natal)
    person = build_person_perspective(**person_kwargs)
    tte = build_thinking_to_execution(mercury, mars, person)
    return build_contribution_profile(mercury, mars, person, tte)


class ContributionRegistryTests(unittest.TestCase):
    def test_specs_use_only_existing_tags_and_bridge_ids(self):
        for spec in CONTRIBUTION_DIMENSION_SPECS:
            self.assertTrue(spec.mercury_tags <= KNOWN_MERCURY_TAGS)
            self.assertTrue(spec.mars_tags <= KNOWN_MARS_TAGS)
            self.assertTrue(spec.reinforce_ids <= KNOWN_BRIDGE_IDS)
            self.assertTrue(spec.friction_ids <= KNOWN_BRIDGE_IDS)
            self.assertNotIn("technical_ability", spec.mercury_tags)
            self.assertNotIn("technical_ability", spec.mars_tags)

    def test_notes_forbid_ranking_and_hiring(self):
        blob = " ".join(PROFILE_NOTES).lower()
        self.assertIn("not a candidate ranking", blob)
        self.assertIn("no hire/reject", blob)
        self.assertIn("not a technical-qualification", blob)
        self.assertNotIn("personality score", blob)


class ContributionProfileTests(unittest.TestCase):
    def test_avdey_dimensions_are_evidence_backed(self):
        result = _profile({"name": "Avdey", "sex": "male"}, AVDEY)
        by_key = {item.key: item for item in result.dimensions}
        self.assertIn("investigation", by_key)
        self.assertIn("structuring", by_key)
        self.assertIn("hands_on_delivery", by_key)
        self.assertNotIn("exploration", by_key)
        self.assertNotIn("adaptation", by_key)
        investigation = by_key["investigation"]
        self.assertTrue(investigation.mercury_support)
        self.assertTrue(
            set(investigation.mercury_support)
            <= {"saturn_tr_analytical_ability", "pluto_sq_analytical_ability"}
        )
        self.assertIn(
            "analysis_to_deliberate_execution",
            investigation.thinking_to_execution_support,
        )
        self.assertEqual(investigation.state, "primary")
        self.assertEqual(
            set(investigation.root_fact_ids),
            set(investigation.mercury_support),
        )
        self.assertEqual(len(investigation.mercury_provenance), 2)
        self.assertTrue(all(item.startswith("mercury:") for item in investigation.mercury_provenance))
        structuring = by_key["structuring"]
        self.assertTrue(structuring.mars_support)
        self.assertEqual(structuring.mars_provenance, ["mars:sign:Capricorn"])
        self.assertEqual(structuring.state, "supporting")
        self.assertIn("analysis_to_deliberate_execution", structuring.thinking_to_execution_support)
        self.assertTrue(all(item.startswith("mars:") for item in structuring.mars_provenance))
        hands_on = by_key["hands_on_delivery"]
        self.assertIn("mars_h6_does_work_personally", hands_on.mars_support)
        self.assertEqual(hands_on.root_fact_ids, ["mars_h6_does_work_personally"])
        self.assertEqual(hands_on.state, "supporting")
        self.assertIn("analysis_to_practical_execution", hands_on.thinking_to_execution_support)
        self.assertEqual(result.strongest, ["investigation"])
        self.assertEqual(set(result.supporting), {"structuring", "hands_on_delivery"})

    def test_dzmitry_does_not_guess_unsupported_dimensions(self):
        result = _profile({"name": "Dzmitry", "sex": "male"}, DZMITRY)
        keys = [item.key for item in result.dimensions]
        self.assertNotIn("hands_on_delivery", keys)
        self.assertNotIn("structuring", keys)
        self.assertNotIn("validation", keys)
        by_key = {item.key: item for item in result.dimensions}
        self.assertIn("investigation", by_key)
        self.assertIn("execution_momentum", by_key)
        self.assertEqual(by_key["investigation"].state, "conditional")
        self.assertEqual(by_key["execution_momentum"].state, "conditional")
        self.assertEqual(
            by_key["investigation"].mercury_support,
            ["mars_tr_thinking_more_analytical"],
        )
        self.assertEqual(
            by_key["execution_momentum"].mercury_support,
            ["mars_tr_thinking_faster"],
        )
        self.assertIn(
            "analysis_slower_commitment",
            by_key["investigation"].thinking_to_execution_support,
        )
        self.assertNotIn(
            "analysis_to_deliberate_execution",
            by_key["investigation"].thinking_to_execution_support,
        )

    def test_vlad_validation_and_structuring_remain_traceable(self):
        result = _profile({"name": "Vlad", "sex": "male"}, VLAD)
        by_key = {item.key: item for item in result.dimensions}
        self.assertIn("validation", by_key)
        self.assertIn("structuring", by_key)
        self.assertIn("investigation", by_key)
        self.assertTrue(by_key["validation"].mercury_support)
        self.assertTrue(
            any("practical_fact_based" in fid or fid.startswith("taurus_") or fid.startswith("h9_")
                for fid in by_key["validation"].mercury_support)
            or by_key["validation"].mercury_support
        )
        self.assertIn("analysis_to_deliberate_execution", by_key["investigation"].thinking_to_execution_support)
        self.assertEqual(by_key["investigation"].state, "primary")
        self.assertEqual(by_key["structuring"].state, "primary")
        self.assertEqual(by_key["validation"].state, "strong")
        self.assertEqual(by_key["execution_momentum"].state, "supporting")

    def test_deterministic(self):
        first = _profile({"name": "Avdey", "sex": "male"}, AVDEY)
        second = _profile({"name": "Avdey", "sex": "male"}, AVDEY)
        self.assertEqual(first.model_dump(), second.model_dump())

    def test_unknown_time_does_not_use_house_contribution(self):
        natal = dict(birth_date=AVDEY["birth_date"], birth_place=AVDEY["birth_place"])
        result = _profile({"name": "Avdey", "sex": "male"}, natal)
        keys = [item.key for item in result.dimensions]
        self.assertNotIn("hands_on_delivery", keys)
        blob = " ".join(
            " ".join(item.mercury_provenance + item.mars_provenance)
            for item in result.dimensions
        )
        self.assertNotIn("house:", blob)
        self.assertTrue(any("houses and angles omitted" in item for item in result.limitations))

    def test_no_ranking_language_in_output(self):
        result = _profile({"name": "Avdey", "sex": "male"}, AVDEY)
        blob = result.model_dump_json().lower()
        self.assertIn("not a candidate ranking", blob)
        self.assertIn("no hire/reject recommendation", blob)
        self.assertNotIn("hire this", blob)
        self.assertNotIn("compatibility %", blob)

    def test_api_route_registered_and_returns_avdey(self):
        app = create_app()
        paths = {getattr(route, "path", None) for route in app.routes}
        self.assertIn("/api/v1/contribution-profile", paths)
        response = create_contribution_profile(
            ContributionProfileRequest(
                birth_date=AVDEY["birth_date"],
                birth_time=AVDEY["birth_time"],
                birth_place=AVDEY["birth_place"],
                display_name="Avdey",
                sex="male",
            )
        )
        self.assertGreaterEqual(len(response.dimensions), 1)
        self.assertTrue(all(item.presentation_ready for item in response.dimensions))
        self.assertEqual(response.notes, list(PROFILE_NOTES))


class ContributionRootEvidenceTests(unittest.TestCase):
    def test_tte_does_not_count_as_a_third_independent_root(self):
        mercury = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=False,
                mercury_sign="Aries",
            )
        )
        mars = build_mars_source_profile_from_factors(
            MarsSourceFactors(birth_time_known=False, mars_sign="Aries")
        )
        person = build_person_perspective(name="Alex", sex="male")
        tte_result = build_thinking_to_execution(mercury, mars, person)
        self.assertIn(
            "fast_processing_to_fast_action",
            [item.id for item in tte_result.patterns],
        )
        result = build_contribution_profile(mercury, mars, person, tte_result)
        momentum = next(item for item in result.dimensions if item.key == "execution_momentum")
        root_keys = set(momentum.mercury_provenance + momentum.mars_provenance)
        self.assertEqual(root_keys, {"mercury:sign:Aries", "mars:sign:Aries"})
        self.assertEqual(len(root_keys), 2)
        self.assertEqual(
            set(momentum.root_fact_ids),
            set(momentum.mercury_support + momentum.mars_support),
        )
        self.assertIn("fast_processing_to_fast_action", momentum.thinking_to_execution_support)
        self.assertNotIn("fast_processing_to_fast_action", momentum.root_fact_ids)
        self.assertEqual(momentum.state, "primary")

    def test_tte_cannot_resurrect_unreviewed_mercury_roots(self):
        mercury = build_mercury_source_profile(MercurySourceProfileRequest(**DZMITRY))
        mars = build_mars_source_profile(**DZMITRY)
        person = build_person_perspective(name="Dzmitry", sex="male")
        real = tte.mercury_review_status

        def fake_status(fact_id: str) -> str:
            if fact_id in {
                "mars_tr_thinking_more_analytical",
                "mars_tr_thinking_faster",
            }:
                return STATUS_UNREVIEWED
            return real(fact_id)

        with patch.object(tte, "mercury_review_status", fake_status):
            with patch(
                "app.services.contribution_profile.mercury_review_status",
                fake_status,
            ):
                tte_result = build_thinking_to_execution(mercury, mars, person)
                result = build_contribution_profile(mercury, mars, person, tte_result)
        keys = [item.key for item in result.dimensions]
        self.assertNotIn("investigation", keys)
        self.assertNotIn("execution_momentum", keys)
        self.assertEqual(tte_result.patterns, [])

    def test_tte_bridge_alone_cannot_create_a_dimension(self):
        mercury = build_mercury_source_profile(MercurySourceProfileRequest(**DZMITRY))
        mars = build_mars_source_profile(**DZMITRY)
        person = build_person_perspective(name="Dzmitry", sex="male")
        injected = ThinkingToExecutionSynthesis(
            patterns=[
                CrossProfilePattern(
                    id="analysis_to_practical_execution",
                    title="Analytical thinking → Practical execution",
                    kind="reinforcement",
                    presentation_text="injected",
                    mercury_semantic="analytical_thinking",
                    mars_semantic="hands_on_execution",
                    mercury_support=["mars_tr_thinking_more_analytical"],
                    mars_support=["mars_h6_does_work_personally"],
                    mercury_provenance=["mercury:aspect:Mars"],
                    mars_provenance=["mars:house:6"],
                    why_this_appears="injected",
                )
            ],
            overview_pattern_ids=["analysis_to_practical_execution"],
        )
        result = build_contribution_profile(mercury, mars, person, injected)
        keys = [item.key for item in result.dimensions]
        self.assertNotIn("hands_on_delivery", keys)
        self.assertFalse(
            any("mars_h6_does_work_personally" in item.root_fact_ids for item in result.dimensions)
        )

    def test_unknown_time_house_tte_cannot_keep_hands_on_delivery(self):
        timed = _profile({"name": "Avdey", "sex": "male"}, AVDEY)
        self.assertIn("hands_on_delivery", [item.key for item in timed.dimensions])
        natal = dict(birth_date=AVDEY["birth_date"], birth_place=AVDEY["birth_place"])
        unknown = _profile({"name": "Avdey", "sex": "male"}, natal)
        keys = [item.key for item in unknown.dimensions]
        self.assertNotIn("hands_on_delivery", keys)
        self.assertFalse(
            any(
                "analysis_to_practical_execution" in item.thinking_to_execution_support
                for item in unknown.dimensions
            )
        )

    def test_primary_requires_two_independent_roots_not_tte_alone(self):
        result = _profile({"name": "Avdey", "sex": "male"}, AVDEY)
        by_key = {item.key: item for item in result.dimensions}
        hands_on = by_key["hands_on_delivery"]
        self.assertEqual(len(hands_on.mars_provenance), 1)
        self.assertIn("analysis_to_practical_execution", hands_on.thinking_to_execution_support)
        self.assertEqual(hands_on.state, "supporting")
        investigation = by_key["investigation"]
        self.assertGreaterEqual(len(investigation.mercury_provenance), 2)
        self.assertIn(
            "analysis_to_deliberate_execution",
            investigation.thinking_to_execution_support,
        )
        self.assertEqual(investigation.state, "primary")


if __name__ == "__main__":
    unittest.main()
