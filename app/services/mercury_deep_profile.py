"""Mercury Deep Profile (M9.5A) — factor-first presentation assembler.

Additive presentation only. Does not recalculate astrology, rewrite source
knowledge, change activation, or replace work/recruiter synthesis sections.

Canonical source ownership:
  sign → Sign block, house → House block, motion → Motion block,
  aspect → that aspect's block.

Aspect interaction synthesis answers:
  What does this aspect ADD, REINFORCE, or CONTRAST relative to base Mercury?

Integrated takeaways may REFERENCE fact ids but must not present source
sentences as new observations.
"""

from __future__ import annotations

from app.schemas.mercury_source_profile import (
    DeepMercuryAdditiveTheme,
    DeepMercuryAspectBlock,
    DeepMercuryAspectIdentity,
    DeepMercuryAspectInteraction,
    DeepMercuryConfiguration,
    DeepMercuryContrastingSignal,
    DeepMercuryFactorBlock,
    DeepMercuryIntegratedTakeaway,
    DeepMercuryReinforcingSignal,
    MercuryDeepProfile,
    MercurySourceProfileResponse,
    SourceFact,
)
from app.schemas.mercury_work_profile import MercuryAspect
from app.services.mercury_human_copy_catalog import (
    STATUS_APPROVED_OVERRIDE,
    STATUS_APPROVED_RAW,
    derive_review_status,
)
from app.services.mercury_source_knowledge import REPEATED_SIGNAL_SPECS

BASE_FACTOR_TYPES = frozenset({"sign", "house", "motion"})
MAX_INTEGRATED_TAKEAWAYS = 5
MAX_HIGHLIGHTS = 5
PRESENTATION_READY_STATUSES = frozenset(
    {STATUS_APPROVED_OVERRIDE, STATUS_APPROVED_RAW}
)

HOUSE_UNAVAILABLE_REASON = (
    "Birth time unknown: Mercury house layer is unavailable "
    "(houses and angles omitted)."
)

SIGN_PURPOSE = "What is the base Mercury mechanism?"
HOUSE_PURPOSE = "Where / through what domain is this Mercury expressed?"
MOTION_PURPOSE = "What processing modifier is present?"

_SIGNAL_TAG_BY_NAME = {
    str(spec["signal"]): str(spec["tag"]) for spec in REPEATED_SIGNAL_SPECS
}


def _aspect_factor_key(aspect: MercuryAspect) -> str:
    return f"{aspect.type}_{aspect.planet}"


def _aspect_title(aspect: MercuryAspect) -> str:
    return f"Mercury {aspect.type} {aspect.planet}"


def _provenance(factor_type: str, factor_key: str) -> str:
    return f"{factor_type}:{factor_key}"


def _labelize(value: str) -> str:
    return value.replace("_", " ")


def _unique_sorted(values: list[str]) -> list[str]:
    return sorted(set(values))


def _activated_facts(facts: list[SourceFact]) -> list[SourceFact]:
    return [fact for fact in facts if fact.activated]


def _fact_ids(facts: list[SourceFact]) -> list[str]:
    return [fact.id for fact in facts]


def _categories(facts: list[SourceFact]) -> list[str]:
    return _unique_sorted([fact.category for fact in facts if fact.category])


def _tags(facts: list[SourceFact]) -> list[str]:
    return _unique_sorted(
        [tag for fact in facts for tag in (fact.tags or ()) if tag]
    )


def _parse_provenance(key: str) -> tuple[str, str]:
    factor_type, _, factor_key = key.partition(":")
    return factor_type, factor_key


def _is_presentation_ready(fact: SourceFact) -> bool:
    if fact.unresolved:
        return False
    return derive_review_status(fact.id) in PRESENTATION_READY_STATUSES


def _primary_tag(fact: SourceFact) -> str:
    tags = sorted(tag for tag in (fact.tags or ()) if tag)
    return tags[0] if tags else ""


