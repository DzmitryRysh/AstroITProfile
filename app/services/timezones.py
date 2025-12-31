from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time, datetime
from zoneinfo import ZoneInfo

from timezonefinder import TimezoneFinder

tf = TimezoneFinder()

@dataclass(frozen=True)
class BirthMoment:
    tz_name: str
    local_dt: datetime
    utc_dt: datetime


def timezone_name_from_coords(*, lat:float, lon: float) -> str:
    tz = tf.timezone_at(lat=lat, lng=lon)
    if not tz:
        raise ValueError("Timezone not found for given coordinates")
    return tz


def to_utc_birth_moment(*, birth_date: date, birth_time: time, tz_name: str) -> BirthMoment:
    tz = ZoneInfo(tz_name)
    local_dt = datetime.combine(birth_date, birth_time).replace(tzinfo=tz)
    utc_dt = local_dt.astimezone(ZoneInfo("UTC"))
    return BirthMoment(tz_name=tz_name, local_dt=local_dt, utc_dt=utc_dt)







