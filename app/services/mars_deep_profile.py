"""Mars Deep Profile (M10.5 Phase 2A) — ownership / presentation assembler.

Additive presentation only. Does not recalculate astrology, rewrite source
knowledge, change work activation (`activated`), or alter TTE / Contribution.

Visibility concepts (kept separate):
  canonical match → chart factor matches catalog definition
  personal visibility → may appear on Deep Mars fact_ids
  narrative eligibility → may drive future human synthesis / highlights
  work activation → existing activated WORK_CORE / WORK_DETAIL only
"""

from __future__ import annotations

from app.schemas.mars_source_profile import (
    DeepMarsAdditiveTheme,
    DeepMarsAspectBlock,
    DeepMarsAspectIdentity,
    DeepMarsAspectInteraction,
    DeepMarsConfiguration,
    DeepMarsFactRef,
    DeepMarsFactorBlock,
    DeepMarsIntegratedTakeaway,
    DeepMarsReinforcingSignal,
    MarsDeepProfile,
    MarsPresentationLane,
    MarsSourceFact,
    MarsSourceProfileResponse,
)
from app.services.mars_facts import aspect_factor_key
from app.services.mars_human_copy_catalog import (
    STATUS_APPROVED_OVERRIDE,
    STATUS_APPROVED_RAW,
    derive_review_status,
)
from app.services.mars_source_knowledge import (
    ALL_MARS_SOURCE_FACTS,
    BIO_PAIR_PACKS,
    BIO_PAIR_PLANETS,
    MARS_MAJOR_ASPECT_TYPES,
    MARS_TENSE_ASPECT_TYPES,
    WORK_PROFILE_SCOPES,
    MarsSourceFactDef,
)

MAX_HIGHLIGHTS = 5
MAX_INTEGRATED_TAKEAWAYS = 4
PRESENTATION_READY_STATUSES = frozenset(
    {STATUS_APPROVED_OVERRIDE, STATUS_APPROVED_RAW}
)

HOUSE_UNAVAILABLE_REASON = (
    "Birth time unknown: Mars house layer is unavailable "
    "(houses and angles omitted)."
)

SIGN_PURPOSE = "What is the base Mars drive / initiation style?"
HOUSE_PURPOSE = "Where / through what domain is this Mars expressed?"
MOTION_PURPOSE = "What action / drive modifier is present?"

# Explicit sensitive personal/source claims (Phase 1.5 inventory).
# Remain personal-visible when matched; never narrative-eligible in 2A.
SENSITIVE_SOURCE_FACT_IDS = frozenset(
    {
        "mars_aquarius_source_democracy_liberalism_irresponsibility",
        "mars_h1_source_close_ascendant_surgical_birth",
        "mars_h3_source_transport_accidents_injuries",
        "mars_h4_source_fire_destruction_risk",
        "mars_h4_source_household_injury_theft_tragedy",
        "mars_h6_source_acute_inflammatory_illness",
        "mars_h6_source_illness_activity_imbalance",
        "mars_h8_source_injury_fire_aggression_danger",
        "mars_h12_source_hidden_violence",
        "mars_h12_affliction_criminal_fraud_activity",
        "mars_h7_affliction_early_marriage_divorce",
        "mars_h4_strong_affliction_domestic_tyranny",
        "mars_h3_harmonious_mars_fast_driving",
        "mars_rx_sexual_temperament_suppression",
        "mars_rx_auto_aggression",
        "mars_neptune_bio_hypnosis_extrasensory",
        "mars_neptune_bio_medical_healing",
        "mars_pluto_bio_hypnosis_extrasensory",
        "mars_pluto_bio_medical_healing",
        "mars_uranus_bio_hypnosis_extrasensory",
    }
)


def _provenance(factor_type: str, factor_key: str) -> str:
    return f"{factor_type}:{factor_key}"


def _unique_sorted(values: list[str]) -> list[str]:
    return sorted(set(values))


def _is_presentation_ready(fact: MarsSourceFact) -> bool:
    if fact.unresolved:
        return False
    return derive_review_status(fact.id) in PRESENTATION_READY_STATUSES