def select_highlight_fact_ids(facts: list[SourceFact]) -> list[str]:
    """Deterministic representative subset. Presentation-ready only; no scores."""
    eligible = [fact for fact in facts if _is_presentation_ready(fact)]
    if not eligible:
        return []

    selected: list[str] = []
    used_categories: set[str] = set()
    used_tags: set[str] = set()

    # Pass 1: prefer category diversity, skip same primary tag.
    for fact in eligible:
        if len(selected) >= MAX_HIGHLIGHTS:
            break
        primary = _primary_tag(fact)
        if fact.category in used_categories:
            continue
        if primary and primary in used_tags:
            continue
        selected.append(fact.id)
        used_categories.add(fact.category)
        if primary:
            used_tags.add(primary)

    # Pass 2: fill with unused primary tags (no same-theme padding).
    for fact in eligible:
        if len(selected) >= MAX_HIGHLIGHTS:
            break
        if fact.id in selected:
            continue
        primary = _primary_tag(fact)
        if primary and primary in used_tags:
            continue
        selected.append(fact.id)
        if primary:
            used_tags.add(primary)

    return selected


def _identity_for_aspect(aspect: MercuryAspect) -> DeepMercuryAspectIdentity:
    return DeepMercuryAspectIdentity(
        factor_key=_aspect_factor_key(aspect),
        aspect_type=aspect.type,
        planet=aspect.planet,
        title=_aspect_title(aspect),
        orb_deg=aspect.orb_deg,
    )


def _build_configuration(
    profile: MercurySourceProfileResponse,
) -> DeepMercuryConfiguration:
    calc = profile.calculated
    house_available = bool(calc.birth_time_known and calc.mercury_house is not None)
    return DeepMercuryConfiguration(
        mercury_sign=calc.mercury_sign,
        mercury_house=calc.mercury_house if house_available else None,
        house_available=house_available,
        house_unavailable_reason=None if house_available else HOUSE_UNAVAILABLE_REASON,
        mercury_motion=calc.mercury_motion,
        birth_time_known=calc.birth_time_known,
        aspects=[_identity_for_aspect(aspect) for aspect in calc.aspects],
    )


def _factor_block(
    *,
    factor_type: str,
    factor_key: str,
    title: str,
    purpose: str,
    availability: str,
    facts: list[SourceFact],
    unavailable_reason: str | None = None,
) -> DeepMercuryFactorBlock:
    return DeepMercuryFactorBlock(
        factor_type=factor_type,  # type: ignore[arg-type]
        factor_key=factor_key,
        title=title,
        purpose=purpose,
        availability=availability,  # type: ignore[arg-type]
        unavailable_reason=unavailable_reason,
        fact_ids=_fact_ids(facts),
        highlight_fact_ids=select_highlight_fact_ids(facts),
        provenance=_provenance(factor_type, factor_key) if factor_key else f"{factor_type}:",
        categories=_categories(facts),
        tags=_tags(facts),
    )


def _build_sign_block(profile: MercurySourceProfileResponse) -> DeepMercuryFactorBlock:
    calc = profile.calculated
    sign = calc.mercury_sign
    if not sign:
        return _factor_block(
            factor_type="sign",
            factor_key="",
            title="Mercury Sign",
            purpose=SIGN_PURPOSE,
            availability="unavailable",
            facts=[],
            unavailable_reason="Mercury sign is not available for this profile.",
        )
    return _factor_block(
        factor_type="sign",
        factor_key=sign,
        title=f"Mercury in {sign}",
        purpose=SIGN_PURPOSE,
        availability="available",
        facts=_activated_facts(list(profile.sign_facts)),
    )


def _build_house_block(profile: MercurySourceProfileResponse) -> DeepMercuryFactorBlock:
    calc = profile.calculated
    if not calc.birth_time_known or calc.mercury_house is None:
        return _factor_block(
            factor_type="house",
            factor_key="",
            title="Mercury House",
            purpose=HOUSE_PURPOSE,
            availability="unavailable",
            facts=[],
            unavailable_reason=HOUSE_UNAVAILABLE_REASON,
        )
    house_key = str(calc.mercury_house)
    return _factor_block(
        factor_type="house",
        factor_key=house_key,
        title=f"Mercury in House {house_key}",
        purpose=HOUSE_PURPOSE,
        availability="available",
        facts=_activated_facts(list(profile.house_facts)),
    )


