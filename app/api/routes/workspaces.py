from fastapi import APIRouter, HTTPException, Response, status

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


@router.post("", response_model=WorkspaceRecord, status_code=status.HTTP_201_CREATED)
def create_workspace(payload: WorkspaceData) -> WorkspaceRecord:
    try:
        return get_workspace_service().create_workspace(payload)
    except WorkspaceStorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("", response_model=WorkspaceListResponse)
def list_workspaces() -> WorkspaceListResponse:
    try:
        return get_workspace_service().list_workspaces()
    except WorkspaceStorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{workspace_id}", response_model=WorkspaceRecord)
def get_workspace(workspace_id: str) -> WorkspaceRecord:
    try:
        return get_workspace_service().get_workspace(workspace_id)
    except WorkspaceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkspaceStorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.put("/{workspace_id}", response_model=WorkspaceRecord)
def update_workspace(workspace_id: str, payload: WorkspaceData) -> WorkspaceRecord:
    try:
        return get_workspace_service().update_workspace(workspace_id, payload)
    except WorkspaceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkspaceStorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workspace(workspace_id: str) -> Response:
    try:
        get_workspace_service().delete_workspace(workspace_id)
    except WorkspaceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except WorkspaceStorageError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
