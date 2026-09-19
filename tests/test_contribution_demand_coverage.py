"""M12 Phase 1 — Contribution × Project Demand Coverage backend tests."""

from __future__ import annotations

import ast
import unittest
from datetime import date, time
from pathlib import Path
from unittest.mock import patch

from app.api.routes.contribution_demand_coverage import create_contribution_demand_coverage
from app.core.app import create_app
from app.schemas.contribution_demand_coverage import (
    ContributionDemandCoverageRequest,
    ContributionDemandCoverageResponse,
)
from app.schemas.contribution_profile import (
    ContributionDimension,
    ContributionProfileRequest,
    ContributionProfileResponse,
    ContributionTraceability,
)
from app.schemas.project_demand import (
    PROJECT_DEMAND_DIMENSION_ORDER,
    ProjectDemand,
    ProjectDemandDimension,
)
from app.services.contribution_demand_coverage import (
    COVERAGE_NOTES,
    apply_coverage_matrix,
    build_contribution_demand_coverage,
    resolve_coverage_status,
)
from app.services.contribution_profile import CONTRIBUTION_DIMENSION_SPECS
from app.services.project_demand import build_project_demand
from app.schemas.project_demand import ProjectDemandRequest


AVDEY = dict(
    birth_date=date(1986, 7, 14),
    birth_time=time(7, 10),
    birth_place="Simferopol, Ukraine",
)

MATRIX_CASES: tuple[tuple[str, str | None, str], ...] = (
    # CRITICAL
    ("critical", "primary", "covered"),
    ("critical", "strong", "covered"),
    ("critical", "supporting", "partially_covered"),
    ("critical", "conditional", "conditional_coverage"),
    ("critical", None, "gap"),
    # IMPORTANT
    ("important", "primary", "covered"),
    ("important", "strong", "covered"),
    ("important", "supporting", "partially_covered"),
    ("important", "conditional", "conditional_coverage"),
    ("important", None, "gap"),
    # USEFUL
    ("useful", "primary", "covered"),
    ("useful", "strong", "covered"),
    ("useful", "supporting", "covered"),
    ("useful", "conditional", "conditional_coverage"),
    ("useful", None, "gap"),
    # NOT_REQUIRED
    ("not_required", "primary", "not_required"),
    ("not_required", "strong", "not_required"),
    ("not_required", "supporting", "not_required"),
    ("not_required", "conditional", "not_required"),
    ("not_required", None, "not_required"),
)

_TITLES = {spec.key: spec.title for spec in CONTRIBUTION_DIMENSION_SPECS}


def _empty_traceability() -> ContributionTraceability:
    return ContributionTraceability(
        dimension_count=0,
        primary_count=0,
        strong_count=0,
        supporting_count=0,
        conditional_count=0,
        mercury_support_count=0,
        mars_support_count=0,
        root_fact_count=0,
        bridge_support_count=0,
    )


def _contrib_dim(key: str, state: str) -> ContributionDimension:
    return ContributionDimension(
        key=key,
        title=_TITLES[key],
        state=state,  # type: ignore[arg-type]
        description=f"{key} description",
        why_this_appears="Evidence present.",
    )


def _contribution_with(states: dict[str, str]) -> ContributionProfileResponse:
    dimensions = [_contrib_dim(key, state) for key, state in states.items()]
    return ContributionProfileResponse(
        dimensions=dimensions,
        strongest=[k for k, s in states.items() if s in {"primary", "strong"}],
        supporting=[k for k, s in states.items() if s == "supporting"],
        conditional=[k for k, s in states.items() if s == "conditional"],
        traceability=_empty_traceability(),
        notes=[],
    )


def _demand_all(level: str, rationale: str = "Rationale for test.") -> ProjectDemand:
    return ProjectDemand(
        label="Coverage matrix project",
        description=None,
        dimensions=[
            ProjectDemandDimension(
                dimension=key,
                demand_level=level,  # type: ignore[arg-type]
                rationale=f"{rationale} ({key})",
                source="user",
            )
            for key in PROJECT_DEMAND_DIMENSION_ORDER
        ],
        assumptions=[],
        created_from="explicit",
        notes=[],
    )