def _build_motion_block(profile: MercurySourceProfileResponse) -> DeepMercuryFactorBlock:
    calc = profile.calculated
    motion = calc.mercury_motion or ""
    facts = _activated_facts(list(profile.motion_facts))
    if not motion:
        return _factor_block(
            factor_type="motion",
            factor_key="",
            title="Mercury Motion",
            purpose=MOTION_PURPOSE,
            availability="unavailable",
            facts=[],
            unavailable_reason="Mercury motion is not available for this profile.",
        )
    if motion.lower() == "direct" and not facts:
        return _factor_block(
            factor_type="motion",
            factor_key=motion,
            title="Mercury Direct",
            purpose=MOTION_PURPOSE,
            availability="neutral_default",
            facts=[],
        )
    return _factor_block(
        factor_type="motion",
        factor_key=motion,
        title=f"Mercury {motion.capitalize()}",
        purpose=MOTION_PURPOSE,
        availability="available",
        facts=facts,
    )


def _facts_by_id(profile: MercurySourceProfileResponse) -> dict[str, SourceFact]:
    return {
        fact.id: fact
        for fact in (
            list(profile.sign_facts)
            + list(profile.house_facts)
            + list(profile.motion_facts)
            + list(profile.aspect_facts)
        )
    }


def _aspect_facts_by_key(
    profile: MercurySourceProfileResponse,
) -> dict[str, list[SourceFact]]:
    grouped: dict[str, list[SourceFact]] = {}
    for fact in _activated_facts(list(profile.aspect_facts)):
        grouped.setdefault(fact.factor_key, []).append(fact)
    return grouped


def _base_fact_ids(profile: MercurySourceProfileResponse) -> set[str]:
    return {
        fact.id
        for fact in (
            list(profile.sign_facts)
            + list(profile.house_facts)
            + list(profile.motion_facts)
        )
        if fact.activated
    }


def _base_provenance_keys(profile: MercurySourceProfileResponse) -> set[str]:
    keys: set[str] = set()
    calc = profile.calculated
    if calc.mercury_sign:
        keys.add(_provenance("sign", calc.mercury_sign))
    if calc.birth_time_known and calc.mercury_house is not None:
        keys.add(_provenance("house", str(calc.mercury_house)))
    if calc.mercury_motion:
        keys.add(_provenance("motion", calc.mercury_motion))
    return keys


def _base_tags(profile: MercurySourceProfileResponse) -> set[str]:
    """Activated, resolved base tags only — used to detect additive themes."""
    tags: set[str] = set()
    for fact in (
        list(profile.sign_facts)
        + list(profile.house_facts)
        + list(profile.motion_facts)
    ):
        if not fact.activated or fact.unresolved:
            continue
        tags.update(tag for tag in (fact.tags or ()) if tag)
    return tags


def _build_additive_themes(
    *,
    aspect_facts: list[SourceFact],
    base_tags: set[str],
) -> list[DeepMercuryAdditiveTheme]:
    """ADD = presentation-ready aspect themes not already in base Mercury."""
    by_tag: dict[str, list[str]] = {}
    for fact in aspect_facts:
        if not _is_presentation_ready(fact):
            continue
        for tag in sorted(tag for tag in (fact.tags or ()) if tag):
            if tag in base_tags:
                continue
            by_tag.setdefault(tag, []).append(fact.id)
    return [
        DeepMercuryAdditiveTheme(
            tag=tag,
            aspect_fact_ids=_unique_sorted(fact_ids),
        )
        for tag, fact_ids in sorted(by_tag.items())
    ]


