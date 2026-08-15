"""Tests for natal Mercury aspect reachability (C10 coverage domain semantics)."""

from __future__ import annotations

import unittest

from app.services.mercury_aspect_reachability import (
    IMPOSSIBLE_NATAL_ASPECT_KEYS,
    MAJOR_ASPECT_TYPES,
    RAW_NATAL_ASPECT_KEYS,
    REACHABLE_NATAL_ASPECT_KEYS,
    TARGET_PLANETS,
    is_natal_mercury_aspect_reachable,
    natal_aspect_reachability_summary,
)
from app.services.mercury_aspects import MERCURY_ASPECT_TARGETS
from app.services.mercury_source_knowledge import (
    ASPECT_PACK_ALIASES,
    SUPPORTED_ASPECT_KEYS,
)

EXPECTED_IMPOSSIBLE = frozenset(
    {
        "sextile_Sun",
        "square_Sun",
        "trine_Sun",
        "opposition_Sun",
        "square_Venus",
        "trine_Venus",
        "opposition_Venus",
    }
)

EXPECTED_MISSING_REACHABLE = frozenset(
    {
        "conjunction_Venus",
        "sextile_Venus",
        "conjunction_Neptune",
        "sextile_Neptune",
        "square_Neptune",
        "trine_Neptune",
        "opposition_Neptune",
        "conjunction_Pluto",
        "opposition_Pluto",
    }
)

FULLY_REACHABLE_PLANETS = (
    "Moon",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
)


class NatalAspectReachabilityTests(unittest.TestCase):
    def test_raw_reachable_impossible_partition(self):
        self.assertEqual(len(RAW_NATAL_ASPECT_KEYS), 45)
        self.assertEqual(len(IMPOSSIBLE_NATAL_ASPECT_KEYS), 7)
        self.assertEqual(len(REACHABLE_NATAL_ASPECT_KEYS), 38)
        self.assertEqual(
            RAW_NATAL_ASPECT_KEYS,
            REACHABLE_NATAL_ASPECT_KEYS | IMPOSSIBLE_NATAL_ASPECT_KEYS,
        )
        self.assertTrue(REACHABLE_NATAL_ASPECT_KEYS.isdisjoint(IMPOSSIBLE_NATAL_ASPECT_KEYS))
        self.assertEqual(IMPOSSIBLE_NATAL_ASPECT_KEYS, EXPECTED_IMPOSSIBLE)
        self.assertEqual(tuple(TARGET_PLANETS), MERCURY_ASPECT_TARGETS)
        self.assertEqual(len(TARGET_PLANETS) * len(MAJOR_ASPECT_TYPES), 45)

    def test_sun_reachability(self):
        self.assertTrue(is_natal_mercury_aspect_reachable("Sun", "conjunction"))
        for aspect in ("sextile", "square", "trine", "opposition"):
            self.assertFalse(is_natal_mercury_aspect_reachable("Sun", aspect))
            self.assertIn(f"{aspect}_Sun", IMPOSSIBLE_NATAL_ASPECT_KEYS)

    def test_venus_reachability(self):
        self.assertTrue(is_natal_mercury_aspect_reachable("Venus", "conjunction"))
        self.assertTrue(is_natal_mercury_aspect_reachable("Venus", "sextile"))
        for aspect in ("square", "trine", "opposition"):
            self.assertFalse(is_natal_mercury_aspect_reachable("Venus", aspect))
            self.assertIn(f"{aspect}_Venus", IMPOSSIBLE_NATAL_ASPECT_KEYS)

    def test_outer_and_moon_families_fully_reachable(self):
        for planet in FULLY_REACHABLE_PLANETS:
            for aspect in MAJOR_ASPECT_TYPES:
                with self.subTest(planet=planet, aspect=aspect):
                    self.assertTrue(is_natal_mercury_aspect_reachable(planet, aspect))
                    self.assertIn(f"{aspect}_{planet}", REACHABLE_NATAL_ASPECT_KEYS)
                    self.assertNotIn(f"{aspect}_{planet}", IMPOSSIBLE_NATAL_ASPECT_KEYS)

    def test_supported_source_keys_are_all_reachable(self):
        self.assertTrue(SUPPORTED_ASPECT_KEYS.isdisjoint(IMPOSSIBLE_NATAL_ASPECT_KEYS))
        self.assertTrue(frozenset(SUPPORTED_ASPECT_KEYS) <= REACHABLE_NATAL_ASPECT_KEYS)

    def test_current_supported_and_missing_reachable_counts(self):
        # Source-snapshot counts are owned by the latest aspect batch (C11+).
        # C10 verifies geometry + that supported keys remain reachable-only.
        self.assertTrue(frozenset(SUPPORTED_ASPECT_KEYS) <= REACHABLE_NATAL_ASPECT_KEYS)
        missing_reachable = REACHABLE_NATAL_ASPECT_KEYS - frozenset(SUPPORTED_ASPECT_KEYS)
        self.assertTrue(IMPOSSIBLE_NATAL_ASPECT_KEYS.isdisjoint(missing_reachable))

    def test_impossible_keys_are_not_missing_source_knowledge(self):
        missing_reachable = REACHABLE_NATAL_ASPECT_KEYS - frozenset(SUPPORTED_ASPECT_KEYS)
        self.assertTrue(IMPOSSIBLE_NATAL_ASPECT_KEYS.isdisjoint(missing_reachable))
        self.assertTrue(IMPOSSIBLE_NATAL_ASPECT_KEYS.isdisjoint(SUPPORTED_ASPECT_KEYS))

    def test_raw_geometry_denominator_unchanged(self):
        # Geometry constants remain fixed; raw source totals are owned by C11+.
        self.assertEqual(len(RAW_NATAL_ASPECT_KEYS), 45)
        self.assertEqual(len(REACHABLE_NATAL_ASPECT_KEYS), 38)
        self.assertEqual(len(IMPOSSIBLE_NATAL_ASPECT_KEYS), 7)
        self.assertEqual(len(ASPECT_PACK_ALIASES), 6)

    def test_summary_helper_geometry_fields(self):
        summary = natal_aspect_reachability_summary(SUPPORTED_ASPECT_KEYS)
        self.assertEqual(summary["raw_total"], 45)
        self.assertEqual(summary["reachable_total"], 38)
        self.assertEqual(summary["impossible_total"], 7)
        self.assertEqual(summary["impossible_keys"], EXPECTED_IMPOSSIBLE)
        self.assertEqual(
            summary["supported_reachable"] + summary["missing_reachable"],
            summary["reachable_total"],
        )
        # After C11, Sun conjunction is supported; remaining missing set is source-owned by C11.
        self.assertNotIn("conjunction_Sun", summary["missing_reachable_keys"])
        self.assertIn("conjunction_Sun", summary["supported_reachable_keys"])
        self.assertTrue(EXPECTED_MISSING_REACHABLE <= summary["missing_reachable_keys"])
        self.assertEqual(len(summary["missing_reachable_keys"]), 9)


if __name__ == "__main__":
    unittest.main()