def derive_presentation_lane(fact: MarsSourceFact) -> MarsPresentationLane:
    """Presentation-layer lane. Does not mutate canonical source facts."""
    if fact.unresolved:
        return "unresolved"
    if fact.scope == "PERSONAL_MARS" or fact.id in SENSITIVE_SOURCE_FACT_IDS:
        return "sensitive_source"
    if fact.scope == "SOURCE_ONLY" or fact.category == "source_specific":
        return "source_specific"
    return "core"


def is_narrative_eligible(fact: MarsSourceFact) -> bool:
    if fact.unresolved:
        return False
    return derive_presentation_lane(fact) == "core"


def _def_to_schema_fact(
    definition: MarsSourceFactDef,
    *,
    factor_key: str,
    activated: bool,
) -> MarsSourceFact:
    return MarsSourceFact(
        id=definition.id,
        factor_type=definition.factor_type,  # type: ignore[arg-type]
        factor_key=factor_key,
        category=definition.category,
        text=definition.text,
        polarity=definition.polarity,  # type: ignore[arg-type]
        scope=definition.scope,  # type: ignore[arg-type]
        tags=list(definition.tags or ()),
        source_reference=definition.source_reference,
        activation_condition=definition.activation_condition,
        activated=activated,
        unresolved=bool(definition.unresolved),
    )


def match_non_work_personal_facts(
    *,
    factor_type: str,
    factor_key: str,
) -> tuple[list[MarsSourceFact], list[MarsSourceFact]]:
    """Chart-matched SOURCE_ONLY / PERSONAL_MARS without work activation.

    Returns (personal_visible_resolved, unresolved_evidence).
    Never sets activated=True.
    """
    visible: list[MarsSourceFact] = []
    unresolved: list[MarsSourceFact] = []
    for definition in ALL_MARS_SOURCE_FACTS:
        if definition.factor_type != factor_type or definition.factor_key != factor_key:
            continue
        if definition.scope in WORK_PROFILE_SCOPES:
            continue
        fact = _def_to_schema_fact(
            definition,
            factor_key=factor_key,
            activated=False,
        )
        if definition.unresolved:
            unresolved.append(fact)
        else:
            visible.append(fact)
    return visible, unresolved


def match_non_work_bio_aspect_facts(
    *,
    calc_key: str,
    planet: str,
) -> tuple[list[MarsSourceFact], list[MarsSourceFact]]:
    """Non-work Bio pair facts for a calculated Mars aspect to planet."""
    visible: list[MarsSourceFact] = []
    unresolved: list[MarsSourceFact] = []
    if planet not in BIO_PAIR_PLANETS:
        return visible, unresolved
    for definition in BIO_PAIR_PACKS[planet]:
        if definition.scope in WORK_PROFILE_SCOPES:
            continue
        fact = _def_to_schema_fact(
            definition,
            factor_key=calc_key,
            activated=False,
        )
        if definition.unresolved:
            unresolved.append(fact)
        else:
            visible.append(fact)
    return visible, unresolved


def _primary_tag(fact: MarsSourceFact) -> str:
    tags = sorted(tag for tag in (fact.tags or ()) if tag)
    return tags[0] if tags else ""


def select_highlight_fact_ids(facts: list[MarsSourceFact]) -> list[str]:
    """Deterministic highlights from narrative-eligible presentation-ready facts."""
    eligible = [
        fact
        for fact in facts
        if is_narrative_eligible(fact) and _is_presentation_ready(fact)
    ]
    if not eligible:
        return []

    selected: list[str] = []
    used_categories: set[str] = set()
    used_tags: set[str] = set()

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

    if len(selected) < MAX_HIGHLIGHTS:
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


def _categories(facts: list[MarsSourceFact]) -> list[str]:
    return _unique_sorted([fact.category for fact in facts if fact.category])


def _tags(facts: list[MarsSourceFact]) -> list[str]:
    return _unique_sorted(
        [tag for fact in facts for tag in (fact.tags or ()) if tag]
    )


