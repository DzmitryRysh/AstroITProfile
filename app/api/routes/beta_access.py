"""Beta access login/logout routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.core.beta_access import (
    LOGIN_PATH,
    LOGOUT_PATH,
    access_code_matches,
    apply_login_cookies,
    clear_auth_cookie,
    is_authenticated,
    read_workspace_scope_id,
)
from app.core.settings import load_beta_settings

BETA_UI_DIR = Path(__file__).resolve().parents[2] / "ui" / "beta"
LOGIN_TEMPLATE = BETA_UI_DIR / "access.html"

router = APIRouter(tags=["beta-access"], include_in_schema=False)


def _render_login(*, error: bool = False) -> HTMLResponse:
    html = LOGIN_TEMPLATE.read_text(encoding="utf-8")
    error_block = (
        '<p class="error" role="alert">That access code is not valid.</p>'
        if error
        else ""
    )
    html = html.replace("__ERROR_BLOCK__", error_block)
    return HTMLResponse(html)


@router.get(LOGIN_PATH, response_class=HTMLResponse)
def beta_access_page(request: Request):
    settings = load_beta_settings()
    if settings.gate_enabled and is_authenticated(request, settings):
        return RedirectResponse(url="/recruiter", status_code=303)
    if not settings.gate_enabled:
        return RedirectResponse(url="/recruiter", status_code=303)
    return _render_login(error=False)


@router.post(LOGIN_PATH)
async def beta_access_submit(
    request: Request,
    access_code: str = Form(default=""),
):
    settings = load_beta_settings()
    if not settings.gate_enabled:
        return RedirectResponse(url="/recruiter", status_code=303)
    if not access_code_matches(access_code, settings.access_code):
        return _render_login(error=True)
    response = RedirectResponse(url="/recruiter", status_code=303)
    existing_scope = read_workspace_scope_id(request, settings)
    apply_login_cookies(response, settings, existing_scope_id=existing_scope)
    return response


@router.post(LOGOUT_PATH)
def beta_logout():
    settings = load_beta_settings()
    response = RedirectResponse(url=LOGIN_PATH if settings.gate_enabled else "/recruiter", status_code=303)
    clear_auth_cookie(response, settings)
    # Keep workspace scope cookie so the same browser can reclaim its workspaces
    # after signing back in with the shared beta code.
    return response
