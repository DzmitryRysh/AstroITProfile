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
    mercury_lon = calc_planet_lon(utc_dt=utc_dt, planet=PLANET_NAME_TO_SWE["Mercury"])
    aspects: list[dict] = []

    for planet_name in MERCURY_ASPECT_TARGETS:
        if planet_name == "Moon" and not include_moon:
            continue

        other_lon = calc_planet_lon(utc_dt=utc_dt, planet=PLANET_NAME_TO_SWE[planet_name])
        aspect_type, orb = detect_major_aspect(mercury_lon, other_lon)
        if not aspect_type:
            continue

        aspects.append(
            {
                "planet": planet_name,
                "type": aspect_type,
                "orb_deg": orb if include_orb else None,
            }
        )

    return aspects