def _interaction_statement(
    *,
    aspect_title: str,
    adds: list[DeepMercuryAdditiveTheme],
    reinforcing: list[DeepMercuryReinforcingSignal],
    contrasting: list[DeepMercuryContrastingSignal],
) -> str | None:
    parts: list[str] = []
    if adds:
        themes = ", ".join(_labelize(item.tag) for item in adds[:5])
        more = "" if len(adds) <= 5 else f" (+{len(adds) - 5} more)"
        parts.append(
            f"{aspect_title} adds {themes}{more} not already present in the "
            f"base Mercury configuration."
        )
    if reinforcing:
        signals = ", ".join(_labelize(item.signal) for item in reinforcing)
        bases = _unique_sorted(
            [key for item in reinforcing for key in item.base_provenance_keys]
        )
        base_labels = ", ".join(_labelize(key.split(":", 1)[-1]) for key in bases)
        layer_bits: list[str] = []
        for key in bases:
            factor_type, _ = _parse_provenance(key)
            if factor_type not in layer_bits:
                layer_bits.append(factor_type)
        layers = ", ".join(layer_bits)
        parts.append(
            f"{aspect_title} reinforces the {signals} theme already present "
            f"in base Mercury ({layers}: {base_labels})."
        )
    if contrasting:
        pairs = "; ".join(
            f"{_labelize(item.tag_a)} vs {_labelize(item.tag_b)}"
            for item in contrasting
        )
        parts.append(
            f"{aspect_title} participates in a supported tension with base "
            f"Mercury factors ({pairs})."
        )
    if not parts:
        return None
    return " ".join(parts)


def _build_aspect_interaction(
    *,
    aspect_key: str,
    aspect_title: str,
    aspect_facts: list[SourceFact],
    profile: MercurySourceProfileResponse,
    facts_by_id: dict[str, SourceFact],
) -> DeepMercuryAspectInteraction:
    aspect_fact_ids = {fact.id for fact in aspect_facts}
    aspect_prov = _provenance("aspect", aspect_key)
    base_provs = _base_provenance_keys(profile)
    base_ids = _base_fact_ids(profile)
    base_tags = _base_tags(profile)

    adds = _build_additive_themes(aspect_facts=aspect_facts, base_tags=base_tags)

    reinforcing: list[DeepMercuryReinforcingSignal] = []
    for signal in profile.repeated_signals:
        sources = set(signal.sources)
        if aspect_prov not in sources:
            continue
        base_sources = sorted(sources & base_provs)
        if not base_sources:
            continue
        aspect_ids = sorted(fid for fid in signal.fact_ids if fid in aspect_fact_ids)
        base_support = sorted(fid for fid in signal.fact_ids if fid in base_ids)
        if not aspect_ids or not base_support:
            continue
        tag = _SIGNAL_TAG_BY_NAME.get(signal.signal, signal.signal)
        reinforcing.append(
            DeepMercuryReinforcingSignal(
                signal=signal.signal,
                tag=tag,
                aspect_fact_ids=aspect_ids,
                base_fact_ids=base_support,
                base_provenance_keys=base_sources,
            )
        )

    contrasting: list[DeepMercuryContrastingSignal] = []
    for pair in profile.contrasting_signals:
        side_a = set(pair.facts_a)
        side_b = set(pair.facts_b)
        aspect_on_a = sorted(aspect_fact_ids & side_a)
        aspect_on_b = sorted(aspect_fact_ids & side_b)
        base_on_a = sorted(base_ids & side_a)
        base_on_b = sorted(base_ids & side_b)
        if aspect_on_a and base_on_b:
            aspect_ids = aspect_on_a
            base_support = base_on_b
        elif aspect_on_b and base_on_a:
            aspect_ids = aspect_on_b
            base_support = base_on_a
        else:
            continue
        base_keys = _unique_sorted(
            [
                _provenance(facts_by_id[fid].factor_type, facts_by_id[fid].factor_key)
                for fid in base_support
                if fid in facts_by_id
            ]
        )
        contrasting.append(
            DeepMercuryContrastingSignal(
                tag_a=pair.tag_a,
                tag_b=pair.tag_b,
                aspect_fact_ids=aspect_ids,
                base_fact_ids=base_support,
                base_provenance_keys=base_keys,
            )
        )

    reinforcing = sorted(reinforcing, key=lambda item: item.signal)
    contrasting = sorted(contrasting, key=lambda item: (item.tag_a, item.tag_b))
    if not adds and not reinforcing and not contrasting:
        return DeepMercuryAspectInteraction(available=False)

    supporting = _unique_sorted(
        [fid for item in adds for fid in item.aspect_fact_ids]
        + [
            fid
            for item in reinforcing
            for fid in item.aspect_fact_ids + item.base_fact_ids
        ]
        + [
            fid
            for item in contrasting
            for fid in item.aspect_fact_ids + item.base_fact_ids
        ]
    )
    provenance_keys = _unique_sorted(
        [aspect_prov]
        + [key for item in reinforcing for key in item.base_provenance_keys]
        + [key for item in contrasting for key in item.base_provenance_keys]
    )
    statement = _interaction_statement(
        aspect_title=aspect_title,
        adds=adds,
        reinforcing=reinforcing,
        contrasting=contrasting,
    )
    return DeepMercuryAspectInteraction(
        available=True,
        adds=adds,
        reinforcing=reinforcing,
        contrasting=contrasting,
        statement=statement,
        supporting_fact_ids=supporting,
        provenance_keys=provenance_keys,
    )


