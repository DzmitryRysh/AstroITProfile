from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from typing import Optional

from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.astro_calc import (
    calc_planet_house,
    calc_planet_lon_and_speed,
    calc_planet_sign,
    motion_from_speed,
    sign_from_longitude,
)
from app.services.it_rulership import PLANET_NAME_TO_SWE
from app.services.mercury_aspects import MERCURY_ASPECT_TARGETS, mercury_aspects_at
from app.services.timezones import to_utc_birth_moment

DEFAULT_HOUSE_SYSTEM = b"P"

UNKNOWN_TIME_PROBES = (
    time(0, 1),
    time(12, 0),
    time(23, 59),
)

SIGN_TO_ELEMENT = {
    "Aries": "fire",
    "Leo": "fire",
    "Sagittarius": "fire",
    "Taurus": "earth",
    "Virgo": "earth",
    "Capricorn": "earth",
    "Gemini": "air",
    "Libra": "air",
    "Aquarius": "air",
    "Cancer": "water",
    "Scorpio": "water",
    "Pisces": "water",
}

# Dedicated Mercury dispositor table. First = major, second = optional minor.
MERCURY_DISPOSITORS: dict[str, tuple[str, Optional[str]]] = {
    "Aries": ("Mars", "Pluto"),
    "Taurus": ("Venus", None),
    "Gemini": ("Mercury", None),
    "Cancer": ("Moon", "Sun"),
    "Leo": ("Sun", "Moon"),
    "Virgo": ("Mercury", None),
    "Libra": ("Venus", None),
    "Scorpio": ("Pluto", "Mars"),
    "Sagittarius": ("Jupiter", "Neptune"),
    "Capricorn": ("Saturn", "Uranus"),
    "Aquarius": ("Uranus", "Saturn"),
    "Pisces": ("Neptune", "Jupiter"),
}

