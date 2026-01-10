from datetime import datetime
import swisseph as swe
from typing import Tuple



SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def safe_houses_ex(
    jd: float,
    lat: float,
    lon: float,
    house_system: bytes,
    flags: int,
) -> Tuple[list[float], object, bytes]:
    """
    Try requested house system first; if it fails (high latitudes),
    fallback to Whole Sign ('W'), then Porphyry ('O').
    Returns: (cusps_raw, ascmc, used_house_system)
    """
    candidates = (house_system, b"W", b"O")
    last_error = None

    for hs in candidates:
        try:
            cusps_raw, ascmc = swe.houses_ex(jd, lat, lon, hs, flags)
            return cusps_raw, ascmc, hs
        except swe.Error as e:
            last_error = e

    raise last_error

def _sign_from_lon(lon: float) -> str:
    index = int(lon // 30)
    return SIGNS[index % 12]


def _julian_day_utc(dt_utc: datetime) -> float:
    y, m, d = dt_utc.year, dt_utc.month, dt_utc.day
    hour = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    return swe.julday(y, m, d, hour, swe.GREG_CAL)


def calc_mercury_sign(*, utc_dt: datetime) -> str:
    jd = _julian_day_utc(utc_dt)
    mercury, _ = swe.calc_ut(jd, swe.MERCURY)
    lon = float(mercury[0])
    return _sign_from_lon(lon)


def calc_planet_sign(*, utc_dt: datetime, planet: int) -> str:
    jd = _julian_day_utc(utc_dt)
    lon = _planet_lon_ut(jd, planet)
    return _sign_from_lon(lon)


def calc_planet_house(
        *, utc_dt: datetime, lat: float, lon: float, planet: int, house_system: bytes = b'P'
) -> tuple[int, bytes]:
    jd = _julian_day_utc(utc_dt)
    cusps_raw, _ascmc, used_hsys = safe_houses_ex(
        jd, lat, lon, house_system, swe.FLG_SWIEPH
    )
    if len(cusps_raw) == 13:
        cusps = [float(cusps_raw[i]) for i in range(1, 13)]
    elif len(cusps_raw) == 12:
        cusps = [float(c) for c in cusps_raw]
    else:
        raise RuntimeError(f"Unexpected cusps length from swe.houses_ex: {len(cusps_raw)}")

    pl_lon = _planet_lon_ut(jd, planet)
    return _house_index_from_lon(pl_lon, cusps), used_hsys


def _planet_lon_ut(jd_ut: float, planet: int) -> float:
    """Ecliptic longitude (0..360) for a planet at UT (Swiss Ephemeris)."""
    pos, _ = swe.calc_ut(jd_ut, planet, swe.FLG_SWIEPH)
    lon = float(pos[0]) % 360.0
    return lon

def _house_index_from_lon(lon: float, cusps: list[float]) -> int:
    """
    Determine house number (1..12) from ecliptic longitude and 12 house cusps.
    Cusps are 1..12 in Swiss Ephemeris (array index 0..11 if we convert).
    """
    lon = lon % 360.0
    # cusps list expected length 12, each in 0..360
    cusps = [(c % 360.0) for c in cusps]

    # Iterate houses: house i spans from cusp[i] to cusp[i+1] (wrap for 12->1)
    for i in range(12):
        start = cusps[i]
        end = cusps[(i + 1) % 12]

        if start <= end:
            if start <= lon < end:
                return i + 1
        else:
            # wrap-around segment, e.g., 350..360 + 0..20
            if lon >= start or lon < end:
                return i + 1

    return 1


def calc_uranus_house(
        *, utc_dt: datetime, lat: float, lon: float, house_system: bytes = b'P'
) -> tuple[int, bytes]:
    jd = _julian_day_utc(utc_dt)

    cusps_raw, _ascmc, used_hsys = safe_houses_ex(
        jd, lat, lon, house_system, swe.FLG_SWIEPH
    )

    # Normalize cusps to a 12-element list (pyswisseph may return len 12 or 13)
    if len(cusps_raw) == 13:
        cusps = [float(cusps_raw[i]) for i in range(1, 13)]
    elif len(cusps_raw) == 12:
        cusps = [float(c) for c in cusps_raw]
    else:
        raise RuntimeError(f"Unexpected cusps length from swe.houses_ex: {len(cusps_raw)}")

    ur_lon = _planet_lon_ut(jd, swe.URANUS)
    return _house_index_from_lon(ur_lon, cusps), used_hsys


def calc_house_signs(
        *, utc_dt: datetime, lat: float, lon: float, house_system: bytes = b'P'
) -> tuple[dict[str, str], bytes]:
    """
    Zodiac signs on cusps of 6th and 10th houses (Swiss Ephemeris).
    """
    jd = _julian_day_utc(utc_dt)
    cusps_raw, _ascmc, used_hsys = safe_houses_ex(
        jd, lat, lon, house_system, swe.FLG_SWIEPH
    )

    # Normalize cusps to 12-element list
    if len(cusps_raw) == 13:
        cusps = [float(cusps_raw[i]) for i in range(1, 13)]
    elif len(cusps_raw) == 12:
        cusps = [float(c) for c in cusps_raw]
    else:
        raise RuntimeError(f"Unexpected cusps length from swe.houses_ex: {len(cusps_raw)}")

    # cusps[0] -> 1st house cusp, cusps[5] -> 6th, cusps[9] -> 10th
    house_6_lon = cusps[5]
    house_10_lon = cusps[9]

    return {
        "house_6_sign": _sign_from_lon(house_6_lon),
        "house_10_sign": _sign_from_lon(house_10_lon),
    }, used_hsys


