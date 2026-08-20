"""Deterministic HOW YOU WORK glance cards.

Presentation-only. Selects and optionally templates existing synthesis
evidence. Does not add tags, rewrite source facts, or score people.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.services.mars_profile_synthesis import MarsProfileSynthesis
from app.services.mars_source_profile import MarsSourceFact
from app.services.person_perspective import (
    PersonPerspective,
    contextualize_neutral_sentence,
    fill_person_template,
    mars_glance_title,
)

GLANCE_EXECUTION = "execution_style"
GLANCE_SLOWDOWN = "what_may_slow_you_down"
GLANCE_PRESSURE = "under_pressure"

EXECUTION_CATEGORIES = frozenset({"execution", "continuation", "work_rhythm", "effort"})
PRESSURE_TAGS = frozenset({"effort_overload", "crisis_execution", "crisis_activation"})


@dataclass(frozen=True)
class MarsGlanceTemplate:
    required_tags: frozenset[str]
    text: str
    display_template: str
    required_repeats: frozenset[str] = frozenset()


@dataclass(frozen=True)
class MarsGlanceCard:
    key: str
    title: str
    text: str
    source: str
    fact_ids: tuple[str, ...]
    tags: tuple[str, ...]
    repeated_signals: tuple[str, ...]
    display_template: str = ""


EXECUTION_TEMPLATES: tuple[MarsGlanceTemplate, ...] = (
    MarsGlanceTemplate(
        required_tags=frozenset({"planned_execution", "task_concentration"}),
        text="Work tends to be deliberate and calculated, with strong focus on the task.",
        display_template=(
            "{name} tends to work in a deliberate and calculated way, "
            "with strong focus on the task."
        ),
    ),
    MarsGlanceTemplate(
        required_tags=frozenset({"planned_execution", "strategic_action"}),
        text="Work tends to be planned and calculated.",
        display_template="{name} tends to work in a planned and calculated way.",
    ),
)

SLOWDOWN_TEMPLATES: tuple[MarsGlanceTemplate, ...] = (
    MarsGlanceTemplate(
        required_tags=frozenset({"action_hesitation", "action_inhibition"}),
        text="Action may slow through internal hesitation and braking.",
        display_template=(
            "{They} may hesitate or feel an internal brake "
            "before fully committing to action."
        ),
    ),
)

PRESSURE_TEMPLATES: tuple[MarsGlanceTemplate, ...] = (
    MarsGlanceTemplate(
        required_tags=frozenset({"effort_overload"}),
        required_repeats=frozenset({"effort_overload"}),
        text="Under pressure, effort may become overloaded.",
        display_template=(
            "Under pressure, {they} may take on too much or push {themself} "
            "into overwork."
        ),
    ),
)


def _human_text(fact: MarsSourceFact, presentation: dict[str, str]) -> str:
    return presentation.get(fact.id, fact.text)


def _facts_for_section(synthesis: MarsProfileSynthesis, key: str) -> list[MarsSourceFact]:
    section = next((item for item in synthesis.sections if item.key == key), None)
    if section is None:
        return []
    return [
        synthesis.facts_by_id[fact_id]
        for fact_id in section.fact_ids
        if fact_id in synthesis.facts_by_id
    ]


def _present_tags(facts: list[MarsSourceFact]) -> set[str]:
    tags: set[str] = set()
    for fact in facts:
        tags.update(fact.tags)
    return tags


def _repeat_names(synthesis: MarsProfileSynthesis) -> set[str]:
    return {item.signal for item in synthesis.repeated_signals}


def _supporting_ids(facts: list[MarsSourceFact], required_tags: frozenset[str]) -> tuple[str, ...]:
    return tuple(fact.id for fact in facts if required_tags & set(fact.tags))


def _match_template(
    templates: tuple[MarsGlanceTemplate, ...],
    facts: list[MarsSourceFact],
    present_repeats: set[str],
) -> tuple[MarsGlanceTemplate, tuple[str, ...]] | tuple[None, tuple[str, ...]]:
    present_tags = _present_tags(facts)
    for template in templates:
        if not template.required_tags <= present_tags:
            continue
        if template.required_repeats and not template.required_repeats <= present_repeats:
            continue
        return template, _supporting_ids(facts, template.required_tags)
    return None, ()


def _fallback_observation(
    facts: list[MarsSourceFact],
    presentation: dict[str, str],
) -> tuple[MarsSourceFact, str] | None:
    if not facts:
        return None
    fact = facts[0]
    return fact, _human_text(fact, presentation)


def _execution_pool(synthesis: MarsProfileSynthesis) -> list[MarsSourceFact]:
    facts: list[MarsSourceFact] = []
    for key in ("how_you_execute", "work_rhythm"):
        facts.extend(_facts_for_section(synthesis, key))
    facts = [fact for fact in facts if fact.category in EXECUTION_CATEGORIES]
    preferred = [fact for fact in facts if fact.polarity in {"strength", "neutral"}]
    return preferred


def _slowdown_pool(synthesis: MarsProfileSynthesis) -> list[MarsSourceFact]:
    facts: list[MarsSourceFact] = []
    seen: set[str] = set()
    for key in ("when_you_get_stuck", "how_you_start"):
        for fact in _facts_for_section(synthesis, key):
            if fact.id in seen:
                continue
            is_blocker = fact.category == "stuck_blocker"
            is_start_friction = fact.category == "action_start" and fact.polarity == "risk"
            is_hesitation = "action_hesitation" in fact.tags
            if not (is_blocker or is_start_friction or is_hesitation):
                continue
            seen.add(fact.id)
            facts.append(fact)
    return facts


def _pressure_pool(synthesis: MarsProfileSynthesis) -> list[MarsSourceFact]:
    facts = list(_facts_for_section(synthesis, "under_pressure"))
    seen = {fact.id for fact in facts}
    for fact in synthesis.facts_by_id.values():
        if fact.id in seen:
            continue
        if PRESSURE_TAGS & set(fact.tags):
            facts.append(fact)
            seen.add(fact.id)
    return facts


def _build_card(
    *,
    key: str,
    title: str,
    templates: tuple[MarsGlanceTemplate, ...],
    facts: list[MarsSourceFact],
    synthesis: MarsProfileSynthesis,
    presentation: dict[str, str],
) -> MarsGlanceCard | None:
    if not facts:
        return None
    repeats = _repeat_names(synthesis)
    template, fact_ids = _match_template(templates, facts, repeats)
    if template is not None:
        return MarsGlanceCard(
            key=key,
            title=title,
            text=template.text,
            source="template",
            fact_ids=fact_ids,
            tags=tuple(sorted(template.required_tags)),
            repeated_signals=tuple(
                item.signal
                for item in synthesis.repeated_signals
                if item.signal in template.required_repeats
            ),
            display_template=template.display_template,
        )
    fallback = _fallback_observation(facts, presentation)
    if fallback is None:
        return None
    fact, text = fallback
    related = tuple(
        item.signal
        for item in synthesis.repeated_signals
        if fact.id in item.fact_ids
    )
    return MarsGlanceCard(
        key=key,
        title=title,
        text=text,
        source="observation",
        fact_ids=(fact.id,),
        tags=tuple(fact.tags),
        repeated_signals=related,
    )


def build_mars_work_glance(synthesis: MarsProfileSynthesis) -> tuple[MarsGlanceCard, ...]:
    """Build 0–3 glance cards from existing synthesis evidence only."""
    presentation = dict(synthesis.presentation_text_by_fact_id)
    cards: list[MarsGlanceCard] = []
    execution = _build_card(
        key=GLANCE_EXECUTION,
        title="Execution style",
        templates=EXECUTION_TEMPLATES,
        facts=_execution_pool(synthesis),
        synthesis=synthesis,
        presentation=presentation,
    )
    slowdown = _build_card(
        key=GLANCE_SLOWDOWN,
        title="What may slow them down",
        templates=SLOWDOWN_TEMPLATES,
        facts=_slowdown_pool(synthesis),
        synthesis=synthesis,
        presentation=presentation,
    )
    pressure = _build_card(
        key=GLANCE_PRESSURE,
        title="Under pressure",
        templates=PRESSURE_TEMPLATES,
        facts=_pressure_pool(synthesis),
        synthesis=synthesis,
        presentation=presentation,
    )
    for card in (execution, slowdown, pressure):
        if card is not None:
            cards.append(card)
    return tuple(cards)


def render_mars_glance_text(card: MarsGlanceCard, person: PersonPerspective) -> str:
    """Render one glance card in recruiter or self perspective."""
    if card.display_template:
        return fill_person_template(card.display_template, person)
    return contextualize_neutral_sentence(card.text, person)


def render_mars_glance_title(card: MarsGlanceCard, person: PersonPerspective) -> str:
    return mars_glance_title(card.key, person, card.title)
