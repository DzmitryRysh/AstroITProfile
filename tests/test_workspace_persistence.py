import json
import os
import tempfile
import time
import unittest
from datetime import date, time as dt_time
from pathlib import Path
from uuid import UUID

from pydantic import ValidationError
from starlette.routing import Route

from app.core.app import create_app
from app.schemas.candidate_compare import CandidateInput
from app.schemas.team_map import TeamMemberInput
from app.schemas.workspace import WorkspaceData
from app.services.workspace_repository import WorkspaceRepository, WorkspaceStorageError
from app.services.workspace_service import WorkspaceNotFoundError, WorkspaceService

DERIVED_KEYS = {
    "team_function",
    "thinking_style",
    "top_skills",
    "key_risks",
    "team_contribution",
    "required_functions",
    "missing_required_functions",
    "workflow_stage",
    "closed_missing_functions",
    "mercury_sign",
    "aspects",
    "dispositor",
}


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
        "members": [_member("A"), _member("B")],
        "candidates": [_candidate("C")],
    }
    data.update(overrides)
    return WorkspaceData(**data)


def _all_keys(payload) -> set[str]:
    if isinstance(payload, dict):
        keys = set(payload.keys())
        for value in payload.values():
            keys |= _all_keys(value)
        return keys
    if isinstance(payload, list):
        keys: set[str] = set()
        for value in payload:
            keys |= _all_keys(value)
        return keys
    return set()