def _build_fact_refs(facts: list[MarsSourceFact]) -> list[DeepMarsFactRef]:
    return [
        DeepMarsFactRef(
            fact_id=fact.id,
            presentation_lane=derive_presentation_lane(fact),
            scope=fact.scope,  # type: ignore[arg-type]
            category=fact.category,
            activated=fact.activated,
            unresolved=fact.unresolved,
        )
        for fact in sorted(facts, key=lambda item: item.id)
    ]


def _partition_factor_facts(
    *,
    work_facts: list[MarsSourceFact],
    personal_non_work: list[MarsSourceFact],
    unresolved: list[MarsSourceFact],
) -> tuple[list[MarsSourceFact], list[MarsSourceFact], list[MarsSourceFact], list[MarsSourceFact]]:
    """Returns personal_visible, work, narrative_eligible, unresolved_evidence."""
    work = [fact for fact in work_facts if fact.activated]
    # Deduplicate by id (work wins for activated flag on shared ids — none expected).
    by_id: dict[str, MarsSourceFact] = {fact.id: fact for fact in personal_non_work}
    for fact in work:
        by_id[fact.id] = fact
    personal_visible = [
        fact for fact in by_id.values() if not fact.unresolved
    ]
    narrative = [fact for fact in personal_visible if is_narrative_eligible(fact)]
    unresolved_evidence = sorted(
        {fact.id: fact for fact in unresolved}.values(),
        key=lambda item: item.id,
    )
    return (
        sorted(personal_visible, key=lambda item: item.id),
        sorted(work, key=lambda item: item.id),
        sorted(narrative, key=lambda item: item.id),
        unresolved_evidence,
    )


def _build_configuration(profile: MarsSourceProfileResponse) -> DeepMarsConfiguration:
    calc = profile.calculated
    house_available = bool(calc.birth_time_known and calc.mars_house is not None)
    aspects = [
        DeepMarsAspectIdentity(
            factor_key=aspect_factor_key(aspect),
            aspect_type=aspect.type,
            planet=aspect.planet,
            title=f"Mars {aspect.type} {aspect.planet}",
            orb_deg=aspect.orb_deg,
        )
        for aspect in calc.aspects
    ]
    return DeepMarsConfiguration(
        mars_sign=calc.mars_sign,
        mars_house=calc.mars_house if house_available else None,
        house_available=house_available,
        house_unavailable_reason=(
            None if house_available else HOUSE_UNAVAILABLE_REASON
        ),
        mars_motion=calc.mars_motion,
        birth_time_known=calc.birth_time_known,
        aspects=aspects,
    )


def _factor_block(
    *,
    factor_type: str,
    factor_key: str,
    title: str,
    purpose: str,
    availability: str,
    unavailable_reason: str | None,
    work_facts: list[MarsSourceFact],
    personal_non_work: list[MarsSourceFact],
    unresolved: list[MarsSourceFact],
) -> DeepMarsFactorBlock:
    if availability != "available":
        return DeepMarsFactorBlock(
            factor_type=factor_type,  # type: ignore[arg-type]
            factor_key=factor_key,
            title=title,
            purpose=purpose,
            availability=availability,  # type: ignore[arg-type]
            unavailable_reason=unavailable_reason,
            provenance=_provenance(factor_type, factor_key),
        )

    personal, work, narrative, unresolved_ev = _partition_factor_facts(
        work_facts=work_facts,
        personal_non_work=personal_non_work,
        unresolved=unresolved,
    )
    all_for_refs = personal + unresolved_ev
    return DeepMarsFactorBlock(
        factor_type=factor_type,  # type: ignore[arg-type]
        factor_key=factor_key,
        title=title,
        purpose=purpose,
        availability="available",
        fact_ids=[fact.id for fact in personal],
        work_fact_ids=[fact.id for fact in work],
        narrative_eligible_fact_ids=[fact.id for fact in narrative],
        unresolved_evidence_ids=[fact.id for fact in unresolved_ev],
        highlight_fact_ids=select_highlight_fact_ids(narrative),
        fact_refs=_build_fact_refs(all_for_refs),
        provenance=_provenance(factor_type, factor_key),
        categories=_categories(personal),
        tags=_tags(narrative),
    )


