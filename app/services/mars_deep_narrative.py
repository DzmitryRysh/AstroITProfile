"""Mars Deep Profile narrative (M10.5 Phase 2B/C) — deterministic human synthesis.

Uses only narrative-eligible Mars facts, approved tags, and ADD/REINFORCE
relations. Does not invent astrology, import Mercury copy, or call an LLM.
"""

from __future__ import annotations

from collections import Counter

from app.schemas.mars_source_profile import (
    DeepMarsAdditiveTheme,
    DeepMarsAspectBlock,
    DeepMarsFactorBlock,
    DeepMarsFactorNarrative,
    DeepMarsIntegratedTakeaway,
    DeepMarsNarrativeSubsection,
    DeepMarsReinforcingSignal,
    MarsSourceFact,
    MarsSourceProfileResponse,
)

# Mars-owned human phrases (not Mercury imports).
TAG_PHRASE: dict[str, str] = {
    "planned_execution": "planning before acting",
    "strategic_action": "strategic action with attention to tactics",
    "task_concentration": "strong task focus",
    "fast_start": "quick mobilization",
    "self_starting": "independent initiation",
    "needs_support_to_start": "needing support to get started",
    "hands_on_execution": "direct, hands-on execution",
    "routine_execution": "routine execution",
    "independent_execution": "independent execution",
    "action_hesitation": "hesitation before committing to action",
    "action_inhibition": "holding action back internally",
    "suppressed_will": "suppressed will under tension",
    "effort_overload": "pushing effort beyond a sustainable level",
    "crisis_execution": "strong mobilization in crisis conditions",
    "crisis_activation": "activation under crisis pressure",
    "difficult_task_tolerance": "tolerance for difficult tasks",
    "competitive_drive": "competitive drive in action",
    "workplace_conflict": "workplace conflict pressure",
    "task_scatter": "attention scattering across tasks",
    "activity_bursts": "activity in bursts",
    "redo_cycle": "repeated redo and rework cycles",
    "push_pull_action": "push-pull swings in how action is expressed",
    "mood_dependent_action": "mood-dependent mobilization",
    "completion_difficulty": "difficulty sustaining or completing action",
    "leadership_action": "leadership action in group contexts",
}

TAG_LABEL: dict[str, str] = {
    "planned_execution": "Planned execution",
    "strategic_action": "Strategic action",
    "task_concentration": "Task concentration",
    "fast_start": "Fast start",
    "self_starting": "Self-starting",
    "needs_support_to_start": "Needs support to start",
    "hands_on_execution": "Hands-on execution",
    "routine_execution": "Routine execution",
    "independent_execution": "Independent execution",
    "action_hesitation": "Action hesitation",
    "action_inhibition": "Action inhibition",
    "suppressed_will": "Suppressed will",
    "effort_overload": "Effort overload",
    "crisis_execution": "Crisis execution",
    "crisis_activation": "Crisis activation",
    "difficult_task_tolerance": "Difficult-task tolerance",
    "competitive_drive": "Competitive drive",
    "workplace_conflict": "Workplace conflict",
    "task_scatter": "Task scatter",
    "activity_bursts": "Activity bursts",
    "redo_cycle": "Redo cycle",
    "push_pull_action": "Push-pull action",
    "mood_dependent_action": "Mood-dependent action",
    "completion_difficulty": "Completion difficulty",
    "leadership_action": "Leadership action",
}

# Themes that read as capability / constructive execution character.
BASE_STRENGTH_TAGS = frozenset(
    {
        "planned_execution",
        "strategic_action",
        "task_concentration",
        "fast_start",
        "self_starting",
        "hands_on_execution",
        "routine_execution",
        "independent_execution",
        "difficult_task_tolerance",
        "competitive_drive",
        "crisis_execution",
        "crisis_activation",
        "leadership_action",
    }
)

# Themes that complicate continuation / mobilization.
ACTION_PRESSURE_TAGS = frozenset(
    {
        "effort_overload",
        "action_hesitation",
        "action_inhibition",
        "suppressed_will",
        "workplace_conflict",
        "task_scatter",
        "activity_bursts",
        "redo_cycle",
        "push_pull_action",
        "mood_dependent_action",
        "completion_difficulty",
        "needs_support_to_start",
    }
)

