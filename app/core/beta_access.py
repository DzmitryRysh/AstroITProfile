"""Invite-only beta access: signed cookies and access-code verification.

Does not log access codes, cookie values, or natal payloads.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any, Optional
from uuid import uuid4

from starlette.requests import Request
from starlette.responses import Response

from app.core.settings import BetaSettings, load_beta_settings

AUTH_COOKIE_NAME = "astroit_beta_auth"
SCOPE_COOKIE_NAME = "astroit_ws_scope"
LOGIN_PATH = "/beta-access"
LOGOUT_PATH = "/beta-logout"


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def sign_token(payload: dict[str, Any], secret: str) -> str:
    body = _b64url_encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    digest = hmac.new(
        secret.encode("utf-8"),
        body.encode("ascii"),
        hashlib.sha256,
    ).hexdigest()
    return f"{body}.{digest}"


def verify_token(token: str, secret: str) -> Optional[dict[str, Any]]:
    if not token or "." not in token or not secret:
        return None
    body, _, signature = token.rpartition(".")
    if not body or not signature:
        return None
    expected = hmac.new(
        secret.encode("utf-8"),
        body.encode("ascii"),
        hashlib.sha256,
    ).hexdigest()
    if not secrets.compare_digest(signature, expected):
        return None
    try:
        payload = json.loads(_b64url_decode(body).decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    exp = payload.get("exp")
    if not isinstance(exp, (int, float)) or time.time() >= float(exp):
        return None
    return payload


def access_code_matches(submitted: str, expected: str) -> bool:
    left = (submitted or "").strip().encode("utf-8")
    right = (expected or "").strip().encode("utf-8")
    if not left or not right:
        return False
    if len(left) != len(right):
        # compare_digest requires equal length; still do a dummy compare.
        secrets.compare_digest(left, left)
        return False
    return secrets.compare_digest(left, right)


def issue_auth_token(settings: BetaSettings) -> str:
    now = int(time.time())
    payload = {
        "typ": "beta_auth",
        "iat": now,
        "exp": now + int(settings.session_max_age_seconds),
        "nonce": secrets.token_urlsafe(16),
    }
    return sign_token(payload, settings.session_secret)


def issue_scope_token(settings: BetaSettings, scope_id: str | None = None) -> tuple[str, str]:
    scope = scope_id or str(uuid4())
    now = int(time.time())
    payload = {
        "typ": "ws_scope",
        "scope": scope,
        "iat": now,
        "exp": now + int(settings.session_max_age_seconds),
    }
    return scope, sign_token(payload, settings.session_secret)


def read_auth_payload(request: Request, settings: BetaSettings | None = None) -> Optional[dict[str, Any]]:
    cfg = settings or load_beta_settings()
    token = request.cookies.get(AUTH_COOKIE_NAME)
    if not token:
        return None
    payload = verify_token(token, cfg.session_secret)
    if not payload or payload.get("typ") != "beta_auth":
        return None
    return payload


def is_authenticated(request: Request, settings: BetaSettings | None = None) -> bool:
    cfg = settings or load_beta_settings()
    if not cfg.gate_enabled:
        return True
    return read_auth_payload(request, cfg) is not None


def read_workspace_scope_id(
    request: Request,
    settings: BetaSettings | None = None,
) -> Optional[str]:
    cfg = settings or load_beta_settings()
    token = request.cookies.get(SCOPE_COOKIE_NAME)
    if not token:
        return None
    payload = verify_token(token, cfg.session_secret)
    if not payload or payload.get("typ") != "ws_scope":
        return None
    scope = payload.get("scope")
    if not isinstance(scope, str) or not scope.strip():
        return None
    return scope.strip()


def _cookie_kwargs(settings: BetaSettings) -> dict[str, Any]:
    return {
        "httponly": True,
        "samesite": "strict",
        "secure": settings.cookie_secure,
        "path": "/",
        "max_age": int(settings.session_max_age_seconds),
    }


def set_auth_cookie(response: Response, token: str, settings: BetaSettings) -> None:
    response.set_cookie(AUTH_COOKIE_NAME, token, **_cookie_kwargs(settings))


def set_scope_cookie(response: Response, token: str, settings: BetaSettings) -> None:
    response.set_cookie(SCOPE_COOKIE_NAME, token, **_cookie_kwargs(settings))


def clear_auth_cookie(response: Response, settings: BetaSettings) -> None:
    response.delete_cookie(
        AUTH_COOKIE_NAME,
        path="/",
        httponly=True,
        samesite="strict",
        secure=settings.cookie_secure,
    )


def clear_scope_cookie(response: Response, settings: BetaSettings) -> None:
    response.delete_cookie(
        SCOPE_COOKIE_NAME,
        path="/",
        httponly=True,
        samesite="strict",
        secure=settings.cookie_secure,
    )


def apply_login_cookies(
    response: Response,
    settings: BetaSettings,
    *,
    existing_scope_id: str | None = None,
) -> str:
    """Set auth + workspace-scope cookies. Returns the active scope id."""
    auth_token = issue_auth_token(settings)
    set_auth_cookie(response, auth_token, settings)
    scope_id, scope_token = issue_scope_token(settings, existing_scope_id)
    set_scope_cookie(response, scope_token, settings)
    return scope_id
