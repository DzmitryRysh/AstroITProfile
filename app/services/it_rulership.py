from __future__ import annotations

import swisseph as swe

SIGN_TO_RULER_TRADITIONAL = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

SIGN_TO_RULER_MODERN = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Pluto",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Uranus",
    "Pisces": "Neptune",
}

SIGN_TO_CO_RULER = {
    "Scorpio": "Mars",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

PLANET_NAME_TO_SWE = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
}


def get_10h_rulers(mc_sign: str) -> tuple[str, str | None]:
    main = SIGN_TO_RULER_MODERN.get(mc_sign)
    if not main:
        main = SIGN_TO_RULER_TRADITIONAL.get(mc_sign, "Saturn")

    co = SIGN_TO_CO_RULER.get(mc_sign)
    return main, co