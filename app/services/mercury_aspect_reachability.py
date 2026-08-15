"""Same-epoch natal Mercury aspect reachability (coverage domain semantics).

This module classifies the static 9×5 major-aspect catalog into:

- RAW natal aspect keys (45)
- IMPOSSIBLE natal geometry (7)
- REACHABLE natal keys (38)

It does NOT change aspect detection, orbs, or planetary longitude math.
It applies ONLY to same-epoch natal Mercury aspects — not transit-to-natal,
synastry, or progressions.
"""

from __future__ import annotations

from typing import Iterable

# Keep aligned with MERCURY_ASPECT_TARGETS in mercury_aspects.py.
TARGET_PLANETS: tuple[str, ...] = (
    "Sun",
    "Moon",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
)

MAJOR_ASPECT_TYPES: tuple[str, ...] = (
    "conjunction",
    "sextile",
    "square",
    "trine",
    "opposition",
)

RAW_NATAL_ASPECT_KEYS: frozenset[str] = frozenset(
    f"{aspect}_{planet}" for planet in TARGET_PLANETS for aspect in MAJOR_ASPECT_TYPES
)

# Inner-planet elongation limits make these major aspects unreachable at one epoch.
IMPOSSIBLE_NATAL_ASPECT_KEYS: frozenset[str] = frozenset(
    {
        "sextile_Sun",
        "square_Sun",
        "trine_Sun",
        "opposition_Sun",
        "square_Venus",
        "trine_Venus",
        "opposition_Venus",
    }
)

REACHABLE_NATAL_ASPECT_KEYS: frozenset[str] = (
    RAW_NATAL_ASPECT_KEYS - IMPOSSIBLE_NATAL_ASPECT_KEYS
)


def natal_aspect_key(planet: str, aspect_type: str) -> str:
    return f"{aspect_type}_{planet}"


def is_natal_mercury_aspect_reachable(planet: str, aspect_type: str) -> bool:
    """Return True if this major aspect is physically reachable for natal Mercury."""
    return natal_aspect_key(planet, aspect_type) in REACHABLE_NATAL_ASPECT_KEYS


def natal_aspect_reachability_summary(
    supported_aspect_keys: Iterable[str],
) -> dict[str, int | frozenset[str]]:
    """Catalog-level raw vs reachable coverage counts (no API/schema)."""
    supported = frozenset(supported_aspect_keys)
    supported_reachable = supported & REACHABLE_NATAL_ASPECT_KEYS
    missing_reachable = REACHABLE_NATAL_ASPECT_KEYS - supported
    return {
        "raw_total": len(RAW_NATAL_ASPECT_KEYS),
        "reachable_total": len(REACHABLE_NATAL_ASPECT_KEYS),
        "impossible_total": len(IMPOSSIBLE_NATAL_ASPECT_KEYS),
        "supported_reachable": len(supported_reachable),
        "missing_reachable": len(missing_reachable),
        "supported_reachable_keys": supported_reachable,
        "missing_reachable_keys": missing_reachable,
        "impossible_keys": IMPOSSIBLE_NATAL_ASPECT_KEYS,
    }
