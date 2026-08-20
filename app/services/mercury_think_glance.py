"""Deterministic HOW YOU THINK glance cards (M8.5).

Presentation-only. Selects existing Mercury synthesis evidence in layer order:
sign → house → motion → aspect. Repeated signals reinforce separately; they do
not replace the baseline glance.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.schemas.mercury_source_profile import SourceFact
from app.services.mercury_human_copy_catalog import (
    STATUS_APPROVED_OVERRIDE,
    STATUS_APPROVED_RAW,
    derive_review_status,
)
from app.services.mercury_profile_synthesis import (
    DETAIL_ONLY_CATEGORIES,
    FACTOR_TYPE_ORDER,
    MercuryProfileSynthesis,
)
from app.services.person_perspective import PersonPerspective, contextualize_neutral_sentence

GLANCE_THINKING = "thinking_style"
GLANCE_COMMUNICATION = "communication_style"
GLANCE_LEARNING = "learning_style"
GLANCE_WATCHOUT = "watchout"

MAX_GLANCE_CARDS = 4
LAYER_ORDER = FACTOR_TYPE_ORDER
WATCHOUT_CATEGORIES = frozenset({"risk", "environment", "mobility"})

_CATEGORY_PREFIXES: tuple[str, ...] = (
    "thinks in ",
    "communicates in ",
    "learns well through ",
    "learns through ",
    "tends to ",
    "may ",
    "can ",
)


@dataclass(frozen=True)
class MercuryGlanceCard:
    key: str
    title: str
    text: str
    source: str
    fact_ids: tuple[str, ...]
    tags: tuple[str, ...]
    repeated_signals: tuple[str, ...]
    display_template: str = ""


def _factor_type_rank(factor_type: str) -> int:
    try:
        return LAYER_ORDER.index(factor_type)
    except ValueError:
        return len(LAYER_ORDER)


def _is_presentation_ready(fact_id: str) -> bool:
    status = derive_review_status(fact_id)
    return status in {STATUS_APPROVED_OVERRIDE, STATUS_APPROVED_RAW}


def _human_text(fact: SourceFact, presentation: dict[str, str]) -> str:
    return presentation.get(fact.id, fact.text)


def _semantic_fingerprint(text: str) -> str:
    """Normalize takeaway text so category-specific phrasing can be deduped."""
    normalized = text.strip().lower().rstrip(".")
    for prefix in _CATEGORY_PREFIXES:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix) :]
            break
    return re.sub(r"\s+", " ", normalized)


def _is_eligible(fact: SourceFact) -> bool:
    return (
        fact.activated
        and not fact.unresolved
        and fact.category not in DETAIL_ONLY_CATEGORIES
        and _is_presentation_ready(fact.id)
    )


def _section_facts_ordered(
    synthesis: MercuryProfileSynthesis,
    section_key: str,
) -> list[SourceFact]:
    section = next((item for item in synthesis.sections if item.key == section_key), None)
    if section is None:
        return []
    return [
        synthesis.facts_by_id[fact_id]
        for fact_id in section.resolved_fact_ids
        if fact_id in synthesis.facts_by_id
    ]


def _related_repeats(fact: SourceFact, synthesis: MercuryProfileSynthesis) -> tuple[str, ...]:
    return tuple(
        item.signal
        for item in synthesis.strongest_patterns
        if fact.id in item.fact_ids
    )


def _ordered_candidates(
    eligible: list[SourceFact],
    *,
    prefer_sign: bool,
    watchout: bool,
) -> list[SourceFact]:
    pool = eligible
    if watchout:
        risk_first = [fact for fact in eligible if fact.polarity == "risk"]
        if risk_first:
            pool = sorted(
                risk_first,
                key=lambda item: (_factor_type_rank(item.factor_type), item.id),
            )
        else:
            pool = eligible

    if prefer_sign:
        ordered: list[SourceFact] = []
        for layer in LAYER_ORDER:
            for fact in pool:
                if fact.factor_type == layer:
                    ordered.append(fact)
        return ordered
    return list(pool)


def _pick_fact(
    facts: list[SourceFact],
    used: set[str],
    *,
    prefer_sign: bool = False,
    exclude_risk: bool = False,
    watchout: bool = False,
    used_fingerprints: set[str] | None = None,
    presentation: dict[str, str] | None = None,
) -> SourceFact | None:
    eligible = [
        fact
        for fact in facts
        if fact.id not in used and _is_eligible(fact)
    ]
    if exclude_risk:
        eligible = [fact for fact in eligible if fact.polarity != "risk"]
    if not eligible:
        return None

    for fact in _ordered_candidates(
        eligible,
        prefer_sign=prefer_sign,
        watchout=watchout,
    ):
        if used_fingerprints is not None and presentation is not None:
            fingerprint = _semantic_fingerprint(_human_text(fact, presentation))
            if fingerprint in used_fingerprints:
                continue
        return fact
    return None


def _observation_card(
    *,
    key: str,
    title: str,
    fact: SourceFact,
    synthesis: MercuryProfileSynthesis,
    presentation: dict[str, str],
) -> MercuryGlanceCard:
    return MercuryGlanceCard(
        key=key,
        title=title,
        text=_human_text(fact, presentation),
        source="observation",
        fact_ids=(fact.id,),
        tags=tuple(fact.tags),
        repeated_signals=_related_repeats(fact, synthesis),
    )


def build_mercury_think_glance(
    synthesis: MercuryProfileSynthesis,
) -> tuple[MercuryGlanceCard, ...]:
    """Build up to four glance cards from existing Mercury synthesis evidence."""
    presentation = dict(synthesis.presentation_text_by_fact_id)
    used: set[str] = set()
    used_fingerprints: set[str] = set()
    cards: list[MercuryGlanceCard] = []

    thinking = _section_facts_ordered(synthesis, "thinking")
    communication = _section_facts_ordered(synthesis, "communication")
    learning = _section_facts_ordered(synthesis, "learning")
    watchout = [
        fact
        for fact in _section_facts_ordered(synthesis, "context_risks")
        if fact.category in WATCHOUT_CATEGORIES
    ]

    picks: tuple[tuple[str, str, list[SourceFact], bool, bool], ...] = (
        (GLANCE_THINKING, "Thinking style", thinking, True, True),
        (GLANCE_COMMUNICATION, "Communication style", communication, True, True),
        (GLANCE_LEARNING, "Learning style", learning, True, True),
    )
    for key, title, pool, prefer_sign, exclude_risk in picks:
        fact = _pick_fact(
            pool,
            used,
            prefer_sign=prefer_sign,
            exclude_risk=exclude_risk,
            used_fingerprints=used_fingerprints,
            presentation=presentation,
        )
        if fact is None:
            continue
        used.add(fact.id)
        used_fingerprints.add(_semantic_fingerprint(_human_text(fact, presentation)))
        cards.append(
            _observation_card(
                key=key,
                title=title,
                fact=fact,
                synthesis=synthesis,
                presentation=presentation,
            )
        )

    watchout_fact = _pick_fact(
        watchout,
        used,
        prefer_sign=True,
        watchout=True,
    )
    if watchout_fact is not None:
        used.add(watchout_fact.id)
        cards.append(
            _observation_card(
                key=GLANCE_WATCHOUT,
                title="Watchout",
                fact=watchout_fact,
                synthesis=synthesis,
                presentation=presentation,
            )
        )

    return tuple(cards[:MAX_GLANCE_CARDS])


def render_mercury_glance_text(card: MercuryGlanceCard, person: PersonPerspective) -> str:
    if card.display_template:
        from app.services.person_perspective import fill_person_template

        return fill_person_template(card.display_template, person)
    return contextualize_neutral_sentence(card.text, person)


def render_mercury_glance_title(card: MercuryGlanceCard) -> str:
    return card.title
