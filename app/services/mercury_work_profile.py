from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.schemas.mercury_work_profile import (
    MercuryWorkProfileRequest,
    MercuryWorkProfileResponse,
)
from app.services.mercury_facts import (
    DEFAULT_HOUSE_SYSTEM,
    compute_exact_time_facts,
    compute_unknown_time_facts,
)
from app.services.mercury_rules import (
    ELEMENT_RULES,
    RETROGRADE_RULE,
    SIGN_RULES,
    SIGN_UNAVAILABLE_LIMITATION,
)
from app.services.places import find_coordinates
from app.services.timezones import timezone_name_from_coords, to_utc_birth_moment


@dataclass(frozen=True)
class MercuryNarrative:
    thinking: str
    learning: str
    communication: str
    strengths: list[str]
    risks: list[str]
    team_value: str
    possible_roles: list[str]
    extra_limitations: list[str]


def _dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def _join_unique_parts(*parts: str) -> str:
    chunks: list[str] = []
    seen: set[str] = set()
    for part in parts:
        text = " ".join((part or "").split())
        if not text:
            continue
        key = text.casefold()
        if key in seen:
            continue
        seen.add(key)
        chunks.append(text)
    return " ".join(chunks)


def synthesize_mercury_narrative(
    *,
    mercury_sign: Optional[str],
    mercury_element: Optional[str],
    mercury_motion: Optional[str],
) -> MercuryNarrative:
    """
    Milestone 2 synthesis: element baseline + sign + retrograde modifier.

    House, aspects, and dispositors must not be passed in or used.
    """
    if not mercury_sign or mercury_sign not in SIGN_RULES:
        return MercuryNarrative(
            thinking="",
            learning="",
            communication="",
            strengths=[],
            risks=[],
            team_value="",
            possible_roles=[],
            extra_limitations=[SIGN_UNAVAILABLE_LIMITATION],
        )

    sign_rule = SIGN_RULES[mercury_sign]
    element_rule = ELEMENT_RULES.get(mercury_element or "")

    thinking_parts = []
    communication_parts = []
    if element_rule:
        thinking_parts.append(f"{element_rule.thinking_type}. {element_rule.thinking}")
        communication_parts.append(element_rule.communication)
    thinking_parts.append(sign_rule.thinking)
    communication_parts.append(sign_rule.communication)

    learning_parts = [sign_rule.learning]
    strengths = list(sign_rule.strengths)
    risks = list(sign_rule.risks)

    if mercury_motion == "retrograde":
        thinking_parts.append(RETROGRADE_RULE.thinking)
        learning_parts.append(RETROGRADE_RULE.learning)
        communication_parts.append(RETROGRADE_RULE.communication)
        strengths.extend(RETROGRADE_RULE.strengths)
        risks.extend(RETROGRADE_RULE.risks)

    return MercuryNarrative(
        thinking=_join_unique_parts(*thinking_parts),
        learning=_join_unique_parts(*learning_parts),
        communication=_join_unique_parts(*communication_parts),
        strengths=_dedupe_keep_order(strengths),
        risks=_dedupe_keep_order(risks),
        team_value=sign_rule.team_value,
        possible_roles=_dedupe_keep_order(list(sign_rule.possible_roles)),
        extra_limitations=[],
    )


def build_mercury_work_profile(
    payload: MercuryWorkProfileRequest,
) -> MercuryWorkProfileResponse:
    coords = find_coordinates(payload.birth_place)
    tz_name = timezone_name_from_coords(lat=coords.lat, lon=coords.lon)

    if payload.birth_time is None:
        source_factors, limitations = compute_unknown_time_facts(
            birth_date=payload.birth_date,
            tz_name=tz_name,
        )
    else:
        moment = to_utc_birth_moment(
            birth_date=payload.birth_date,
            birth_time=payload.birth_time,
            tz_name=tz_name,
        )
        source_factors, limitations = compute_exact_time_facts(
            utc_dt=moment.utc_dt,
            lat=coords.lat,
            lon=coords.lon,
            house_system=DEFAULT_HOUSE_SYSTEM,
        )

    narrative = synthesize_mercury_narrative(
        mercury_sign=source_factors.mercury_sign,
        mercury_element=source_factors.mercury_element,
        mercury_motion=source_factors.mercury_motion,
    )
    all_limitations = limitations + narrative.extra_limitations

    return MercuryWorkProfileResponse(
        thinking=narrative.thinking,
        learning=narrative.learning,
        communication=narrative.communication,
        strengths=narrative.strengths,
        risks=narrative.risks,
        team_value=narrative.team_value,
        possible_roles=narrative.possible_roles,
        source_factors=source_factors,
        limitations=all_limitations,
    )
