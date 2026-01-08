from __future__ import annotations

from dataclasses import dataclass

from app.schemas.profile import ProfileRequest, ProfileResponse
from app.services.astro import get_sun_sign
from app.services.astro_calc import (
    calc_mercury_sign,
    calc_uranus_house,
    calc_house_signs,
    calc_planet_sign,
    calc_planet_house,
)
from app.services.day_night import is_day_chart
from app.services.it_profile import build_it_profile, get_10h_rulers, PLANET_NAME_TO_SWE
from app.services.places import find_coordinates
from app.services.timezones import timezone_name_from_coords, to_utc_birth_moment


@dataclass
class AstroService:
    default_house_system: bytes = b"P"

    def build_profile(self, payload: ProfileRequest) -> ProfileResponse:
        # 1) Place -> coords
        coords = find_coordinates(payload.birth_place)

        # 2) coords -> timezone name
        tz_name = timezone_name_from_coords(lat=coords.lat, lon=coords.lon)

        # 3) local birth moment -> utc
        moment = to_utc_birth_moment(
            birth_date=payload.birth_date,
            birth_time=payload.birth_time,
            tz_name=tz_name,
        )
        utc_dt = moment.utc_dt
        day_chart = is_day_chart(moment.local_dt)

        # 4) astrology parts (no rewrite, call existing funcs)
        sun_sign = get_sun_sign(payload.birth_date)
        mercury_sign = calc_mercury_sign(utc_dt=utc_dt)

        uranus_house = calc_uranus_house(
            utc_dt=utc_dt,
            lat=coords.lat,
            lon=coords.lon,
            house_system=self.default_house_system,
        )

        house_signs = calc_house_signs(
            utc_dt=utc_dt,
            lat=coords.lat,
            lon=coords.lon,
            house_system=self.default_house_system,
        )
        house_6_sign = house_signs["house_6_sign"]
        house_10_sign = house_signs["house_10_sign"]

        main_ruler_name, co_ruler_name = get_10h_rulers(house_10_sign)

        main_ruler_id = PLANET_NAME_TO_SWE[main_ruler_name]
        main_ruler_sign = calc_planet_sign(utc_dt=utc_dt, planet=main_ruler_id)
        main_ruler_house = calc_planet_house(
            utc_dt=utc_dt,
            lat=coords.lat,
            lon=coords.lon,
            planet=main_ruler_id,
            house_system=self.default_house_system,
        )

        co_ruler_sign = None
        co_ruler_house = None
        if co_ruler_name:
            co_ruler_id = PLANET_NAME_TO_SWE[co_ruler_name]
            co_ruler_sign = calc_planet_sign(utc_dt=utc_dt, planet=co_ruler_id)
            co_ruler_house = calc_planet_house(
                utc_dt=utc_dt,
                lat=coords.lat,
                lon=coords.lon,
                planet=co_ruler_id,
                house_system=self.default_house_system,
            )

        # 5) IT profile aggregation
        it = build_it_profile(
            sun_sign=sun_sign,
            is_day=day_chart,
            mercury_sign=mercury_sign,
            uranus_house=uranus_house,
            house_6_sign=house_6_sign,
            house_10_sign=house_10_sign,
            main_ruler_name=main_ruler_name,
            main_ruler_sign=main_ruler_sign,
            main_ruler_house=main_ruler_house,
            co_ruler_name=co_ruler_name,
            co_ruler_sign=co_ruler_sign,
            co_ruler_house=co_ruler_house,
        )

        return ProfileResponse(
            title="Astro IT Profile (draft)",
            sun_sign=sun_sign,
            it_fit_score=it.score,
            personality_style_archetype=it.personality_style_archetype,
            it_archetype=it.it_archetype,
            strengths=it.strengths,
            risks=it.risks,
            notes=it.notes,
            chart_type="day" if day_chart else "night",
            mercury_sign=mercury_sign,
            uranus_house=uranus_house,
            house_6_sign=house_6_sign,
            house_10_sign=house_10_sign,

        )