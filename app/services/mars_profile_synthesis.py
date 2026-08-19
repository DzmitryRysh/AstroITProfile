"""Mars Profile Synthesis v1 — deterministic HOW YOU WORK assembler.

Assembles activated Mars source facts into stable sections.
Does not rewrite facts, score traits, resolve contradictions, or call an LLM.
Canonical source evidence stays on facts; human-facing presentation uses
reviewed human copy when an override exists.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.schemas.mars_source_profile import (
    CalculatedMarsSnapshot,
    MarsAspect as MarsAspectSchema,
    MarsGlanceCard as MarsGlanceCardSchema,
    MarsProfileSynthesisResponse,
    MarsRepeatedSignal as MarsRepeatedSignalSchema,
    MarsSourceCoverage as MarsSourceCoverageSchema,
    MarsSourceFact as MarsSourceFactSchema,
    MarsSourceProfileResponse,
    MarsSynthesisSection as MarsSynthesisSectionSchema,
    MarsSynthesisTraceability as MarsSynthesisTraceabilitySchema,
)
from app.services.mars_human_copy import presentation_overrides_for_facts
from app.services.mars_repeated_signals import MarsRepeatedSignal, detect_mars_repeated_signals
from app.services.mars_source_profile import MarsSourceCoverage, MarsSourceFact, MarsSourceProfile

FACTOR_TYPE_ORDER = ("sign", "house", "motion", "aspect")

# Tag-driven exclusive section. Remaining facts map by category.
SECTION_SPECS: tuple[tuple[str, str, tuple[str, ...], tuple[str, ...]], ...] = (
    ("how_you_start", "How you start", ("action_start", "initiative"), ()),
    ("how_you_execute", "How you execute", ("execution", "continuation", "effort"), ()),
    ("work_rhythm", "Work rhythm", ("work_rhythm",), ()),
    ("when_you_get_stuck", "When you get stuck", ("stuck_blocker",), ()),
    ("under_pressure", "Under pressure", (), ("effort_overload", "crisis_execution", "crisis_activation")),
    ("how_you_handle_obstacles", "How you handle obstacles", ("obstacle",), ()),
    ("conflict_style", "Conflict style", ("conflict",), ()),
    ("best_work_conditions", "Best work conditions", ("work_conditions",), ()),
    ("watchouts", "Watchouts", ("watchout",), ()),
    ("professional_associations", "Professional associations", ("professional_association",), ()),
    ("compensations", "Compensations", ("compensation",), ()),
)

CATEGORY_TO_SECTION: dict[str, str] = {
    category: key
    for key, _title, categories, _tags in SECTION_SPECS
    for category in categories
}


@dataclass(frozen=True)
class MarsSynthesisSection:
    key: str
    title: str
    categories: tuple[str, ...]
    tags: tuple[str, ...]
    fact_ids: tuple[str, ...]
    fact_count: int
    factor_keys: tuple[str, ...]
    factor_count: int
    repeated_fact_ids: tuple[str, ...]
    repeated_signals: tuple[str, ...]


@dataclass(frozen=True)
class MarsSynthesisTraceability:
    activated_fact_count: int
    section_fact_count: int
    detail_fact_count: int
    unresolved_fact_count: int
    unclassified_fact_count: int


@dataclass(frozen=True)
class MarsProfileSynthesis:
    repeated_signals: tuple[MarsRepeatedSignal, ...]
    sections: tuple[MarsSynthesisSection, ...]
    source_specific_fact_ids: tuple[str, ...]
    unresolved_fact_ids: tuple[str, ...]
    coverage: MarsSourceCoverage
    limitations: tuple[str, ...]
    traceability: MarsSynthesisTraceability
    facts_by_id: dict[str, MarsSourceFact] = field(repr=False)
    presentation_text_by_fact_id: dict[str, str] = field(default_factory=dict)


def collect_activated_mars_facts(profile: MarsSourceProfile) -> list[MarsSourceFact]:
    ordered: list[MarsSourceFact] = []
    seen: set[str] = set()
    for fact in (
        list(profile.sign_facts)
        + list(profile.house_facts)
        + list(profile.motion_facts)
        + list(profile.aspect_facts)
    ):
        if fact.id in seen:
            continue
        if not fact.activated or fact.unresolved:
            continue
        seen.add(fact.id)
        ordered.append(fact)
    return ordered


def _provenance_key(fact: MarsSourceFact) -> str:
    return fact.provenance_key


def _factor_type_rank(factor_type: str) -> int:
    try:
        return FACTOR_TYPE_ORDER.index(factor_type)
    except ValueError:
        return len(FACTOR_TYPE_ORDER)


def _order_section_facts(
    facts: list[MarsSourceFact],
    repeated_signals: tuple[MarsRepeatedSignal, ...],
) -> list[MarsSourceFact]:
    repeated_ids: list[str] = []
    seen: set[str] = set()
    for signal in repeated_signals:
        for fact_id in signal.fact_ids:
            if fact_id not in seen:
                seen.add(fact_id)
                repeated_ids.append(fact_id)
    repeated_rank = {fact_id: index for index, fact_id in enumerate(repeated_ids)}

    def sort_key(fact: MarsSourceFact) -> tuple:
        in_repeat = 0 if fact.id in repeated_rank else 1
        repeat_index = repeated_rank.get(fact.id, len(repeated_rank))
        return (
            in_repeat,
            repeat_index,
            _factor_type_rank(fact.factor_type),
            fact.factor_key,
            fact.id,
        )

    return sorted(facts, key=sort_key)


def _assign_facts(
    canonical: list[MarsSourceFact],
) -> dict[str, list[MarsSourceFact]]:
    assigned: dict[str, list[MarsSourceFact]] = {key: [] for key, *_ in SECTION_SPECS}
    claimed: set[str] = set()

    for key, _title, _categories, tags in SECTION_SPECS:
        if not tags:
            continue
        tag_set = set(tags)
        for fact in canonical:
            if fact.id in claimed:
                continue
            if tag_set & set(fact.tags):
                assigned[key].append(fact)
                claimed.add(fact.id)

    for key, _title, categories, _tags in SECTION_SPECS:
        if not categories:
            continue
        category_set = set(categories)
        for fact in canonical:
            if fact.id in claimed:
                continue
            if fact.category in category_set:
                assigned[key].append(fact)
                claimed.add(fact.id)
    return assigned


def build_mars_profile_synthesis(profile: MarsSourceProfile) -> MarsProfileSynthesis:
    canonical = collect_activated_mars_facts(profile)
    facts_by_id = {fact.id: fact for fact in canonical}
    repeated = profile.repeated_signals or detect_mars_repeated_signals(canonical)
    assigned = _assign_facts(canonical)

    sections: list[MarsSynthesisSection] = []
    section_ids: set[str] = set()
    for key, title, categories, tags in SECTION_SPECS:
        section_facts = _order_section_facts(assigned[key], repeated)
        fact_ids = tuple(fact.id for fact in section_facts)
        section_ids.update(fact_ids)
        factor_keys = tuple(dict.fromkeys(_provenance_key(fact) for fact in section_facts))
        overlapping_signals = tuple(
            signal.signal
            for signal in repeated
            if set(signal.fact_ids) & set(fact_ids)
        )
        repeated_fact_ids = tuple(
            fact_id
            for fact_id in fact_ids
            if any(fact_id in signal.fact_ids for signal in repeated)
        )
        sections.append(
            MarsSynthesisSection(
                key=key,
                title=title,
                categories=categories,
                tags=tags,
                fact_ids=fact_ids,
                fact_count=len(fact_ids),
                factor_keys=factor_keys,
                factor_count=len(factor_keys),
                repeated_fact_ids=repeated_fact_ids,
                repeated_signals=overlapping_signals,
            )
        )

    source_specific_ids = tuple(
        fact.id for fact in canonical if fact.category == "source_specific" and fact.id not in section_ids
    )
    owned = section_ids | set(source_specific_ids)
    unclassified = [fact.id for fact in canonical if fact.id not in owned]
    unresolved_ids = tuple(fact.id for fact in profile.conditional_unresolved)

    return MarsProfileSynthesis(
        repeated_signals=repeated,
        sections=tuple(sections),
        source_specific_fact_ids=source_specific_ids,
        unresolved_fact_ids=unresolved_ids,
        coverage=profile.coverage,
        limitations=profile.limitations,
        traceability=MarsSynthesisTraceability(
            activated_fact_count=len(canonical),
            section_fact_count=len(section_ids),
            detail_fact_count=len(source_specific_ids),
            unresolved_fact_count=len(unresolved_ids),
            unclassified_fact_count=len(unclassified),
        ),
        facts_by_id=facts_by_id,
        presentation_text_by_fact_id=presentation_overrides_for_facts(canonical),
    )


MARS_PREVIEW_FACT_LIMIT = 3


def _to_fact_schema(fact: MarsSourceFact) -> MarsSourceFactSchema:
    return MarsSourceFactSchema(
        id=fact.id,
        factor_type=fact.factor_type,  # type: ignore[arg-type]
        factor_key=fact.factor_key,
        category=fact.category,
        text=fact.text,
        polarity=fact.polarity,  # type: ignore[arg-type]
        scope=fact.scope,  # type: ignore[arg-type]
        tags=list(fact.tags),
        source_reference=fact.source_reference,
        activation_condition=fact.activation_condition,
        activated=fact.activated,
        unresolved=fact.unresolved,
    )


def _to_repeated_schema(signal: MarsRepeatedSignal) -> MarsRepeatedSignalSchema:
    return MarsRepeatedSignalSchema(
        signal=signal.signal,
        tag=signal.tag,
        source_count=signal.source_count,
        sources=list(signal.sources),
        fact_ids=list(signal.fact_ids),
    )


def _to_coverage_schema(coverage: MarsSourceCoverage) -> MarsSourceCoverageSchema:
    return MarsSourceCoverageSchema(
        status=coverage.status,  # type: ignore[arg-type]
        covered_factors=list(coverage.covered_factors),
        unimplemented_source_factors=list(coverage.unimplemented_source_factors),
    )


def serialize_mars_profile_synthesis(
    synthesis: MarsProfileSynthesis,
) -> MarsProfileSynthesisResponse:
    """Convert internal Mars synthesis dataclasses to the API response schema."""
    from app.services.mars_work_glance import build_mars_work_glance

    glance = build_mars_work_glance(synthesis)
    return MarsProfileSynthesisResponse(
        work_style_at_a_glance=[
            MarsGlanceCardSchema(
                key=card.key,
                title=card.title,
                text=card.text,
                source=card.source,  # type: ignore[arg-type]
                fact_ids=list(card.fact_ids),
                tags=list(card.tags),
                repeated_signals=list(card.repeated_signals),
                display_template=card.display_template,
            )
            for card in glance
        ],
        repeated_signals=[_to_repeated_schema(item) for item in synthesis.repeated_signals],
        sections=[
            MarsSynthesisSectionSchema(
                key=item.key,
                title=item.title,
                categories=list(item.categories),
                tags=list(item.tags),
                fact_ids=list(item.fact_ids),
                fact_count=item.fact_count,
                factor_keys=list(item.factor_keys),
                factor_count=item.factor_count,
                repeated_fact_ids=list(item.repeated_fact_ids),
                repeated_signals=list(item.repeated_signals),
                preview_fact_ids=list(item.fact_ids[:MARS_PREVIEW_FACT_LIMIT]),
            )
            for item in synthesis.sections
        ],
        source_specific_fact_ids=list(synthesis.source_specific_fact_ids),
        unresolved_fact_ids=list(synthesis.unresolved_fact_ids),
        coverage=_to_coverage_schema(synthesis.coverage),
        limitations=list(synthesis.limitations),
        traceability=MarsSynthesisTraceabilitySchema(
            activated_fact_count=synthesis.traceability.activated_fact_count,
            section_fact_count=synthesis.traceability.section_fact_count,
            detail_fact_count=synthesis.traceability.detail_fact_count,
            unresolved_fact_count=synthesis.traceability.unresolved_fact_count,
            unclassified_fact_count=synthesis.traceability.unclassified_fact_count,
        ),
        facts_by_id={
            fact_id: _to_fact_schema(fact) for fact_id, fact in synthesis.facts_by_id.items()
        },
        presentation_text_by_fact_id=dict(synthesis.presentation_text_by_fact_id),
    )


def serialize_mars_source_profile(profile: MarsSourceProfile) -> MarsSourceProfileResponse:
    """Serialize calculated Mars source + additive synthesis for API/UI delivery."""
    calculated = profile.calculated
    synthesis = serialize_mars_profile_synthesis(build_mars_profile_synthesis(profile))
    return MarsSourceProfileResponse(
        calculated=CalculatedMarsSnapshot(
            mars_sign=calculated.mars_sign,
            mars_house=calculated.mars_house,
            mars_motion=calculated.mars_motion,  # type: ignore[arg-type]
            birth_time_known=calculated.birth_time_known,
            aspects=[
                MarsAspectSchema(
                    planet=item.planet,
                    type=item.type,
                    orb_deg=item.orb_deg,
                )
                for item in calculated.mars_aspects
            ],
            house_system_used=calculated.house_system_used,
        ),
        sign_facts=[_to_fact_schema(fact) for fact in profile.sign_facts],
        house_facts=[_to_fact_schema(fact) for fact in profile.house_facts],
        motion_facts=[_to_fact_schema(fact) for fact in profile.motion_facts],
        aspect_facts=[_to_fact_schema(fact) for fact in profile.aspect_facts],
        repeated_signals=[_to_repeated_schema(item) for item in profile.repeated_signals],
        conditional_unresolved=[_to_fact_schema(fact) for fact in profile.conditional_unresolved],
        coverage=_to_coverage_schema(profile.coverage),
        limitations=list(profile.limitations),
        synthesis=synthesis,
    )
