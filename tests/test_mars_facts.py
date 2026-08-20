import inspect
import unittest
from datetime import date, time

from app.services.aspects import ASPECTS
from app.services.astro_calc import (
    calc_planet_house,
    calc_planet_lon_and_speed,
    motion_from_speed,
    sign_from_longitude,
)
from app.services.it_rulership import PLANET_NAME_TO_SWE
from app.services import mars_facts as mars_facts_module
from app.services.mars_facts import (
    SOURCE_PLANET,
    calculated_mars_factor_keys,
    compute_mars_source_factors,
)
from app.services.mercury_aspect_reachability import is_natal_mercury_aspect_reachable
from app.services.mercury_aspects import planet_aspects_at
from app.services.places import find_coordinates
from app.services.timezones import timezone_name_from_coords, to_utc_birth_moment

AVDEY = {
    "birth_date": date(1986, 7, 14),
    "birth_time": time(7, 10),
    "birth_place": "Simferopol, Ukraine",
}
VLAD = {
    "birth_date": date(1986, 5, 16),
    "birth_time": time(15, 0),
    "birth_place": "Dnipro, Ukraine",
}
DZMITRY = {
    "birth_date": date(1985, 11, 12),
    "birth_time": time(14, 15),
    "birth_place": "Zhodino, Belarus",
}

ASPECT_ORB_LIMITS = {name: orb for name, _exact, orb in ASPECTS}
MOTIONS = {"direct", "retrograde"}


def _utc_for(**payload):
    coords = find_coordinates(payload["birth_place"])
    tz_name = timezone_name_from_coords(lat=coords.lat, lon=coords.lon)
    moment = to_utc_birth_moment(
        birth_date=payload["birth_date"],
        birth_time=payload["birth_time"],
        tz_name=tz_name,
    )
    return moment.utc_dt, coords


def _generic_mars_snapshot(**payload):
    utc_dt, coords = _utc_for(**payload)
    mars_id = PLANET_NAME_TO_SWE["Mars"]
    lon, speed = calc_planet_lon_and_speed(utc_dt=utc_dt, planet=mars_id)
    house, used_hsys = calc_planet_house(
        utc_dt=utc_dt,
        lat=coords.lat,
        lon=coords.lon,
        planet=mars_id,
    )
    aspects = planet_aspects_at(
        utc_dt=utc_dt,
        planet_name="Mars",
        include_moon=True,
        include_orb=True,
    )
    return {
        "sign": sign_from_longitude(lon),
        "longitude": round(lon, 6),
        "house": house,
        "motion": motion_from_speed(speed),
        "house_system": used_hsys.decode("ascii"),
        "aspects": aspects,
    }


class AvdeyMarsFactsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.factors = compute_mars_source_factors(**AVDEY)
        cls.generic = _generic_mars_snapshot(**AVDEY)

    def test_avdey_sign_house_motion(self):
        self.assertEqual(self.factors.mars_sign, "Capricorn")
        self.assertEqual(self.factors.mars_house, 6)
        self.assertEqual(self.factors.mars_motion, "retrograde")
        self.assertTrue(self.factors.birth_time_known)
        self.assertEqual(self.factors.mars_sign, self.generic["sign"])
        self.assertEqual(self.factors.mars_house, self.generic["house"])
        self.assertEqual(self.factors.mars_motion, self.generic["motion"])
        self.assertEqual(self.factors.mars_longitude, self.generic["longitude"])
        self.assertIn(self.factors.mars_motion, MOTIONS)
        self.assertNotEqual(self.factors.mars_motion, "weak")

    def test_avdey_aspects_match_generic_mars_as_source(self):
        factor_rows = [
            (item.planet, item.type, item.orb_deg) for item in self.factors.mars_aspects
        ]
        generic_rows = [
            (item["planet"], item["type"], item["orb_deg"])
            for item in self.generic["aspects"]
        ]
        self.assertEqual(factor_rows, generic_rows)
        self.assertTrue(all(item.planet != SOURCE_PLANET for item in self.factors.mars_aspects))

    def test_avdey_sun_opposition_and_moon_square(self):
        by_planet = {item.planet: item for item in self.factors.mars_aspects}
        self.assertEqual(set(by_planet), {"Sun", "Moon"})
        self.assertEqual(by_planet["Sun"].type, "opposition")
        self.assertEqual(by_planet["Moon"].type, "square")
        self.assertAlmostEqual(by_planet["Sun"].orb_deg, 4.86, places=2)
        self.assertAlmostEqual(by_planet["Moon"].orb_deg, 4.07, places=2)

    def test_avdey_orbs_within_project_limits(self):
        for aspect in self.factors.mars_aspects:
            self.assertIsInstance(aspect.orb_deg, float)
            self.assertLessEqual(aspect.orb_deg, ASPECT_ORB_LIMITS[aspect.type])

    def test_avdey_factor_keys_ready_for_mars_profile(self):
        keys = calculated_mars_factor_keys(self.factors)
        self.assertEqual(
            keys,
            (
                "sign:Capricorn",
                "house:6",
                "motion:retrograde",
                "aspect:opposition_Sun",
                "aspect:square_Moon",
            ),
        )