SUBSECTION_META: tuple[tuple[str, str, frozenset[str]], ...] = (
    ("start", "How you start", frozenset({"action_start", "initiative"})),
    (
        "execute",
        "How you execute",
        frozenset({"execution", "continuation", "effort"}),
    ),
    ("rhythm", "Effort and rhythm", frozenset({"work_rhythm"})),
    ("continuation", "Continuation", frozenset({"continuation"})),
    ("strengths", "Strengths", frozenset({"work_conditions"})),
    ("watchouts", "Watch-outs", frozenset({"watchout", "stuck_blocker", "conflict"})),
    (
        "work_context",
        "Work-context themes",
        frozenset({"professional_association", "obstacle"}),
    ),
)

ALWAYS_KEEP = frozenset({"watchouts", "work_context", "strengths"})
MAX_SUMMARY_TAGS = 3
MAX_SUBSECTION_TAGS = 3
MAX_INTEGRATED_TAKEAWAYS = 4
DEBUG_MARKERS = (
    "supported across",
    "carried by",
    "appears across",
    "sign:",
    "house:",
    "motion:",
    "aspect:",
    "among other themes",
)


def tag_phrase(tag: str) -> str:
    if tag in TAG_PHRASE:
        return TAG_PHRASE[tag]
    return tag.replace("_", " ")


def tag_label(tag: str) -> str:
    if tag in TAG_LABEL:
        return TAG_LABEL[tag]
    return " ".join(part.capitalize() for part in tag.split("_") if part)


def _join_human(parts: list[str]) -> str:
    clean = [item for item in parts if item]
    if not clean:
        return ""
    if len(clean) == 1:
        return clean[0]
    if len(clean) == 2:
        return f"{clean[0]} and {clean[1]}"
    return f"{', '.join(clean[:-1])}, and {clean[-1]}"


def _top_tags(facts: list[MarsSourceFact], limit: int) -> list[str]:
    counts: Counter = Counter()
    for fact in facts:
        for tag in fact.tags or ():
            if tag in TAG_PHRASE:
                counts[tag] += 1
    return [tag for tag, _ in counts.most_common(limit)]


def _facts_for_categories(
    facts: list[MarsSourceFact], categories: frozenset[str]
) -> list[MarsSourceFact]:
    return [fact for fact in facts if fact.category in categories]


def _support_for_tags(facts: list[MarsSourceFact], tags: list[str]) -> list[str]:
    wanted = set(tags)
    return sorted(
        {
            fact.id
            for fact in facts
            if wanted & set(fact.tags or ())
        }
    )


def _subsection_text(key: str, tags: list[str]) -> str:
    joined = _join_human([tag_phrase(tag) for tag in tags])
    if key == "start":
        return f"Starting style includes {joined}."
    if key == "execute":
        return f"Execution style includes {joined}."
    if key == "rhythm":
        return f"Effort and rhythm include {joined}."
    if key == "continuation":
        return f"Continuation patterns include {joined}."
    if key == "strengths":
        return f"Supportive work conditions include {joined}."
    if key == "watchouts":
        return f"Watch-outs include {joined}."
    if key == "work_context":
        return f"Work-context themes include {joined}."
    return f"This layer includes {joined}."


def _house_summary(factor_key: str, dominant: list[str]) -> str:
    strengths = [tag for tag in dominant if tag in BASE_STRENGTH_TAGS]
    pressures = [tag for tag in dominant if tag in ACTION_PRESSURE_TAGS]
    if strengths and pressures:
        return (
            f"House {factor_key} channels Mars into "
            f"{_join_human([tag_phrase(tag) for tag in strengths])}. "
            f"It can also increase the tendency toward "
            f"{_join_human([tag_phrase(tag) for tag in pressures])}."
        )
    if strengths:
        return (
            f"House {factor_key} channels Mars into "
            f"{_join_human([tag_phrase(tag) for tag in strengths])}."
        )
    return (
        f"House {factor_key} shapes how this Mars applies effort through "
        f"{_join_human([tag_phrase(tag) for tag in dominant])}."
    )


