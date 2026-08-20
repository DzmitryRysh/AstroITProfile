"""Contribution Profile v1 — deterministic work-contribution assembler.

Derives qualitative contribution dimensions from already-built Mercury,
Mars, and Thinking → Execution evidence. Does not merge source catalogs,
invent tags, score people, or recommend hiring.

Root evidence vs TTE
--------------------
Independent roots are presentation-ready Mercury/Mars source facts mapped to
the dimension, counted by distinct provenance keys
(``mercury:{factor_type}:{factor_key}``, ``mars:{provenance_key}``).

Thinking-to-Execution patterns are derived from those same facts. They may
strengthen (reinforcement) or qualify (friction) a dimension, but they are
never an extra independent root and cannot create a dimension by themselves.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.schemas.contribution_profile import (
    ContributionDimension,
    ContributionProfileResponse,
    ContributionTraceability,
)
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
from app.services.thinking_to_execution import (
    EXCLUDED_MARS_SCOPES,
    build_thinking_to_execution,
)

PRESENTATION_READY_STATUSES = frozenset(
    {
        MERCURY_APPROVED_OVERRIDE,
        MERCURY_APPROVED_RAW,
        MARS_APPROVED_OVERRIDE,
        MARS_APPROVED_RAW,
    }
)

PROFILE_NOTES = (
    "Contribution Profile describes work-style hypotheses and is not a candidate ranking.",
    "No hire/reject recommendation is produced.",
    "This is not a technical-qualification assessment or compatibility percentage.",
)

FRICTION_LIMITATION = (
    "A thinking-to-execution friction pattern qualifies how this contribution may show up."
)

WHY_TEMPLATE = (
    "This contribution appears because current source-backed evidence includes "
    "exact {evidence_kinds} already present in Mercury, Mars, and/or "
    "thinking-to-execution patterns."
)


@dataclass(frozen=True)
class ContributionDimensionSpec:
    key: str
    title: str
    mercury_tags: frozenset[str]
    mars_tags: frozenset[str]
    reinforce_ids: frozenset[str]
    friction_ids: frozenset[str]
    description_template: str


# Exact existing tags and existing TTE pattern ids only.
# technical_ability is excluded: aptitude signal must not become verified skill.
CONTRIBUTION_DIMENSION_SPECS: tuple[ContributionDimensionSpec, ...] = (
    ContributionDimensionSpec(
        key="investigation",
        title="Investigation",
        mercury_tags=frozenset(
            {"analytical_thinking", "insight", "vulnerability_detection"}
        ),
        mars_tags=frozenset(),
        reinforce_ids=frozenset(
            {
                "analysis_to_deliberate_execution",
                "analysis_to_practical_execution",
            }
        ),
        friction_ids=frozenset({"analysis_slower_commitment"}),
        description_template=(
            "{name} may contribute by examining problems analytically "
            "and looking for what is not obvious."
        ),
    ),
    ContributionDimensionSpec(
        key="structuring",
        title="Structuring",
        mercury_tags=frozenset({"planning", "deliberate_processing"}),
        mars_tags=frozenset(
            {"planned_execution", "task_concentration", "strategic_action"}
        ),
        reinforce_ids=frozenset({"analysis_to_deliberate_execution"}),
        friction_ids=frozenset(),
        description_template=(
            "{name} may contribute by organizing work into a planned, "
            "deliberate sequence rather than improvising."
        ),
    ),
    ContributionDimensionSpec(
        key="validation",
        title="Validation",
        mercury_tags=frozenset({"practical_fact_based", "evidence_requirement"}),
        mars_tags=frozenset(),
        reinforce_ids=frozenset(),
        friction_ids=frozenset(),
        description_template=(
            "{name} may contribute by staying close to facts and checking "
            "claims against available evidence."
        ),
    ),
    ContributionDimensionSpec(
        key="execution_momentum",
        title="Execution momentum",
        mercury_tags=frozenset({"fast_thinking"}),
        mars_tags=frozenset({"fast_start", "self_starting"}),
        reinforce_ids=frozenset({"fast_processing_to_fast_action"}),
        friction_ids=frozenset({"fast_processing_slower_commitment"}),
        description_template=(
            "{name} may contribute by moving from thought into action quickly "
            "when starting conditions are clear."
        ),
    ),
    ContributionDimensionSpec(
        key="hands_on_delivery",
        title="Hands-on delivery",
        mercury_tags=frozenset(),
        mars_tags=frozenset({"hands_on_execution"}),
        reinforce_ids=frozenset({"analysis_to_practical_execution"}),
        friction_ids=frozenset(),
        description_template=(
            "{name} may contribute by preferring practical, hands-on execution "
            "over purely abstract planning."
        ),
    ),
)


def _mercury_is_presentation_ready(fact: SourceFact) -> bool:
    return mercury_review_status(fact.id) in PRESENTATION_READY_STATUSES


def _mars_is_presentation_ready(fact: MarsSourceFact) -> bool:
    return mars_review_status(fact.id) in PRESENTATION_READY_STATUSES


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
            if not _mercury_is_presentation_ready(fact):
                continue
            seen.add(fact.id)
            facts.append(fact)
    return tuple(facts)


def _active_mars_facts(profile: MarsSourceProfile) -> tuple[MarsSourceFact, ...]:
    return tuple(
        fact
        for fact in collect_activated_mars_facts(profile)
        if fact.scope not in EXCLUDED_MARS_SCOPES and _mars_is_presentation_ready(fact)
    )


def _facts_with_tags(facts, tags: frozenset[str]):
    if not tags:
        return []
    return [fact for fact in facts if tags.intersection(fact.tags or ())]


def _mercury_provenance(fact: SourceFact) -> str:
    return f"mercury:{fact.factor_type}:{fact.factor_key}"


def _mars_provenance(fact: MarsSourceFact) -> str:
    return f"mars:{fact.provenance_key}"


def _unique_sorted(values: list[str]) -> list[str]:
    return sorted(set(values))


def _root_provenance_keys(mercury_facts, mars_facts) -> set[str]:
    return {
        _mercury_provenance(fact) for fact in mercury_facts
    } | {
        _mars_provenance(fact) for fact in mars_facts
    }


def _resolve_state(
    *,
    mercury_facts: list,
    mars_facts: list,
    reinforce: list[CrossProfilePattern],
    friction: list[CrossProfilePattern],
) -> str | None:
    """Assign state from independent roots; TTE only modifies.

    primary     = at least two independent roots, plus TTE reinforcement
    strong      = at least two independent roots
    supporting  = one independent root, no limiting friction
    conditional = one independent root limited by TTE friction
    None        = no root facts (TTE cannot resurrect a dimension)
    """
    if not mercury_facts and not mars_facts:
        return None
    root_count = len(_root_provenance_keys(mercury_facts, mars_facts))
    sufficient_roots = root_count >= 2
    if sufficient_roots and reinforce:
        return "primary"
    if sufficient_roots:
        return "strong"
    if friction:
        return "conditional"
    return "supporting"


def _evidence_kinds(
    spec: ContributionDimensionSpec,
    mercury_facts,
    mars_facts,
    tte_ids: list[str],
) -> str:
    parts: list[str] = []
    mercury_tags = sorted(
        {
            tag
            for fact in mercury_facts
            for tag in (fact.tags or ())
            if tag in spec.mercury_tags
        }
    )
    mars_tags = sorted(
        {
            tag
            for fact in mars_facts
            for tag in (fact.tags or ())
            if tag in spec.mars_tags
        }
    )
    if mercury_tags:
        parts.append("Mercury tags " + ", ".join(mercury_tags))
    if mars_tags:
        parts.append("Mars tags " + ", ".join(mars_tags))
    if tte_ids:
        parts.append("thinking-to-execution patterns " + ", ".join(tte_ids))
    return "; ".join(parts) if parts else "matching source evidence"


def build_contribution_profile(
    mercury_profile: MercurySourceProfileResponse,
    mars_profile: MarsSourceProfile,
    person: PersonPerspective,
    thinking_to_execution: ThinkingToExecutionSynthesis | None = None,
) -> ContributionProfileResponse:
    """Assemble contribution dimensions from already-built profiles."""
    tte = thinking_to_execution or build_thinking_to_execution(
        mercury_profile, mars_profile, person
    )
    mercury_facts = _active_mercury_facts(mercury_profile)
    mars_facts = _active_mars_facts(mars_profile)
    bridges_by_id = {item.id: item for item in tte.patterns}

    dimensions: list[ContributionDimension] = []
    for spec in CONTRIBUTION_DIMENSION_SPECS:
        mercury_support = _facts_with_tags(mercury_facts, spec.mercury_tags)
        mars_support = _facts_with_tags(mars_facts, spec.mars_tags)
        reinforce = [
            bridges_by_id[pattern_id]
            for pattern_id in spec.reinforce_ids
            if pattern_id in bridges_by_id
        ]
        friction = [
            bridges_by_id[pattern_id]
            for pattern_id in spec.friction_ids
            if pattern_id in bridges_by_id
        ]
        state = _resolve_state(
            mercury_facts=mercury_support,
            mars_facts=mars_support,
            reinforce=reinforce,
            friction=friction,
        )
        if state is None:
            continue
        tte_ids = [item.id for item in reinforce + friction]
        root_fact_ids = _unique_sorted(
            [fact.id for fact in mercury_support] + [fact.id for fact in mars_support]
        )
        limitations: list[str] = []
        if friction:
            limitations.append(FRICTION_LIMITATION)
        dimensions.append(
            ContributionDimension(
                key=spec.key,
                title=spec.title,
                state=state,
                description=fill_person_template(spec.description_template, person),
                mercury_support=[fact.id for fact in mercury_support],
                mars_support=[fact.id for fact in mars_support],
                root_fact_ids=root_fact_ids,
                thinking_to_execution_support=tte_ids,
                mercury_provenance=_unique_sorted(
                    [_mercury_provenance(fact) for fact in mercury_support]
                ),
                mars_provenance=_unique_sorted(
                    [_mars_provenance(fact) for fact in mars_support]
                ),
                why_this_appears=WHY_TEMPLATE.format(
                    evidence_kinds=_evidence_kinds(
                        spec, mercury_support, mars_support, tte_ids
                    )
                ),
                limitations=limitations,
                presentation_ready=True,
            )
        )

    strongest = [
        item.key for item in dimensions if item.state in {"primary", "strong"}
    ]
    supporting = [item.key for item in dimensions if item.state == "supporting"]
    conditional = [item.key for item in dimensions if item.state == "conditional"]
    by_state = {item.state: 0 for item in dimensions}
    for item in dimensions:
        by_state[item.state] = by_state.get(item.state, 0) + 1

    limitations = _unique_sorted(
        list(mercury_profile.limitations or []) + list(mars_profile.limitations or [])
    )
    mercury_ids = {fid for item in dimensions for fid in item.mercury_support}
    mars_ids = {fid for item in dimensions for fid in item.mars_support}
    bridge_ids = {
        fid for item in dimensions for fid in item.thinking_to_execution_support
    }
    return ContributionProfileResponse(
        dimensions=dimensions,
        strongest=strongest,
        supporting=supporting,
        conditional=conditional,
        traceability=ContributionTraceability(
            dimension_count=len(dimensions),
            primary_count=by_state.get("primary", 0),
            strong_count=by_state.get("strong", 0),
            supporting_count=by_state.get("supporting", 0),
            conditional_count=by_state.get("conditional", 0),
            mercury_support_count=len(mercury_ids),
            mars_support_count=len(mars_ids),
            root_fact_count=len(mercury_ids | mars_ids),
            bridge_support_count=len(bridge_ids),
        ),
        limitations=limitations,
        notes=list(PROFILE_NOTES),
    )
