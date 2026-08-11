"""JSON file repository for recruiter workspace input state."""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.schemas.workspace import WorkspaceData, WorkspaceRecord

SCHEMA_VERSION = 1
_DEFAULT_STORE = Path(__file__).resolve().parents[2] / "runtime" / "workspaces.json"
_ENV_STORE = "ASTROIT_WORKSPACE_STORE_PATH"


class WorkspaceStorageError(Exception):
    """Raised when the workspace store cannot be read or written safely."""


def default_store_path() -> Path:
    override = os.environ.get(_ENV_STORE)
    if override:
        return Path(override).expanduser().resolve()
    return _DEFAULT_STORE.resolve()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _serialize_record(record: WorkspaceRecord) -> dict[str, Any]:
    return json.loads(record.model_dump_json())


class WorkspaceRepository:
    def __init__(self, store_path: Path | None = None) -> None:
        self.store_path = (store_path or default_store_path()).resolve()
        self._lock = threading.RLock()

    def list_records(self) -> list[WorkspaceRecord]:
        with self._lock:
            document = self._read_document()
            return [self._parse_record(item) for item in document["workspaces"]]

    def get_record(self, workspace_id: str) -> WorkspaceRecord | None:
        with self._lock:
            document = self._read_document()
            for item in document["workspaces"]:
                if item.get("workspace_id") == workspace_id:
                    return self._parse_record(item)
            return None

    def create_record(self, payload: WorkspaceData) -> WorkspaceRecord:
        with self._lock:
            document = self._read_document()
            now = _utc_now()
            record = WorkspaceRecord(
                workspace_id=str(uuid4()),
                team_name=payload.team_name,
                coverage_profile=payload.coverage_profile,
                target_role=payload.target_role,
                members=list(payload.members),
                candidates=list(payload.candidates),
                created_at=now,
                updated_at=now,
            )
            document["workspaces"].append(_serialize_record(record))
            self._write_document(document)
            return record

    def update_record(self, workspace_id: str, payload: WorkspaceData) -> WorkspaceRecord | None:
        with self._lock:
            document = self._read_document()
            for index, item in enumerate(document["workspaces"]):
                if item.get("workspace_id") != workspace_id:
                    continue
                existing = self._parse_record(item)
                updated = WorkspaceRecord(
                    workspace_id=existing.workspace_id,
                    team_name=payload.team_name,
                    coverage_profile=payload.coverage_profile,
                    target_role=payload.target_role,
                    members=list(payload.members),
                    candidates=list(payload.candidates),
                    created_at=existing.created_at,
                    updated_at=_utc_now(),
                )
                document["workspaces"][index] = _serialize_record(updated)
                self._write_document(document)
                return updated
            return None

    def delete_record(self, workspace_id: str) -> bool:
        with self._lock:
            document = self._read_document()
            before = len(document["workspaces"])
            document["workspaces"] = [
                item
                for item in document["workspaces"]
                if item.get("workspace_id") != workspace_id
            ]
            if len(document["workspaces"]) == before:
                return False
            self._write_document(document)
            return True

    def _empty_document(self) -> dict[str, Any]:
        return {"schema_version": SCHEMA_VERSION, "workspaces": []}

    def _read_document(self) -> dict[str, Any]:
        if not self.store_path.exists():
            return self._empty_document()
        try:
            raw = self.store_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise WorkspaceStorageError(
                "Workspace storage could not be read."
            ) from exc
        if not raw.strip():
            return self._empty_document()
        try:
            document = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise WorkspaceStorageError(
                "Workspace storage is corrupt and cannot be used."
            ) from exc
        if not isinstance(document, dict):
            raise WorkspaceStorageError(
                "Workspace storage is corrupt and cannot be used."
            )
        workspaces = document.get("workspaces")
        if workspaces is None:
            document["workspaces"] = []
        elif not isinstance(workspaces, list):
            raise WorkspaceStorageError(
                "Workspace storage is corrupt and cannot be used."
            )
        if "schema_version" not in document:
            document["schema_version"] = SCHEMA_VERSION
        return document

    def _write_document(self, document: dict[str, Any]) -> None:
        document = {
            "schema_version": int(document.get("schema_version", SCHEMA_VERSION)),
            "workspaces": list(document.get("workspaces") or []),
        }
        try:
            self.store_path.parent.mkdir(parents=True, exist_ok=True)
            payload = json.dumps(document, ensure_ascii=False, indent=2)
            temp_path = self.store_path.with_name(
                f".{self.store_path.name}.{os.getpid()}.tmp"
            )
            temp_path.write_text(payload, encoding="utf-8", newline="\n")
            os.replace(temp_path, self.store_path)
        except OSError as exc:
            raise WorkspaceStorageError(
                "Workspace storage could not be written."
            ) from exc
        finally:
            try:
                if "temp_path" in locals() and temp_path.exists():
                    temp_path.unlink(missing_ok=True)
            except OSError:
                pass

    @staticmethod
    def _parse_record(item: dict[str, Any]) -> WorkspaceRecord:
        try:
            return WorkspaceRecord.model_validate(item)
        except Exception as exc:
            raise WorkspaceStorageError(
                "Workspace storage contains an invalid record."
            ) from exc