def _motion_summary(factor_key: str, dominant: list[str]) -> str:
    if factor_key == "retrograde":
        phrases = [tag_phrase(tag) for tag in dominant]
        if set(dominant) >= {"action_inhibition", "redo_cycle", "push_pull_action"}:
            return (
                "Retrograde Mars can hold action back internally, create "
                "repeated redo/rework cycles, and produce push-pull swings "
                "in how action is expressed."
            )
        if len(phrases) == 1:
            return f"Retrograde Mars can introduce {phrases[0]}."
        if len(phrases) == 2:
            return (
                f"Retrograde Mars can introduce {phrases[0]} and {phrases[1]}."
            )
        return (
            f"Retrograde Mars can hold action back internally, create "
            f"{phrases[1] if len(phrases) > 1 else 'redo cycles'}, and produce "
            f"{phrases[-1]}."
        )
    return (
        f"{factor_key.capitalize()} Mars relates to "
        f"{_join_human([tag_phrase(tag) for tag in dominant])}."
    )


def build_factor_narrative(
    *,
    factor_type: str,
    factor_key: str,
    title: str,
    eligible_facts: list[MarsSourceFact],
) -> DeepMarsFactorNarrative | None:
    """Build factor narrative from narrative-eligible facts only."""
    tagged = [
        fact
        for fact in eligible_facts
        if any(tag in TAG_PHRASE for tag in (fact.tags or ()))
    ]
    dominant = _top_tags(tagged or eligible_facts, MAX_SUMMARY_TAGS)
    if not dominant:
        return DeepMarsFactorNarrative(
            core_theme=title,
            summary=(
                f"{title} contributes to this Mars configuration. "
                f"See key observations for reviewed source detail."
            ),
            subsections=[],
            supporting_fact_ids=sorted({fact.id for fact in eligible_facts}),
            conditional_fact_ids=[],
        )

    theme_labels = [tag_label(tag) for tag in dominant[:2]]
    core_theme = _join_human(theme_labels)
    phrases = [tag_phrase(tag) for tag in dominant]
    consumed = set(dominant)

    if factor_type == "sign":
        summary = f"Mars in {factor_key} tends toward {_join_human(phrases)}."
    elif factor_type == "house":
        summary = _house_summary(factor_key, dominant)
    elif factor_type == "motion":
        summary = _motion_summary(factor_key, dominant)
    else:
        summary = f"This Mars factor centers on {_join_human(phrases)}."

    subsections: list[DeepMarsNarrativeSubsection] = []
    support: list[str] = _support_for_tags(eligible_facts, dominant)

    for key, heading, categories in SUBSECTION_META:
        bucket = _facts_for_categories(eligible_facts, categories)
        tags = _top_tags(bucket, MAX_SUBSECTION_TAGS)
        if not tags:
            continue
        fresh = (
            [tag for tag in tags if tag not in consumed]
            if key not in ALWAYS_KEEP
            else tags
        )
        if key not in ALWAYS_KEEP and not fresh:
            continue
        display = fresh if key not in ALWAYS_KEEP else tags
        if not display:
            continue
        sub_support = _support_for_tags(bucket, display) or [
            fact.id for fact in bucket
        ]
        subsections.append(
            DeepMarsNarrativeSubsection(
                key=key,
                title=heading,
                text=_subsection_text(key, display),
                supporting_fact_ids=sorted(set(sub_support)),
            )
        )
        support.extend(sub_support)
        if key not in ALWAYS_KEEP:
            consumed.update(display)

    return DeepMarsFactorNarrative(
        core_theme=core_theme,
        summary=summary,
        subsections=subsections,
        supporting_fact_ids=sorted(
            set(support) or {fact.id for fact in eligible_facts}
        ),
        conditional_fact_ids=[],
    )


def _aspect_label(aspect_type: str, planet: str) -> str:
    return f"{planet} {aspect_type}".strip()


