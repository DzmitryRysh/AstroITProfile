"""Mars natal factor snapshot — calculated HOW YOU WORK geometry only.

This module does not interpret Mars, score strength, or activate source knowledge.
Retrograde is calculated motion (speed < 0), not weakness.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from typing import Optional

from app.services.astro_calc import (
    calc_planet_house,
    calc_planet_lon_and_speed,
    motion_from_speed,
    sign_from_longitude,
)
from app.services.it_rulership import PLANET_NAME_TO_SWE
from app.services.mercury_aspects import DISPOSITOR_ASPECT_TARGETS, planet_aspects_at
from app.services.places import find_coordinates
from app.services.timezones import timezone_name_from_coords, to_utc_birth_moment

SOURCE_PLANET = "Mars"
DEFAULT_HOUSE_SYSTEM = b"P"

# Same day-probe policy as mercury_facts.UNKNOWN_TIME_PROBES.
UNKNOWN_TIME_PROBES = (
    time(0, 1),
    time(12, 0),
    time(23, 59),
)

UNKNOWN_TIME_BASE_LIMITATIONS = (
    "Birth time unknown: houses and angles omitted.",
    "Birth time unknown: exact Mars longitude omitted.",
    "Birth time unknown: aspect orbs omitted.",
    "Birth time unknown: Moon aspects excluded.",
)


@dataclass(frozen=True)
class MarsAspect:
    planet: str
    type: str
    orb_deg: Optional[float] = None


@dataclass(frozen=True)
class MarsSourceFactors:
    birth_time_known: bool
    mars_sign: Optional[str] = None
    mars_longitude: Optional[float] = None
    mars_house: Optional[int] = None
    mars_motion: Optional[str] = None
    mars_aspects: tuple[MarsAspect, ...] = ()
    house_system_used: Optional[str] = None
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True)
class _MarsDayProbe:
    mars_sign: str
    mars_motion: str
    aspect_types: dict[str, str]


def _stable_value(values: list):
    if not values:
        return None
    first = values[0]
    if all(item == first for item in values):
        return first
    return None


def _aspect_models(raw_items: list[dict]) -> tuple[MarsAspect, ...]:
    return tuple(
        MarsAspect(
            planet=item["planet"],
            type=item["type"],
            orb_deg=item["orb_deg"],
        )
        for item in raw_items
    )


def aspect_factor_key(aspect: MarsAspect) -> str:
    return f"{aspect.type}_{aspect.planet}"


def calculated_mars_factor_keys(factors: MarsSourceFactors) -> tuple[str, ...]:
    """M2-ready keys scoped inside a future MarsSourceProfile (unprefixed)."""
    keys: list[str] = []
    if factors.mars_sign:
        keys.append(f"sign:{factors.mars_sign}")
    if factors.mars_house is not None:
        keys.append(f"house:{factors.mars_house}")
    if factors.mars_motion == "retrograde":
        keys.append(f"motion:{factors.mars_motion}")
    for aspect in factors.mars_aspects:
        keys.append(f"aspect:{aspect_factor_key(aspect)}")
    return tuple(keys)


def _snapshot_mars_probe(*, utc_dt) -> _MarsDayProbe:
    mars_lon, mars_speed = calc_planet_lon_and_speed(
        utc_dt=utc_dt,
        planet=PLANET_NAME_TO_SWE[SOURCE_PLANET],
    )
    items = planet_aspects_at(
        utc_dt=utc_dt,
        planet_name=SOURCE_PLANET,
        include_moon=False,
        include_orb=False,
    )
    return _MarsDayProbe(
        mars_sign=sign_from_longitude(mars_lon),
        mars_motion=motion_from_speed(mars_speed),
        aspect_types={item["planet"]: item["type"] for item in items},
    )


def _compute_unknown_time_facts(
    *,
    birth_date: date,
    tz_name: str,
) -> MarsSourceFactors:
    probes = []
    for probe_time in UNKNOWN_TIME_PROBES:
        moment = to_utc_birth_moment(
            birth_date=birth_date,
            birth_time=probe_time,
            tz_name=tz_name,
        )
        probes.append(_snapshot_mars_probe(utc_dt=moment.utc_dt))

    limitations = list(UNKNOWN_TIME_BASE_LIMITATIONS)

    mars_sign = _stable_value([probe.mars_sign for probe in probes])
    if mars_sign is None:
        limitations.append("Mars sign is not stable across the birth date; omitted.")

    mars_motion = _stable_value([probe.mars_motion for probe in probes])
    if mars_motion is None:
        limitations.append("Mars motion is not stable across the birth date; omitted.")

    aspects: list[MarsAspect] = []
    for target_name in DISPOSITOR_ASPECT_TARGETS:
        if target_name in {SOURCE_PLANET, "Moon"}:
            continue
        types = [probe.aspect_types.get(target_name) for probe in probes]
        if types[0] is not None and _stable_value(types) is not None:
            aspects.append(MarsAspect(planet=target_name, type=types[0], orb_deg=None))
        elif any(item is not None for item in types):
            limitations.append(
                f"Mars-{target_name} aspect is not stable across the birth date; omitted."
            )

    return MarsSourceFactors(
        birth_time_known=False,
        mars_sign=mars_sign,
        mars_longitude=None,
        mars_house=None,
        mars_motion=mars_motion,
        mars_aspects=tuple(aspects),
        house_system_used=None,
        limitations=tuple(limitations),
    )


def _compute_exact_time_facts(
    *,
    utc_dt,
    lat: float,
    lon: float,
    house_system: bytes = DEFAULT_HOUSE_SYSTEM,
) -> MarsSourceFactors:
    mars_id = PLANET_NAME_TO_SWE[SOURCE_PLANET]
    mars_lon, mars_speed = calc_planet_lon_and_speed(
        utc_dt=utc_dt,
        planet=mars_id,
    )
    mars_house, used_hsys = calc_planet_house(
        utc_dt=utc_dt,
        lat=lat,
        lon=lon,
        planet=mars_id,
        house_system=house_system,
    )
    aspects = _aspect_models(
        planet_aspects_at(
            utc_dt=utc_dt,
            planet_name=SOURCE_PLANET,
            include_moon=True,
            include_orb=True,
        )
    )
    return MarsSourceFactors(
        birth_time_known=True,
        mars_sign=sign_from_longitude(mars_lon),
        mars_longitude=round(mars_lon, 6),
        mars_house=mars_house,
        mars_motion=motion_from_speed(mars_speed),
        mars_aspects=aspects,
        house_system_used=used_hsys.decode("ascii"),
        limitations=(),
    )


def compute_mars_source_factors(
    *,
    birth_date: date,
    birth_place: str,
    birth_time: Optional[time] = None,
) -> MarsSourceFactors:
    """Calculate Mars natal factors from birth input. No source interpretation."""
    coords = find_coordinates(birth_place)
    tz_name = timezone_name_from_coords(lat=coords.lat, lon=coords.lon)
    if birth_time is None:
        return _compute_unknown_time_facts(birth_date=birth_date, tz_name=tz_name)
    moment = to_utc_birth_moment(
        birth_date=birth_date,
        birth_time=birth_time,
        tz_name=tz_name,
    )
    return _compute_exact_time_facts(
        utc_dt=moment.utc_dt,
        lat=coords.lat,
        lon=coords.lon,
    )
