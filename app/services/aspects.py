from typing import Optional, Tuple
from app.services.aspect_texts import ASPECT_TEXTS


ASPECTS = [
    ("conjunction", 0, 6),
    ("sextile", 60, 5),
    ("square", 90, 5),
    ("trine", 120, 5),
    ("opposition", 180, 5),
]


def detect_major_aspect(
    lon1: float, lon2: float
) -> Tuple[Optional[str], Optional[float]]:
    """
    Detect major aspect between two planets.
    Returns (aspect_name, orb_deg) or (None, None)
    """
    diff = abs(lon1 - lon2)
    if diff > 180:
        diff = 360 - diff

    for name, exact_deg, orb in ASPECTS:
        if abs(diff - exact_deg) <= orb:
            orb_deg = round(abs(diff - exact_deg), 2)
            return name, orb_deg

    return None, None

ASPECT_SCORE = {
    "conjunction": 6,
    "trine": 5,
    "sextile": 3,
    "square": 2,
    "opposition": 1,
}

ASPECT_IMPACT = {
    "conjunction": "support",
    "trine": "support",
    "sextile": "support",
    "square": "tension",
    "opposition": "tension",
}

def orb_bonus(orb_deg: float) -> int:
    if orb_deg <= 1.0:
        return 2
    if orb_deg <= 3.0:
        return 1
    return 0


def score_aspect(aspect_name: str, orb_deg: float) -> tuple[int, str]:
    base = ASPECT_SCORE.get(aspect_name, 0)
    bonus = orb_bonus(orb_deg)
    delta = base + bonus
    impact = ASPECT_IMPACT.get(aspect_name, "neutral")
    return delta, impact


def ruler_aspects_package(
    *,
    ruler_lon: float,
    mercury_lon: float,
    uranus_lon: float,
) -> tuple[list[dict], int]:
    """
    Returns:
      - aspects: list of aspect dicts (with text)
      - total_delta: capped sum of score deltas (max +8)
    """
    aspects: list[dict] = []
    total = 0

    for planet_name, lon in (("Mercury", mercury_lon), ("Uranus", uranus_lon)):
        aspect_name, orb = detect_major_aspect(ruler_lon, lon)
        if not aspect_name:
            continue

        delta, impact = score_aspect(aspect_name, orb)

        aspect = {
            "with": planet_name,
            "type": aspect_name,
            "orb_deg": orb,
            "impact": impact,
            "score_delta": delta,
        }

        text_data = ASPECT_TEXTS.get((planet_name, aspect_name))
        if text_data:
            aspect["title"] = text_data["title"]
            aspect["text"] = text_data["text"]
            aspect["advice"] = text_data["advice"]

        aspects.append(aspect)
        total += delta

    if total > 8:
        total = 8

    return aspects, total