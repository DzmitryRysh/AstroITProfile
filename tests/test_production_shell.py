"""M13A — production shell runtime checks and app factory."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.responses import RedirectResponse
from fastapi.testclient import TestClient

from app.core.app import create_app
from app.core.runtime_checks import (
    places_data_path,
    validate_places_data,
    validate_runtime,
    validate_workspace_store_writable,
    workspace_store_path,
)
from app.services.workspace_repository import default_store_path


class RuntimePathTests(unittest.TestCase):
    def test_places_path_is_posix_friendly_and_exists(self):
        path = places_data_path()
        self.assertTrue(path.is_file())
        self.assertEqual(path.name, "places.json")
        # No Windows drive-letter hardcoding in helper output.
        self.assertFalse(str(path).startswith("C:\\app\\"))

    def test_workspace_env_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "nested" / "workspaces.json"
            previous = os.environ.get("ASTROIT_WORKSPACE_STORE_PATH")
            os.environ["ASTROIT_WORKSPACE_STORE_PATH"] = str(target)
            try:
                resolved = default_store_path()
                self.assertEqual(resolved, target.resolve())
                self.assertEqual(workspace_store_path(), target.resolve())
            finally:
                if previous is None:
                    os.environ.pop("ASTROIT_WORKSPACE_STORE_PATH", None)
                else:
                    os.environ["ASTROIT_WORKSPACE_STORE_PATH"] = previous

    def test_validate_places_missing_fails_explicitly(self):
        missing = Path(tempfile.gettempdir()) / "astroit-missing-places.json"
        if missing.exists():
            missing.unlink()
        with self.assertRaises(RuntimeError) as ctx:
            validate_places_data(missing)
        self.assertIn("places data", str(ctx.exception).lower())

    def test_validate_workspace_store_creates_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "vol" / "workspaces.json"
            resolved = validate_workspace_store_writable(store)
            self.assertEqual(resolved, store.resolve())
            self.assertTrue(store.parent.is_dir())

    def test_validate_runtime_ok_with_temp_store(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "workspaces.json"
            result = validate_runtime(workspace_store=store)
            self.assertEqual(result["workspace_store_path"], str(store.resolve()))
            self.assertTrue(Path(result["places_path"]).is_file())


class ProductionAppFactoryTests(unittest.TestCase):
    def test_create_app_with_valid_runtime_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "workspaces.json"
            previous = os.environ.get("ASTROIT_WORKSPACE_STORE_PATH")
            os.environ["ASTROIT_WORKSPACE_STORE_PATH"] = str(store)
            try:
                app = create_app()
                paths = {getattr(route, "path", None) for route in app.routes}
                self.assertIn("/health", paths)
                self.assertIn("/recruiter", paths)
                self.assertIn("/api/v1/health", paths)
                health_routes = [
                    route
                    for route in app.routes
                    if getattr(route, "path", None) == "/health"
                ]
                self.assertTrue(health_routes)
                endpoint = health_routes[0].endpoint
                self.assertEqual(endpoint(), {"status": "ok"})
            finally:
                if previous is None:
                    os.environ.pop("ASTROIT_WORKSPACE_STORE_PATH", None)
                else:
                    os.environ["ASTROIT_WORKSPACE_STORE_PATH"] = previous

    def test_create_app_fails_when_places_missing(self):
        with patch("app.core.app.validate_runtime") as mocked:
            mocked.side_effect = RuntimeError(
                "Required places data file is missing or unreadable: x"
            )
            with self.assertRaises(RuntimeError):
                create_app()

    def test_startup_checks_can_be_skipped(self):
        app = create_app(run_startup_checks=False)
        self.assertIsNotNone(app)

    def test_root_redirects_to_recruiter(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "workspaces.json"
            previous = os.environ.get("ASTROIT_WORKSPACE_STORE_PATH")
            gate_prev = os.environ.get("ASTROIT_BETA_GATE_ENABLED")
            os.environ["ASTROIT_WORKSPACE_STORE_PATH"] = str(store)
            os.environ.pop("ASTROIT_BETA_GATE_ENABLED", None)
            client = None
            try:
                app = create_app()
                client = TestClient(app)
                response = client.get("/", follow_redirects=False)
                self.assertEqual(response.status_code, 303)
                self.assertEqual(response.headers["location"], "/recruiter")
                root_route = next(
                    route
                    for route in app.routes
                    if getattr(route, "path", None) == "/"
                )
                payload = root_route.endpoint()
                self.assertIsInstance(payload, RedirectResponse)
                self.assertEqual(payload.headers["location"], "/recruiter")
            finally:
                if client is not None:
                    client.close()
                if previous is None:
                    os.environ.pop("ASTROIT_WORKSPACE_STORE_PATH", None)
                else:
                    os.environ["ASTROIT_WORKSPACE_STORE_PATH"] = previous
                if gate_prev is None:
                    os.environ.pop("ASTROIT_BETA_GATE_ENABLED", None)
                else:
                    os.environ["ASTROIT_BETA_GATE_ENABLED"] = gate_prev

    def test_health_remains_public_ok_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "workspaces.json"
            previous = os.environ.get("ASTROIT_WORKSPACE_STORE_PATH")
            os.environ["ASTROIT_WORKSPACE_STORE_PATH"] = str(store)
            client = None
            try:
                app = create_app()
                client = TestClient(app)
                response = client.get("/health")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), {"status": "ok"})
            finally:
                if client is not None:
                    client.close()
                if previous is None:
                    os.environ.pop("ASTROIT_WORKSPACE_STORE_PATH", None)
                else:
                    os.environ["ASTROIT_WORKSPACE_STORE_PATH"] = previous


class DebugNoiseTests(unittest.TestCase):
    def test_astro_service_has_no_debug_aspects_print(self):
        source = (
            Path(__file__).resolve().parents[1]
            / "app"
            / "services"
            / "astro_service.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("DEBUG ASPECTS", source)
        self.assertNotIn('print("DEBUG ASPECTS"', source)


if __name__ == "__main__":
    unittest.main()
