from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from app.services.career_axis import build_career_axis
from app.services.it_dictionaries import (
    SUN_SIGN_TO_IT,
    MERCURY_TO_THINKING,
    URANUS_HOUSE_TO_IT,
    HOUSE6_SIGN_TO_WORKSTYLE,
    HOUSE10_SIGN_TO_CAREER,
)
from app.services.it_scoring import (
    URANUS_HOUSE_TO_SCORE,
    DEFAULT_URANUS_SCORE,
    HOUSE6_SIGN_TO_SCORE,
    HOUSE10_SIGN_TO_SCORE,
    DEFAULT_HOUSE_SCORE,
    mercury_points_to_score,
    clamp_0_100,
    calc_career_ruler_bonus,
)


@dataclass(frozen=True)
class ITProfile:
    score: int
    personality_style_archetype: str
    it_archetype: str
    career_axis: dict[str, Any]
    strengths: list[str]
    risks: list[str]
    notes: str


def build_it_profile(
    *,
    sun_sign: str,
    is_day: bool,
    mercury_sign: str,
    uranus_house: int,
    house_6_sign: str,
    house_10_sign: str,
    main_ruler_name: str,
    main_ruler_sign: str,
    main_ruler_house: int,
    co_ruler_name: Optional[str] = None,
    co_ruler_sign: Optional[str] = None,
    co_ruler_house: Optional[int] = None,
) -> ITProfile:

    # ---- 0) Sun is STYLE only (NO score impact) ----
    sun_base = SUN_SIGN_TO_IT.get(
        sun_sign,
        (
            0,
            "Balanced Engineer",
            ["adaptability", "learning mindset"],
            ["needs clearer structure"],
            "General profile: suitable for IT with the right direction.",
        ),
    )
    _unused, personality_style_archetype, strengths, risks, notes = sun_base

    # day/night -> narrative only
    if is_day:
        strengths = strengths + ["team-oriented work style"]
        notes = f"{notes} | Day chart: energy is more externally expressed."
    else:
        strengths = strengths + ["deep focus potential"]
        notes = f"{notes} | Night chart: energy is more internal and focused."

    # ---- 1) Mercury block (0..100) ----
    m_points, m_strengths, m_risks, m_notes = MERCURY_TO_THINKING.get(
        mercury_sign,
        (2, [], [], "Mercury: default practical thinking."),
    )
    mercury_score = mercury_points_to_score(int(m_points))
    strengths = strengths + m_strengths
    risks = risks + m_risks
    notes = f"{notes} | {m_notes}"

    # ---- 2) Uranus block (0..100) ----
    allowed = {1, 6, 10, 11}
    if uranus_house not in allowed:
        uranus_house = 0

    if uranus_house:
        _u_points, u_strengths, u_risks, u_note = URANUS_HOUSE_TO_IT[uranus_house]
        strengths = strengths + u_strengths
        risks = risks + u_risks
        notes = f"{notes} | {u_note}"

    uranus_score = URANUS_HOUSE_TO_SCORE.get(uranus_house, DEFAULT_URANUS_SCORE)

    # ---- 3) House 6 block (soft) ----
    h6_strengths, h6_risks, h6_note = HOUSE6_SIGN_TO_WORKSTYLE.get(
        house_6_sign, ([], [], f"6th house {house_6_sign}: daily style noted.")
    )
    strengths += h6_strengths
    risks += h6_risks
    notes = f"{notes} | {h6_note}"
    workstyle_score = HOUSE6_SIGN_TO_SCORE.get(house_6_sign, DEFAULT_HOUSE_SCORE)

    # ---- 4) House 10 block (soft) ----
    arch, h10_strengths, h10_risks, h10_note = HOUSE10_SIGN_TO_CAREER.get(
        house_10_sign,
        ("Backend Astronaut", [], [], f"10th house {house_10_sign}: career style noted."),
    )

    it_archetype = arch
    strengths += h10_strengths
    risks += h10_risks
    notes = f"{notes} | {h10_note}"
    career_score = HOUSE10_SIGN_TO_SCORE.get(house_10_sign, DEFAULT_HOUSE_SCORE)

    # ---- 4.1) Career ruler bonus ----
    career_ruler_bonus = calc_career_ruler_bonus(main_ruler_name, main_ruler_house)
    career_score = min(100, career_score + career_ruler_bonus)
    notes = f"{notes} | Career ruler bonus: +{career_ruler_bonus}"

    # ---- 4.2) Archetype prefix by ruler house ----
    def ruler_prefix(house_num: int) -> str:
        if house_num == 1:
            return "Public / Visible"
        if house_num == 10:
            return "Career Axis"
        if house_num == 11:
            return "Network / Platform"
        if house_num == 6:
            return "Craft / Skill Builder"
        return "Strategic"

    it_archetype = f"{ruler_prefix(main_ruler_house)} {it_archetype}"


    # ---- 4.3) Career Axis block (for frontend) ----
    career_axis = build_career_axis(
        mc_sign=house_10_sign,
        main_ruler_name=main_ruler_name,
        main_ruler_sign=main_ruler_sign,
        main_ruler_house=main_ruler_house,
    )

    # ---- 5) Final weighted score (0..100) ----
    tech_signature = (
        0.45 * uranus_score +
        0.35 * mercury_score +
        0.10 * career_score +
        0.10 * workstyle_score
    )
    score = clamp_0_100(tech_signature)

    # clean duplicates
    strengths = list(dict.fromkeys(strengths))
    risks = list(dict.fromkeys(risks))

    # optional co-ruler info (keep short)
    if co_ruler_name:
        notes = f"{notes} | Co-ruler: {co_ruler_name} (H{co_ruler_house})"

    # debug note
    notes = (
        f"{notes} | Scores: Uranus={uranus_score}, Mercury={mercury_score}, "
        f"Career(10H+Ruler)={career_score}, Workstyle(6H)={workstyle_score} -> Total={score}"
    )

    return ITProfile(
        score=score,
        personality_style_archetype=personality_style_archetype,
        it_archetype=it_archetype,
        career_axis=career_axis,
        strengths=strengths,
        risks=risks,
        notes=notes,
    )