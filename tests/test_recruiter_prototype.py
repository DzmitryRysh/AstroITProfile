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


if __name__ == "__main__":
    unittest.main()
