"""Deterministic Thinking → Execution presentation bridge (M9).

Reads already-built Mercury and Mars profiles separately.
Does not merge fact lists, invent tags, rank people, or run mixed-profile
repeat detection.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.schemas.mercury_source_profile import MercurySourceProfileResponse, SourceFact
from app.schemas.thinking_to_execution import (
    CrossProfilePattern,
    ThinkingToExecutionSynthesis,
)
from app.services.mars_human_copy_catalog import (
    STATUS_APPROVED_OVERRIDE as MARS_APPROVED_OVERRIDE,
    STATUS_APPROVED_RAW as MARS_APPROVED_RAW,
    derive_review_status as mars_review_status,
)
from app.services.mars_profile_synthesis import collect_activated_mars_facts
from app.services.mars_source_profile import MarsSourceFact, MarsSourceProfile
from app.services.mercury_human_copy_catalog import (
    STATUS_APPROVED_OVERRIDE as MERCURY_APPROVED_OVERRIDE,
    STATUS_APPROVED_RAW as MERCURY_APPROVED_RAW,
    derive_review_status as mercury_review_status,
)
from app.services.person_perspective import PersonPerspective, fill_person_template

EXCLUDED_MARS_SCOPES = frozenset({"SOURCE_ONLY", "PERSONAL_MARS"})
OVERVIEW_BRIDGE_LIMIT = 3
PRESENTATION_READY_STATUSES = frozenset(
    {
        MERCURY_APPROVED_OVERRIDE,
        MERCURY_APPROVED_RAW,
        MARS_APPROVED_OVERRIDE,
        MARS_APPROVED_RAW,
    }
)

WHY_TEMPLATE = (
    "This connection appears because both an exact Mercury {mercury_semantic} "
    "signal and an exact Mars {mars_semantic} signal are present in the current "
    "source-backed evidence."
)


@dataclass(frozen=True)
class CrossPatternSpec:
    id: str
    title: str
    kind: str
    mercury_semantic: str
    mars_semantic: str
    presentation_template: str


# Exact existing Mercury tag + exact existing Mars tag only.
# technical_ability + hands_on_execution is rejected: aptitude signal vs action
# behavior must not be presented as verified technical skill.
CROSS_PATTERN_SPECS: tuple[CrossPatternSpec, ...] = (
    CrossPatternSpec(
        id="analysis_to_deliberate_execution",
        title="Analytical thinking → Deliberate execution",
        kind="reinforcement",
        mercury_semantic="analytical_thinking",
        mars_semantic="planned_execution",
        presentation_template=(
            "{NamePossessive} analytical thinking can pair with a deliberate, "
            "planned approach to execution."
        ),
    ),
    CrossPatternSpec(
        id="analysis_slower_commitment",
        title="More analytical thinking → Slower commitment",
        kind="friction",
        mercury_semantic="analytical_thinking",
        mars_semantic="action_hesitation",
        presentation_template=(
            "{NamePossessive} thinking may become more analytical while still "
            "taking more time to commit to action."
        ),
    ),
    CrossPatternSpec(
        id="fast_processing_to_fast_action",
        title="Fast processing → Fast action",
        kind="reinforcement",
        mercury_semantic="fast_thinking",
        mars_semantic="fast_start",
        presentation_template=(
            "{name} may process quickly and also start action quickly."
        ),
    ),
    CrossPatternSpec(
        id="fast_processing_slower_commitment",
        title="Faster thinking → Slower commitment",
        kind="friction",
        mercury_semantic="fast_thinking",
        mars_semantic="action_hesitation",
        presentation_template=(
            "{NamePossessive} thinking may move faster while still hesitating "
            "before fully committing to action."
        ),
    ),
    CrossPatternSpec(
        id="analysis_to_practical_execution",
        title="Analytical thinking → Practical execution",
        kind="reinforcement",
        mercury_semantic="analytical_thinking",
        mars_semantic="hands_on_execution",
        presentation_template=(
            "Analytical thinking may be paired with a preference for practical, "
            "hands-on execution."
        ),
    ),
)


def _active_mercury_facts(profile: MercurySourceProfileResponse) -> tuple[SourceFact, ...]:
    facts: list[SourceFact] = []
    seen: set[str] = set()
    for bucket in (
        profile.sign_facts,
        profile.house_facts,
        profile.motion_facts,
        profile.aspect_facts,
    ):
        for fact in bucket:
            if fact.id in seen:
                continue
            if not fact.activated or fact.unresolved:
                continue
            seen.add(fact.id)
            facts.append(fact)
    return tuple(facts)


def _active_mars_facts(profile: MarsSourceProfile) -> tuple[MarsSourceFact, ...]:
    return tuple(
        fact
        for fact in collect_activated_mars_facts(profile)
        if fact.scope not in EXCLUDED_MARS_SCOPES
    )


def _facts_with_tag(facts, tag: str):
    return [fact for fact in facts if tag in (fact.tags or ())]


def _mercury_is_presentation_ready(fact: SourceFact) -> bool:
    return mercury_review_status(fact.id) in PRESENTATION_READY_STATUSES


def _mars_is_presentation_ready(fact: MarsSourceFact) -> bool:
    return mars_review_status(fact.id) in PRESENTATION_READY_STATUSES


def _mercury_provenance(fact: SourceFact) -> str:
    return f"mercury:{fact.factor_type}:{fact.factor_key}"


def _mars_provenance(fact: MarsSourceFact) -> str:
    return f"mars:{fact.provenance_key}"


def _unique_sorted(values: list[str]) -> tuple[str, ...]:
    return tuple(sorted(set(values)))


def build_thinking_to_execution(
    mercury_profile: MercurySourceProfileResponse,
    mars_profile: MarsSourceProfile,
    person: PersonPerspective,
) -> ThinkingToExecutionSynthesis:
    """Bridge two already-built profiles. Empty patterns is a valid result."""
    mercury_facts = _active_mercury_facts(mercury_profile)
    mars_facts = _active_mars_facts(mars_profile)
    patterns: list[CrossProfilePattern] = []
    for spec in CROSS_PATTERN_SPECS:
        mercury_support = [
            fact
            for fact in _facts_with_tag(mercury_facts, spec.mercury_semantic)
            if _mercury_is_presentation_ready(fact)
        ]
        mars_support = [
            fact
            for fact in _facts_with_tag(mars_facts, spec.mars_semantic)
            if _mars_is_presentation_ready(fact)
        ]
        if not mercury_support or not mars_support:
            continue
        patterns.append(
            CrossProfilePattern(
                id=spec.id,
                title=spec.title,
                kind=spec.kind,
                presentation_text=fill_person_template(spec.presentation_template, person),
                mercury_semantic=spec.mercury_semantic,
                mars_semantic=spec.mars_semantic,
                mercury_support=[fact.id for fact in mercury_support],
                mars_support=[fact.id for fact in mars_support],
                mercury_provenance=list(
                    _unique_sorted([_mercury_provenance(fact) for fact in mercury_support])
                ),
                mars_provenance=list(
                    _unique_sorted([_mars_provenance(fact) for fact in mars_support])
                ),
                why_this_appears=WHY_TEMPLATE.format(
                    mercury_semantic=spec.mercury_semantic,
                    mars_semantic=spec.mars_semantic,
                ),
            )
        )
        if len(patterns) >= OVERVIEW_BRIDGE_LIMIT:
            break
    return ThinkingToExecutionSynthesis(patterns=patterns)
