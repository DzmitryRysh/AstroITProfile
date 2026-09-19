"""M11 Phase 2A — Project Demand v1 backend contract tests."""

from __future__ import annotations

import ast
import inspect
import unittest
from pathlib import Path

from pydantic import ValidationError

from app.core.app import create_app
from app.schemas.project_demand import (
    PROJECT_DEMAND_DIMENSION_ORDER,
    ProjectDemandRequest,
)
from app.services.contribution_profile import CONTRIBUTION_DIMENSION_SPECS
from app.services.project_demand import PROJECT_DEMAND_NOTES, build_project_demand
from app.api.routes.project_demand import create_project_demand


def _dim(dimension: str, level: str, rationale: str) -> dict:
    return {
        "dimension": dimension,
        "demand_level": level,
        "rationale": rationale,
    }


def _complete_dimensions(**overrides: dict) -> list[dict]:
    base = {
        "investigation": _dim(
            "investigation",
            "critical",
            "Requirements are ambiguous and root-cause analysis is central.",
        ),
        "structuring": _dim(
            "structuring",
            "important",
            "Delivery needs a planned sequence before build starts.",
        ),
        "validation": _dim(
            "validation",
            "important",
            "Claims must be checked against evidence before release.",
        ),
        "execution_momentum": _dim(
            "execution_momentum",
            "useful",
            "Once scoped, the work benefits from quick starts.",
        ),
        "hands_on_delivery": _dim(
            "hands_on_delivery",
            "not_required",
            "This phase is planning-only; implementation is handled elsewhere.",
        ),
    }
    base.update(overrides)
    # Non-canonical request order on purpose.
    return [
        base["hands_on_delivery"],
        base["validation"],
        base["investigation"],
        base["execution_momentum"],
        base["structuring"],
    ]


def _request(**kwargs) -> ProjectDemandRequest:
    payload = {
        "label": "Ambiguous discovery sprint",
        "description": "Clarify requirements before build.",
        "dimensions": _complete_dimensions(),
        "assumptions": ["Planning phase only"],
    }
    payload.update(kwargs)
    return ProjectDemandRequest(**payload)


class ProjectDemandParityTests(unittest.TestCase):
    def test_dimension_keys_match_contribution_exactly(self):
        contribution_keys = tuple(spec.key for spec in CONTRIBUTION_DIMENSION_SPECS)
        self.assertEqual(PROJECT_DEMAND_DIMENSION_ORDER, contribution_keys)
        self.assertEqual(
            set(PROJECT_DEMAND_DIMENSION_ORDER),
            {
                "investigation",
                "structuring",
                "validation",
                "execution_momentum",
                "hands_on_delivery",
            },
        )


class ProjectDemandDomainTests(unittest.TestCase):
    def test_canonical_ordering_and_metadata(self):
        result = build_project_demand(_request())
        self.assertEqual(
            [item.dimension for item in result.dimensions],
            list(PROJECT_DEMAND_DIMENSION_ORDER),
        )
        self.assertEqual(result.created_from, "explicit")
        self.assertTrue(all(item.source == "user" for item in result.dimensions))
        self.assertEqual(len(result.dimensions), 5)
        self.assertEqual(result.label, "Ambiguous discovery sprint")
        self.assertEqual(result.assumptions, ["Planning phase only"])
        self.assertEqual(result.notes, list(PROJECT_DEMAND_NOTES))

    def test_request_order_does_not_affect_response(self):
        forward = build_project_demand(_request())
        reverse_dims = list(reversed(_complete_dimensions()))
        # Rebuild a valid complete set in another shuffle.
        by_key = {item["dimension"]: item for item in reverse_dims}
        shuffled = [
            by_key["validation"],
            by_key["hands_on_delivery"],
            by_key["structuring"],
            by_key["investigation"],
            by_key["execution_momentum"],
        ]
        backward = build_project_demand(
            ProjectDemandRequest(
                label="Ambiguous discovery sprint",
                description="Clarify requirements before build.",
                dimensions=shuffled,
                assumptions=["Planning phase only"],
            )
        )
        self.assertEqual(forward.model_dump(), backward.model_dump())

    def test_deterministic_identical_requests(self):
        first = build_project_demand(_request())
        second = build_project_demand(_request())
        self.assertEqual(first.model_dump(), second.model_dump())