def _build_aspect_blocks(
    profile: MercurySourceProfileResponse,
) -> list[DeepMercuryAspectBlock]:
    grouped = _aspect_facts_by_key(profile)
    facts_by_id = _facts_by_id(profile)
    blocks: list[DeepMercuryAspectBlock] = []
    for aspect in profile.calculated.aspects:
        identity = _identity_for_aspect(aspect)
        facts = grouped.get(identity.factor_key, [])
        interaction = _build_aspect_interaction(
            aspect_key=identity.factor_key,
            aspect_title=identity.title,
            aspect_facts=facts,
            profile=profile,
            facts_by_id=facts_by_id,
        )
        blocks.append(
            DeepMercuryAspectBlock(
                identity=identity,
                fact_ids=_fact_ids(facts),
                highlight_fact_ids=select_highlight_fact_ids(facts),
                provenance=_provenance("aspect", identity.factor_key),
                categories=_categories(facts),
                tags=_tags(facts),
                interaction=interaction,
            )
        )
    return blocks


def _factor_type_span(sources: list[str]) -> set[str]:
    return {_parse_provenance(key)[0] for key in sources if ":" in key}


def _build_integrated(
    profile: MercurySourceProfileResponse,
    aspect_blocks: list[DeepMercuryAspectBlock],
) -> list[DeepMercuryIntegratedTakeaway]:
    """Concise synthesis from reinforcement, contrast, and aspect additions."""
    takeaways: list[DeepMercuryIntegratedTakeaway] = []

    for signal in sorted(profile.repeated_signals, key=lambda item: item.signal):
        types = _factor_type_span(signal.sources)
        if len(types) < 2:
            continue
        layers = sorted(
            types,
            key=lambda item: ("sign", "house", "motion", "aspect").index(item)
            if item in {"sign", "house", "motion", "aspect"}
            else 99,
        )
        layer_label = " + ".join(layers)
        text = (
            f"The {_labelize(signal.signal)} theme is supported across "
            f"{layer_label} ({', '.join(signal.sources)})."
        )
        takeaways.append(
            DeepMercuryIntegratedTakeaway(
                key=f"repeat:{signal.signal}",
                text=text,
                basis="repeated_signal",
                signal=signal.signal,
                supporting_fact_ids=list(signal.fact_ids),
                provenance_keys=list(signal.sources),
            )
        )

    facts_by_id = _facts_by_id(profile)
    for pair in sorted(
        profile.contrasting_signals, key=lambda item: (item.tag_a, item.tag_b)
    ):
        all_ids = list(pair.facts_a) + list(pair.facts_b)
        provs = _unique_sorted(
            [
                _provenance(facts_by_id[fid].factor_type, facts_by_id[fid].factor_key)
                for fid in all_ids
                if fid in facts_by_id
            ]
        )
        if len(_factor_type_span(provs)) < 2:
            continue
        text = (
            f"Supported tension between {_labelize(pair.tag_a)} and "
            f"{_labelize(pair.tag_b)} across {', '.join(provs)}."
        )
        takeaways.append(
            DeepMercuryIntegratedTakeaway(
                key=f"contrast:{pair.tag_a}:{pair.tag_b}",
                text=text,
                basis="contrasting_signal",
                signal=f"{pair.tag_a}_vs_{pair.tag_b}",
                supporting_fact_ids=_unique_sorted(all_ids),
                provenance_keys=provs,
            )
        )

    for block in aspect_blocks:
        adds = block.interaction.adds
        if not adds:
            continue
        # One concise additive takeaway per aspect with supported ADD themes.
        theme_labels = ", ".join(_labelize(item.tag) for item in adds[:3])
        more = "" if len(adds) <= 3 else f" (+{len(adds) - 3} more)"
        support_ids = _unique_sorted(
            [fid for item in adds for fid in item.aspect_fact_ids]
        )
        takeaways.append(
            DeepMercuryIntegratedTakeaway(
                key=f"add:{block.identity.factor_key}",
                text=(
                    f"{block.identity.title} adds {theme_labels}{more} as an "
                    f"aspect-backed modification of Mercury (not a base "
                    f"sign/house/motion trait)."
                ),
                basis="aspect_addition",
                signal=adds[0].tag,
                supporting_fact_ids=support_ids,
                provenance_keys=[block.provenance],
            )
        )

    def _rank(item: DeepMercuryIntegratedTakeaway) -> tuple:
        has_sign = any(key.startswith("sign:") for key in item.provenance_keys)
        if item.basis == "repeated_signal":
            basis_rank = 0
        elif item.basis == "contrasting_signal":
            basis_rank = 1
        else:
            basis_rank = 2
        return (basis_rank, 0 if has_sign else 1, item.key)

    # Prefer covering additive aspects that would otherwise be absent from
    # the selected cross-factor set when slots remain.
    ordered = sorted(takeaways, key=_rank)
    selected: list[DeepMercuryIntegratedTakeaway] = []
    selected_keys: set[str] = set()
    covered_aspects: set[str] = set()

    def _note_aspect_coverage(item: DeepMercuryIntegratedTakeaway) -> None:
        for key in item.provenance_keys:
            if key.startswith("aspect:"):
                covered_aspects.add(key.partition(":")[2])

    for item in ordered:
        if len(selected) >= MAX_INTEGRATED_TAKEAWAYS:
            break
        if item.basis == "aspect_addition":
            continue
        selected.append(item)
        selected_keys.add(item.key)
        _note_aspect_coverage(item)

    for item in ordered:
        if len(selected) >= MAX_INTEGRATED_TAKEAWAYS:
            break
        if item.basis != "aspect_addition":
            continue
        aspect_key = item.key.partition(":")[2]
        if aspect_key in covered_aspects:
            # Aspect already represented via reinforce/contrast; still allow
            # additive takeaway only if slots remain after uncovered ones.
            continue
        selected.append(item)
        selected_keys.add(item.key)
        covered_aspects.add(aspect_key)

    # Fill remaining slots with additive takeaways for already-covered aspects
    # only if space remains and they were not selected.
    if len(selected) < MAX_INTEGRATED_TAKEAWAYS:
        for item in ordered:
            if len(selected) >= MAX_INTEGRATED_TAKEAWAYS:
                break
            if item.basis != "aspect_addition" or item.key in selected_keys:
                continue
            selected.append(item)
            selected_keys.add(item.key)

    return sorted(selected, key=_rank)[:MAX_INTEGRATED_TAKEAWAYS]


def build_mercury_deep_profile(
    profile: MercurySourceProfileResponse,
) -> MercuryDeepProfile:
    """Assemble factor-first Deep Mercury presentation from an existing profile."""
    configuration = _build_configuration(profile)
    aspects = _build_aspect_blocks(profile)
    return MercuryDeepProfile(
        configuration=configuration,
        sign=_build_sign_block(profile),
        house=_build_house_block(profile),
        motion=_build_motion_block(profile),
        aspects=aspects,
        integrated=_build_integrated(profile, aspects),
        limitations=list(profile.limitations or []),
    )