def _unresolved_for_factor(
    profile: MarsSourceProfileResponse,
    factor_type: str,
    factor_key: str,
) -> list[MarsSourceFact]:
    return [
        fact
        for fact in profile.conditional_unresolved
        if fact.factor_type == factor_type and fact.factor_key == factor_key
    ]


def _build_sign_block(profile: MarsSourceProfileResponse) -> DeepMarsFactorBlock:
    calc = profile.calculated
    sign = calc.mars_sign or ""
    personal, unresolved_extra = (
        match_non_work_personal_facts(factor_type="sign", factor_key=sign)
        if sign
        else ([], [])
    )
    unresolved = _unresolved_for_factor(profile, "sign", sign) + unresolved_extra
    # Dedupe unresolved by id
    unresolved = list({fact.id: fact for fact in unresolved}.values())
    return _factor_block(
        factor_type="sign",
        factor_key=sign or "unknown",
        title=f"Mars in {sign}" if sign else "Mars sign",
        purpose=SIGN_PURPOSE,
        availability="available" if sign else "unavailable",
        unavailable_reason=None if sign else "Mars sign is unavailable.",
        work_facts=list(profile.sign_facts),
        personal_non_work=personal,
        unresolved=unresolved,
    )


def _build_house_block(profile: MarsSourceProfileResponse) -> DeepMarsFactorBlock:
    calc = profile.calculated
    if not calc.birth_time_known or calc.mars_house is None:
        return DeepMarsFactorBlock(
            factor_type="house",
            factor_key="unavailable",
            title="Mars house",
            purpose=HOUSE_PURPOSE,
            availability="unavailable",
            unavailable_reason=HOUSE_UNAVAILABLE_REASON,
            provenance="house:unavailable",
        )
    house_key = str(calc.mars_house)
    personal, unresolved_extra = match_non_work_personal_facts(
        factor_type="house",
        factor_key=house_key,
    )
    unresolved = _unresolved_for_factor(profile, "house", house_key) + unresolved_extra
    unresolved = list({fact.id: fact for fact in unresolved}.values())
    return _factor_block(
        factor_type="house",
        factor_key=house_key,
        title=f"Mars in House {house_key}",
        purpose=HOUSE_PURPOSE,
        availability="available",
        unavailable_reason=None,
        work_facts=list(profile.house_facts),
        personal_non_work=personal,
        unresolved=unresolved,
    )


def _build_motion_block(profile: MarsSourceProfileResponse) -> DeepMarsFactorBlock:
    calc = profile.calculated
    motion = (calc.mars_motion or "").lower()
    if motion == "direct":
        return DeepMarsFactorBlock(
            factor_type="motion",
            factor_key="direct",
            title="Direct Mars",
            purpose=MOTION_PURPOSE,
            availability="neutral_default",
            unavailable_reason=None,
            provenance=_provenance("motion", "direct"),
        )
    if motion != "retrograde":
        return DeepMarsFactorBlock(
            factor_type="motion",
            factor_key=motion or "unknown",
            title="Mars motion",
            purpose=MOTION_PURPOSE,
            availability="unavailable",
            unavailable_reason="Mars motion is unavailable.",
            provenance=_provenance("motion", motion or "unknown"),
        )
    personal, unresolved_extra = match_non_work_personal_facts(
        factor_type="motion",
        factor_key="retrograde",
    )
    unresolved = (
        _unresolved_for_factor(profile, "motion", "retrograde") + unresolved_extra
    )
    unresolved = list({fact.id: fact for fact in unresolved}.values())
    return _factor_block(
        factor_type="motion",
        factor_key="retrograde",
        title="Retrograde Mars",
        purpose=MOTION_PURPOSE,
        availability="available",
        unavailable_reason=None,
        work_facts=list(profile.motion_facts),
        personal_non_work=personal,
        unresolved=unresolved,
    )


def _base_work_tags(profile: MarsSourceProfileResponse) -> set[str]:
    tags: set[str] = set()
    for fact in (
        list(profile.sign_facts)
        + list(profile.house_facts)
        + list(profile.motion_facts)
    ):
        if not fact.activated or fact.unresolved:
            continue
        if fact.scope not in WORK_PROFILE_SCOPES:
            continue
        tags.update(tag for tag in (fact.tags or ()) if tag)
    return tags