_DISPOSITOR_PLANETS = (
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

UNKNOWN_TIME_BASE_LIMITATIONS = (
    "Birth time unknown: houses and angles omitted.",
    "Birth time unknown: exact Mercury longitude omitted.",
    "Birth time unknown: aspect orbs omitted.",
    "Birth time unknown: Moon aspects excluded.",
)


@dataclass(frozen=True)
class DayProbeSnapshot:
    mercury_sign: str
    mercury_motion: str
    planet_signs: dict[str, str]
    aspect_types: dict[str, str]


def element_from_sign(sign: Optional[str]) -> Optional[str]:
    if not sign:
        return None
    return SIGN_TO_ELEMENT.get(sign)


def dispositors_for_sign(sign: str) -> tuple[str, Optional[str]]:
    return MERCURY_DISPOSITORS[sign]


def snapshot_day_probe(*, utc_dt) -> DayProbeSnapshot:
    mercury_lon, mercury_speed = calc_planet_lon_and_speed(
        utc_dt=utc_dt,
        planet=PLANET_NAME_TO_SWE["Mercury"],
    )
    planet_signs = {
        name: calc_planet_sign(utc_dt=utc_dt, planet=planet_id)
        for name, planet_id in PLANET_NAME_TO_SWE.items()
        if name in _DISPOSITOR_PLANETS
    }
    aspects = mercury_aspects_at(utc_dt=utc_dt, include_moon=False, include_orb=False)
    aspect_types = {item["planet"]: item["type"] for item in aspects}

    return DayProbeSnapshot(
        mercury_sign=sign_from_longitude(mercury_lon),
        mercury_motion=motion_from_speed(mercury_speed),
        planet_signs=planet_signs,
        aspect_types=aspect_types,
    )


def _stable_value(values: list) -> Optional[object]:
    if not values:
        return None
    first = values[0]
    if all(v == first for v in values):
        return first
    return None


def merge_unknown_time_probes(
    probes: list[DayProbeSnapshot],
) -> tuple[MercurySourceFactors, list[str]]:
    limitations = list(UNKNOWN_TIME_BASE_LIMITATIONS)

    mercury_sign = _stable_value([p.mercury_sign for p in probes])
    if mercury_sign is None:
        limitations.append("Mercury sign is not stable across the birth date; omitted.")

    mercury_element = element_from_sign(mercury_sign)

    mercury_motion = _stable_value([p.mercury_motion for p in probes])
    if mercury_motion is None:
        limitations.append("Mercury motion is not stable across the birth date; omitted.")

    aspects: list[MercuryAspect] = []
    for planet_name in MERCURY_ASPECT_TARGETS:
        if planet_name == "Moon":
            continue
        types = [p.aspect_types.get(planet_name) for p in probes]
        if types[0] is not None and _stable_value(types) is not None:
            aspects.append(
                MercuryAspect(planet=planet_name, type=types[0], orb_deg=None)
            )
        elif any(t is not None for t in types):
            limitations.append(
                f"Mercury–{planet_name} aspect is not stable across the birth date; omitted."
            )

    major_dispositor: Optional[str] = None
    minor_dispositor: Optional[str] = None
    major_dispositor_sign: Optional[str] = None
    minor_dispositor_sign: Optional[str] = None

    if mercury_sign:
        major_dispositor, minor_dispositor = dispositors_for_sign(mercury_sign)

        major_signs = [p.planet_signs[major_dispositor] for p in probes]
        major_dispositor_sign = _stable_value(major_signs)
        if major_dispositor_sign is None:
            limitations.append(
                f"Major dispositor ({major_dispositor}) sign is not stable "
                "across the birth date; omitted."
            )

        if minor_dispositor:
            minor_signs = [p.planet_signs[minor_dispositor] for p in probes]
            minor_dispositor_sign = _stable_value(minor_signs)
            if minor_dispositor_sign is None:
                limitations.append(
                    f"Minor dispositor ({minor_dispositor}) sign is not stable "
                    "across the birth date; omitted."
                )
    else:
        limitations.append("Dispositor names omitted because Mercury sign is not stable.")

    factors = MercurySourceFactors(
        birth_time_known=False,
        mercury_sign=mercury_sign,
        mercury_element=mercury_element,
        mercury_longitude=None,
        mercury_motion=mercury_motion,
        mercury_house=None,
        house_system_used=None,
        aspects=aspects,
        major_dispositor=major_dispositor,
        minor_dispositor=minor_dispositor,
        major_dispositor_sign=major_dispositor_sign,
        minor_dispositor_sign=minor_dispositor_sign,
        major_dispositor_house=None,
        minor_dispositor_house=None,
    )
    return factors, limitations


def compute_unknown_time_facts(
    *,
    birth_date: date,
    tz_name: str,
) -> tuple[MercurySourceFactors, list[str]]:
    probes = []
    for probe_time in UNKNOWN_TIME_PROBES:
        moment = to_utc_birth_moment(
            birth_date=birth_date,
            birth_time=probe_time,
            tz_name=tz_name,
        )
        probes.append(snapshot_day_probe(utc_dt=moment.utc_dt))
    return merge_unknown_time_probes(probes)


def compute_exact_time_facts(
    *,
    utc_dt,
    lat: float,
    lon: float,
    house_system: bytes = DEFAULT_HOUSE_SYSTEM,
) -> tuple[MercurySourceFactors, list[str]]:
    mercury_id = PLANET_NAME_TO_SWE["Mercury"]
    mercury_lon, mercury_speed = calc_planet_lon_and_speed(
        utc_dt=utc_dt,
        planet=mercury_id,
    )
    mercury_sign = sign_from_longitude(mercury_lon)
    mercury_house, used_hsys = calc_planet_house(
        utc_dt=utc_dt,
        lat=lat,
        lon=lon,
        planet=mercury_id,
        house_system=house_system,
    )

    aspects_raw = mercury_aspects_at(utc_dt=utc_dt, include_moon=True, include_orb=True)
    aspects = [MercuryAspect(**item) for item in aspects_raw]

    major_dispositor, minor_dispositor = dispositors_for_sign(mercury_sign)
    major_dispositor_sign = calc_planet_sign(
        utc_dt=utc_dt,
        planet=PLANET_NAME_TO_SWE[major_dispositor],
    )
    major_dispositor_house, _ = calc_planet_house(
        utc_dt=utc_dt,
        lat=lat,
        lon=lon,
        planet=PLANET_NAME_TO_SWE[major_dispositor],
        house_system=house_system,
    )

    minor_dispositor_sign = None
    minor_dispositor_house = None
    if minor_dispositor:
        minor_dispositor_sign = calc_planet_sign(
            utc_dt=utc_dt,
            planet=PLANET_NAME_TO_SWE[minor_dispositor],
        )
        minor_dispositor_house, _ = calc_planet_house(
            utc_dt=utc_dt,
            lat=lat,
            lon=lon,
            planet=PLANET_NAME_TO_SWE[minor_dispositor],
            house_system=house_system,
        )

    factors = MercurySourceFactors(
        birth_time_known=True,
        mercury_sign=mercury_sign,
        mercury_element=element_from_sign(mercury_sign),
        mercury_longitude=round(mercury_lon, 6),
        mercury_motion=motion_from_speed(mercury_speed),
        mercury_house=mercury_house,
        house_system_used=used_hsys.decode("ascii"),
        aspects=aspects,
        major_dispositor=major_dispositor,
        minor_dispositor=minor_dispositor,
        major_dispositor_sign=major_dispositor_sign,
        minor_dispositor_sign=minor_dispositor_sign,
        major_dispositor_house=major_dispositor_house,
        minor_dispositor_house=minor_dispositor_house,
    )
    return factors, []
