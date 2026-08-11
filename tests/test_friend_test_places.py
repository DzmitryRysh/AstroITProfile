import unittest
from datetime import date, time

from app.core.app import create_app
from app.services.places import find_coordinates, list_places
from app.services.timezones import timezone_name_from_coords, to_utc_birth_moment

FRIEND_PLACES = {
    "Simferopol, Ukraine": {"lat": 44.95719, "lon": 34.11079},
    "Dnipro, Ukraine": {"lat": 48.46664, "lon": 35.04066},
    "Zhodino, Belarus": {"lat": 54.0985, "lon": 28.3331},
}

FRIEND_BIRTHS = [
    ("Avdey", date(1986, 7, 14), time(7, 10), "Simferopol, Ukraine"),
    ("Vlad", date(1986, 5, 16), time(15, 0), "Dnipro, Ukraine"),
    ("Dzmitry", date(1985, 11, 12), time(14, 15), "Zhodino, Belarus"),
]


class FriendTestPlacesTests(unittest.TestCase):
    def test_coordinates_resolve_for_friend_places(self):
        for place, expected in FRIEND_PLACES.items():
            with self.subTest(place=place):
                coords = find_coordinates(place)
                self.assertAlmostEqual(coords.lat, expected["lat"])
                self.assertAlmostEqual(coords.lon, expected["lon"])

    def test_timezone_and_historical_utc_conversion(self):
        for name, birth_date, birth_time, place in FRIEND_BIRTHS:
            with self.subTest(person=name, place=place):
                coords = find_coordinates(place)
                tz_name = timezone_name_from_coords(lat=coords.lat, lon=coords.lon)
                self.assertTrue(tz_name)
                moment = to_utc_birth_moment(
                    birth_date=birth_date,
                    birth_time=birth_time,
                    tz_name=tz_name,
                )
                self.assertEqual(moment.tz_name, tz_name)
                self.assertEqual(moment.local_dt.date(), birth_date)
                self.assertEqual(moment.local_dt.hour, birth_time.hour)
                self.assertEqual(moment.local_dt.minute, birth_time.minute)
                self.assertEqual(moment.utc_dt.tzname(), "UTC")

    def test_profile_places_endpoint_includes_friend_places(self):
        from app.api.routes.profile import available_places

        payload = available_places()
        places = payload["places"]
        for place in FRIEND_PLACES:
            self.assertIn(place, places)
        self.assertEqual(payload["count"], len(places))

    def test_create_app_still_exposes_places_route(self):
        app = create_app()
        paths = {getattr(route, "path", None) for route in app.routes}
        self.assertIn("/api/v1/profile/places", paths)


if __name__ == "__main__":
    unittest.main()