def _add_sentence(aspect_type: str, planet: str, tags: set[str]) -> str | None:
    label = _aspect_label(aspect_type, planet)
    if "completion_difficulty" in tags:
        return (
            f"{label} can make it harder to sustain action through to completion."
        )
    if "mood_dependent_action" in tags:
        return (
            f"{label} can make mobilization more dependent on emotional state."
        )
    if tags & {"action_hesitation", "action_inhibition", "suppressed_will"}:
        return (
            f"{label} can increase hesitation or inhibition under pressure."
        )
    if tags & {"effort_overload", "crisis_execution", "crisis_activation"}:
        return f"{label} can intensify effort-overload pressure."
    if not tags:
        return None
    return f"{label} can intensify {_join_human([tag_phrase(tag) for tag in sorted(tags)[:2]])}."


def _reinforce_sentence(reinforcing: list[DeepMarsReinforcingSignal]) -> str | None:
    if not reinforcing:
        return None
    labels = []
    for item in reinforcing:
        raw = tag_label(item.tag).lower()
        labels.append("effort-overload" if raw == "effort overload" else raw)
    if len(labels) == 1:
        article = "an" if labels[0][0] in "aeiou" else "a"
        return (
            f"It also reinforces {article} {labels[0]} pattern already present "
            f"in the base Mars configuration."
        )
    return (
        f"It also reinforces {_join_human(labels)} patterns already present "
        f"in the base Mars configuration."
    )


def build_aspect_narrative_statement(
    *,
    aspect_type: str,
    planet: str,
    adds: list[DeepMarsAdditiveTheme],
    reinforcing: list[DeepMarsReinforcingSignal],
    source_interpretation_available: bool,
) -> str | None:
    if not source_interpretation_available:
        return (
            "Source interpretation for this Mars aspect is not currently available."
        )
    parts: list[str] = []
    add_tags = {item.tag for item in adds}
    add_sentence = _add_sentence(aspect_type, planet, add_tags)
    if add_sentence:
        parts.append(add_sentence)
    reinforce = _reinforce_sentence(reinforcing)
    if reinforce:
        parts.append(reinforce)
    if not parts:
        return None
    return " ".join(parts)


def enrich_adds(items: list[DeepMarsAdditiveTheme]) -> list[DeepMarsAdditiveTheme]:
    return [
        item.model_copy(update={"label": item.label or tag_label(item.tag)})
        for item in items
    ]


def enrich_reinforcing(
    items: list[DeepMarsReinforcingSignal],
) -> list[DeepMarsReinforcingSignal]:
    return [
        item.model_copy(update={"label": item.label or tag_label(item.tag)})
        for item in items
    ]


def _eligible_facts_for_block(
    block: DeepMarsFactorBlock,
    by_id: dict[str, MarsSourceFact],
) -> list[MarsSourceFact]:
    return [
        by_id[fid]
        for fid in block.narrative_eligible_fact_ids
        if fid in by_id
    ]


def _base_character_takeaway(
    sign: DeepMarsFactorBlock,
    facts: list[MarsSourceFact],
) -> DeepMarsIntegratedTakeaway | None:
    if sign.availability != "available" or not facts:
        return None
    tags = _top_tags(facts, MAX_SUMMARY_TAGS)
    strength = [tag for tag in tags if tag in BASE_STRENGTH_TAGS] or tags
    if not strength:
        return None
    support = _support_for_tags(facts, strength)
    if not support:
        return None
    phrases = [tag_phrase(tag) for tag in strength]
    text = f"Base Mars acts with {_join_human(phrases)}."
    return DeepMarsIntegratedTakeaway(
        key=f"base:{sign.factor_key}",
        basis="base_character",
        signal=strength[0],
        supporting_fact_ids=support,
        provenance_keys=[f"sign:{sign.factor_key}"],
        text=text,
    )


def _house_modifier_takeaway(
    house: DeepMarsFactorBlock,
    facts: list[MarsSourceFact],
) -> DeepMarsIntegratedTakeaway | None:
    if house.availability != "available" or not facts:
        return None
    tags = _top_tags(facts, MAX_SUMMARY_TAGS)
    if not tags:
        return None
    strengths = [tag for tag in tags if tag in BASE_STRENGTH_TAGS]
    pressures = [tag for tag in tags if tag in ACTION_PRESSURE_TAGS]
    used = (strengths + pressures) or tags
    support = _support_for_tags(facts, used)
    if not support:
        return None
    if strengths and pressures:
        text = (
            f"House {house.factor_key} adds "
            f"{_join_human([tag_phrase(tag) for tag in strengths])}, "
            f"while also creating a tendency toward "
            f"{_join_human([tag_phrase(tag) for tag in pressures])}."
        )
    elif strengths:
        text = (
            f"House {house.factor_key} adds "
            f"{_join_human([tag_phrase(tag) for tag in strengths])} "
            f"to how this Mars is applied."
        )
    else:
        text = (
            f"House {house.factor_key} modifies action through "
            f"{_join_human([tag_phrase(tag) for tag in used])}."
        )
    return DeepMarsIntegratedTakeaway(
        key=f"house:{house.factor_key}",
        basis="factor_modifier",
        signal=used[0],
        supporting_fact_ids=support,
        provenance_keys=[f"house:{house.factor_key}"],
        text=text,
    )


