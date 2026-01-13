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
    calc_planet_lon,
)
from app.services.day_night import is_day_chart
from app.services.it_profile import build_it_profile
from app.services.it_rulership import get_10h_rulers, PLANET_NAME_TO_SWE
from app.services.places import find_coordinates
from app.services.timezones import timezone_name_from_coords, to_utc_birth_moment
from app.services.aspects import ruler_aspects_package
from app.services.technical_mind import technical_mind_aspect


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

        # 4) astrology parts
        sun_sign = get_sun_sign(payload.birth_date)
        mercury_sign = calc_mercury_sign(utc_dt=utc_dt)

        # Uranus house (now returns: (house, used_house_system))
        uranus_house, used_hsys_uranus = calc_uranus_house(
            utc_dt=utc_dt,
            lat=coords.lat,
            lon=coords.lon,
            house_system=self.default_house_system,
        )

        # house signs (now returns: (dict, used_house_system))
        house_signs, used_hsys_houses = calc_house_signs(
            utc_dt=utc_dt,
            lat=coords.lat,
            lon=coords.lon,
            house_system=self.default_house_system,
        )
        house_6_sign = house_signs["house_6_sign"]
        house_10_sign = house_signs["house_10_sign"]

        # 10H rulers
        main_ruler_name, co_ruler_name = get_10h_rulers(house_10_sign)

        # main ruler sign + house (planet house now returns: (house, used_house_system))
        main_ruler_id = PLANET_NAME_TO_SWE[main_ruler_name]
        main_ruler_sign = calc_planet_sign(utc_dt=utc_dt, planet=main_ruler_id)
        main_ruler_house, used_hsys_main_ruler = calc_planet_house(
            utc_dt=utc_dt,
            lat=coords.lat,
            lon=coords.lon,
            planet=main_ruler_id,
            house_system=self.default_house_system,
        )

        # ---- longitudes for aspects (Level 2) ----
        mercury_lon = calc_planet_lon(utc_dt=utc_dt, planet=PLANET_NAME_TO_SWE["Mercury"])
        uranus_lon = calc_planet_lon(utc_dt=utc_dt, planet=PLANET_NAME_TO_SWE["Uranus"])
        ruler_lon = calc_planet_lon(utc_dt=utc_dt, planet=main_ruler_id)

        technical_mind, tech_mind_bonus = technical_mind_aspect(
            mercury_lon=mercury_lon,
            uranus_lon=uranus_lon,
        )

        aspects_list, aspects_bonus = ruler_aspects_package(
            ruler_lon=ruler_lon,
            mercury_lon=mercury_lon,
            uranus_lon=uranus_lon,
        )


        print("DEBUG ASPECTS:", aspects_list, "BONUS", aspects_bonus)

        # co-ruler (optional)
        co_ruler_sign = None
        co_ruler_house = None
        used_hsys_co_ruler = None

        if co_ruler_name:
            co_ruler_id = PLANET_NAME_TO_SWE[co_ruler_name]
            co_ruler_sign = calc_planet_sign(utc_dt=utc_dt, planet=co_ruler_id)
            co_ruler_house, used_hsys_co_ruler = calc_planet_house(
                utc_dt=utc_dt,
                lat=coords.lat,
                lon=coords.lon,
                planet=co_ruler_id,
                house_system=self.default_house_system,
            )

        # Decide which house system was actually used (usually they will match)
        # We pick the first non-default that appeared, otherwise keep the default.
        used_system = (
            used_hsys_uranus
            or used_hsys_houses
            or used_hsys_main_ruler
            or used_hsys_co_ruler
            or self.default_house_system
        )
        house_system_used = used_system.decode("ascii")

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
            aspects_bonus=aspects_bonus,
            tech_mind_bonus=tech_mind_bonus,

        )


        # attach aspects list for frontend
        career_axis_dict = it.career_axis.__dict__ if hasattr(it.career_axis, "__dict__") else dict(it.career_axis)
        career_axis_dict["aspects"] = aspects_list
        career_axis_dict["aspects_bonus"] = aspects_bonus


        return ProfileResponse(
            title="Astro IT Profile (draft)",
            sun_sign=sun_sign,
            it_fit_score=it.score,
            personality_style_archetype=it.personality_style_archetype,
            it_archetype=it.it_archetype,
            career_axis=career_axis_dict,
            strengths=it.strengths,
            risks=it.risks,
            notes=it.notes,
            chart_type="day" if day_chart else "night",
            mercury_sign=mercury_sign,
            uranus_house=uranus_house,
            house_6_sign=house_6_sign,
            house_10_sign=house_10_sign,
            house_system_used=house_system_used,
            technical_mind= technical_mind,

        )