def _build_aspect_interaction(
    *,
    aspect_key: str,
    work_aspect_facts: list[MarsSourceFact],
    profile: MarsSourceProfileResponse,
) -> DeepMarsAspectInteraction:
    base_tags = _base_work_tags(profile)
    aspect_prov = _provenance("aspect", aspect_key)
    base_provs = {
        _provenance("sign", profile.calculated.mars_sign or ""),
        _provenance("motion", profile.calculated.mars_motion or ""),
    }
    if profile.calculated.birth_time_known and profile.calculated.mars_house is not None:
        base_provs.add(_provenance("house", str(profile.calculated.mars_house)))

    adds: list[DeepMarsAdditiveTheme] = []
    by_tag: dict[str, list[str]] = {}
    for fact in work_aspect_facts:
        if not fact.activated or fact.unresolved:
            continue
        if fact.scope not in WORK_PROFILE_SCOPES:
            continue
        if not _is_presentation_ready(fact):
            continue
        for tag in sorted(tag for tag in (fact.tags or ()) if tag):
            if tag in base_tags:
                continue
            by_tag.setdefault(tag, []).append(fact.id)
    adds = [
        DeepMarsAdditiveTheme(tag=tag, aspect_fact_ids=_unique_sorted(ids))
        for tag, ids in sorted(by_tag.items())
    ]

    work_aspect_ids = {fact.id for fact in work_aspect_facts if fact.activated}
    base_work_ids = {
        fact.id
        for fact in (
            list(profile.sign_facts)
            + list(profile.house_facts)
            + list(profile.motion_facts)
        )
        if fact.activated and fact.scope in WORK_PROFILE_SCOPES
    }

    reinforcing: list[DeepMarsReinforcingSignal] = []
    for signal in profile.repeated_signals:
        sources = set(signal.sources)
        if aspect_prov not in sources:
            continue
        base_sources = sorted(sources & base_provs)
        if not base_sources:
            continue
        aspect_ids = sorted(
            fid for fid in signal.fact_ids if fid in work_aspect_ids
        )
        base_support = sorted(fid for fid in signal.fact_ids if fid in base_work_ids)
        if not aspect_ids or not base_support:
            continue
        # Presentation-ready gate on supporting facts
        ready_aspect = [
            fid
            for fid in aspect_ids
            if any(
                f.id == fid and _is_presentation_ready(f) for f in work_aspect_facts
            )
        ]
        if not ready_aspect:
            continue
        reinforcing.append(
            DeepMarsReinforcingSignal(
                signal=signal.signal,
                tag=signal.tag,
                aspect_fact_ids=ready_aspect,
                base_fact_ids=base_support,
                base_provenance_keys=base_sources,
            )
        )

    reinforcing = sorted(reinforcing, key=lambda item: item.signal)
    # COMPLICATE: no Mars-native contrast catalog in v1.
    if not adds and not reinforcing:
        return DeepMarsAspectInteraction(available=False)

    supporting = _unique_sorted(
        [fid for item in adds for fid in item.aspect_fact_ids]
        + [
            fid
            for item in reinforcing
            for fid in item.aspect_fact_ids + item.base_fact_ids
        ]
    )
    provenance_keys = _unique_sorted(
        [aspect_prov]
        + [key for item in reinforcing for key in item.base_provenance_keys]
    )
    return DeepMarsAspectInteraction(
        available=True,
        adds=adds,
        reinforcing=reinforcing,
        contrasting=[],
        statement=None,
        supporting_fact_ids=supporting,
        provenance_keys=provenance_keys,
    )


def _aspect_work_facts(
    profile: MarsSourceProfileResponse, factor_key: str
) -> list[MarsSourceFact]:
    return [
        fact
        for fact in profile.aspect_facts
        if fact.factor_key == factor_key and fact.activated
    ]


