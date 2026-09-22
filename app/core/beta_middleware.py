"""Beta-gate middleware: protect product routes when invite mode is enabled."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response

from app.core.beta_access import LOGIN_PATH, LOGOUT_PATH, is_authenticated
from app.core.settings import load_beta_settings


def is_public_path(path: str, method: str) -> bool:
    normalized = path.rstrip("/") or "/"
    method_u = method.upper()
    if normalized == "/health":
        return True
    if normalized == LOGIN_PATH and method_u in {"GET", "POST"}:
        return True
    if normalized == LOGOUT_PATH and method_u == "POST":
        return True
    return False


def is_api_style_request(request: Request) -> bool:
    path = request.url.path
    if path.startswith("/api/"):
        return True
    if path == "/openapi.json":
        return True
    accept = (request.headers.get("accept") or "").lower()
    if "application/json" in accept and "text/html" not in accept:
        return True
    return False


class BetaGateMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        settings = load_beta_settings()
        if not settings.gate_enabled:
            return await call_next(request)

        if is_public_path(request.url.path, request.method):
            return await call_next(request)

        if is_authenticated(request, settings):
            return await call_next(request)

        path = request.url.path
        if path in {"/docs", "/redoc"} or path.startswith("/docs/") or path.startswith("/redoc/"):
            return RedirectResponse(url=LOGIN_PATH, status_code=303)

        if is_api_style_request(request):
            return JSONResponse(
                {"detail": "Authentication required"},
                status_code=401,
            )

        return RedirectResponse(url=LOGIN_PATH, status_code=303)
