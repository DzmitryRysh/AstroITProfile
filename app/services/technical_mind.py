from app.services.aspects import detect_major_aspect, score_aspect
from app.services.aspect_texts import TECH_MIND_TEXTS


def technical_mind_aspect(
    *,
    mercury_lon: float,
    uranus_lon: float,
) -> tuple[dict | None, int]:
    aspect_name, orb = detect_major_aspect(mercury_lon, uranus_lon)
    if not aspect_name:
        return None, 0

    delta, impact = score_aspect(aspect_name, orb)

    delta = min(delta,5)


    payload = {
        "with":"Uranus",
        "type": aspect_name,
        "orb_deg": orb,
        "impact": impact,
        "score_delta": delta,
    }

    text_data = TECH_MIND_TEXTS.get(aspect_name)
    if text_data:
        payload["title"] = text_data["title"]
        payload["text"] = text_data["text"]
        payload["advice"] = text_data["advice"]

    return payload, delta