from datetime import datetime
import swisseph as swe


SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]


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