def _demand_mixed() -> ProjectDemand:
    levels = {
        "investigation": ("critical", "Investigation is central."),
        "structuring": ("important", "Planning matters."),
        "validation": ("useful", "Helpful checks."),
        "execution_momentum": ("not_required", "Not needed here."),
        "hands_on_delivery": ("useful", "Hands-on helps."),
    }
    return ProjectDemand(
        label="Mixed demand project",
        dimensions=[
            ProjectDemandDimension(
                dimension=key,
                demand_level=levels[key][0],  # type: ignore[arg-type]
                rationale=levels[key][1],
            )
            for key in PROJECT_DEMAND_DIMENSION_ORDER
        ],
        created_from="explicit",
    )


class CoverageMatrixResolveTests(unittest.TestCase):
    def test_matrix_exhaustive(self):
        for demand_level, contribution_state, expected in MATRIX_CASES:
            with self.subTest(demand=demand_level, state=contribution_state):
                self.assertEqual(
                    resolve_coverage_status(demand_level, contribution_state),
                    expected,
                )


class CoverageMatrixApplyTests(unittest.TestCase):
    def test_absent_contribution_state_is_null(self):
        demand = _demand_all("critical")
        contribution = _contribution_with({"investigation": "primary"})
        rows = apply_coverage_matrix(demand, contribution)
        by_key = {row.dimension: row for row in rows}
        self.assertIsNone(by_key["structuring"].contribution_state)
        self.assertEqual(by_key["structuring"].coverage_status, "gap")
        self.assertEqual(by_key["investigation"].contribution_state, "primary")
        self.assertEqual(by_key["investigation"].coverage_status, "covered")

    def test_always_five_dimensions_in_canonical_order(self):
        demand = _demand_mixed()
        contribution = _contribution_with({})
        rows = apply_coverage_matrix(demand, contribution)
        self.assertEqual(len(rows), 5)
        self.assertEqual(
            [row.dimension for row in rows],
            list(PROJECT_DEMAND_DIMENSION_ORDER),
        )

    def test_demand_level_and_rationale_preserved(self):
        demand = _demand_mixed()
        contribution = _contribution_with({})
        rows = apply_coverage_matrix(demand, contribution)
        by_key = {row.dimension: row for row in rows}
        self.assertEqual(by_key["investigation"].demand_level, "critical")
        self.assertEqual(by_key["investigation"].demand_rationale, "Investigation is central.")
        self.assertEqual(by_key["validation"].demand_level, "useful")
        self.assertEqual(by_key["validation"].coverage_status, "gap")
        self.assertEqual(by_key["execution_momentum"].coverage_status, "not_required")

    def test_useful_gap_keeps_useful_demand_level(self):
        demand = _demand_all("useful", "Useful need.")
        rows = apply_coverage_matrix(demand, _contribution_with({}))
        for row in rows:
            self.assertEqual(row.demand_level, "useful")
            self.assertEqual(row.coverage_status, "gap")

    def test_absent_gap_explanations_preserve_demand_meaning(self):
        contribution = _contribution_with({})
        critical_rows = apply_coverage_matrix(_demand_all("critical"), contribution)
        important_rows = apply_coverage_matrix(_demand_all("important"), contribution)
        useful_rows = apply_coverage_matrix(_demand_all("useful"), contribution)
        for row in critical_rows:
            self.assertEqual(row.coverage_status, "gap")
            self.assertIn("requires", row.explanation.lower())
            self.assertNotIn("would be useful", row.explanation.lower())
        for row in important_rows:
            self.assertEqual(row.coverage_status, "gap")
            self.assertIn("requires", row.explanation.lower())
            self.assertNotIn("would be useful", row.explanation.lower())
        for row in useful_rows:
            self.assertEqual(row.demand_level, "useful")
            self.assertEqual(row.coverage_status, "gap")
            self.assertNotIn("requires", row.explanation.lower())
            self.assertIn("would be useful", row.explanation.lower())
            self.assertIn("does not contain this dimension", row.explanation.lower())

    def test_matrix_unchanged_for_useful_absent(self):
        self.assertEqual(resolve_coverage_status("useful", None), "gap")
        self.assertEqual(resolve_coverage_status("critical", None), "gap")
        self.assertEqual(resolve_coverage_status("important", None), "gap")
        self.assertEqual(resolve_coverage_status("not_required", None), "not_required")

    def test_critical_gap_keeps_critical_demand_level(self):
        demand = _demand_all("critical", "Critical need.")
        rows = apply_coverage_matrix(demand, _contribution_with({}))
        for row in rows:
            self.assertEqual(row.demand_level, "critical")
            self.assertEqual(row.coverage_status, "gap")

    def test_useful_supporting_is_covered(self):
        demand = _demand_all("useful")
        contribution = _contribution_with(
            {key: "supporting" for key in PROJECT_DEMAND_DIMENSION_ORDER}
        )
        rows = apply_coverage_matrix(demand, contribution)
        self.assertTrue(all(row.coverage_status == "covered" for row in rows))

    def test_critical_supporting_is_partially_covered(self):
        demand = _demand_all("critical")
        contribution = _contribution_with(
            {key: "supporting" for key in PROJECT_DEMAND_DIMENSION_ORDER}
        )
        rows = apply_coverage_matrix(demand, contribution)
        self.assertTrue(all(row.coverage_status == "partially_covered" for row in rows))

    def test_not_required_any_state(self):
        for state in ("primary", "strong", "supporting", "conditional", None):
            with self.subTest(state=state):
                states = (
                    {}
                    if state is None
                    else {key: state for key in PROJECT_DEMAND_DIMENSION_ORDER}
                )
                rows = apply_coverage_matrix(
                    _demand_all("not_required"),
                    _contribution_with(states),
                )
                self.assertTrue(all(row.coverage_status == "not_required" for row in rows))

    def test_does_not_invent_contribution_dimensions(self):
        demand = _demand_mixed()
        contribution = _contribution_with({"investigation": "strong"})
        rows = apply_coverage_matrix(demand, contribution)
        # Coverage has five demand rows; contribution_state only where present.
        present = [row for row in rows if row.contribution_state is not None]
        self.assertEqual(len(present), 1)
        self.assertEqual(present[0].dimension, "investigation")
        self.assertNotIn("leadership", [row.dimension for row in rows])

    def test_explanations_are_descriptive(self):
        demand = _demand_mixed()
        contribution = _contribution_with(
            {
                "investigation": "primary",
                "structuring": "supporting",
                "validation": "conditional",
            }
        )
        rows = apply_coverage_matrix(demand, contribution)
        blob = " ".join(row.explanation for row in rows).lower()
        for banned in (
            "the person can",
            "the person cannot",
            "good fit",
            "bad fit",
            "qualified",
            "unqualified",
            "hire",
            "reject",
        ):
            self.assertNotIn(banned, blob)
        by_key = {row.dimension: row for row in rows}
        self.assertIn("not required", by_key["execution_momentum"].explanation.lower())
        self.assertIn("would be useful", by_key["hands_on_delivery"].explanation.lower())
        self.assertNotIn("requires", by_key["hands_on_delivery"].explanation.lower())
        self.assertIn("does not contain", by_key["hands_on_delivery"].explanation.lower())


