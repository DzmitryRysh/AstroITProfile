"""Production runtime checks and path helpers.

Validates local files required for a healthy process start.
Does not log natal or personal data.
"""

from __future__ import annotations

import os
from pathlib import Path

from app.services.workspace_repository import default_store_path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_PLACES_PATH = _REPO_ROOT / "data" / "places.json"


def places_data_path() -> Path:
    return _DEFAULT_PLACES_PATH.resolve()


def workspace_store_path() -> Path:
    """Resolved workspace JSON path (respects ASTROIT_WORKSPACE_STORE_PATH)."""
    return default_store_path()


def validate_places_data(places_path: Path | None = None) -> Path:
    path = (places_path or places_data_path()).resolve()
    if not path.is_file():
        raise RuntimeError(
            f"Required places data file is missing or unreadable: {path}. "
            "Ensure data/places.json is packaged with the application."
        )
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(
            f"Required places data file could not be read: {path}."
        ) from exc
    if not raw.strip():
        raise RuntimeError(f"Required places data file is empty: {path}.")
    return path


def validate_workspace_store_writable(store_path: Path | None = None) -> Path:
    path = (store_path or workspace_store_path()).resolve()
    parent = path.parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise RuntimeError(
            f"Workspace store directory could not be created: {parent}. "
            "Set ASTROIT_WORKSPACE_STORE_PATH to a writable location "
            "(for example /data/workspaces.json)."
        ) from exc
    probe = parent / f".astroit_write_probe.{os.getpid()}"
    try:
        probe.write_text("ok", encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(
            f"Workspace store directory is not writable: {parent}. "
            "Set ASTROIT_WORKSPACE_STORE_PATH to a writable location "
            "(for example /data/workspaces.json)."
        ) from exc
    finally:
        try:
            if probe.exists():
                probe.unlink()
        except OSError:
            pass
    return path


def validate_runtime(
    *,
    places_path: Path | None = None,
    workspace_store: Path | None = None,
) -> dict[str, str]:
    """Fail-fast checks for production-critical local filesystem dependencies."""
    places = validate_places_data(places_path)
    store = validate_workspace_store_writable(workspace_store)
    return {
        "places_path": str(places),
        "workspace_store_path": str(store),
    }
