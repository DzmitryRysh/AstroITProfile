"""Recruiter View v1 — presentation layer over existing Mercury synthesis.

Does not add astrology rules. Compresses/translates engine output only.
"""

from __future__ import annotations

import re
from typing import Optional, Protocol

from app.schemas.mercury_work_profile import RecruiterView
from app.services.mercury_rules import ELEMENT_RULES, LABEL_THEME, SIGN_RULES


class _NarrativeLike(Protocol):
    thinking: str
    learning: str
    communication: str
    strengths: list[str]
    risks: list[str]
    team_value: str
    possible_roles: list[str]


def _dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


# Compressions of existing SIGN_RULES.thinking — not a second astrology system.
RECRUITER_THINKING_STYLE: dict[str, str] = {
    "Aries": (
        "Fast, action-oriented thinker who reaches conclusions quickly and "
        "naturally challenges weak logic."
    ),
    "Taurus": (
        "Deliberate, practical thinker who verifies facts, retains material well, "
        "and needs more time for abstract material."
    ),
    "Gemini": (
        "Fast information processor who thinks through connections, dialogue "
        "and multiple information streams."
    ),
    "Cancer": (
        "Contextual, associative thinker who connects ideas with past experience "
        "and may find intuitive conclusions hard to verbalize."
    ),
    "Leo": (
        "Presentation-oriented thinker who reshapes information into a personal "
        "form and pays attention to audience effect."
    ),
    "Virgo": (
        "Analytical, detail-focused thinker who works best through structure, "
        "verification and precise examination."
    ),
    "Libra": (
        "Comparative thinker who sees several sides, synthesizes viewpoints, "
        "and evaluates ideas for balance and completeness."
    ),
    "Scorpio": (
        "Deep investigative thinker who looks beneath the obvious answer and "
        "searches for root causes."
    ),
    "Sagittarius": (
        "Big-picture conceptual thinker who looks for meaning, direction and "
        "the larger framework before details."
    ),
    "Capricorn": (
        "Structured, logical thinker who prefers one task at a time and looks "
        "for the core principle before expanding."
    ),
    "Aquarius": (
        "Independent, abstract thinker who explores many alternatives quickly "
        "and draws knowledge across domains."
    ),
    "Pisces": (
        "Imaginative, non-linear thinker who works through impressions, "
        "associations and hidden meaning more than isolated facts."
    ),
}

# Team-function labels compressed from existing SIGN_RULES.team_value.
RECRUITER_TEAM_FUNCTION: dict[str, str] = {
    "Aries": "Challenger / Rapid Problem Solver",
    "Taurus": "Grounder / Verifier",
    "Gemini": "Connector / Communicator",
    "Cancer": "Context Keeper",
    "Leo": "Presenter / Idea Advocate",
    "Virgo": "Precision Analyst / Validator",
    "Libra": "Mediator / Integrator",
    "Scorpio": "Investigator / Root-Cause Analyst",
    "Sagittarius": "Conceptualizer / Explorer",
    "Capricorn": "Structurer / Planner",
    "Aquarius": "Explorer / Innovator",
    "Pisces": "Creative Reframer",
}

# Sign communication identity — compressed from SIGN_RULES.communication.
RECRUITER_COMMUNICATION_BASE: dict[str, str] = {
    "Aries": "Communicates directly and quickly.",
    "Taurus": (
        "Communicates in a measured, structured way and prefers conversation "
        "that leads to a useful result."
    ),
    "Gemini": (
        "Communicates quickly, explains ideas clearly, and connects information "
        "across people and topics."
    ),
    "Cancer": (
        "Communicates with attention to atmosphere and context, and may find "
        "intuitive conclusions hard to put into words."
    ),
    "Leo": (
        "Communicates expressively and presentation-first, reshaping information "
        "into a memorable personal form."
    ),
    "Virgo": (
        "Communicates with precise, practical formulations and asks for clarification."
    ),
    "Libra": (
        "Communicates diplomatically, adapts to the other person, and looks for "
        "fair, balanced agreement."
    ),
    "Scorpio": (
        "Communicates in a probing, intense way, asking questions that go beneath "
        "the surface answer."
    ),
    "Sagittarius": (
        "Communicates conceptually and from the top down, often in a teaching-oriented way."
    ),
    "Capricorn": (
        "Communicates formally, concisely, and without rush, based on verified information."
    ),
    "Aquarius": (
        "Communicates informally and can speak across many topics, with a less predictable rhythm."
    ),
    "Pisces": (
        "Communicates through images, metaphor, and subtext more than a single hard line."
    ),
}

