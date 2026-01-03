from fastapi import APIRouter

from app.schemas.profile import ProfileRequest, ProfileResponse
from app.services.astro import get_sun_sign
from app.services.astro_calc import calc_mercury_sign, calc_uranus_house, calc_house_signs
from app.services.it_profile import build_it_profile
from app.services.places import find_coordinates

from fastapi import HTTPException

from app.services.timezones import timezone_name_from_coords, to_utc_birth_moment

from app.services.day_night import is_day_chart


router = APIRouter(prefix="/profile", tags=["profile"])



@router.post("", response_model=ProfileResponse)
def build_profile(payload: ProfileRequest) -> ProfileResponse:
    try:
        coords = find_coordinates(payload.birth_place)
        tz_name = timezone_name_from_coords(lat=coords.lat, lon=coords.lon)



        moment = to_utc_birth_moment(
            birth_date=payload.birth_date,
            birth_time=payload.birth_time,
            tz_name=tz_name,
        )

        day_chart = is_day_chart(moment.local_dt)
        utc_dt = moment.utc_dt



    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    sun_sign = get_sun_sign(payload.birth_date)

    mercury_sign = calc_mercury_sign(utc_dt=utc_dt)

    uranus_house = calc_uranus_house(
        utc_dt=utc_dt,
        lat=coords.lat,
        lon=coords.lon,
    )

    house_signs = calc_house_signs(
        utc_dt=utc_dt,
        lat=coords.lat,
        lon=coords.lon,
    )

    house_6_sign = house_signs["house_6_sign"]
    house_10_sign = house_signs["house_10_sign"]


    it = build_it_profile(
        sun_sign=sun_sign,
        is_day=day_chart,
        mercury_sign=mercury_sign,
        uranus_house=uranus_house,
        house_6_sign=house_6_sign,
        house_10_sign=house_10_sign,

    )

    return ProfileResponse(
        title="Astro IT Profile (draft)",
        sun_sign=sun_sign,
        it_fit_score=it.score,
        it_archetype=it.archetype,
        strengths=it.strengths,
        risks=it.risks,
        notes=f"{it.notes} | chart={'day' if day_chart else 'night'} | mercury={mercury_sign} | uranus_house={uranus_house}",

    )






