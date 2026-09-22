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


def _owned_by_scope(record: WorkspaceRecord, workspace_scope_id: str | None) -> bool:
    if not workspace_scope_id:
        return False
    return bool(record.workspace_scope_id) and record.workspace_scope_id == workspace_scope_id


class WorkspaceService:
    def __init__(self, repository: WorkspaceRepository | None = None) -> None:
        self.repository = repository or WorkspaceRepository()

    def list_workspaces(
        self,
        *,
        workspace_scope_id: str | None = None,
        require_scope: bool = False,
    ) -> WorkspaceListResponse:
        records = self.repository.list_records()
        if require_scope:
            # Beta mode: only scoped records for this browser. Legacy/unscoped
            # records stay hidden so they are never shared across beta visitors.
            records = [
                item
                for item in records
                if _owned_by_scope(item, workspace_scope_id)
            ]
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

    def get_workspace(
        self,
        workspace_id: str,
        *,
        workspace_scope_id: str | None = None,
        require_scope: bool = False,
    ) -> WorkspaceRecord:
        record = self.repository.get_record(workspace_id)
        if record is None:
            raise WorkspaceNotFoundError(workspace_id)
        if require_scope and not _owned_by_scope(record, workspace_scope_id):
            raise WorkspaceNotFoundError(workspace_id)
        return record

    def create_workspace(
        self,
        payload: WorkspaceData,
        *,
        workspace_scope_id: str | None = None,
    ) -> WorkspaceRecord:
        return self.repository.create_record(
            payload,
            workspace_scope_id=workspace_scope_id,
        )

    def update_workspace(
        self,
        workspace_id: str,
        payload: WorkspaceData,
        *,
        workspace_scope_id: str | None = None,
        require_scope: bool = False,
    ) -> WorkspaceRecord:
        updated = self.repository.update_record(
            workspace_id,
            payload,
            workspace_scope_id=workspace_scope_id,
            require_scope=require_scope,
        )
        if updated is None:
            raise WorkspaceNotFoundError(workspace_id)
        return updated

    def delete_workspace(
        self,
        workspace_id: str,
        *,
        workspace_scope_id: str | None = None,
        require_scope: bool = False,
    ) -> None:
        deleted = self.repository.delete_record(
            workspace_id,
            workspace_scope_id=workspace_scope_id,
            require_scope=require_scope,
        )
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
