"""M13B — invite-only beta gate and workspace scope privacy."""

from __future__ import annotations

import os
import tempfile
import unittest
from datetime import date, time as dt_time
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.app import create_app
from app.core.beta_access import (
    AUTH_COOKIE_NAME,
    SCOPE_COOKIE_NAME,
    access_code_matches,
    issue_auth_token,
    verify_token,
)
from app.core.settings import (
    load_beta_settings,
    parse_bool_env,
    validate_beta_settings,
)
from app.schemas.candidate_compare import CandidateInput
from app.schemas.team_map import TeamMemberInput
from app.schemas.workspace import WorkspaceData
from app.services.workspace_repository import WorkspaceRepository
from app.services.workspace_service import WorkspaceService


def _member(member_id: str = "A") -> TeamMemberInput:
    return TeamMemberInput(
        member_id=member_id,
        display_name=f"Member {member_id}",
        current_role="ML Engineer",
        birth_date=date(1986, 2, 8),
        birth_time=dt_time(20, 20),
        birth_place="Kingisepp, Russia",
    )


def _candidate(candidate_id: str = "C") -> CandidateInput:
    return CandidateInput(
        candidate_id=candidate_id,
        display_name=f"Candidate {candidate_id}",
        birth_date=date(1997, 1, 28),
        birth_time=dt_time(10, 0),
        birth_place="Miami, USA",
    )


def _payload(**overrides) -> WorkspaceData:
    data = {
        "team_name": "AI Platform Team",
        "coverage_profile": "ai_ml_product_delivery",
        "target_role": "ML Engineer",
        "members": [_member("A")],
        "candidates": [_candidate("C")],
    }
    data.update(overrides)
    return WorkspaceData(**data)


class _EnvGuard:
    def __init__(self, **values: str | None):
        self.values = values
        self.previous: dict[str, str | None] = {}

    def __enter__(self):
        for key, value in self.values.items():
            self.previous[key] = os.environ.get(key)
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        return self

    def __exit__(self, *exc):
        for key, value in self.previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


class BetaConfigTests(unittest.TestCase):
    def test_gate_disabled_by_default(self):
        with _EnvGuard(
            ASTROIT_BETA_GATE_ENABLED=None,
            ASTROIT_BETA_ACCESS_CODE="secret-code",
            ASTROIT_SESSION_SECRET="abcdefghijklmnopqrstuv",
        ):
            settings = load_beta_settings()
            self.assertFalse(settings.gate_enabled)
            validate_beta_settings(settings)

    def test_gate_enabled_requires_access_code(self):
        with _EnvGuard(
            ASTROIT_BETA_GATE_ENABLED="true",
            ASTROIT_BETA_ACCESS_CODE="",
            ASTROIT_SESSION_SECRET="abcdefghijklmnopqrstuv",
        ):
            with self.assertRaises(RuntimeError) as ctx:
                validate_beta_settings()
            self.assertIn("ASTROIT_BETA_ACCESS_CODE", str(ctx.exception))

    def test_gate_enabled_requires_session_secret(self):
        with _EnvGuard(
            ASTROIT_BETA_GATE_ENABLED="yes",
            ASTROIT_BETA_ACCESS_CODE="invite",
            ASTROIT_SESSION_SECRET="short",
        ):
            with self.assertRaises(RuntimeError) as ctx:
                validate_beta_settings()
            self.assertIn("ASTROIT_SESSION_SECRET", str(ctx.exception))

    def test_bool_parser(self):
        self.assertTrue(parse_bool_env("1"))
        self.assertTrue(parse_bool_env("TRUE"))
        self.assertTrue(parse_bool_env("on"))
        self.assertFalse(parse_bool_env("0"))
        self.assertFalse(parse_bool_env(None))


