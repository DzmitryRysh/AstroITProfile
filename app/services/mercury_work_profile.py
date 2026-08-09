from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from app.schemas.mercury_work_profile import (
    MercuryAspect,
    MercuryWorkProfileRequest,
    MercuryWorkProfileResponse,
    PlanetAspect,
)
from app.services.mercury_facts import (
    DEFAULT_HOUSE_SYSTEM,
    compute_exact_time_facts,
    compute_unknown_time_facts,
)
from app.services.mercury_rules import (
    ASPECT_APPLY_ORDER,
    DISPOSITOR_FUNCTION_RULES,
    ELEMENT_RULES,
    HOUSE_RULES,
    LABEL_THEME,
    RETROGRADE_RULE,
    SIGN_RULES,
    SIGN_THEMES,
    SIGN_UNAVAILABLE_LIMITATION,
    TALKATIVE_THEMES,
    DispositorFunctionRule,
    MercuryAspectRule,
    MercuryHouseRule,
    effective_dispositor_condition_state,
    get_aspect_rule,
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


def _extend_labels(existing: list[str], new_items: Iterable[str]) -> list[str]:
    seen_labels = set(existing)
    seen_themes = {LABEL_THEME[item] for item in existing if item in LABEL_THEME}
    for item in new_items:
        if item in seen_labels:
            continue
        theme = LABEL_THEME.get(item)
        if theme and theme in seen_themes:
            continue
        seen_labels.add(item)
        if theme:
            seen_themes.add(theme)
        existing.append(item)
    return existing


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


def _pick_text(
    *,
    base: str,
    reinforce: str,
    overlapping: bool,
) -> str:
    if overlapping and reinforce:
        return reinforce
    return base


def _apply_house(
    *,
    house: int,
    sign_themes: frozenset[str],
    thinking_parts: list[str],
    learning_parts: list[str],
    communication_parts: list[str],
    team_value_parts: list[str],
    strengths: list[str],
    risks: list[str],
) -> None:
    rule: MercuryHouseRule | None = HOUSE_RULES.get(house)
    if not rule:
        return
    overlapping = bool(sign_themes & rule.themes)
    thinking_parts.append(
        _pick_text(base=rule.thinking, reinforce=rule.thinking_reinforce, overlapping=overlapping)
    )
    learning_parts.append(
        _pick_text(base=rule.learning, reinforce=rule.learning_reinforce, overlapping=overlapping)
    )
    communication_parts.append(
        _pick_text(
            base=rule.communication,
            reinforce=rule.communication_reinforce,
            overlapping=overlapping,
        )
    )
    team_value_parts.append(
        _pick_text(
            base=rule.team_value,
            reinforce=rule.team_value_reinforce,
            overlapping=overlapping,
        )
    )
    _extend_labels(strengths, rule.strengths)
    _extend_labels(risks, rule.risks)


def _apply_aspect(
    *,
    rule: MercuryAspectRule,
    sign_themes: frozenset[str],
    thinking_parts: list[str],
    learning_parts: list[str],
    communication_parts: list[str],
    strengths: list[str],
    risks: list[str],
) -> None:
    overlapping = bool(sign_themes & rule.themes)
    thinking_parts.append(
        _pick_text(base=rule.thinking, reinforce=rule.thinking_reinforce, overlapping=overlapping)
    )
    learning_parts.append(
        _pick_text(base=rule.learning, reinforce=rule.learning_reinforce, overlapping=overlapping)
    )
    if rule.communication_if_talkative and (sign_themes & TALKATIVE_THEMES):
        communication_parts.append(rule.communication_if_talkative)
    else:
        communication_parts.append(
            _pick_text(
                base=rule.communication,
                reinforce=rule.communication_reinforce,
                overlapping=overlapping,
            )
        )
    _extend_labels(strengths, rule.strengths)
    _extend_labels(risks, rule.risks)


def _major_dispositor_text(
    rule: DispositorFunctionRule,
    state: str,
    overlapping: bool,
) -> str:
    if overlapping and state == "supported":
        return rule.supported
    if overlapping and state == "pressured":
        return rule.pressured
    base = rule.routing_reinforce if overlapping else rule.routing
    extra = {
        "supported": "" if overlapping else rule.supported,
        "pressured": "" if overlapping else rule.pressured,
        "mixed": rule.mixed,
        "neutral": "",
    }[state]
    return _join_unique_parts(base, extra)


def _minor_dispositor_text(rule: DispositorFunctionRule, state: str) -> str:
    if state == "pressured" and rule.minor_pressured:
        return rule.minor_pressured
    if state == "supported" and rule.minor_supported:
        return rule.minor_supported
    if state == "mixed" and rule.minor_mixed:
        return rule.minor_mixed
    return rule.minor_routing


def _apply_dispositor_function(
    *,
    planet_name: Optional[str],
    aspects: Optional[Iterable[PlanetAspect | dict]],
    sign_themes: frozenset[str],
    role: str,
    thinking_parts: list[str],
    learning_parts: list[str],
    communication_parts: list[str],
    team_value_parts: list[str],
    strengths: list[str],
    risks: list[str],
) -> None:
    if not planet_name or planet_name == "Mercury":
        return
    rule = DISPOSITOR_FUNCTION_RULES.get(planet_name)
    if not rule:
        return
    state = effective_dispositor_condition_state(aspects)
    overlapping = bool(sign_themes & rule.themes)

    if role == "minor":
        thinking_parts.append(_minor_dispositor_text(rule, state))
        if state == "pressured":
            _extend_labels(risks, rule.risks[:1])
        return

    thinking_parts.append(_major_dispositor_text(rule, state, overlapping))
    if rule.learning and not overlapping:
        learning_parts.append(rule.learning)
    if rule.communication and not overlapping:
        communication_parts.append(rule.communication)
    if rule.team_value and not overlapping:
        team_value_parts.append(rule.team_value)
    _extend_labels(strengths, rule.strengths)
    _extend_labels(risks, rule.risks)


def _normalize_aspects(
    aspects: Optional[Iterable[MercuryAspect | dict]],
) -> list[tuple[str, str]]:
    normalized: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in aspects or []:
        if isinstance(item, MercuryAspect):
            planet, aspect_type = item.planet, item.type
        else:
            planet, aspect_type = item.get("planet"), item.get("type")
        if not planet or not aspect_type:
            continue
        key = (planet, aspect_type)
        if key in seen:
            continue
        seen.add(key)
        normalized.append(key)
    return normalized


def synthesize_mercury_narrative(
    *,
    mercury_sign: Optional[str],
    mercury_element: Optional[str],
    mercury_motion: Optional[str],
    mercury_house: Optional[int] = None,
    aspects: Optional[Iterable[MercuryAspect | dict]] = None,
    major_dispositor: Optional[str] = None,
    minor_dispositor: Optional[str] = None,
    major_dispositor_aspects: Optional[Iterable[PlanetAspect | dict]] = None,
    minor_dispositor_aspects: Optional[Iterable[PlanetAspect | dict]] = None,
) -> MercuryNarrative:
    """
    element → sign → retrograde → house → Mercury aspects → dispositor function → dedupe.

    Dispositor sign and house are not interpreted.
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
    sign_themes = SIGN_THEMES.get(mercury_sign, frozenset())

    thinking_parts: list[str] = []
    communication_parts: list[str] = []
    if element_rule:
        thinking_parts.append(f"{element_rule.thinking_type}. {element_rule.thinking}")
        communication_parts.append(element_rule.communication)
    thinking_parts.append(sign_rule.thinking)
    communication_parts.append(sign_rule.communication)

    learning_parts = [sign_rule.learning]
    team_value_parts = [sign_rule.team_value]
    strengths = list(sign_rule.strengths)
    risks = list(sign_rule.risks)

    if mercury_motion == "retrograde":
        thinking_parts.append(RETROGRADE_RULE.thinking)
        learning_parts.append(RETROGRADE_RULE.learning)
        communication_parts.append(RETROGRADE_RULE.communication)
        _extend_labels(strengths, RETROGRADE_RULE.strengths)
        _extend_labels(risks, RETROGRADE_RULE.risks)

    if mercury_house is not None:
        _apply_house(
            house=mercury_house,
            sign_themes=sign_themes,
            thinking_parts=thinking_parts,
            learning_parts=learning_parts,
            communication_parts=communication_parts,
            team_value_parts=team_value_parts,
            strengths=strengths,
            risks=risks,
        )

    by_planet = {planet: aspect_type for planet, aspect_type in _normalize_aspects(aspects)}
    for planet in ASPECT_APPLY_ORDER:
        aspect_type = by_planet.get(planet)
        if not aspect_type:
            continue
        rule = get_aspect_rule(planet, aspect_type)
        if not rule:
            continue
        _apply_aspect(
            rule=rule,
            sign_themes=sign_themes,
            thinking_parts=thinking_parts,
            learning_parts=learning_parts,
            communication_parts=communication_parts,
            strengths=strengths,
            risks=risks,
        )

    _apply_dispositor_function(
        planet_name=major_dispositor,
        aspects=major_dispositor_aspects,
        sign_themes=sign_themes,
        role="major",
        thinking_parts=thinking_parts,
        learning_parts=learning_parts,
        communication_parts=communication_parts,
        team_value_parts=team_value_parts,
        strengths=strengths,
        risks=risks,
    )
    _apply_dispositor_function(
        planet_name=minor_dispositor,
        aspects=minor_dispositor_aspects,
        sign_themes=sign_themes,
        role="minor",
        thinking_parts=thinking_parts,
        learning_parts=learning_parts,
        communication_parts=communication_parts,
        team_value_parts=team_value_parts,
        strengths=strengths,
        risks=risks,
    )

    return MercuryNarrative(
        thinking=_join_unique_parts(*thinking_parts),
        learning=_join_unique_parts(*learning_parts),
        communication=_join_unique_parts(*communication_parts),
        strengths=_dedupe_keep_order(strengths),
        risks=_dedupe_keep_order(risks),
        team_value=_join_unique_parts(*team_value_parts),
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
        mercury_house=source_factors.mercury_house if source_factors.birth_time_known else None,
        aspects=source_factors.aspects,
        major_dispositor=source_factors.major_dispositor,
        minor_dispositor=source_factors.minor_dispositor,
        major_dispositor_aspects=source_factors.major_dispositor_aspects,
        minor_dispositor_aspects=source_factors.minor_dispositor_aspects,
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