def _motion_modifier_takeaway(
    motion: DeepMarsFactorBlock,
    facts: list[MarsSourceFact],
) -> DeepMarsIntegratedTakeaway | None:
    if motion.availability != "available" or not facts:
        return None
    tags = _top_tags(facts, MAX_SUMMARY_TAGS)
    if not tags:
        return None
    support = _support_for_tags(facts, tags)
    if not support:
        return None
    if motion.factor_key == "retrograde":
        if set(tags) & {"action_inhibition", "redo_cycle", "push_pull_action", "action_hesitation"}:
            text = (
                "Retrograde motion adds inhibition, redo/rework cycles, "
                "and push-pull dynamics to action."
            )
        else:
            text = (
                "Retrograde motion modifies drive through "
                f"{_join_human([tag_phrase(tag) for tag in tags])}."
            )
    else:
        text = (
            f"{motion.factor_key.capitalize()} motion modifies drive through "
            f"{_join_human([tag_phrase(tag) for tag in tags])}."
        )
    return DeepMarsIntegratedTakeaway(
        key=f"motion:{motion.factor_key}",
        basis="factor_modifier",
        signal=tags[0],
        supporting_fact_ids=support,
        provenance_keys=[f"motion:{motion.factor_key}"],
        text=text,
    )


def _aspect_modifier_takeaway(
    aspect_blocks: list[DeepMarsAspectBlock],
) -> DeepMarsIntegratedTakeaway | None:
    active = [
        block
        for block in aspect_blocks
        if block.source_interpretation_available
        and (block.interaction.adds or block.interaction.reinforcing)
    ]
    if not active:
        return None

    add_tags: list[str] = []
    reinf_tags: list[str] = []
    support: list[str] = []
    planets: list[str] = []
    for block in active:
        planets.append(block.identity.planet)
        for item in block.interaction.adds:
            if item.tag not in add_tags:
                add_tags.append(item.tag)
            support.extend(item.aspect_fact_ids)
        for item in block.interaction.reinforcing:
            if item.tag not in reinf_tags:
                reinf_tags.append(item.tag)
            support.extend(item.aspect_fact_ids)
            support.extend(item.base_fact_ids)

    support = sorted(set(support))
    if not support:
        return None

    parts: list[str] = []
    actor = " and ".join(dict.fromkeys(planets))
    if "completion_difficulty" in add_tags and "mood_dependent_action" in add_tags:
        parts.append(
            f"{actor} aspect pressure can make completion harder and action "
            f"more mood-dependent"
        )
    elif "completion_difficulty" in add_tags:
        parts.append(
            f"{actor} aspect pressure can make it harder to sustain action "
            f"through to completion"
        )
    elif "mood_dependent_action" in add_tags:
        parts.append(
            f"{actor} aspect pressure can make mobilization more dependent "
            f"on emotional state"
        )
    elif add_tags:
        parts.append(
            f"{actor} aspect pressure can intensify "
            f"{_join_human([tag_phrase(tag) for tag in add_tags[:2]])}"
        )

    if "effort_overload" in reinf_tags:
        reinf_planets = [
            block.identity.planet
            for block in active
            if any(item.tag == "effort_overload" for item in block.interaction.reinforcing)
        ]
        actor_reinf = reinf_planets[0] if reinf_planets else "Aspect pressure"
        if parts:
            if actor_reinf != "Aspect pressure":
                parts[0] = (
                    parts[0]
                    + f"; {actor_reinf} also reinforces effort overload"
                )
            else:
                parts[0] = (
                    parts[0]
                    + "; aspect pressure also reinforces effort overload"
                )
        else:
            parts.append(
                "Aspect pressure reinforces an effort-overload pattern "
                "already present in the base Mars configuration"
            )
    elif reinf_tags and not parts:
        parts.append(
            "Aspect pressure reinforces "
            f"{_join_human([tag_phrase(tag) for tag in reinf_tags[:2]])} "
            "already present in the base Mars configuration"
        )

    if not parts:
        return None
    text = parts[0].rstrip(".") + "."
    signal = add_tags[0] if add_tags else reinf_tags[0]
    return DeepMarsIntegratedTakeaway(
        key="aspect:combined",
        basis="aspect_addition",
        signal=signal,
        supporting_fact_ids=support,
        provenance_keys=[block.provenance for block in active],
        text=text,
    )


