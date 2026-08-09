from __future__ import annotations

from app.schemas.mercury_work_profile import (
    MercuryWorkProfileRequest,
    MercuryWorkProfileResponse,
)
from app.services.mercury_facts import (
    DEFAULT_HOUSE_SYSTEM,
    compute_exact_time_facts,
    compute_unknown_time_facts,
)
from app.services.places import find_coordinates
from app.services.timezones import timezone_name_from_coords, to_utc_birth_moment


def build_mercury_work_profile(
    payload: MercuryWorkProfileRequest,
) -> MercuryWorkProfileResponse:
    coords = find_coordinates(payload.birth_place)
    tz_name = timezone_name_from_coords(lat=coords.lat, lon=coords.lon)

    if payload.birth_time is None:
        source_factors, limitations = compute_unknown_time_facts(
            birth_date=payload.birth_date,
            tz_name=tz_name,
        )
    else:
        moment = to_utc_birth_moment(
            birth_date=payload.birth_date,
            birth_time=payload.birth_time,
            tz_name=tz_name,
        )
        source_factors, limitations = compute_exact_time_facts(
            utc_dt=moment.utc_dt,
            lat=coords.lat,
            lon=coords.lon,
            house_system=DEFAULT_HOUSE_SYSTEM,
        )

    return MercuryWorkProfileResponse(
        thinking="",
        learning="",
        communication="",
        strengths=[],
        risks=[],
        team_value="",
        possible_roles=[],
        source_factors=source_factors,
        limitations=limitations,
    )
