from fastapi import APIRouter, HTTPException, Request, Response, status

from app.core.beta_access import read_workspace_scope_id
from app.core.settings import load_beta_settings
from app.schemas.workspace import (
    WorkspaceData,
    WorkspaceListResponse,
    WorkspaceRecord,
)
from app.services.workspace_service import (
    WorkspaceNotFoundError,
    WorkspaceService,
    WorkspaceStorageError,
)

router = APIRouter(prefix="/workspaces", tags=["workspaces"])
_service = WorkspaceService()


def get_workspace_service() -> WorkspaceService:
    return _service


def _scope_context(request: Request) -> tuple[str | None, bool]:
    """Return (scope_id, require_scope) for the current request."""
    settings = load_beta_settings()
    if not settings.gate_enabled:
        return None, False
    scope_id = read_workspace_scope_id(request, settings)
    return scope_id, True


@router.post("", response_model=WorkspaceRecord, status_code=status.HTTP_201_CREATED)
def create_workspace(payload: WorkspaceData, request: Request) -> WorkspaceRecord:
    scope_id, require_scope = _scope_context(request)
    if require_scope and not scope_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        return get_workspace_service().create_workspace(
            payload,
            workspace_scope_id=scope_id if require_scope else None,
        )
    except WorkspaceStorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("", response_model=WorkspaceListResponse)
def list_workspaces(request: Request) -> WorkspaceListResponse:
    scope_id, require_scope = _scope_context(request)
    if require_scope and not scope_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        return get_workspace_service().list_workspaces(
            workspace_scope_id=scope_id,
            require_scope=require_scope,
        )
    except WorkspaceStorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{workspace_id}", response_model=WorkspaceRecord)
def get_workspace(workspace_id: str, request: Request) -> WorkspaceRecord:
    scope_id, require_scope = _scope_context(request)
    if require_scope and not scope_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        return get_workspace_service().get_workspace(
            workspace_id,
            workspace_scope_id=scope_id,
            require_scope=require_scope,
        )
    except WorkspaceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkspaceStorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.put("/{workspace_id}", response_model=WorkspaceRecord)
def update_workspace(
    workspace_id: str,
    payload: WorkspaceData,
    request: Request,
) -> WorkspaceRecord:
    scope_id, require_scope = _scope_context(request)
    if require_scope and not scope_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        return get_workspace_service().update_workspace(
            workspace_id,
            payload,
            workspace_scope_id=scope_id,
            require_scope=require_scope,
        )
    except WorkspaceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkspaceStorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(workspace_id: str, request: Request) -> Response:
    scope_id, require_scope = _scope_context(request)
    if require_scope and not scope_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        get_workspace_service().delete_workspace(
            workspace_id,
            workspace_scope_id=scope_id,
            require_scope=require_scope,
        )
    except WorkspaceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkspaceStorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
