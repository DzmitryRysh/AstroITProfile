"""Mercury Source Profile v2 — activate source facts from calculated Mercury data."""

from __future__ import annotations

from collections import defaultdict

from app.schemas.mercury_source_profile import (
    CalculatedMercurySnapshot,
    ContrastingSignalPair,
    MercurySourceProfileRequest,
    MercurySourceProfileResponse,
    RepeatedSignal,
    SourceCoverage,
    SourceFact,
)
from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_source_knowledge import (
    ALL_SOURCE_FACTS,
    ASPECT_PACK_ALIASES,
    CONTRAST_PAIRS,
    REPEATED_SIGNAL_SPECS,
    SUPPORTED_ASPECT_KEYS,
    SUPPORTED_HOUSE_KEYS,
    SUPPORTED_MOTION_KEYS,
    SUPPORTED_SIGN_KEYS,
    SourceFactDef,
)
from app.services.mercury_work_profile import build_mercury_work_profile

HARD_ASPECT_TYPES = {"square", "opposition"}


def _aspect_factor_key(aspect: MercuryAspect) -> str:
    return f"{aspect.type}_{aspect.planet}"


def is_hard_aspected(aspects: list[MercuryAspect]) -> bool:
    return any(item.type in HARD_ASPECT_TYPES for item in aspects)


def _to_fact(
    definition: SourceFactDef,
    *,
    activated: bool,
    factor_key_override: str | None = None,
) -> SourceFact:
    return SourceFact(
        id=definition.id,
        factor_type=definition.factor_type,  # type: ignore[arg-type]
        factor_key=factor_key_override or definition.factor_key,
        category=definition.category,
        text=definition.text,
        polarity=definition.polarity,  # type: ignore[arg-type]
        tags=list(definition.tags),
        source_reference=definition.source_reference,
        activation_condition=definition.activation_condition,
        activated=activated,
        unresolved=definition.unresolved,
    )


def _match_definitions(
    *,
    factor_type: str,
    factor_key: str,
    hard_aspected: bool,
    aspect_orb_deg: float | None = None,
) -> list[SourceFact]:
    catalog_key = factor_key
    factor_key_override: str | None = None
    if factor_type == "aspect" and factor_key in ASPECT_PACK_ALIASES:
        catalog_key = ASPECT_PACK_ALIASES[factor_key]
        factor_key_override = factor_key

    selected: list[SourceFact] = []
    for definition in ALL_SOURCE_FACTS:
        if definition.factor_type != factor_type or definition.factor_key != catalog_key:
            continue
        condition = definition.activation_condition
        if condition is None:
            selected.append(
                _to_fact(
                    definition,
                    activated=True,
                    factor_key_override=factor_key_override,
                )
            )
            continue
        if condition == "hard_aspected":
            if hard_aspected:
                selected.append(
                    _to_fact(
                        definition,
                        activated=True,
                        factor_key_override=factor_key_override,
                    )
                )
            continue
        if condition == "sun_mercury_combustion_orb_lt_5":
            # Deterministic Bioastrology combustion: conjunction orb strictly < 5°.
            # Does not change the engine conjunction orb (6°).
            if aspect_orb_deg is not None and aspect_orb_deg < 5.0:
                selected.append(
                    _to_fact(
                        definition,
                        activated=True,
                        factor_key_override=factor_key_override,
                    )
                )
            continue
        if condition in {
            "pluto_strength_unresolved",
            "strength_unresolved",
            "creative_core_strength_unresolved",
            "female_chart_context_unresolved",
            "intellectual_work_context_unresolved",
            "external_affliction_context_unresolved",
        }:
            # Always include when this aspect factor is present; leave unresolved.
            # No strength / winner / creative-core / gender / intellectual-work /
            # external-affliction resolver is applied.
            selected.append(
                _to_fact(
                    definition,
                    activated=True,
                    factor_key_override=factor_key_override,
                )
            )
            continue
    return selected


def _provenance_key(fact: SourceFact) -> str:
    return f"{fact.factor_type}:{fact.factor_key}"


def detect_repeated_signals(facts: list[SourceFact]) -> list[RepeatedSignal]:
    active = [item for item in facts if item.activated and not item.unresolved]
    signals: list[RepeatedSignal] = []

    for spec in REPEATED_SIGNAL_SPECS:
        tag = spec["tag"]
        by_factor: dict[str, list[SourceFact]] = defaultdict(list)
        for fact in active:
            if tag in fact.tags:
                by_factor[_provenance_key(fact)].append(fact)
        if len(by_factor) < int(spec["min_factor_keys"]):
            continue
        sources = sorted(by_factor.keys())
        fact_ids = sorted({fact.id for group in by_factor.values() for fact in group})
        signals.append(
            RepeatedSignal(
                signal=spec["signal"],
                source_count=len(sources),
                sources=sources,
                fact_ids=fact_ids,
            )
        )
    return signals