class CoverageOrchestrationTests(unittest.TestCase):
    def test_deterministic_identical_dumps(self):
        demand = build_project_demand(
            ProjectDemandRequest(
                label="Determinism check",
                dimensions=[
                    {
                        "dimension": key,
                        "demand_level": "important",
                        "rationale": f"Need {key}.",
                    }
                    for key in PROJECT_DEMAND_DIMENSION_ORDER
                ],
            )
        )
        person = ContributionProfileRequest(
            display_name="Avdey",
            sex="male",
            **AVDEY,
        )
        request = ContributionDemandCoverageRequest(
            project_demand=demand,
            person=person,
        )
        first = build_contribution_demand_coverage(request)
        second = build_contribution_demand_coverage(request)
        self.assertEqual(first.model_dump(), second.model_dump())

    def test_reuses_contribution_pipeline(self):
        demand = _demand_mixed()
        person = ContributionProfileRequest(display_name="Avdey", sex="male", **AVDEY)
        request = ContributionDemandCoverageRequest(
            project_demand=demand,
            person=person,
        )
        with patch(
            "app.services.contribution_demand_coverage.build_contribution_profile"
        ) as mock_build:
            mock_build.return_value = _contribution_with({"investigation": "primary"})
            with patch(
                "app.services.contribution_demand_coverage.build_mercury_source_profile"
            ) as mock_merc, patch(
                "app.services.contribution_demand_coverage.build_mars_source_profile"
            ) as mock_mars, patch(
                "app.services.contribution_demand_coverage.build_thinking_to_execution"
            ) as mock_tte, patch(
                "app.services.contribution_demand_coverage.build_person_perspective"
            ) as mock_person:
                mock_merc.return_value = object()
                mock_mars.return_value = object()
                mock_tte.return_value = object()
                mock_person.return_value = object()
                result = build_contribution_demand_coverage(request)
        mock_build.assert_called_once()
        self.assertEqual(result.dimensions[0].coverage_status, "covered")
        self.assertEqual(result.project_label, "Mixed demand project")
        self.assertEqual(result.person_display_name, "Avdey")

    def test_no_score_or_ranking_fields(self):
        demand = _demand_mixed()
        person = ContributionProfileRequest(display_name="Avdey", sex="male", **AVDEY)
        result = build_contribution_demand_coverage(
            ContributionDemandCoverageRequest(project_demand=demand, person=person)
        )
        dumped = result.model_dump()
        for banned in (
            "score",
            "fit_percent",
            "fit_percentage",
            "match_percent",
            "ranking",
            "suitability",
            "verdict",
        ):
            self.assertNotIn(banned, dumped)
        blob = result.model_dump_json().lower()
        self.assertNotIn("hire this", blob)
        self.assertNotIn("reject this", blob)
        self.assertNotIn("compatibility %", blob)
        self.assertNotIn("fit %", blob)
        for note in COVERAGE_NOTES:
            self.assertIn(note, result.notes)
        self.assertIn("not a candidate ranking", " ".join(result.notes).lower())
        self.assertIn("no hire/reject", " ".join(result.notes).lower())

    def test_endpoint_registered_and_returns_coverage(self):
        app = create_app()
        paths = {getattr(route, "path", None) for route in app.routes}
        self.assertIn("/api/v1/contribution-demand-coverage", paths)
        demand = build_project_demand(
            ProjectDemandRequest(
                label="API coverage project",
                dimensions=[
                    {
                        "dimension": key,
                        "demand_level": "useful",
                        "rationale": f"Useful {key}.",
                    }
                    for key in PROJECT_DEMAND_DIMENSION_ORDER
                ],
            )
        )
        response = create_contribution_demand_coverage(
            ContributionDemandCoverageRequest(
                project_demand=demand,
                person=ContributionProfileRequest(
                    display_name="Avdey",
                    sex="male",
                    **AVDEY,
                ),
            )
        )
        self.assertIsInstance(response, ContributionDemandCoverageResponse)
        self.assertEqual(len(response.dimensions), 5)
        self.assertEqual(
            [item.dimension for item in response.dimensions],
            list(PROJECT_DEMAND_DIMENSION_ORDER),
        )
        self.assertEqual(response.project_label, "API coverage project")
        self.assertEqual(response.notes, list(COVERAGE_NOTES))