class VladDzmitryMarsRegressionTests(unittest.TestCase):
    def test_vlad_mars_matches_generic_calc(self):
        factors = compute_mars_source_factors(**VLAD)
        generic = _generic_mars_snapshot(**VLAD)
        self.assertEqual(factors.mars_sign, "Capricorn")
        self.assertEqual(factors.mars_house, 4)
        self.assertEqual(factors.mars_motion, "direct")
        self.assertEqual(factors.mars_sign, generic["sign"])
        self.assertEqual(factors.mars_house, generic["house"])
        self.assertEqual(factors.mars_motion, generic["motion"])
        pairs = {(item.type, item.planet) for item in factors.mars_aspects}
        self.assertEqual(pairs, {("trine", "Mercury"), ("sextile", "Jupiter")})
        by_planet = {item.planet: item for item in factors.mars_aspects}
        self.assertAlmostEqual(by_planet["Mercury"].orb_deg, 2.48, places=2)
        self.assertAlmostEqual(by_planet["Jupiter"].orb_deg, 1.93, places=2)
        self.assertEqual(
            [(item.planet, item.type, item.orb_deg) for item in factors.mars_aspects],
            [
                (item["planet"], item["type"], item["orb_deg"])
                for item in generic["aspects"]
            ],
        )

    def test_dzmitry_mars_matches_generic_calc(self):
        factors = compute_mars_source_factors(**DZMITRY)
        generic = _generic_mars_snapshot(**DZMITRY)
        self.assertEqual(factors.mars_sign, "Libra")
        self.assertEqual(factors.mars_house, 7)
        self.assertEqual(factors.mars_motion, "direct")
        self.assertEqual(factors.mars_sign, generic["sign"])
        self.assertEqual(factors.mars_house, generic["house"])
        self.assertEqual(factors.mars_motion, generic["motion"])
        pairs = {(item.type, item.planet) for item in factors.mars_aspects}
        self.assertEqual(pairs, {("sextile", "Mercury"), ("trine", "Jupiter")})
        by_planet = {item.planet: item for item in factors.mars_aspects}
        self.assertAlmostEqual(by_planet["Mercury"].orb_deg, 2.58, places=2)
        self.assertAlmostEqual(by_planet["Jupiter"].orb_deg, 0.25, places=2)
        self.assertEqual(
            [(item.planet, item.type, item.orb_deg) for item in factors.mars_aspects],
            [
                (item["planet"], item["type"], item["orb_deg"])
                for item in generic["aspects"]
            ],
        )


class MarsUnknownTimeAndSafetyTests(unittest.TestCase):
    def test_avdey_unknown_time_omits_house_longitude_moon_and_orbs(self):
        factors = compute_mars_source_factors(
            birth_date=AVDEY["birth_date"],
            birth_place=AVDEY["birth_place"],
            birth_time=None,
        )
        self.assertFalse(factors.birth_time_known)
        self.assertIsNone(factors.mars_house)
        self.assertIsNone(factors.mars_longitude)
        self.assertIsNone(factors.house_system_used)
        self.assertEqual(factors.mars_sign, "Capricorn")
        self.assertEqual(factors.mars_motion, "retrograde")
        self.assertTrue(
            any("houses and angles omitted" in item for item in factors.limitations)
        )
        self.assertTrue(
            any("exact Mars longitude omitted" in item for item in factors.limitations)
        )
        self.assertTrue(
            any("Moon aspects excluded" in item for item in factors.limitations)
        )
        self.assertEqual([item.planet for item in factors.mars_aspects if item.planet == "Moon"], [])
        self.assertEqual([item.planet for item in factors.mars_aspects if item.planet == "Sun"], [])
        self.assertTrue(
            any("Mars-Sun aspect is not stable" in item for item in factors.limitations)
        )
        for aspect in factors.mars_aspects:
            self.assertIsNone(aspect.orb_deg)
        keys = calculated_mars_factor_keys(factors)
        self.assertIn("sign:Capricorn", keys)
        self.assertIn("motion:retrograde", keys)
        self.assertNotIn("house:6", keys)
        self.assertNotIn("aspect:opposition_Sun", keys)

    def test_mars_does_not_use_mercury_reachability(self):
        source = inspect.getsource(mars_facts_module)
        self.assertNotIn("mercury_aspect_reachability", source)
        self.assertFalse(is_natal_mercury_aspect_reachable("Sun", "opposition"))
        factors = compute_mars_source_factors(**AVDEY)
        pairs = {(item.type, item.planet) for item in factors.mars_aspects}
        self.assertIn(("opposition", "Sun"), pairs)
