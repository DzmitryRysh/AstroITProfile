from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CareerAxisBlock:
    title: str
    summary: str
    roles_hint: list[str]
    factors: dict


HOUSE_TO_CAREER_STYLE = {
    1: {
        "title": "Public Presence",
        "text": "visibility, identity, and personal brand are strongly tied to career realization",
        "roles": ["public expert", "technical leadership", "DevRel", "mentoring"],
    },
    2: {
        "title": "Value & Monetization",
        "text": "career growth comes through building value, monetization, and resources",
        "roles": ["product engineering", "business-minded developer", "founder mindset"],
    },
    3: {
        "title": "Communication & Learning",
        "text": "career develops through communication, learning, writing, and teaching",
        "roles": ["DevRel", "solutions engineer", "technical writer", "educator"],
    },
    6: {
        "title": "Craft & Systems",
        "text": "career grows through mastery, reliability, and continuous system improvement",
        "roles": ["SRE/DevOps", "QA/quality", "backend reliability", "automation"],
    },
    9: {
        "title": "Research & Vision",
        "text": "career grows through exploration, research, and big-picture strategy",
        "roles": ["research engineer", "AI/ML exploration", "architecture", "strategy"],
    },
    10: {
        "title": "Career Axis",
        "text": "career is a central life axis: responsibility, leadership, and long-term achievement",
        "roles": ["engineering manager", "architect", "leadership track"],
    },
    11: {
        "title": "Networks & Platforms",
        "text": "career develops through communities, teams, platforms, and large-scale systems",
        "roles": ["platform engineer", "distributed systems", "open-source", "community tech"],
    },
    12: {
        "title": "Behind-the-Scenes R&D",
        "text": "career expression is strongest in deep work, research, and behind-the-scenes problem solving",
        "roles": ["R&D", "security research", "deep backend work"],
    },
}

PLANET_TO_CAREER_TONE = {
    "Mercury": {
        "text": "analytical thinking, communication, and rapid skill acquisition",
        "roles": ["systems analyst", "engineering problem solver", "documentation"],
    },
    "Uranus": {
        "text": "innovation, technology-first thinking, and non-standard solutions",
        "roles": ["R&D", "automation", "platform futurist"],
    },
    "Saturn": {
        "text": "structure, discipline, architecture, and long-term responsibility",
        "roles": ["architect", "SRE", "platform reliability"],
    },
    "Jupiter": {
        "text": "growth through learning, mentoring, scaling, and expanding influence",
        "roles": ["mentor", "DevRel", "vision roles"],
    },
    "Mars": {
        "text": "speed, initiative, execution, and competitive drive",
        "roles": ["startup builder", "incident leadership"],
    },
    "Venus": {
        "text": "design sense, harmony, and relationship-building",
        "roles": ["UX-minded engineer", "design systems"],
    },
    "Sun": {"text": "leadership, visibility, and ownership", "roles": ["technical leadership"]},
    "Moon": {"text": "supportive approach and strong context awareness", "roles": ["team anchor", "support culture"]},
    "Neptune": {"text": "imagination and abstraction (best when grounded with structure)", "roles": ["creative tech", "product vision"]},
    "Pluto": {"text": "depth and transformation in complex systems", "roles": ["security", "deep systems"]},
}


def build_career_axis(
    *,
    mc_sign: str,
    main_ruler_name: str,
    main_ruler_sign: str,
    main_ruler_house: int,
) -> CareerAxisBlock:
    house_pack = HOUSE_TO_CAREER_STYLE.get(
        main_ruler_house,
        {
            "title": "Career Expression",
            "text": "career expression is shaped by your overall life context",
            "roles": [],
        },
    )
    planet_pack = PLANET_TO_CAREER_TONE.get(
        main_ruler_name,
        {"text": "a balanced professional tone", "roles": []},
    )

    # Тон “вариант 4” (IT-friendly)
    summary = (
        "This is a strong signature for public expertise in technology. "
        f"It points to roles where {house_pack['text']} matters — such as research, innovation, DevRel, "
        "technical leadership, or mentoring. "
        f"The career ruler {main_ruler_name} emphasizes {planet_pack['text']}. "
        "This combination often supports roles that mix expertise, visibility, and impact."
    )

    roles_hint = list(dict.fromkeys(house_pack["roles"] + planet_pack["roles"]))

    return CareerAxisBlock(
        title=house_pack["title"],
        summary=summary,
        roles_hint=roles_hint,
        factors={
            "mc_sign": mc_sign,
            "main_ruler": main_ruler_name,
            "main_ruler_sign": main_ruler_sign,
            "main_ruler_house": main_ruler_house,
        },
    )