# Inherent sign friction shown only when no stronger external modifier is present.
RECRUITER_COMMUNICATION_FRICTION: dict[str, str] = {
    "Aries": (
        "Discussion can turn into debate, and listening may drop when a position "
        "is already being defended."
    ),
    "Leo": "Impression can outrun precision, and competing views may not be fully heard.",
    "Sagittarius": "The style can sound more like a lecture than a dialogue.",
    "Scorpio": "Answers can become sharp when the drive is to get beneath the surface.",
}

# Highest-priority first. Keywords come from existing house/aspect/Rx communication text.
_COMM_MODIFIERS: tuple[tuple[tuple[str, ...], str], ...] = (
    (
        ("guarded", "self-censor", "self-censored", "blocked", "inhibit speech"),
        ", but external expression may become more guarded or self-censored under pressure.",
    ),
    (
        (
            "under pressure",
            "listening can drop further",
            "interrupting or arguing",
            "wording can become sharper",
            "wording can get sharper",
        ),
        (
            "; under pressure this can become more interruptive, argumentative, "
            "or insufficiently attentive to counterarguments."
        ),
    ),
    (
        ("probing hidden", "verbal influence", "wording may become sharp", "probing communication"),
        "In deeper investigative discussions, expression can become more probing or sharp.",
    ),
    (
        ("written expression", "internal processing before speaking"),
        "Written expression may be easier than spontaneous speech, so time to process before speaking helps.",
    ),
    (
        ("spontaneous public expression", "stay private too long", "ideas may stay private"),
        "Spontaneous public expression can be harder, and useful ideas may stay private too long.",
    ),
    (
        ("run long", "lose the core message", "lose the core"),
        "Explanation can run long and lose the core message.",
    ),
    (
        ("larger argument", "not only local detail"),
        "Discussion often wants the larger argument, not only local detail.",
    ),
    (
        ("tact", "diplomatic expression", "diplomatically confident"),
        "Tact and socially smoother expression come more easily.",
    ),
    (
        ("approval", "risk offence", "say no"),
        "Attention to approval can make it harder to say no or risk offence.",
    ),
    (
        ("one-to-one", "more argumentative", "conflict-prone exchange"),
        "In one-to-one exchange the style can become more argumentative.",
    ),
)

RECRUITER_TEAM_CONTRIBUTION_BASE: dict[str, str] = {
    "Aries": (
        "Brings fast challenge, direct feedback, and a willingness to attack weak logic."
    ),
    "Taurus": "Brings grounding, verification, consistency, and practical judgment.",
    "Gemini": "Connects people, information, and different technical contexts.",
    "Cancer": (
        "Brings memory, context, and a sense of how information connects with prior experience."
    ),
    "Leo": "Helps present and champion an idea and give information a memorable form.",
    "Virgo": "Brings accuracy, error-spotting, data-quality focus, and methodical examination.",
    "Libra": "Helps reconcile people, departments, or viewpoints that need to be integrated.",
    "Scorpio": (
        "Stays with non-obvious problems, finds vulnerabilities, and works toward root causes."
    ),
    "Sagittarius": (
        "Frames direction, explores ideas, and explains why a system or project matters."
    ),
    "Capricorn": "Brings structure, sequence, planning, and disciplined technical reasoning.",
    "Aquarius": (
        "Surfaces alternatives, experimental approaches, and unconventional technical options."
    ),
    "Pisces": "Brings imaginative reframing, intuitive connections, and sensitivity to subtle information.",
}

_TEAM_EXTRA_CLAUSES: tuple[tuple[tuple[str, ...], str], ...] = (
    (
        ("theory", "knowledge synthesis", "conceptual framing"),
        "especially in work that also requires conceptual framing and knowledge synthesis",
    ),
    (
        ("complex or non-obvious", "stay with complex"),
        "especially in work that also requires staying with complex or non-obvious information",
    ),
    (
        ("initiative", "fast, visible verbal"),
        "especially where initiative and a fast verbal response are needed",
    ),
    (
        ("practically usable", "practical value"),
        "especially where analysis needs to become practically usable",
    ),
    (
        ("high-contact", "short-cycle"),
        "especially in high-contact, short-cycle information exchange",
    ),
    (
        ("private, focused", "context-heavy", "always-on visibility"),
        "especially in private, focused, or context-heavy settings",
    ),
    (
        ("engaging or publicly", "publicly explainable"),
        "especially where ideas need to be engaging or publicly explainable",
    ),
    (
        ("methodically under workload", "handled methodically"),
        "especially where information must be handled methodically under workload",
    ),
    (
        ("dialogue, feedback", "negotiated clarity"),
        "especially where work depends on dialogue, feedback, and negotiated clarity",
    ),
    (
        ("professional visibility", "sit close to professional"),
        "especially where knowledge and communication sit close to professional visibility",
    ),
    (
        ("collaborative, network", "idea-exchange"),
        "especially in collaborative or idea-exchange settings",
    ),
    (
        ("internal processing and private", "immediate public speech"),
        "especially through internal processing and private deep work rather than immediate public speech",
    ),
    (
        ("expanded, given meaning", "transferred"),
        "especially where information needs to be expanded, given meaning, or transferred",
    ),
)