def _build_aspect_blocks(
    profile: MarsSourceProfileResponse,
) -> list[DeepMarsAspectBlock]:
    from app.services.mars_deep_narrative import attach_mars_aspect_human_copy

    blocks: list[DeepMarsAspectBlock] = []
    for aspect in profile.calculated.aspects:
        calc_key = aspect_factor_key(aspect)
        identity = DeepMarsAspectIdentity(
            factor_key=calc_key,
            aspect_type=aspect.type,
            planet=aspect.planet,
            title=f"Mars {aspect.type} {aspect.planet}",
            orb_deg=aspect.orb_deg,
        )
        work_facts = _aspect_work_facts(profile, calc_key)
        personal: list[MarsSourceFact] = []
        unresolved: list[MarsSourceFact] = []

        if aspect.type in MARS_TENSE_ASPECT_TYPES:
            p, u = match_non_work_personal_facts(
                factor_type="aspect",
                factor_key=calc_key,
            )
            personal.extend(p)
            unresolved.extend(u)
        if aspect.type in MARS_MAJOR_ASPECT_TYPES and aspect.planet in BIO_PAIR_PLANETS:
            p, u = match_non_work_bio_aspect_facts(
                calc_key=calc_key,
                planet=aspect.planet,
            )
            personal.extend(p)
            unresolved.extend(u)

        unresolved.extend(
            fact
            for fact in profile.conditional_unresolved
            if fact.factor_type == "aspect" and fact.factor_key == calc_key
        )
        unresolved = list({fact.id: fact for fact in unresolved}.values())
        personal = list({fact.id: fact for fact in personal}.values())

        personal_vis, work, narrative, unresolved_ev = _partition_factor_facts(
            work_facts=work_facts,
            personal_non_work=personal,
            unresolved=unresolved,
        )
        interaction = _build_aspect_interaction(
            aspect_key=calc_key,
            work_aspect_facts=work_facts,
            profile=profile,
        )
        block = DeepMarsAspectBlock(
            identity=identity,
            fact_ids=[fact.id for fact in personal_vis],
            work_fact_ids=[fact.id for fact in work],
            narrative_eligible_fact_ids=[fact.id for fact in narrative],
            unresolved_evidence_ids=[fact.id for fact in unresolved_ev],
            highlight_fact_ids=select_highlight_fact_ids(narrative),
            fact_refs=_build_fact_refs(personal_vis + unresolved_ev),
            provenance=_provenance("aspect", calc_key),
            categories=_categories(personal_vis),
            tags=_tags(narrative),
            source_interpretation_available=bool(work),
            interaction=interaction,
        )
        blocks.append(attach_mars_aspect_human_copy(block))
    return blocks


def _factor_type_span(sources: list[str]) -> set[str]:
    return {key.partition(":")[0] for key in sources if ":" in key}


def _build_integrated(
    profile: MarsSourceProfileResponse,
    aspect_blocks: list[DeepMarsAspectBlock],
) -> list[DeepMarsIntegratedTakeaway]:
    """Integrated Mars items — structure first; human text attached later."""
    takeaways: list[DeepMarsIntegratedTakeaway] = []

    for signal in sorted(profile.repeated_signals, key=lambda item: item.signal):
        types = _factor_type_span(list(signal.sources))
        if len(types) < 2:
            continue
        # Only WORK-backed fact ids from the signal.
        work_ids = {
            fact.id
            for fact in (
                list(profile.sign_facts)
                + list(profile.house_facts)
                + list(profile.motion_facts)
                + list(profile.aspect_facts)
            )
            if fact.activated and fact.scope in WORK_PROFILE_SCOPES
        }
        support = [fid for fid in signal.fact_ids if fid in work_ids]
        if not support:
            continue
        takeaways.append(
            DeepMarsIntegratedTakeaway(
                key=f"repeat:{signal.signal}",
                basis="repeated_signal",
                signal=signal.signal,
                supporting_fact_ids=support,
                provenance_keys=list(signal.sources),
                text=None,
            )
        )

    for block in aspect_blocks:
        if not block.interaction.adds:
            continue
        support = _unique_sorted(
            [
                fid
                for item in block.interaction.adds
                for fid in item.aspect_fact_ids
            ]
        )
        if not support:
            continue
        takeaways.append(
            DeepMarsIntegratedTakeaway(
                key=f"add:{block.identity.factor_key}",
                basis="aspect_addition",
                signal=block.interaction.adds[0].tag,
                supporting_fact_ids=support,
                provenance_keys=[block.provenance],
                text=None,
            )
        )

    def _rank(item: DeepMarsIntegratedTakeaway) -> tuple:
        basis_rank = 0 if item.basis == "repeated_signal" else 1
        return (basis_rank, item.key)

    return sorted(takeaways, key=_rank)[:MAX_INTEGRATED_TAKEAWAYS]