def _repeated_signal_takeaway(
    profile: MarsSourceProfileResponse,
    covered_tags: set[str],
) -> DeepMarsIntegratedTakeaway | None:
    work_ids = {
        fact.id
        for fact in (
            list(profile.sign_facts)
            + list(profile.house_facts)
            + list(profile.motion_facts)
            + list(profile.aspect_facts)
        )
        if fact.activated
    }
    for signal in sorted(profile.repeated_signals, key=lambda item: item.signal):
        if signal.signal in covered_tags or signal.tag in covered_tags:
            continue
        types = {
            key.partition(":")[0] for key in signal.sources if ":" in key
        }
        if len(types) < 2:
            continue
        support = [fid for fid in signal.fact_ids if fid in work_ids]
        if not support:
            continue
        phrase = tag_phrase(signal.signal)
        if signal.signal == "effort_overload":
            text = (
                "Effort-overload pressure shows up as a recurring pattern "
                "across this Mars configuration."
            )
        else:
            text = f"This Mars shows {phrase} as a recurring action pattern."
        return DeepMarsIntegratedTakeaway(
            key=f"repeat:{signal.signal}",
            basis="repeated_signal",
            signal=signal.signal,
            supporting_fact_ids=support,
            provenance_keys=list(signal.sources),
            text=text,
        )
    return None


def build_integrated_mars_takeaways(
    *,
    profile: MarsSourceProfileResponse,
    sign: DeepMarsFactorBlock,
    house: DeepMarsFactorBlock,
    motion: DeepMarsFactorBlock,
    aspects: list[DeepMarsAspectBlock],
) -> list[DeepMarsIntegratedTakeaway]:
    """Priority-ordered Integrated Mars outcomes (max 3–4)."""
    by_id = _facts_by_id(profile)
    # Also map secondary-eligible facts already on profile work lists only.
    sign_facts = _eligible_facts_for_block(sign, by_id)
    house_facts = _eligible_facts_for_block(house, by_id)
    motion_facts = _eligible_facts_for_block(motion, by_id)

    selected: list[DeepMarsIntegratedTakeaway] = []
    covered: set[str] = set()

    def _accept(item: DeepMarsIntegratedTakeaway | None, extra_tags: set[str] | None = None) -> None:
        if item is None or len(selected) >= MAX_INTEGRATED_TAKEAWAYS:
            return
        selected.append(item)
        if item.signal:
            covered.add(item.signal)
        if extra_tags:
            covered.update(extra_tags)

    # A. Base execution character
    base = _base_character_takeaway(sign, sign_facts)
    base_tags = set(_top_tags(sign_facts, MAX_SUMMARY_TAGS)) if base else set()
    _accept(base, base_tags)

    # B. House / motion modifiers
    house_item = _house_modifier_takeaway(house, house_facts)
    house_tags = set(_top_tags(house_facts, MAX_SUMMARY_TAGS)) if house_item else set()
    _accept(house_item, house_tags)

    motion_item = _motion_modifier_takeaway(motion, motion_facts)
    motion_tags = set(_top_tags(motion_facts, MAX_SUMMARY_TAGS)) if motion_item else set()
    _accept(motion_item, motion_tags)

    # D. Aspect modification before C when both compete for the last slot,
    # so hard-aspect ADDs are not dropped behind a repeat already represented
    # in house/motion copy. Repeated fills remaining room afterward.
    if len(selected) < MAX_INTEGRATED_TAKEAWAYS:
        aspect_item = _aspect_modifier_takeaway(aspects)
        aspect_extra = set()
        if aspect_item:
            for block in aspects:
                for item in block.interaction.adds:
                    aspect_extra.add(item.tag)
                for item in block.interaction.reinforcing:
                    aspect_extra.add(item.tag)
        _accept(aspect_item, aspect_extra)

    # C. Cross-factor repeated pattern (skip tags already represented)
    if len(selected) < MAX_INTEGRATED_TAKEAWAYS:
        _accept(_repeated_signal_takeaway(profile, covered))

    return selected[:MAX_INTEGRATED_TAKEAWAYS]


