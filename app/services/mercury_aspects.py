from __future__ import annotations

from datetime import datetime

from app.services.aspects import detect_major_aspect
from app.services.astro_calc import calc_planet_lon
from app.services.it_rulership import PLANET_NAME_TO_SWE

MERCURY_ASPECT_TARGETS = (
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

DISPOSITOR_ASPECT_TARGETS = (
    "Sun",
    "Moon",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
)

HARMONIOUS_ASPECT_TYPES = frozenset({"trine", "sextile"})
TENSE_ASPECT_TYPES = frozenset({"square", "opposition"})


def planet_aspects_at(
    *,
    utc_dt: datetime,
    planet_name: str,
    include_moon: bool = True,
    include_orb: bool = True,
) -> list[dict]:
    """
    Geometry-only major aspects from one natal planet to the shared planet set.

    Skips self-aspects. Does not attach interpretation text or scores.
    """
    source_lon = calc_planet_lon(utc_dt=utc_dt, planet=PLANET_NAME_TO_SWE[planet_name])
    aspects: list[dict] = []

    for target_name in DISPOSITOR_ASPECT_TARGETS:
        if target_name == planet_name:
            continue
        if target_name == "Moon" and not include_moon:
            continue

        other_lon = calc_planet_lon(utc_dt=utc_dt, planet=PLANET_NAME_TO_SWE[target_name])
        aspect_type, orb = detect_major_aspect(source_lon, other_lon)
        if not aspect_type:
            continue

        aspects.append(
            {
                "planet": target_name,
                "type": aspect_type,
                "orb_deg": orb if include_orb else None,
            }
        )

    return aspects


def mercury_aspects_at(
    *,
    utc_dt: datetime,
    include_moon: bool = True,
    include_orb: bool = True,
) -> list[dict]:
    """
    Geometry-only Mercury major aspects.

    Does not attach MVP aspect texts, scores, or technical-mind bonuses.
    """
    aspects = planet_aspects_at(
        utc_dt=utc_dt,
        planet_name="Mercury",
        include_moon=include_moon,
        include_orb=include_orb,
    )
    return [item for item in aspects if item["planet"] in MERCURY_ASPECT_TARGETS]
