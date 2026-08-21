"""Schemas for Mercury Source Profile v2 — source-first deterministic layer."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.mercury_work_profile import MercuryAspect, MercuryWorkProfileRequest

MercurySourceProfileRequest = MercuryWorkProfileRequest

FactorType = Literal["sign", "house", "motion", "aspect"]
Polarity = Literal["strength", "risk", "neutral", "conditional"]
CoverageStatus = Literal["complete", "partial"]


class SourceFact(BaseModel):
    id: str
    factor_type: FactorType
    factor_key: str
    category: str
    text: str
    polarity: Polarity
    tags: list[str] = Field(default_factory=list)
    source_reference: str
    activation_condition: Optional[str] = None
    activated: bool = True
    unresolved: bool = False


class CalculatedMercurySnapshot(BaseModel):
    mercury_sign: Optional[str] = None
    mercury_element: Optional[str] = None
    mercury_house: Optional[int] = None
    mercury_motion: Optional[str] = None
    birth_time_known: bool
    aspects: list[MercuryAspect] = Field(default_factory=list)
    hard_aspected: bool = False


class RepeatedSignal(BaseModel):
    signal: str
    source_count: int
    sources: list[str]
    fact_ids: list[str]


class ContrastingSignalPair(BaseModel):
    tag_a: str
    tag_b: str
    facts_a: list[str]
    facts_b: list[str]


class SourceCoverage(BaseModel):
    status: CoverageStatus
    covered_factors: list[str]
    missing_factors: list[str]


class SynthesisStrongestPattern(BaseModel):
    signal: str
    source_count: int
    sources: list[str]
    fact_ids: list[str]
    section_keys: list[str] = Field(default_factory=list)


class SynthesisTension(BaseModel):
    tag_a: str
    tag_b: str
    facts_a: list[str]
    facts_b: list[str]
    state: Literal["resolved", "conditional"]


class SynthesisSection(BaseModel):
    key: str
    title: str
    categories: list[str]
    resolved_fact_ids: list[str]
    resolved_fact_count: int
    factor_keys: list[str]
    factor_count: int
    preview_fact_ids: list[str]


class SynthesisConditionalGroup(BaseModel):
    factor_type: str
    factor_key: str
    fact_ids: list[str]
    activation_conditions: list[str] = Field(default_factory=list)


class SynthesisDetailBucket(BaseModel):
    key: str
    fact_ids: list[str]


class SynthesisTraceability(BaseModel):
    total_fact_count: int
    resolved_section_fact_count: int
    conditional_fact_count: int
    detail_only_fact_count: int
    unclassified_fact_count: int


class MercuryGlanceCard(BaseModel):
    """Presentation-only takeaway. Does not add source meaning."""

    key: str
    title: str
    text: str
    source: Literal["template", "observation"]
    fact_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    repeated_signals: list[str] = Field(default_factory=list)
    display_template: str = ""


# --- Mercury Deep Profile (M9.5A) — additive factor-first presentation ---

FactorAvailability = Literal["available", "unavailable", "neutral_default"]
DeepContentKind = Literal["source", "synthesis"]


class DeepMercuryAspectIdentity(BaseModel):
    factor_key: str
    aspect_type: str
    planet: str
    title: str
    orb_deg: Optional[float] = None


class DeepMercuryConfiguration(BaseModel):
    """Concise Mercury configuration header. No recalculation."""

    mercury_sign: Optional[str] = None
    mercury_house: Optional[int] = None
    house_available: bool
    house_unavailable_reason: Optional[str] = None
    mercury_motion: Optional[str] = None
    birth_time_known: bool
    aspects: list[DeepMercuryAspectIdentity] = Field(default_factory=list)


class DeepMercuryNarrativeSubsection(BaseModel):
    """Optional thematic subsection inside a factor narrative."""

    key: str
    title: str
    text: str
    supporting_fact_ids: list[str] = Field(default_factory=list)


class DeepMercuryFactorNarrative(BaseModel):
    """Deterministic human synthesis for a Mercury factor. Not a source fact.

    Core theme/summary are owned by unconditional factor facts only.
    Conditionally activated facts (e.g. hard_aspected) stay visible under a
    dedicated subsection and conditional_fact_ids — they do not redefine base.
    """

    kind: DeepContentKind = "synthesis"
    core_theme: str
    summary: str
    subsections: list[DeepMercuryNarrativeSubsection] = Field(default_factory=list)
    supporting_fact_ids: list[str] = Field(default_factory=list)
    conditional_fact_ids: list[str] = Field(default_factory=list)


class DeepMercuryFactorBlock(BaseModel):
    """Canonical source ownership for one Mercury factor layer."""

    factor_type: FactorType
    factor_key: str
    title: str
    purpose: str
    availability: FactorAvailability
    unavailable_reason: Optional[str] = None
    content_kind: DeepContentKind = "source"
    ownership: Literal["canonical_source"] = "canonical_source"
    fact_ids: list[str] = Field(default_factory=list)
    highlight_fact_ids: list[str] = Field(default_factory=list)
    provenance: str
    categories: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    narrative: Optional[DeepMercuryFactorNarrative] = None


class DeepMercuryAdditiveTheme(BaseModel):
    """Theme introduced by an aspect and not already present in base Mercury."""

    tag: str
    label: str = ""
    aspect_fact_ids: list[str] = Field(default_factory=list)


class DeepMercuryReinforcingSignal(BaseModel):
    signal: str
    tag: str
    label: str = ""
    aspect_fact_ids: list[str] = Field(default_factory=list)
    base_fact_ids: list[str] = Field(default_factory=list)
    base_provenance_keys: list[str] = Field(default_factory=list)


class DeepMercuryContrastingSignal(BaseModel):
    tag_a: str
    tag_b: str
    label: str = ""
    aspect_fact_ids: list[str] = Field(default_factory=list)
    base_fact_ids: list[str] = Field(default_factory=list)
    base_provenance_keys: list[str] = Field(default_factory=list)


class DeepMercuryAspectInteraction(BaseModel):
    """Aspect modifier synthesis: adds / reinforces / contrasts base Mercury."""

    available: bool = False
    content_kind: DeepContentKind = "synthesis"
    adds: list[DeepMercuryAdditiveTheme] = Field(default_factory=list)
    reinforcing: list[DeepMercuryReinforcingSignal] = Field(default_factory=list)
    contrasting: list[DeepMercuryContrastingSignal] = Field(default_factory=list)
    statement: Optional[str] = None
    supporting_fact_ids: list[str] = Field(default_factory=list)
    provenance_keys: list[str] = Field(default_factory=list)


class DeepMercuryAspectBlock(BaseModel):
    """One calculated Mercury aspect: source observations + optional base interaction."""

    identity: DeepMercuryAspectIdentity
    content_kind: DeepContentKind = "source"
    ownership: Literal["canonical_source"] = "canonical_source"
    fact_ids: list[str] = Field(default_factory=list)
    highlight_fact_ids: list[str] = Field(default_factory=list)
    provenance: str
    categories: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    interaction: DeepMercuryAspectInteraction = Field(
        default_factory=DeepMercuryAspectInteraction
    )


class DeepMercuryIntegratedTakeaway(BaseModel):
    """Cross-factor or additive synthesis. References source ids; not a source fact."""

    kind: DeepContentKind = "synthesis"
    key: str
    text: str
    basis: Literal["repeated_signal", "contrasting_signal", "aspect_addition"]
    signal: Optional[str] = None
    supporting_fact_ids: list[str] = Field(default_factory=list)
    provenance_keys: list[str] = Field(default_factory=list)


class MercuryDeepProfile(BaseModel):
    """Factor-first personal Mercury presentation (additive to work synthesis)."""

    configuration: DeepMercuryConfiguration
    sign: DeepMercuryFactorBlock
    house: DeepMercuryFactorBlock
    motion: DeepMercuryFactorBlock
    aspects: list[DeepMercuryAspectBlock] = Field(default_factory=list)
    integrated: list[DeepMercuryIntegratedTakeaway] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class MercuryProfileSynthesisResponse(BaseModel):
    """API-facing synthesis presentation index (additive to source profile)."""

    thinking_at_a_glance: list[MercuryGlanceCard] = Field(default_factory=list)
    strongest_patterns: list[SynthesisStrongestPattern] = Field(default_factory=list)
    resolved_tensions: list[SynthesisTension] = Field(default_factory=list)
    conditional_tensions: list[SynthesisTension] = Field(default_factory=list)
    sections: list[SynthesisSection] = Field(default_factory=list)
    conditional_details: list[SynthesisConditionalGroup] = Field(default_factory=list)
    source_details: list[SynthesisDetailBucket] = Field(default_factory=list)
    traceability: SynthesisTraceability
    facts_by_id: dict[str, SourceFact] = Field(default_factory=dict)
    presentation_text_by_fact_id: dict[str, str] = Field(default_factory=dict)
    deep_profile: Optional[MercuryDeepProfile] = None


class MercurySourceProfileResponse(BaseModel):
    calculated: CalculatedMercurySnapshot
    sign_facts: list[SourceFact] = Field(default_factory=list)
    house_facts: list[SourceFact] = Field(default_factory=list)
    motion_facts: list[SourceFact] = Field(default_factory=list)
    aspect_facts: list[SourceFact] = Field(default_factory=list)
    repeated_signals: list[RepeatedSignal] = Field(default_factory=list)
    conditional_unresolved: list[SourceFact] = Field(default_factory=list)
    contrasting_signals: list[ContrastingSignalPair] = Field(default_factory=list)
    coverage: SourceCoverage
    limitations: list[str] = Field(default_factory=list)
    synthesis: Optional[MercuryProfileSynthesisResponse] = None
