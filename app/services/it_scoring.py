from __future__ import annotations

# Uranus block: only house-based for MVP
URANUS_HOUSE_TO_SCORE = {
    1: 60,
    6: 68,
    10: 75,
    11: 72,
}
DEFAULT_URANUS_SCORE = 50

# House signs as "soft modifiers"
HOUSE6_SIGN_TO_SCORE = {
    "Virgo": 70,
    "Capricorn": 68,
    "Scorpio": 66,
    "Aquarius": 66,
    "Gemini": 64,
    "Aries": 62,
    "Taurus": 60,
    "Libra": 60,
    "Cancer": 58,
    "Leo": 58,
    "Sagittarius": 58,
    "Pisces": 56,
}
HOUSE10_SIGN_TO_SCORE = {
    "Capricorn": 70,
    "Aquarius": 68,
    "Virgo": 68,
    "Scorpio": 66,
    "Aries": 64,
    "Gemini": 64,
    "Taurus": 62,
    "Libra": 62,
    "Leo": 60,
    "Cancer": 60,
    "Sagittarius": 60,
    "Pisces": 58,
}
DEFAULT_HOUSE_SCORE = 60


def clamp_0_100(x: float) -> int:
    return int(max(0, min(100, round(x))))


def mercury_points_to_score(points: int) -> int:
    # 0 -> 55, 5 -> 75
    return max(0, min(100, 55 + points * 4))


# ---- career ruler bonus ----
HOUSE_TO_BONUS = {
    10: 10, 1: 8, 11: 7, 6: 6,
    3: 4, 2: 4, 7: 3, 9: 3,
    12: 2, 4: 1, 5: 1, 8: 1,
}

PLANET_TO_BONUS = {
    "Uranus": 7,
    "Mercury": 6,
    "Saturn": 6,
    "Jupiter": 5,
    "Mars": 4,
    "Sun": 3,
    "Venus": 3,
    "Pluto": 3,
    "Neptune": 3,
    "Moon": 2,
}


def calc_career_ruler_bonus(main_ruler_name: str, main_ruler_house: int) -> int:
    house_bonus = HOUSE_TO_BONUS.get(main_ruler_house, 1)
    planet_bonus = PLANET_TO_BONUS.get(main_ruler_name, 2)
    return min(15, house_bonus + planet_bonus)