"""Mercury Profile Synthesis v1 — deterministic presentation assembler.

SOURCE FACTS ARE IMMUTABLE EVIDENCE.

This layer only orders, groups, partitions, and previews an existing
MercurySourceProfileResponse. It does not recalculate astrology, rewrite
facts, merge tags, resolve contradictions, score traits, or call an LLM.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.schemas.mercury_source_profile import (
    MercuryProfileSynthesisResponse,
    MercurySourceProfileResponse,
    SourceFact,
    SynthesisConditionalGroup as SynthesisConditionalGroupSchema,
    SynthesisDetailBucket as SynthesisDetailBucketSchema,
    SynthesisSection as SynthesisSectionSchema,
    SynthesisStrongestPattern as SynthesisStrongestPatternSchema,
    SynthesisTension as SynthesisTensionSchema,
    SynthesisTraceability as SynthesisTraceabilitySchema,
)
from app.services.mercury_human_copy import presentation_overrides_for_facts

DETAIL_ONLY_CATEGORIES = frozenset(
    {
        "source_specific",
        "compensation",
        "secondary_gain",
    }
)

SECTION_SPECS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("thinking", "How you think", ("thinking",)),
    ("communication", "How you communicate", ("communication",)),
    ("learning", "How you learn", ("learning",)),
    ("memory_focus", "Memory & focus", ("memory", "focus")),
    ("work_application", "How it can show up in work", ("work_application",)),
    (
        "context_risks",
        "Context & watch-outs",
        ("risk", "environment", "mobility"),
    ),
)

CATEGORY_TO_SECTION: dict[str, str] = {
    category: key
    for key, _title, categories in SECTION_SPECS
    for category in categories
}

MAX_PREVIEW_FACTS = 3
FACTOR_TYPE_ORDER = ("sign", "house", "motion", "aspect")


@dataclass(frozen=True)
class SynthesisStrongestPattern:
    signal: str
    source_count: int
    sources: tuple[str, ...]
    fact_ids: tuple[str, ...]
    section_keys: tuple[str, ...]


@dataclass(frozen=True)
class SynthesisTension:
    tag_a: str
    tag_b: str
    facts_a: tuple[str, ...]
    facts_b: tuple[str, ...]
    state: str  # "resolved" | "conditional"


@dataclass(frozen=True)
class SynthesisSection:
    key: str
    title: str
    categories: tuple[str, ...]
    resolved_fact_ids: tuple[str, ...]
    resolved_fact_count: int
    factor_keys: tuple[str, ...]
    factor_count: int
    preview_fact_ids: tuple[str, ...]


@dataclass(frozen=True)
class SynthesisConditionalGroup:
    factor_type: str
    factor_key: str
    fact_ids: tuple[str, ...]
    activation_conditions: tuple[str, ...]


@dataclass(frozen=True)
class SynthesisDetailBucket:
    key: str
    fact_ids: tuple[str, ...]


@dataclass(frozen=True)
class SynthesisTraceability:
    total_fact_count: int
    resolved_section_fact_count: int
    conditional_fact_count: int
    detail_only_fact_count: int
    unclassified_fact_count: int


@dataclass(frozen=True)
class MercuryProfileSynthesis:
    strongest_patterns: tuple[SynthesisStrongestPattern, ...]
    resolved_tensions: tuple[SynthesisTension, ...]
    conditional_tensions: tuple[SynthesisTension, ...]
    sections: tuple[SynthesisSection, ...]
    conditional_details: tuple[SynthesisConditionalGroup, ...]
    source_details: tuple[SynthesisDetailBucket, ...]
    traceability: SynthesisTraceability
    facts_by_id: dict[str, SourceFact] = field(repr=False)
    presentation_text_by_fact_id: dict[str, str] = field(default_factory=dict)


def _provenance_key(fact: SourceFact) -> str:
    return f"{fact.factor_type}:{fact.factor_key}"


def _factor_type_rank(factor_type: str) -> int:
    try:
        return FACTOR_TYPE_ORDER.index(factor_type)
    except ValueError:
        return len(FACTOR_TYPE_ORDER)


def collect_canonical_facts(profile: MercurySourceProfileResponse) -> list[SourceFact]:
    """Deduplicate layer facts by id, preserving sign→house→motion→aspect order."""
    ordered: list[SourceFact] = []
    seen: set[str] = set()
    for fact in (
        list(profile.sign_facts)
        + list(profile.house_facts)
        + list(profile.motion_facts)
        + list(profile.aspect_facts)
    ):
        if fact.id in seen:
            continue
        seen.add(fact.id)
        ordered.append(fact)
    return ordered


def _fill_preview_by_factor_diversity(
    facts: list[SourceFact],
    *,
    limit: int,
    used_provenance: set[str] | None = None,
    already_selected: set[str] | None = None,
) -> list[str]:
    """Representative diversity fill: one fact per provenance, then fill in order."""
    if limit <= 0 or not facts:
        return []
    preview: list[str] = []
    used = set(used_provenance or ())
    selected = set(already_selected or ())
    for fact in facts:
        if len(preview) >= limit:
            break
        if fact.id in selected:
            continue
        key = _provenance_key(fact)
        if key in used:
            continue
        used.add(key)
        preview.append(fact.id)
        selected.add(fact.id)
    if len(preview) < limit:
        for fact in facts:
            if len(preview) >= limit:
                break
            if fact.id in selected:
                continue
            preview.append(fact.id)
            selected.add(fact.id)
    return preview


def _select_preview_fact_ids(
    facts: list[SourceFact],
    repeated_signals: list | tuple = (),
) -> tuple[str, ...]:
    """Repeat-supported-first previews, then factor-diversity fallback.

    Prefer facts that already appear in profile.repeated_signals (section-local
    fact_ids only). One fact per distinct repeated signal, in existing signal
    order. Remaining slots use the prior provenance-diversity algorithm.
    """
    if not facts:
        return ()

    preview: list[str] = []
    selected: set[str] = set()
    used_provenance: set[str] = set()

    for signal in repeated_signals:
        if len(preview) >= MAX_PREVIEW_FACTS:
            break
        signal_ids = set(signal.fact_ids)
        eligible = [
            fact
            for fact in facts
            if fact.id in signal_ids and fact.id not in selected
        ]
        if not eligible:
            continue
        preferred = [
            fact for fact in eligible if _provenance_key(fact) not in used_provenance
        ]
        chosen = preferred[0] if preferred else eligible[0]
        preview.append(chosen.id)
        selected.add(chosen.id)
        used_provenance.add(_provenance_key(chosen))

    remaining = MAX_PREVIEW_FACTS - len(preview)
    if remaining > 0:
        preview.extend(
            _fill_preview_by_factor_diversity(
                facts,
                limit=remaining,
                used_provenance=used_provenance,
                already_selected=selected,
            )
        )
    return tuple(preview)


def _build_strongest_patterns(
    profile: MercurySourceProfileResponse,
    facts_by_id: dict[str, SourceFact],
) -> tuple[SynthesisStrongestPattern, ...]:
    patterns: list[SynthesisStrongestPattern] = []
    for signal in profile.repeated_signals:
        section_keys: list[str] = []
        seen_sections: set[str] = set()
        for fact_id in signal.fact_ids:
            fact = facts_by_id.get(fact_id)
            if fact is None or fact.unresolved:
                continue
            section_key = CATEGORY_TO_SECTION.get(fact.category)
            if section_key and section_key not in seen_sections:
                seen_sections.add(section_key)
                section_keys.append(section_key)
        patterns.append(
            SynthesisStrongestPattern(
                signal=signal.signal,
                source_count=signal.source_count,
                sources=tuple(signal.sources),
                fact_ids=tuple(signal.fact_ids),
                section_keys=tuple(section_keys),
            )
        )
    return tuple(patterns)


def _build_tensions(
    profile: MercurySourceProfileResponse,
    facts_by_id: dict[str, SourceFact],
) -> tuple[tuple[SynthesisTension, ...], tuple[SynthesisTension, ...]]:
    resolved: list[SynthesisTension] = []
    conditional: list[SynthesisTension] = []
    for pair in profile.contrasting_signals:
        side_a = [facts_by_id[fid] for fid in pair.facts_a if fid in facts_by_id]
        side_b = [facts_by_id[fid] for fid in pair.facts_b if fid in facts_by_id]
        a_resolved = any(not fact.unresolved for fact in side_a)
        b_resolved = any(not fact.unresolved for fact in side_b)
        state = "resolved" if a_resolved and b_resolved else "conditional"
        tension = SynthesisTension(
            tag_a=pair.tag_a,
            tag_b=pair.tag_b,
            facts_a=tuple(pair.facts_a),
            facts_b=tuple(pair.facts_b),
            state=state,
        )
        if state == "resolved":
            resolved.append(tension)
        else:
            conditional.append(tension)
    return tuple(resolved), tuple(conditional)


def _build_sections(
    canonical: list[SourceFact],
    repeated_signals: list | tuple = (),
) -> tuple[SynthesisSection, ...]:
    sections: list[SynthesisSection] = []
    for key, title, categories in SECTION_SPECS:
        category_set = set(categories)
        section_facts = [
            fact
            for fact in canonical
            if (not fact.unresolved) and fact.category in category_set
        ]
        factor_keys = tuple(dict.fromkeys(_provenance_key(fact) for fact in section_facts))
        sections.append(
            SynthesisSection(
                key=key,
                title=title,
                categories=categories,
                resolved_fact_ids=tuple(fact.id for fact in section_facts),
                resolved_fact_count=len(section_facts),
                factor_keys=factor_keys,
                factor_count=len(factor_keys),
                preview_fact_ids=_select_preview_fact_ids(section_facts, repeated_signals),
            )
        )
    return tuple(sections)


def _build_conditional_details(
    canonical: list[SourceFact],
) -> tuple[SynthesisConditionalGroup, ...]:
    by_factor: dict[tuple[str, str], list[SourceFact]] = {}
    for fact in canonical:
        if not fact.unresolved:
            continue
        key = (fact.factor_type, fact.factor_key)
        by_factor.setdefault(key, []).append(fact)

    groups: list[SynthesisConditionalGroup] = []
    for factor_type, factor_key in sorted(
        by_factor.keys(),
        key=lambda item: (_factor_type_rank(item[0]), item[0], item[1]),
    ):
        facts = by_factor[(factor_type, factor_key)]
        conditions = tuple(
            dict.fromkeys(
                fact.activation_condition
                for fact in facts
                if fact.activation_condition
            )
        )
        groups.append(
            SynthesisConditionalGroup(
                factor_type=factor_type,
                factor_key=factor_key,
                fact_ids=tuple(fact.id for fact in facts),
                activation_conditions=conditions,
            )
        )
    return tuple(groups)


def _build_source_details(canonical: list[SourceFact]) -> tuple[SynthesisDetailBucket, ...]:
    buckets: dict[str, list[str]] = {
        "source_specific": [],
        "compensation": [],
        "secondary_gain": [],
        "other": [],
    }
    for fact in canonical:
        if fact.unresolved:
            continue
        if fact.category in DETAIL_ONLY_CATEGORIES:
            buckets[fact.category].append(fact.id)
        elif fact.category not in CATEGORY_TO_SECTION:
            buckets["other"].append(fact.id)
    return tuple(
        SynthesisDetailBucket(key=key, fact_ids=tuple(fact_ids))
        for key, fact_ids in buckets.items()
        if fact_ids
    )


def build_mercury_profile_synthesis(
    profile: MercurySourceProfileResponse,
) -> MercuryProfileSynthesis:
    """Assemble a deterministic presentation index over an existing source profile."""
    canonical = collect_canonical_facts(profile)
    facts_by_id = {fact.id: fact for fact in canonical}

    strongest_patterns = _build_strongest_patterns(profile, facts_by_id)
    resolved_tensions, conditional_tensions = _build_tensions(profile, facts_by_id)
    sections = _build_sections(canonical, profile.repeated_signals)
    conditional_details = _build_conditional_details(canonical)
    source_details = _build_source_details(canonical)

    resolved_section_ids = {
        fact_id for section in sections for fact_id in section.resolved_fact_ids
    }
    conditional_ids = {
        fact_id for group in conditional_details for fact_id in group.fact_ids
    }
    detail_ids = {
        fact_id for bucket in source_details for fact_id in bucket.fact_ids
    }

    owned = resolved_section_ids | conditional_ids | detail_ids
    unclassified = [fact.id for fact in canonical if fact.id not in owned]

    # Future unknown categories already land in source_details["other"];
    # unclassified_fact_count should stay 0 for the current catalog.
    if unclassified:
        # Defensive: append any stray IDs into an explicit other bucket.
        existing_other = next((b for b in source_details if b.key == "other"), None)
        if existing_other is None:
            source_details = source_details + (
                SynthesisDetailBucket(key="other", fact_ids=tuple(unclassified)),
            )
        else:
            merged = existing_other.fact_ids + tuple(unclassified)
            source_details = tuple(
                SynthesisDetailBucket(key=b.key, fact_ids=merged)
                if b.key == "other"
                else b
                for b in source_details
            )
        detail_ids = {
            fact_id for bucket in source_details for fact_id in bucket.fact_ids
        }
        owned = resolved_section_ids | conditional_ids | detail_ids
        unclassified = [fact.id for fact in canonical if fact.id not in owned]

    traceability = SynthesisTraceability(
        total_fact_count=len(canonical),
        resolved_section_fact_count=len(resolved_section_ids),
        conditional_fact_count=len(conditional_ids),
        detail_only_fact_count=len(detail_ids),
        unclassified_fact_count=len(unclassified),
    )

    return MercuryProfileSynthesis(
        strongest_patterns=strongest_patterns,
        resolved_tensions=resolved_tensions,
        conditional_tensions=conditional_tensions,
        sections=sections,
        conditional_details=conditional_details,
        source_details=source_details,
        traceability=traceability,
        facts_by_id=facts_by_id,
        presentation_text_by_fact_id=presentation_overrides_for_facts(canonical),
    )


def serialize_mercury_profile_synthesis(
    synthesis: MercuryProfileSynthesis,
) -> MercuryProfileSynthesisResponse:
    """Convert internal synthesis dataclasses to the API response schema."""
    from app.schemas.mercury_source_profile import MercuryGlanceCard as MercuryGlanceCardSchema
    from app.services.mercury_think_glance import build_mercury_think_glance

    glance = build_mercury_think_glance(synthesis)
    return MercuryProfileSynthesisResponse(
        thinking_at_a_glance=[
            MercuryGlanceCardSchema(
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
        strongest_patterns=[
            SynthesisStrongestPatternSchema(
                signal=item.signal,
                source_count=item.source_count,
                sources=list(item.sources),
                fact_ids=list(item.fact_ids),
                section_keys=list(item.section_keys),
            )
            for item in synthesis.strongest_patterns
        ],
        resolved_tensions=[
            SynthesisTensionSchema(
                tag_a=item.tag_a,
                tag_b=item.tag_b,
                facts_a=list(item.facts_a),
                facts_b=list(item.facts_b),
                state=item.state,  # type: ignore[arg-type]
            )
            for item in synthesis.resolved_tensions
        ],
        conditional_tensions=[
            SynthesisTensionSchema(
                tag_a=item.tag_a,
                tag_b=item.tag_b,
                facts_a=list(item.facts_a),
                facts_b=list(item.facts_b),
                state=item.state,  # type: ignore[arg-type]
            )
            for item in synthesis.conditional_tensions
        ],
        sections=[
            SynthesisSectionSchema(
                key=item.key,
                title=item.title,
                categories=list(item.categories),
                resolved_fact_ids=list(item.resolved_fact_ids),
                resolved_fact_count=item.resolved_fact_count,
                factor_keys=list(item.factor_keys),
                factor_count=item.factor_count,
                preview_fact_ids=list(item.preview_fact_ids),
            )
            for item in synthesis.sections
        ],
        conditional_details=[
            SynthesisConditionalGroupSchema(
                factor_type=item.factor_type,
                factor_key=item.factor_key,
                fact_ids=list(item.fact_ids),
                activation_conditions=list(item.activation_conditions),
            )
            for item in synthesis.conditional_details
        ],
        source_details=[
            SynthesisDetailBucketSchema(
                key=item.key,
                fact_ids=list(item.fact_ids),
            )
            for item in synthesis.source_details
        ],
        traceability=SynthesisTraceabilitySchema(
            total_fact_count=synthesis.traceability.total_fact_count,
            resolved_section_fact_count=synthesis.traceability.resolved_section_fact_count,
            conditional_fact_count=synthesis.traceability.conditional_fact_count,
            detail_only_fact_count=synthesis.traceability.detail_only_fact_count,
            unclassified_fact_count=synthesis.traceability.unclassified_fact_count,
        ),
        facts_by_id=dict(synthesis.facts_by_id),
        presentation_text_by_fact_id=dict(synthesis.presentation_text_by_fact_id),
    )


def attach_mercury_profile_synthesis(
    profile: MercurySourceProfileResponse,
) -> MercurySourceProfileResponse:
    """Attach additive synthesis to an already-built source profile (no recalculation)."""
    from app.services.mercury_deep_profile import build_mercury_deep_profile

    synthesis = serialize_mercury_profile_synthesis(
        build_mercury_profile_synthesis(profile)
    )
    deep_profile = build_mercury_deep_profile(profile)
    synthesis = synthesis.model_copy(update={"deep_profile": deep_profile})
    return profile.model_copy(update={"synthesis": synthesis})
