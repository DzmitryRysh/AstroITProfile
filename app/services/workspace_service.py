"""Workspace persistence service — input state only."""

from __future__ import annotations

from pathlib import Path

from app.schemas.workspace import (
    WorkspaceData,
    WorkspaceListResponse,
    WorkspaceRecord,
    WorkspaceSummary,
)
from app.services.workspace_repository import WorkspaceRepository, WorkspaceStorageError


class WorkspaceNotFoundError(Exception):
    def __init__(self, workspace_id: str) -> None:
        self.workspace_id = workspace_id
        super().__init__(f"Workspace not found: {workspace_id}")


class WorkspaceService:
    def __init__(self, repository: WorkspaceRepository | None = None) -> None:
        self.repository = repository or WorkspaceRepository()

    def list_workspaces(self) -> WorkspaceListResponse:
        records = self.repository.list_records()
        summaries = [
            WorkspaceSummary(
                workspace_id=item.workspace_id,
                team_name=item.team_name,
                coverage_profile=item.coverage_profile,
                target_role=item.target_role,
                member_count=len(item.members),
                candidate_count=len(item.candidates),
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in records
        ]
        summaries.sort(key=lambda item: item.updated_at, reverse=True)
        return WorkspaceListResponse(workspaces=summaries)

    def get_workspace(self, workspace_id: str) -> WorkspaceRecord:
        record = self.repository.get_record(workspace_id)
        if record is None:
            raise WorkspaceNotFoundError(workspace_id)
        return record

    def create_workspace(self, payload: WorkspaceData) -> WorkspaceRecord:
        return self.repository.create_record(payload)

    def update_workspace(self, workspace_id: str, payload: WorkspaceData) -> WorkspaceRecord:
        updated = self.repository.update_record(workspace_id, payload)
        if updated is None:
            raise WorkspaceNotFoundError(workspace_id)
        return updated

    def delete_workspace(self, workspace_id: str) -> None:
        deleted = self.repository.delete_record(workspace_id)
        if not deleted:
            raise WorkspaceNotFoundError(workspace_id)


def build_workspace_service(store_path: Path | None = None) -> WorkspaceService:
    return WorkspaceService(WorkspaceRepository(store_path=store_path))


__all__ = [
    "WorkspaceNotFoundError",
    "WorkspaceService",
    "WorkspaceStorageError",
    "build_workspace_service",
]