class CoverageImportBoundaryTests(unittest.TestCase):
    def test_coverage_service_does_not_import_source_catalogs(self):
        path = (
            Path(__file__).resolve().parents[1]
            / "app"
            / "services"
            / "contribution_demand_coverage.py"
        )
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        banned = {
            "app.services.mercury_source_knowledge",
            "app.services.mars_source_knowledge",
            "app.services.mercury_facts",
            "app.services.mars_facts",
            "app.services.mars_profile_synthesis",
        }
        self.assertTrue(banned.isdisjoint(imported), imported & banned)
        source = path.read_text(encoding="utf-8")
        self.assertIn("build_contribution_profile", source)
        self.assertIn("resolve_coverage_status", source)
        self.assertIn("apply_coverage_matrix", source)

    def test_team_gap_route_still_registered(self):
        app = create_app()
        paths = {getattr(route, "path", None) for route in app.routes}
        self.assertIn("/api/v1/team-gap", paths)
        team_gap_path = (
            Path(__file__).resolve().parents[1] / "app" / "api" / "routes" / "team_gap.py"
        )
        self.assertTrue(team_gap_path.exists())
        # Team Gap module source unchanged in intent: still analyzes team functions.
        src = team_gap_path.read_text(encoding="utf-8")
        self.assertIn("analyze_team_gap", src)
        self.assertNotIn("contribution-demand-coverage", src)
        self.assertNotIn("CoverageStatus", src)


if __name__ == "__main__":
    unittest.main()
