"""Environment configuration for beta gate and related runtime flags."""

from __future__ import annotations

import os
from dataclasses import dataclass


def parse_bool_env(value: str | None, *, default: bool = False) -> bool:
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class BetaSettings:
    """Invite-only beta access configuration.

    Gate is OFF unless ASTROIT_BETA_GATE_ENABLED is explicitly true.
    Presence of an access code alone does not enable the gate.
    """

    gate_enabled: bool
    access_code: str
    session_secret: str
    cookie_secure: bool
    session_max_age_seconds: int = 60 * 60 * 24 * 7  # 7 days


def load_beta_settings() -> BetaSettings:
    return BetaSettings(
        gate_enabled=parse_bool_env(os.environ.get("ASTROIT_BETA_GATE_ENABLED")),
        access_code=str(os.environ.get("ASTROIT_BETA_ACCESS_CODE") or ""),
        session_secret=str(os.environ.get("ASTROIT_SESSION_SECRET") or ""),
        cookie_secure=parse_bool_env(os.environ.get("ASTROIT_COOKIE_SECURE")),
    )


def validate_beta_settings(settings: BetaSettings | None = None) -> BetaSettings:
    """Fail fast when the beta gate is enabled without required secrets."""
    cfg = settings or load_beta_settings()
    if not cfg.gate_enabled:
        return cfg
    if not cfg.access_code.strip():
        raise RuntimeError(
            "ASTROIT_BETA_GATE_ENABLED is true but ASTROIT_BETA_ACCESS_CODE is missing. "
            "Set a non-empty shared beta access code."
        )
    if len(cfg.session_secret.strip()) < 16:
        raise RuntimeError(
            "ASTROIT_BETA_GATE_ENABLED is true but ASTROIT_SESSION_SECRET is missing "
            "or too short. Set a strong secret of at least 16 characters."
        )
    return cfg