_THINKING_QUALIFIERS: tuple[tuple[tuple[str, ...], str], ...] = (
    (
        ("deep investigation", "hidden dependencies", "complex information", "keep digging"),
        "especially when information is complex or not obvious",
    ),
    (
        ("immediate response under pressure", "intensify haste"),
        "under pressure the drive to answer immediately can intensify haste",
    ),
    (
        ("more inward", "revisit and rethink"),
        "processing may turn more inward and revisit material before settling",
    ),
)

_TEAM_LEAD_IN = re.compile(
    r"^(?:"
    r"Potential [^.]+?\.\s*"
    r"|Can be useful where the team needs\s+"
    r"|Can be useful where\s+"
    r"|Useful where the team needs someone willing to\s+"
    r"|Useful where the team needs\s+"
    r"|Useful where\s+"
    r"|Useful for\s+"
    r"|Useful in\s+"
    r"|Can help where\s+"
    r"|Can bring\s+"
    r"|Can contribute\s+"
    r"|Contributes more through\s+"
    r"|Contributes more in\s+"
    r")",
    re.IGNORECASE,
)

# Learning-method keywords → practical instruction. Search learning text only.
_ONBOARDING_FROM_LEARNING: tuple[tuple[tuple[str, ...], str], ...] = (
    (
        ("debate", "competition", "proving a position"),
        "Use challenge and discussion rather than passive instruction.",
    ),
    (
        ("hands-on practice that applies", "applies knowledge immediately", "immediate application"),
        "Give a concrete problem early.",
    ),
    (
        ("dialogue", "lectures", "groups", "exchanging information", "exchange of opinions"),
        "Explain the overall topic, then allow questions and discussion.",
    ),
    (
        ("books", "lectures"),
        "Provide written material for rapid independent exploration.",
    ),
    (
        ("groups", "collaborative", "several people", "another person"),
        "Use collaborative learning and knowledge exchange.",
    ),
    (
        ("notes", "algorithms", "diagrams", "tables", "methodologies"),
        "Provide structured documentation and clear procedures.",
    ),
    (
        ("diagrams", "tables", "algorithms", "indicators"),
        "Use examples, checklists, diagrams and measurable criteria.",
    ),
    (
        ("compiling and comparing", "comparing information"),
        "Allow hands-on verification.",
    ),
    (
        ("hands-on", "practical application", "practical exploration"),
        "Allow hands-on practice quickly.",
    ),
    (
        ("enough time", "absorb material", "one task", "one thought"),
        "Allow enough time to absorb material before switching context.",
    ),
    (
        ("independent preparation", "independent study", "solitude"),
        "Offer independent study time in a quieter setting.",
    ),
    (
        ("clear practical benefit", "purpose and sequence", "why the knowledge", "having a clear goal"),
        "State the practical purpose and sequence of the material up front.",
    ),
    (
        ("systems", "schedules", "plans", "structure", "sequence"),
        "Present work as a clear sequence, plan or system.",
    ),
    (
        ("presenting", "vivid", "engaging delivery", "creatively reworking"),
        "Let them learn by presenting or creatively reworking the material.",
    ),
    (
        ("passing knowledge", "teaching"),
        "Ask them to explain the material back or teach a piece to others.",
    ),
    (
        ("deep investigation", "quiet environment", "vulnerabilities", "deep concepts"),
        "Allow focused investigation time rather than only surface walkthroughs.",
    ),
    (
        ("video", "images", "intuitive impression", "creative reinterpretation"),
        "Use visual examples and space for creative reinterpretation.",
    ),
    (
        ("broader frameworks", "why the knowledge matters"),
        "Connect new material to a larger framework and why it matters.",
    ),
)