class WorkspacePersistenceTests(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.store_path = Path(self._tmpdir.name) / "workspaces.json"
        self.repo = WorkspaceRepository(store_path=self.store_path)
        self.service = WorkspaceService(repository=self.repo)

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_empty_storage_lists_empty(self):
        result = self.service.list_workspaces()
        self.assertEqual(result.workspaces, [])
        self.assertFalse(self.store_path.exists())

    def test_create_workspace(self):
        created = self.service.create_workspace(_payload())
        self.assertEqual(created.team_name, "AI Platform Team")
        self.assertEqual(created.coverage_profile, "ai_ml_product_delivery")
        self.assertEqual(len(created.members), 2)
        self.assertEqual(len(created.candidates), 1)
        self.assertTrue(self.store_path.exists())

    def test_created_workspace_has_uuid_like_id(self):
        created = self.service.create_workspace(_payload())
        UUID(created.workspace_id)

    def test_created_at_and_updated_at_populated(self):
        created = self.service.create_workspace(_payload())
        self.assertIsNotNone(created.created_at)
        self.assertIsNotNone(created.updated_at)
        self.assertEqual(created.created_at.tzinfo is not None, True)
        self.assertEqual(created.updated_at.tzinfo is not None, True)

    def test_get_workspace(self):
        created = self.service.create_workspace(_payload())
        fetched = self.service.get_workspace(created.workspace_id)
        self.assertEqual(fetched.workspace_id, created.workspace_id)
        self.assertEqual(fetched.members[0].birth_place, "Kingisepp, Russia")

    def test_list_returns_summary_without_birth_data(self):
        self.service.create_workspace(_payload())
        listed = self.service.list_workspaces()
        self.assertEqual(len(listed.workspaces), 1)
        summary = listed.workspaces[0].model_dump()
        keys = _all_keys(summary)
        self.assertIn("member_count", keys)
        self.assertIn("candidate_count", keys)
        self.assertNotIn("members", keys)
        self.assertNotIn("candidates", keys)
        self.assertNotIn("birth_date", keys)
        self.assertNotIn("birth_place", keys)
        self.assertNotIn("birth_time", keys)

    def test_list_sorted_updated_at_descending(self):
        first = self.service.create_workspace(_payload(team_name="First"))
        time.sleep(0.02)
        second = self.service.create_workspace(_payload(team_name="Second"))
        time.sleep(0.02)
        self.service.update_workspace(
            first.workspace_id,
            _payload(team_name="First Updated", target_role="Senior ML Engineer"),
        )
        names = [item.team_name for item in self.service.list_workspaces().workspaces]
        self.assertEqual(names[0], "First Updated")
        self.assertEqual(set(names), {"First Updated", "Second"})

    def test_update_preserves_workspace_id_and_created_at(self):
        created = self.service.create_workspace(_payload())
        time.sleep(0.02)
        updated = self.service.update_workspace(
            created.workspace_id,
            _payload(target_role="Senior ML Engineer"),
        )
        self.assertEqual(updated.workspace_id, created.workspace_id)
        self.assertEqual(updated.created_at, created.created_at)
        self.assertGreater(updated.updated_at, created.updated_at)
        self.assertEqual(updated.target_role, "Senior ML Engineer")

    def test_delete_works_and_get_returns_not_found(self):
        created = self.service.create_workspace(_payload())
        self.service.delete_workspace(created.workspace_id)
        with self.assertRaises(WorkspaceNotFoundError):
            self.service.get_workspace(created.workspace_id)

    def test_update_unknown_workspace_raises(self):
        with self.assertRaises(WorkspaceNotFoundError):
            self.service.update_workspace(str(UUID(int=1)), _payload())

    def test_delete_unknown_workspace_raises(self):
        with self.assertRaises(WorkspaceNotFoundError):
            self.service.delete_workspace(str(UUID(int=2)))

    def test_zero_candidates_allowed(self):
        created = self.service.create_workspace(_payload(candidates=[]))
        self.assertEqual(created.candidates, [])

    def test_one_candidate_allowed(self):
        created = self.service.create_workspace(_payload(candidates=[_candidate("C")]))
        self.assertEqual(len(created.candidates), 1)

    def test_more_than_eight_candidates_rejected(self):
        candidates = [_candidate(str(index)) for index in range(9)]
        with self.assertRaises(ValidationError):
            _payload(candidates=candidates)

    def test_duplicate_member_id_rejected(self):
        with self.assertRaises(ValidationError):
            _payload(members=[_member("A"), _member("A")])

    def test_duplicate_candidate_id_rejected(self):
        with self.assertRaises(ValidationError):
            _payload(candidates=[_candidate("C"), _candidate("C")])

    def test_candidate_member_id_collision_rejected(self):
        with self.assertRaises(ValidationError):
            _payload(members=[_member("A")], candidates=[_candidate("A")])

    def test_more_than_thirty_members_rejected(self):
        members = [_member(str(index)) for index in range(31)]
        with self.assertRaises(ValidationError):
            _payload(members=members)

    def test_persisted_json_contains_only_input_and_metadata(self):
        self.service.create_workspace(_payload())
        raw = json.loads(self.store_path.read_text(encoding="utf-8"))
        self.assertEqual(raw["schema_version"], 1)
        keys = _all_keys(raw)
        self.assertTrue(DERIVED_KEYS.isdisjoint(keys), keys & DERIVED_KEYS)
        self.assertIn("members", keys)
        self.assertIn("candidates", keys)
        self.assertIn("birth_date", keys)

    def test_storage_survives_new_repository_instance(self):
        created = self.service.create_workspace(_payload(team_name="Durable"))
        fresh = WorkspaceService(WorkspaceRepository(store_path=self.store_path))
        fetched = fresh.get_workspace(created.workspace_id)
        self.assertEqual(fetched.team_name, "Durable")
        listed = fresh.list_workspaces()
        self.assertEqual(len(listed.workspaces), 1)

    def test_corrupt_json_fails_clearly_and_is_not_overwritten(self):
        self.store_path.write_text("{not-json", encoding="utf-8")
        before = self.store_path.read_text(encoding="utf-8")
        with self.assertRaises(WorkspaceStorageError):
            self.service.list_workspaces()
        with self.assertRaises(WorkspaceStorageError):
            self.service.create_workspace(_payload())
        after = self.store_path.read_text(encoding="utf-8")
        self.assertEqual(before, after)

    def test_missing_file_does_not_error_on_list(self):
        self.assertFalse(self.store_path.exists())
        result = self.service.list_workspaces()
        self.assertEqual(result.workspaces, [])

    def test_env_override_is_used_by_default_path(self):
        custom = Path(self._tmpdir.name) / "custom" / "store.json"
        previous = os.environ.get("ASTROIT_WORKSPACE_STORE_PATH")
        os.environ["ASTROIT_WORKSPACE_STORE_PATH"] = str(custom)
        try:
            from app.services.workspace_repository import default_store_path

            self.assertEqual(default_store_path(), custom.resolve())
            service = WorkspaceService(WorkspaceRepository())
            service.create_workspace(_payload(team_name="Env Store"))
            self.assertTrue(custom.exists())
        finally:
            if previous is None:
                os.environ.pop("ASTROIT_WORKSPACE_STORE_PATH", None)
            else:
                os.environ["ASTROIT_WORKSPACE_STORE_PATH"] = previous


class WorkspaceRouteRegistrationTests(unittest.TestCase):
    def test_workspace_routes_are_registered(self):
        app = create_app()
        paths = {getattr(route, "path", None) for route in app.routes}
        self.assertIn("/api/v1/workspaces", paths)
        self.assertIn("/api/v1/workspaces/{workspace_id}", paths)
        methods_by_path: dict[str, set[str]] = {}
        for route in app.routes:
            if not isinstance(route, Route):
                continue
            methods_by_path.setdefault(route.path, set()).update(route.methods or set())
        self.assertIn("POST", methods_by_path["/api/v1/workspaces"])
        self.assertIn("GET", methods_by_path["/api/v1/workspaces"])
        self.assertIn("GET", methods_by_path["/api/v1/workspaces/{workspace_id}"])
        self.assertIn("PUT", methods_by_path["/api/v1/workspaces/{workspace_id}"])
        self.assertIn("DELETE", methods_by_path["/api/v1/workspaces/{workspace_id}"])


if __name__ == "__main__":
    unittest.main()