def detect_contrasting_signals(facts: list[SourceFact]) -> list[ContrastingSignalPair]:
    active = [item for item in facts if item.activated]
    pairs: list[ContrastingSignalPair] = []
    for tag_a, tag_b in CONTRAST_PAIRS:
        facts_a = [item.id for item in active if tag_a in item.tags]
        facts_b = [item.id for item in active if tag_b in item.tags]
        if facts_a and facts_b:
            pairs.append(
                ContrastingSignalPair(
                    tag_a=tag_a,
                    tag_b=tag_b,
                    facts_a=sorted(set(facts_a)),
                    facts_b=sorted(set(facts_b)),
                )
            )
    return pairs


def _coverage_for(factors: MercurySourceFactors) -> SourceCoverage:
    covered: list[str] = []
    missing: list[str] = []

    if factors.mercury_sign:
        key = f"sign:{factors.mercury_sign}"
        if factors.mercury_sign in SUPPORTED_SIGN_KEYS:
            covered.append(key)
        else:
            missing.append(key)

    if factors.mercury_house is not None:
        house_key = str(factors.mercury_house)
        key = f"house:{house_key}"
        if house_key in SUPPORTED_HOUSE_KEYS:
            covered.append(key)
        else:
            missing.append(key)

    if factors.mercury_motion:
        key = f"motion:{factors.mercury_motion}"
        if factors.mercury_motion in SUPPORTED_MOTION_KEYS:
            covered.append(key)
        elif factors.mercury_motion == "direct":
            # Direct is the neutral default calculated state, not a missing source pack.
            pass
        else:
            missing.append(key)

    for aspect in factors.aspects:
        aspect_key = _aspect_factor_key(aspect)
        key = f"aspect:{aspect_key}"
        if aspect_key in SUPPORTED_ASPECT_KEYS:
            covered.append(key)
        else:
            missing.append(key)

    status = "complete" if not missing else "partial"
    return SourceCoverage(status=status, covered_factors=covered, missing_factors=missing)


def build_source_profile_from_factors(
    factors: MercurySourceFactors,
    *,
    base_limitations: list[str] | None = None,
) -> MercurySourceProfileResponse:
    hard = is_hard_aspected(list(factors.aspects))
    sign_facts: list[SourceFact] = []
    house_facts: list[SourceFact] = []
    motion_facts: list[SourceFact] = []
    aspect_facts: list[SourceFact] = []
    limitations = list(base_limitations or [])

    if factors.mercury_sign in SUPPORTED_SIGN_KEYS:
        sign_facts = _match_definitions(
            factor_type="sign",
            factor_key=factors.mercury_sign or "",
            hard_aspected=hard,
        )
    elif factors.mercury_sign:
        limitations.append(
            f"Source coverage for Mercury in {factors.mercury_sign} is not implemented in v2."
        )

    if factors.mercury_house is not None:
        house_key = str(factors.mercury_house)
        if house_key in SUPPORTED_HOUSE_KEYS:
            house_facts = _match_definitions(
                factor_type="house",
                factor_key=house_key,
                hard_aspected=hard,
            )
        else:
            limitations.append(
                f"Source coverage for Mercury in house {factors.mercury_house} is not implemented in v2."
            )

    if factors.mercury_motion in SUPPORTED_MOTION_KEYS:
        motion_facts = _match_definitions(
            factor_type="motion",
            factor_key=factors.mercury_motion or "",
            hard_aspected=hard,
        )
    elif factors.mercury_motion and factors.mercury_motion != "direct":
        limitations.append(
            f"Source coverage for Mercury motion '{factors.mercury_motion}' is not implemented in v2."
        )

    for aspect in factors.aspects:
        aspect_key = _aspect_factor_key(aspect)
        if aspect_key in SUPPORTED_ASPECT_KEYS:
            aspect_facts.extend(
                _match_definitions(
                    factor_type="aspect",
                    factor_key=aspect_key,
                    hard_aspected=hard,
                    aspect_orb_deg=aspect.orb_deg,
                )
            )
        else:
            limitations.append(
                f"Source coverage for Mercury {aspect.type} {aspect.planet} is not implemented in v2."
            )

    all_facts = sign_facts + house_facts + motion_facts + aspect_facts
    conditional = [item for item in all_facts if item.unresolved]
    repeated = detect_repeated_signals(all_facts)
    contrasting = detect_contrasting_signals(all_facts)
    coverage = _coverage_for(factors)

    return MercurySourceProfileResponse(
        calculated=CalculatedMercurySnapshot(
            mercury_sign=factors.mercury_sign,
            mercury_element=factors.mercury_element,
            mercury_house=factors.mercury_house,
            mercury_motion=factors.mercury_motion,
            birth_time_known=factors.birth_time_known,
            aspects=list(factors.aspects),
            hard_aspected=hard,
        ),
        sign_facts=sign_facts,
        house_facts=house_facts,
        motion_facts=motion_facts,
        aspect_facts=aspect_facts,
        repeated_signals=repeated,
        conditional_unresolved=conditional,
        contrasting_signals=contrasting,
        coverage=coverage,
        limitations=limitations,
    )


def build_mercury_source_profile(
    payload: MercurySourceProfileRequest,
) -> MercurySourceProfileResponse:
    """Calculate Mercury via existing engine, then attach source-first profile."""
    work = build_mercury_work_profile(payload)
    return build_source_profile_from_factors(
        work.source_factors,
        base_limitations=list(work.limitations),
    )