class ProjectDemandValidationTests(unittest.TestCase):
    def test_missing_dimension_rejected(self):
        dims = _complete_dimensions()
        dims = [item for item in dims if item["dimension"] != "validation"]
        dims.append(
            _dim(
                "investigation",
                "useful",
                "Duplicate filler that still leaves validation missing.",
            )
        )
        with self.assertRaises(ValidationError):
            ProjectDemandRequest(
                label="Incomplete",
                dimensions=dims[:5],
            )

    def test_duplicate_dimension_rejected(self):
        dims = _complete_dimensions()
        dims[0] = _dim(
            "investigation",
            "useful",
            "Duplicate investigation entry.",
        )
        # Now investigation appears twice and hands_on may still be present —
        # force duplicate by replacing another slot with investigation.
        dims[1] = _dim(
            "investigation",
            "important",
            "Second investigation entry.",
        )
        with self.assertRaises(ValidationError) as ctx:
            ProjectDemandRequest(label="Dupes", dimensions=dims)
        self.assertIn("duplicate", str(ctx.exception).lower())

    def test_unknown_dimension_rejected(self):
        dims = _complete_dimensions()
        dims[0] = {
            "dimension": "leadership",
            "demand_level": "critical",
            "rationale": "Unsupported dimension must fail.",
        }
        with self.assertRaises(ValidationError):
            ProjectDemandRequest(label="Unknown dim", dimensions=dims)

    def test_invalid_level_rejected(self):
        dims = _complete_dimensions(
            investigation=_dim(
                "investigation",
                "primary",
                "Person states are not demand levels.",
            )
        )
        with self.assertRaises(ValidationError):
            ProjectDemandRequest(label="Bad level", dimensions=dims)

    def test_blank_rationale_rejected(self):
        dims = _complete_dimensions(
            investigation=_dim("investigation", "critical", "   ")
        )
        with self.assertRaises(ValidationError):
            ProjectDemandRequest(label="Blank rationale", dimensions=dims)

    def test_blank_label_rejected(self):
        with self.assertRaises(ValidationError):
            ProjectDemandRequest(label="   ", dimensions=_complete_dimensions())

    def test_not_required_still_needs_rationale(self):
        dims = _complete_dimensions(
            hands_on_delivery=_dim("hands_on_delivery", "not_required", "")
        )
        with self.assertRaises(ValidationError):
            ProjectDemandRequest(label="Needs rationale", dimensions=dims)

    def test_missing_dimension_not_silently_not_required(self):
        """Four dimensions must fail — absence is not not_required."""
        dims = [
            item
            for item in _complete_dimensions()
            if item["dimension"] != "hands_on_delivery"
        ]
        with self.assertRaises(ValidationError):
            ProjectDemandRequest(label="Four only", dimensions=dims)


class ProjectDemandIndependenceTests(unittest.TestCase):
    def test_request_schema_has_no_natal_fields(self):
        fields = set(ProjectDemandRequest.model_fields)
        for forbidden in (
            "birth_date",
            "birth_time",
            "birth_place",
            "display_name",
            "sex",
            "person",
            "mercury",
            "mars",
        ):
            self.assertNotIn(forbidden, fields)

    def test_service_module_has_no_astrology_imports(self):
        service_path = (
            Path(__file__).resolve().parents[1]
            / "app"
            / "services"
            / "project_demand.py"
        )
        tree = ast.parse(service_path.read_text(encoding="utf-8"))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.add(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        forbidden_prefixes = (
            "app.services.mercury",
            "app.services.mars",
            "app.services.thinking_to_execution",
            "app.services.contribution_profile",
            "app.services.astro",
            "app.services.team_gap",
            "app.services.team_map",
            "app.services.candidate",
        )
        for module in imported:
            self.assertFalse(
                any(module == prefix or module.startswith(prefix + ".") for prefix in forbidden_prefixes),
                msg=f"unexpected import: {module}",
            )
        source = inspect.getsource(build_project_demand)
        self.assertNotIn("build_mercury", source)
        self.assertNotIn("build_mars", source)
        self.assertNotIn("birth_", source)


class ProjectDemandSafetyTests(unittest.TestCase):
    def test_no_score_fit_or_hire_fields(self):
        result = build_project_demand(_request())
        dumped = result.model_dump()
        blob = result.model_dump_json().lower()
        for key in (
            "score",
            "fit",
            "percentage",
            "rank",
            "compatibility",
            "suitability",
        ):
            self.assertNotIn(key, dumped)
        self.assertNotIn("hire this", blob)
        self.assertNotIn("reject this", blob)
        self.assertNotIn("compatibility %", blob)
        self.assertIn("not a candidate ranking", blob)
        self.assertIn("work contribution requirements", blob)
        self.assertIn("no hire/reject recommendation", blob)
        for note in result.notes:
            self.assertNotIn("%", note)


class ProjectDemandApiTests(unittest.TestCase):
    def test_route_registered_and_returns_canonical(self):
        app = create_app()
        paths = {getattr(route, "path", None) for route in app.routes}
        self.assertIn("/api/v1/project-demand", paths)
        response = create_project_demand(_request())
        self.assertEqual(
            [item.dimension for item in response.dimensions],
            list(PROJECT_DEMAND_DIMENSION_ORDER),
        )
        self.assertEqual(response.created_from, "explicit")


class ProjectDemandTeamGapBoundaryTests(unittest.TestCase):
    def test_team_gap_files_untouched_by_this_module(self):
        # Boundary documentation: Project Demand must not import Team Gap.
        service_src = (
            Path(__file__).resolve().parents[1]
            / "app"
            / "services"
            / "project_demand.py"
        ).read_text(encoding="utf-8")
        self.assertIn("Team Gap", service_src)
        self.assertNotIn("from app.services.team_gap", service_src)
        self.assertNotIn("team_coverage_profiles", service_src)
        self.assertNotIn("candidate_team_impact", service_src)


if __name__ == "__main__":
    unittest.main()