_ONBOARDING_FROM_LEARNING_OR_RISKS: tuple[tuple[tuple[str, ...], str], ...] = (
    (
        ("fact verification", "weak fact verification", "verify information", "written facts"),
        "Ask for fact-checking before immediate execution.",
    ),
    (
        ("many information streams", "information streams", "scattered attention", "too many parallel"),
        "Keep priorities explicit when many information streams are present.",
    ),
    (
        ("losing the big picture", "lost inside details", "strategy may be lost"),
        "Explain the larger objective so detail work stays connected to the goal.",
    ),
    (
        ("fear of error", "replaying mistakes"),
        "Treat early mistakes as review material, not a performance test.",
    ),
)

_ONBOARDING_FROM_RETROGRADE: tuple[tuple[tuple[str, ...], str], ...] = (
    (
        ("revisiting", "repetition", "reprocessing", "rewriting", "own words"),
        "Allow time to revisit material in writing, and do not demand an instant verbal response.",
    ),
)


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", (text or "").strip())
    return [p.strip() for p in parts if p.strip()]


def _normalize_sentence(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().rstrip(".!?")).lower()


def _extra_sentences(full_text: str, *baseline_texts: str) -> list[str]:
    baseline = {
        _normalize_sentence(sentence)
        for text in baseline_texts
        for sentence in _split_sentences(text or "")
        if _normalize_sentence(sentence)
    }
    extras: list[str] = []
    for sentence in _split_sentences(full_text or ""):
        key = _normalize_sentence(sentence)
        if key and key not in baseline:
            extras.append(sentence)
    return extras


def _first_matching_clause(
    source: str,
    mapping: tuple[tuple[tuple[str, ...], str], ...],
) -> Optional[str]:
    lower = source.lower()
    for keywords, clause in mapping:
        if any(keyword in lower for keyword in keywords):
            return clause
    return None


def _element_baselines(field: str) -> list[str]:
    return [getattr(rule, field) for rule in ELEMENT_RULES.values()]


def _join_base_and_modifier(base: str, modifier: str) -> str:
    base = base.rstrip()
    if modifier.startswith((",", ";", ":")):
        return f"{base.rstrip('.')}{modifier}"
    return f"{base} {modifier}"


def _join_trailing_clause(base: str, clause: str) -> str:
    clause = clause.strip().rstrip(".")
    if clause.lower().startswith(("especially", "under", "processing", "with ")):
        return f"{base.rstrip('.')}, {clause}."
    return f"{base.rstrip('.')} {clause}."


def _thinking_style(sign: str, thinking: str) -> str:
    base = RECRUITER_THINKING_STYLE[sign]
    extras = _extra_sentences(
        thinking,
        SIGN_RULES[sign].thinking,
        *_element_baselines("thinking"),
    )
    if not extras:
        return base
    qualifier = _first_matching_clause(" ".join(extras), _THINKING_QUALIFIERS)
    if not qualifier:
        return base
    return _join_trailing_clause(base, qualifier)


def _communication_style(sign: str, communication: str) -> str:
    base = RECRUITER_COMMUNICATION_BASE[sign]
    extras = _extra_sentences(
        communication,
        SIGN_RULES[sign].communication,
        *_element_baselines("communication"),
    )
    modifier = _first_matching_clause(" ".join(extras), _COMM_MODIFIERS) if extras else None
    if modifier:
        return _join_base_and_modifier(base, modifier)
    friction = RECRUITER_COMMUNICATION_FRICTION.get(sign)
    if friction:
        return f"{base} {friction}"
    return base


def _strip_team_lead_in(sentence: str) -> str:
    text = (sentence or "").strip()
    text = re.sub(r"^Potential [^.]+?\.\s*", "", text)
    text = _TEAM_LEAD_IN.sub("", text).strip()
    return text.rstrip(".")


def _synthesize_team_contribution(sign: str, team_value: str) -> str:
    base = RECRUITER_TEAM_CONTRIBUTION_BASE[sign]
    extras = _extra_sentences(team_value, SIGN_RULES[sign].team_value)
    if not extras:
        return base
    extra_source = " ".join(extras)
    clause = _first_matching_clause(extra_source, _TEAM_EXTRA_CLAUSES)
    if not clause:
        stripped = _strip_team_lead_in(extras[0])
        if not stripped or _normalize_sentence(stripped) in _normalize_sentence(base):
            return base
        clause = f"especially in work that also requires {stripped[0].lower() + stripped[1:]}"
    if _normalize_sentence(clause) in _normalize_sentence(base):
        return base
    return _join_trailing_clause(base, clause)