class BetaAuthFlowTests(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.store = Path(self._tmpdir.name) / "workspaces.json"
        self.env = _EnvGuard(
            ASTROIT_BETA_GATE_ENABLED="true",
            ASTROIT_BETA_ACCESS_CODE="beta-invite-code",
            ASTROIT_SESSION_SECRET="unit-test-session-secret-key",
            ASTROIT_COOKIE_SECURE="false",
            ASTROIT_WORKSPACE_STORE_PATH=str(self.store),
        )
        self.env.__enter__()
        self.app = create_app()
        self.client = TestClient(self.app)

    def tearDown(self):
        self.client.close()
        self.env.__exit__(None, None, None)
        self._tmpdir.cleanup()

    def test_health_remains_public(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_unauthenticated_root_lands_at_beta_access(self):
        response = self.client.get("/", follow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "/beta-access")

    def test_authenticated_root_redirects_to_recruiter(self):
        self.client.post(
            "/beta-access",
            data={"access_code": "beta-invite-code"},
            follow_redirects=False,
        )
        response = self.client.get("/", follow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "/recruiter")

    def test_beta_login_includes_product_framing(self):
        response = self.client.get("/beta-access")
        self.assertEqual(response.status_code, 200)
        body = response.text
        self.assertIn("Private Beta", body)
        self.assertIn("work-style and team-contribution patterns", body)
        self.assertIn("structured", body.lower())
        self.assertIn("astrological profiles", body)

    def test_unauthenticated_recruiter_redirects(self):
        response = self.client.get("/recruiter", follow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "/beta-access")

    def test_unauthenticated_api_returns_401(self):
        response = self.client.get("/api/v1/workspaces")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Authentication required")

    def test_docs_and_openapi_protected(self):
        docs = self.client.get("/docs", follow_redirects=False)
        self.assertEqual(docs.status_code, 303)
        self.assertEqual(docs.headers["location"], "/beta-access")
        openapi = self.client.get("/openapi.json")
        self.assertEqual(openapi.status_code, 401)

    def test_correct_access_code_authenticates(self):
        response = self.client.post(
            "/beta-access",
            data={"access_code": "beta-invite-code"},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "/recruiter")
        self.assertIn(AUTH_COOKIE_NAME, response.cookies)
        self.assertIn(SCOPE_COOKIE_NAME, response.cookies)
        set_cookies = response.headers.get_list("set-cookie")
        joined = ";".join(set_cookies).lower()
        self.assertIn("httponly", joined)
        self.assertIn(AUTH_COOKIE_NAME.lower(), joined)

        recruiter = self.client.get("/recruiter", follow_redirects=False)
        self.assertEqual(recruiter.status_code, 200)

    def test_incorrect_access_code_fails(self):
        response = self.client.post(
            "/beta-access",
            data={"access_code": "wrong-code"},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("not valid", response.text)
        self.assertNotIn(AUTH_COOKIE_NAME, response.cookies)

    def test_tampered_auth_cookie_rejected(self):
        self.client.post(
            "/beta-access",
            data={"access_code": "beta-invite-code"},
            follow_redirects=False,
        )
        self.client.cookies.set(AUTH_COOKIE_NAME, "tampered.payload.signature")
        response = self.client.get("/api/v1/workspaces")
        self.assertEqual(response.status_code, 401)

    def test_logout_clears_auth_session(self):
        self.client.post(
            "/beta-access",
            data={"access_code": "beta-invite-code"},
            follow_redirects=False,
        )
        logout = self.client.post("/beta-logout", follow_redirects=False)
        self.assertEqual(logout.status_code, 303)
        response = self.client.get("/recruiter", follow_redirects=False)
        self.assertEqual(response.status_code, 303)

    def test_docs_accessible_after_login(self):
        self.client.post(
            "/beta-access",
            data={"access_code": "beta-invite-code"},
            follow_redirects=False,
        )
        docs = self.client.get("/docs", follow_redirects=False)
        self.assertEqual(docs.status_code, 200)


class WorkspacePrivacyTests(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.store = Path(self._tmpdir.name) / "workspaces.json"
        self.env = _EnvGuard(
            ASTROIT_BETA_GATE_ENABLED="true",
            ASTROIT_BETA_ACCESS_CODE="beta-invite-code",
            ASTROIT_SESSION_SECRET="unit-test-session-secret-key",
            ASTROIT_COOKIE_SECURE="false",
            ASTROIT_WORKSPACE_STORE_PATH=str(self.store),
        )
        self.env.__enter__()
        self.app = create_app()

    def tearDown(self):
        self.env.__exit__(None, None, None)
        self._tmpdir.cleanup()

    def _login_client(self) -> TestClient:
        client = TestClient(self.app)
        client.post(
            "/beta-access",
            data={"access_code": "beta-invite-code"},
            follow_redirects=False,
        )
        return client

    def test_scopes_isolate_workspaces(self):
        client_a = self._login_client()
        client_b = self._login_client()
        try:
            created = client_a.post(
                "/api/v1/workspaces",
                json=_payload(team_name="Scope A Team").model_dump(mode="json"),
            )
            self.assertEqual(created.status_code, 201)
            workspace_id = created.json()["workspace_id"]

            list_a = client_a.get("/api/v1/workspaces")
            self.assertEqual(list_a.status_code, 200)
            self.assertEqual(len(list_a.json()["workspaces"]), 1)
            self.assertEqual(list_a.json()["workspaces"][0]["workspace_id"], workspace_id)

            list_b = client_b.get("/api/v1/workspaces")
            self.assertEqual(list_b.status_code, 200)
            self.assertEqual(list_b.json()["workspaces"], [])

            get_b = client_b.get(f"/api/v1/workspaces/{workspace_id}")
            self.assertEqual(get_b.status_code, 404)

            update_b = client_b.put(
                f"/api/v1/workspaces/{workspace_id}",
                json=_payload(team_name="Hijacked").model_dump(mode="json"),
            )
            self.assertEqual(update_b.status_code, 404)

            delete_b = client_b.delete(f"/api/v1/workspaces/{workspace_id}")
            self.assertEqual(delete_b.status_code, 404)

            get_a = client_a.get(f"/api/v1/workspaces/{workspace_id}")
            self.assertEqual(get_a.status_code, 200)
            self.assertEqual(get_a.json()["team_name"], "Scope A Team")
        finally:
            client_a.close()
            client_b.close()

    def test_legacy_unscoped_hidden_when_gate_enabled(self):
        repo = WorkspaceRepository(store_path=self.store)
        legacy = repo.create_record(_payload(team_name="Legacy Team"))
        self.assertIsNone(legacy.workspace_scope_id)

        client = self._login_client()
        try:
            listed = client.get("/api/v1/workspaces")
            self.assertEqual(listed.status_code, 200)
            self.assertEqual(listed.json()["workspaces"], [])
            opened = client.get(f"/api/v1/workspaces/{legacy.workspace_id}")
            self.assertEqual(opened.status_code, 404)
        finally:
            client.close()

    def test_scoping_survives_repository_reload(self):
        client = self._login_client()
        try:
            created = client.post(
                "/api/v1/workspaces",
                json=_payload(team_name="Persistent Scope").model_dump(mode="json"),
            )
            self.assertEqual(created.status_code, 201)
            workspace_id = created.json()["workspace_id"]
        finally:
            client.close()

        fresh_repo = WorkspaceRepository(store_path=self.store)
        record = fresh_repo.get_record(workspace_id)
        self.assertIsNotNone(record)
        self.assertTrue(record.workspace_scope_id)

        service = WorkspaceService(repository=fresh_repo)
        visible = service.list_workspaces(
            workspace_scope_id=record.workspace_scope_id,
            require_scope=True,
        )
        self.assertEqual(len(visible.workspaces), 1)
        hidden = service.list_workspaces(
            workspace_scope_id="other-scope",
            require_scope=True,
        )
        self.assertEqual(hidden.workspaces, [])

    def test_gate_disabled_keeps_unscoped_visible(self):
        repo = WorkspaceRepository(store_path=self.store)
        legacy = repo.create_record(_payload(team_name="Local Legacy"))
        service = WorkspaceService(repository=repo)
        listed = service.list_workspaces(require_scope=False)
        ids = [item.workspace_id for item in listed.workspaces]
        self.assertIn(legacy.workspace_id, ids)


class BetaTokenHelperTests(unittest.TestCase):
    def test_access_code_compare(self):
        self.assertTrue(access_code_matches("abc", "abc"))
        self.assertFalse(access_code_matches("abc", "abd"))
        self.assertFalse(access_code_matches("", "abc"))

    def test_token_roundtrip_and_tamper(self):
        with _EnvGuard(
            ASTROIT_BETA_GATE_ENABLED="true",
            ASTROIT_BETA_ACCESS_CODE="code",
            ASTROIT_SESSION_SECRET="unit-test-session-secret-key",
        ):
            settings = load_beta_settings()
            token = issue_auth_token(settings)
            payload = verify_token(token, settings.session_secret)
            self.assertIsNotNone(payload)
            self.assertEqual(payload["typ"], "beta_auth")
            bad = token[:-4] + "dead"
            self.assertIsNone(verify_token(bad, settings.session_secret))


class GateDisabledAppTests(unittest.TestCase):
    def test_gate_disabled_preserves_open_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "workspaces.json"
            with _EnvGuard(
                ASTROIT_BETA_GATE_ENABLED="false",
                ASTROIT_BETA_ACCESS_CODE=None,
                ASTROIT_SESSION_SECRET=None,
                ASTROIT_WORKSPACE_STORE_PATH=str(store),
            ):
                app = create_app()
                with TestClient(app) as client:
                    health = client.get("/health")
                    self.assertEqual(health.status_code, 200)
                    recruiter = client.get("/recruiter")
                    self.assertEqual(recruiter.status_code, 200)
                    workspaces = client.get("/api/v1/workspaces")
                    self.assertEqual(workspaces.status_code, 200)


if __name__ == "__main__":
    unittest.main()