def _collect_secondary_facts(
    *,
    sign: DeepMarsFactorBlock,
    house: DeepMarsFactorBlock,
    motion: DeepMarsFactorBlock,
    aspects: list[DeepMarsAspectBlock],
    profile: MarsSourceProfileResponse,
) -> list[MarsSourceFact]:
    """Personal-visible non-work + unresolved facts for UI reachability.

    Work facts already live on the profile response; these extras are matched
    only in the Deep builder and must still be inspectable under secondary lanes.
    """
    known = {
        fact.id
        for fact in (
            list(profile.sign_facts)
            + list(profile.house_facts)
            + list(profile.motion_facts)
            + list(profile.aspect_facts)
            + list(profile.conditional_unresolved)
        )
    }
    extras: dict[str, MarsSourceFact] = {}

    def _ingest_factor(factor_type: str, factor_key: str, block: DeepMarsFactorBlock) -> None:
        if block.availability != "available" or not factor_key:
            return
        personal, unresolved = match_non_work_personal_facts(
            factor_type=factor_type,
            factor_key=factor_key,
        )
        for fact in personal + unresolved:
            if fact.id in known:
                continue
            if fact.id in block.fact_ids or fact.id in block.unresolved_evidence_ids:
                extras[fact.id] = fact

    _ingest_factor("sign", sign.factor_key, sign)
    _ingest_factor("house", house.factor_key, house)
    _ingest_factor("motion", motion.factor_key, motion)
    for block in aspects:
        calc_key = block.identity.factor_key
        planet = block.identity.planet
        aspect_type = block.identity.aspect_type
        if aspect_type in MARS_TENSE_ASPECT_TYPES:
            personal, unresolved = match_non_work_personal_facts(
                factor_type="aspect",
                factor_key=calc_key,
            )
            for fact in personal + unresolved:
                if fact.id not in known and (
                    fact.id in block.fact_ids
                    or fact.id in block.unresolved_evidence_ids
                ):
                    extras[fact.id] = fact
        if aspect_type in MARS_MAJOR_ASPECT_TYPES and planet in BIO_PAIR_PLANETS:
            personal, unresolved = match_non_work_bio_aspect_facts(
                calc_key=calc_key,
                planet=planet,
            )
            for fact in personal + unresolved:
                if fact.id not in known and (
                    fact.id in block.fact_ids
                    or fact.id in block.unresolved_evidence_ids
                ):
                    extras[fact.id] = fact
    return sorted(extras.values(), key=lambda item: item.id)


def build_mars_deep_profile(
    profile: MarsSourceProfileResponse,
) -> MarsDeepProfile:
    """Assemble factor-first Deep Mars ownership + human narrative presentation."""
    from app.services.mars_deep_narrative import (
        attach_mars_factor_narrative,
        attach_mars_integrated_human_copy,
        build_integrated_mars_takeaways,
    )

    aspects = _build_aspect_blocks(profile)
    sign = attach_mars_factor_narrative(_build_sign_block(profile), profile)
    house = attach_mars_factor_narrative(_build_house_block(profile), profile)
    motion = attach_mars_factor_narrative(_build_motion_block(profile), profile)
    integrated = attach_mars_integrated_human_copy(
        build_integrated_mars_takeaways(
            profile=profile,
            sign=sign,
            house=house,
            motion=motion,
            aspects=aspects,
        )
    )
    secondary = _collect_secondary_facts(
        sign=sign,
        house=house,
        motion=motion,
        aspects=aspects,
        profile=profile,
    )
    return MarsDeepProfile(
        configuration=_build_configuration(profile),
        sign=sign,
        house=house,
        motion=motion,
        aspects=aspects,
        integrated=integrated,
        secondary_facts=secondary,
        limitations=list(profile.limitations or []),
    )