def humanize_integrated_takeaway(
    item: DeepMarsIntegratedTakeaway,
) -> DeepMarsIntegratedTakeaway:
    """Ensure text is present; prefer already-authored outcome wording."""
    if item.text:
        lowered = item.text.lower()
        text = item.text
        for marker in DEBUG_MARKERS:
            if marker in lowered:
                text = text.replace(marker, "")
        return item.model_copy(update={"text": text.strip()})

    signal = item.signal or ""
    phrase = tag_phrase(signal) if signal else "this action theme"
    if item.basis == "base_character":
        text = f"Base Mars acts with {phrase}."
    elif item.basis == "factor_modifier":
        text = f"This Mars layer modifies action through {phrase}."
    elif item.basis == "repeated_signal":
        text = f"This Mars shows {phrase} as a recurring action pattern."
    else:
        text = (
            f"Aspect pressure can intensify {phrase} beyond the base "
            f"Mars pattern."
        )
    return item.model_copy(update={"text": text})


def _facts_by_id(profile: MarsSourceProfileResponse) -> dict[str, MarsSourceFact]:
    mapping: dict[str, MarsSourceFact] = {}
    for fact in (
        list(profile.sign_facts)
        + list(profile.house_facts)
        + list(profile.motion_facts)
        + list(profile.aspect_facts)
        + list(profile.conditional_unresolved)
    ):
        mapping[fact.id] = fact
    return mapping


def attach_mars_factor_narrative(
    block: DeepMarsFactorBlock,
    profile: MarsSourceProfileResponse,
) -> DeepMarsFactorBlock:
    if block.availability != "available":
        return block
    by_id = _facts_by_id(profile)
    eligible = _eligible_facts_for_block(block, by_id)
    narrative = build_factor_narrative(
        factor_type=block.factor_type,
        factor_key=block.factor_key,
        title=block.title,
        eligible_facts=eligible,
    )
    if narrative is None:
        return block
    return block.model_copy(update={"narrative": narrative})


def attach_mars_aspect_human_copy(
    block: DeepMarsAspectBlock,
) -> DeepMarsAspectBlock:
    source_available = bool(block.work_fact_ids)
    interaction = block.interaction
    adds = enrich_adds(list(interaction.adds)) if source_available else []
    reinforcing = (
        enrich_reinforcing(list(interaction.reinforcing)) if source_available else []
    )
    if not source_available:
        statement = (
            "Source interpretation for this Mars aspect is not currently available."
        )
        interaction_out = interaction.model_copy(
            update={
                "available": False,
                "adds": [],
                "reinforcing": [],
                "contrasting": [],
                "statement": statement,
                "supporting_fact_ids": [],
            }
        )
    else:
        statement = build_aspect_narrative_statement(
            aspect_type=block.identity.aspect_type,
            planet=block.identity.planet,
            adds=adds,
            reinforcing=reinforcing,
            source_interpretation_available=True,
        )
        interaction_out = interaction.model_copy(
            update={
                "adds": adds,
                "reinforcing": reinforcing,
                "statement": statement,
                "available": bool(adds or reinforcing),
            }
        )
    return block.model_copy(
        update={
            "source_interpretation_available": source_available,
            "interaction": interaction_out,
        }
    )


def attach_mars_integrated_human_copy(
    items: list[DeepMarsIntegratedTakeaway],
) -> list[DeepMarsIntegratedTakeaway]:
    return [humanize_integrated_takeaway(item) for item in items]