def _label_theme(label: str) -> Optional[str]:
    return LABEL_THEME.get(label)


def _distinct_modifier_labels(ordered: list[str], base_set: set[str]) -> list[str]:
    base_themes = {_label_theme(item) for item in base_set if _label_theme(item)}
    distinct: list[str] = []
    seen_themes: set[str] = set()
    for item in ordered:
        if item in base_set:
            continue
        theme = _label_theme(item)
        if theme and (theme in base_themes or theme in seen_themes):
            continue
        if theme:
            seen_themes.add(theme)
        distinct.append(item)
    return distinct


def _select_presented_labels(
    items: list[str],
    *,
    base_items: tuple[str, ...] | list[str],
    limit: int,
    modifier_slots: int = 1,
) -> list[str]:
    """Keep base identity dominant; reserve slots for distinct synthesis modifiers."""
    ordered = _dedupe_keep_order(list(items))
    base_set = set(base_items)
    base_ordered = [item for item in ordered if item in base_set]
    modifiers = _distinct_modifier_labels(ordered, base_set)

    reserve = min(max(modifier_slots, 0), len(modifiers), max(limit - 1, 0))
    base_limit = limit - reserve

    selected: list[str] = []
    seen_themes: set[str] = set()

    def _take(candidates: list[str], remaining: int) -> None:
        for item in candidates:
            if remaining is not None and len(selected) >= remaining:
                return
            if item in selected:
                continue
            theme = _label_theme(item)
            if theme and theme in seen_themes:
                continue
            if theme:
                seen_themes.add(theme)
            selected.append(item)
            if len(selected) >= limit:
                return

    _take(base_ordered, base_limit)
    _take(modifiers, limit)
    if len(selected) < limit:
        _take(base_ordered, limit)
    return selected[:limit]


def _match_onboarding(
    source: str,
    triggers: tuple[tuple[tuple[str, ...], str], ...],
) -> list[str]:
    matched: list[str] = []
    for keywords, instruction in triggers:
        if any(keyword in source for keyword in keywords) and instruction not in matched:
            matched.append(instruction)
    return matched


def _polish_onboarding(items: list[str]) -> list[str]:
    merged: list[str] = []
    skip_practice = False
    concrete = "Give a concrete problem early."
    practice = "Allow hands-on practice quickly."
    combined = "Give a concrete problem early and allow hands-on practice quickly."
    if concrete in items and practice in items:
        skip_practice = True
    for item in items:
        if skip_practice and item == concrete:
            merged.append(combined)
            continue
        if skip_practice and item == practice:
            continue
        if item not in merged:
            merged.append(item)
    return merged


def _onboarding_guidance(learning: str, risks: list[str]) -> list[str]:
    learning_text = (learning or "").lower()
    combined = f"{learning_text} {' '.join(risks)}".lower()
    from_learning = _match_onboarding(learning_text, _ONBOARDING_FROM_LEARNING)
    from_friction = _match_onboarding(combined, _ONBOARDING_FROM_LEARNING_OR_RISKS)
    from_rx = _match_onboarding(combined, _ONBOARDING_FROM_RETROGRADE)

    guidance = _polish_onboarding(
        [item for item in from_learning + from_friction if item]
    )[:4]
    if from_rx:
        rx_item = from_rx[0]
        if rx_item not in guidance and len(guidance) < 5:
            guidance.append(rx_item)
    return guidance[:5]


def build_recruiter_view(
    *,
    mercury_sign: Optional[str],
    narrative: _NarrativeLike,
) -> Optional[RecruiterView]:
    if not mercury_sign or mercury_sign not in SIGN_RULES or not narrative.thinking:
        return None

    team_function = RECRUITER_TEAM_FUNCTION[mercury_sign]
    view = RecruiterView(
        thinking_style=_thinking_style(mercury_sign, narrative.thinking),
        top_skills=_select_presented_labels(
            narrative.strengths,
            base_items=SIGN_RULES[mercury_sign].strengths,
            limit=5,
        ),
        key_risks=_select_presented_labels(
            narrative.risks,
            base_items=SIGN_RULES[mercury_sign].risks,
            limit=4,
        ),
        team_function=team_function,
        team_contribution=_synthesize_team_contribution(mercury_sign, narrative.team_value),
        communication_style=_communication_style(mercury_sign, narrative.communication),
        onboarding_guidance=_onboarding_guidance(narrative.learning, narrative.risks),
        role_directions=_dedupe_keep_order(list(narrative.possible_roles))[:5],
    )
    return view
