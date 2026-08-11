import unittest
from pathlib import Path

from fastapi.responses import FileResponse
from starlette.routing import Mount, Route

from app.core.app import RECRUITER_UI_DIR, create_app

RECRUITER_INDEX = RECRUITER_UI_DIR / "index.html"
RECRUITER_CSS = RECRUITER_UI_DIR / "styles.css"
RECRUITER_JS = RECRUITER_UI_DIR / "app.js"


class RecruiterPrototypeAssetTests(unittest.TestCase):
    def test_recruiter_html_exists(self):
        self.assertTrue(RECRUITER_INDEX.is_file())

    def test_recruiter_css_exists(self):
        self.assertTrue(RECRUITER_CSS.is_file())

    def test_recruiter_js_exists(self):
        self.assertTrue(RECRUITER_JS.is_file())

    def test_recruiter_dir_is_pathlib_based(self):
        self.assertIsInstance(RECRUITER_UI_DIR, Path)
        self.assertTrue(RECRUITER_UI_DIR.is_dir())
        self.assertEqual(RECRUITER_UI_DIR.name, "recruiter")


class RecruiterPrototypeRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()

    def test_recruiter_route_is_registered(self):
        paths = {getattr(route, "path", None) for route in self.app.routes}
        self.assertIn("/recruiter", paths)

    def test_recruiter_serves_intended_index_file(self):
        route = next(
            item
            for item in self.app.routes
            if isinstance(item, Route) and item.path == "/recruiter"
        )
        response = route.endpoint()
        self.assertIsInstance(response, FileResponse)
        self.assertEqual(Path(response.path).resolve(), RECRUITER_INDEX.resolve())
        body = RECRUITER_INDEX.read_text(encoding="utf-8")
        self.assertIn("AstroIT", body)
        self.assertIn("Team Intelligence", body)
        self.assertIn("/recruiter/assets/styles.css", body)
        self.assertIn("/recruiter/assets/app.js", body)

    def test_recruiter_assets_mount_uses_ui_directory(self):
        mount = next(
            item
            for item in self.app.routes
            if isinstance(item, Mount) and item.path == "/recruiter/assets"
        )
        self.assertEqual(Path(mount.app.directory).resolve(), RECRUITER_UI_DIR.resolve())
        self.assertTrue((RECRUITER_UI_DIR / "styles.css").is_file())
        self.assertTrue((RECRUITER_UI_DIR / "app.js").is_file())

    def test_existing_api_routes_remain_registered(self):
        paths = {getattr(route, "path", None) for route in self.app.routes}
        self.assertIn("/api/v1/profile", paths)
        self.assertIn("/api/v1/mercury-work-profile", paths)
        self.assertIn("/api/v1/candidate-compare", paths)
        self.assertIn("/api/v1/team-map", paths)
        self.assertIn("/api/v1/team-gap", paths)
        self.assertIn("/api/v1/candidate-team-impact", paths)
        self.assertIn("/", paths)
        self.assertIn("/health", paths)


class RecruiterUxPolishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = RECRUITER_INDEX.read_text(encoding="utf-8")
        cls.css = RECRUITER_CSS.read_text(encoding="utf-8")
        cls.js = RECRUITER_JS.read_text(encoding="utf-8")
        cls.blob = f"{cls.html}\n{cls.css}\n{cls.js}"

    def test_setup_forms_are_not_primary_visible_content(self):
        self.assertIn('id="empty-state"', self.html)
        self.assertIn('id="setup-overlay"', self.html)
        self.assertIn("hidden", self.html.split('id="setup-overlay"', 1)[1].split(">", 1)[0])
        empty_pos = self.html.find('id="empty-state"')
        members_pos = self.html.find('id="members-list"')
        self.assertLess(empty_pos, members_pos)
        self.assertIn("setup-drawer", self.html)

    def test_workspace_empty_state_exists(self):
        self.assertIn("Build a team intelligence view", self.html)
        self.assertIn("Load Demo Scenario", self.html)
        self.assertIn("Set Up Team", self.html)

    def test_edit_team_data_action_exists(self):
        self.assertIn("Edit Team Data", self.html)
        self.assertIn("Apply &amp; Analyze", self.html)

    def test_load_demo_scenario_exists(self):
        self.assertIn("Load Demo Scenario", self.html)
        self.assertIn("loadDemoAndAnalyze", self.js)
        self.assertIn("AI Platform Team", self.js)

    def test_workflow_stage_ui_contains_lifecycle(self):
        blob = f"{self.html}\n{self.js}\n{self.css}"
        for stage in ("Explore", "Validate", "Productionize", "Connect"):
            self.assertIn(stage, blob)
        self.assertIn("workflow-strip", self.html)
        self.assertIn("workflow-strip", self.css)
        self.assertIn("renderWorkflowStrip", self.js)

    def test_candidate_impact_preview_calls_existing_endpoint(self):
        self.assertIn("loadImpactPreviews", self.js)
        self.assertIn('/api/v1/candidate-team-impact', self.js)
        self.assertIn("closed_missing_functions", self.js)
        self.assertIn("CLOSES CURRENT GAP", self.js)
        self.assertNotIn("inferTeamFunction", self.js)
        self.assertNotIn("calculateGap", self.js)

    def test_full_before_after_is_secondary(self):
        self.assertIn("View Full Before / After", self.js)
        self.assertIn("<details", self.js)
        self.assertIn("ba-table", self.js)

    def test_no_score_ranking_or_hire_ui(self):
        lowered = self.blob.lower()
        forbidden = [
            "impact_score",
            "fit_score",
            "match_percentage",
            "coverage_percentage",
            "recommended_candidate",
            "best candidate",
            "hire recommendation",
            "reject candidate",
            "rank #",
            "candidate_rank",
        ]
        for term in forbidden:
            self.assertNotIn(term, lowered, term)

    def test_no_astrology_engine_terms_in_main_workspace(self):
        workspace_html = self.html.split("id=\"workspace\"", 1)[1].split("id=\"setup-overlay\"", 1)[0].lower()
        empty_html = self.html.split("id=\"empty-state\"", 1)[1].split("id=\"workspace\"", 1)[0].lower()
        for term in ("mercury", "zodiac", "aspect", "dispositor", "retrograde", "longitude", "house"):
            self.assertNotIn(term, workspace_html, term)
            self.assertNotIn(term, empty_html, term)

    def test_workspace_header_is_single_compact_context(self):
        self.assertIn('id="workspace-context"', self.html)
        self.assertNotIn('id="workspace-summary"', self.html)
        self.assertIn("renderWorkspaceHeader", self.js)
        self.assertIn("shortlisted candidate", self.js)
        self.assertNotIn("Target role:", self.js)

    def test_workflow_gap_appears_once_under_coverage_strip(self):
        self.assertEqual(self.html.count('id="gap-priority"'), 1)
        self.assertIn("gap-priority", self.html.split('id="workflow-strip"', 1)[1])
        self.assertNotIn("summary-gap", self.js)

    def test_impact_delta_uses_before_after_labels_without_duplicate_status_text(self):
        self.assertIn("statusTransitionHtml", self.js)
        self.assertIn("delta-label", self.js)
        self.assertIn(">Before<", self.js)
        self.assertIn(">After<", self.js)
        # Chips carry the status wording; do not repeat it as sibling strong text.
        self.assertNotIn("${statusChip(\"missing\")}<strong>Missing</strong>", self.js)
        self.assertNotIn("${statusChip(\"single_coverage\")}<strong>Single Coverage</strong>", self.js)


if __name__ == "__main__":
    unittest.main()
