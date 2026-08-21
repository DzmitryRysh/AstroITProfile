"""Schemas for Mars Source Profile — HOW YOU WORK delivery layer."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.mercury_work_profile import MercuryWorkProfileRequest, PlanetAspect

MarsSourceProfileRequest = MercuryWorkProfileRequest

FactorType = Literal["sign", "house", "motion", "aspect"]
Polarity = Literal["strength", "risk", "neutral", "conditional"]
CoverageStatus = Literal["complete", "partial"]
MarsScope = Literal["WORK_CORE", "WORK_DETAIL", "PERSONAL_MARS", "SOURCE_ONLY"]
MarsMotion = Literal["direct", "retrograde"]


class MarsAspect(PlanetAspect):
    """Mars-to-planet aspect. Same geometry shape as PlanetAspect."""


class MarsSourceFact(BaseModel):
    id: str
    factor_type: FactorType
    factor_key: str
    category: str
    text: str
    polarity: Polarity
    scope: MarsScope
    tags: list[str] = Field(default_factory=list)
    source_reference: str
    activation_condition: Optional[str] = None
    activated: bool = True
    unresolved: bool = False


class CalculatedMarsSnapshot(BaseModel):
    mars_sign: Optional[str] = None
    mars_house: Optional[int] = None
    mars_motion: Optional[MarsMotion] = None
    birth_time_known: bool
    aspects: list[MarsAspect] = Field(default_factory=list)
    house_system_used: Optional[str] = None


class MarsRepeatedSignal(BaseModel):
    signal: str
    tag: str
    source_count: int
    sources: list[str]
    fact_ids: list[str]


class MarsSourceCoverage(BaseModel):
    status: CoverageStatus
    covered_factors: list[str]
    unimplemented_source_factors: list[str]


class MarsSynthesisSection(BaseModel):
    key: str
    title: str
    categories: list[str]
    tags: list[str]
    fact_ids: list[str]
    fact_count: int
    factor_keys: list[str]
    factor_count: int
    repeated_fact_ids: list[str] = Field(default_factory=list)
    repeated_signals: list[str] = Field(default_factory=list)
    preview_fact_ids: list[str] = Field(default_factory=list)


class MarsSynthesisTraceability(BaseModel):
    activated_fact_count: int
    section_fact_count: int
    detail_fact_count: int
    unresolved_fact_count: int
    unclassified_fact_count: int


class MarsGlanceCard(BaseModel):
    """Presentation-only takeaway. Does not add source meaning."""

    key: str
    title: str
    text: str
    source: Literal["template", "observation"]
    fact_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    repeated_signals: list[str] = Field(default_factory=list)
    display_template: str = ""


class MarsProfileSynthesisResponse(BaseModel):
    """API-facing HOW YOU WORK synthesis index (additive to source profile)."""

    work_style_at_a_glance: list[MarsGlanceCard] = Field(default_factory=list)
    repeated_signals: list[MarsRepeatedSignal] = Field(default_factory=list)
    sections: list[MarsSynthesisSection] = Field(default_factory=list)
    source_specific_fact_ids: list[str] = Field(default_factory=list)
    unresolved_fact_ids: list[str] = Field(default_factory=list)
    coverage: MarsSourceCoverage
    limitations: list[str] = Field(default_factory=list)
    traceability: MarsSynthesisTraceability
    facts_by_id: dict[str, MarsSourceFact] = Field(default_factory=dict)
    presentation_text_by_fact_id: dict[str, str] = Field(default_factory=dict)
    deep_profile: Optional["MarsDeepProfile"] = None


class MarsSourceProfileResponse(BaseModel):
    calculated: CalculatedMarsSnapshot
    sign_facts: list[MarsSourceFact] = Field(default_factory=list)
    house_facts: list[MarsSourceFact] = Field(default_factory=list)
    motion_facts: list[MarsSourceFact] = Field(default_factory=list)
    aspect_facts: list[MarsSourceFact] = Field(default_factory=list)
    repeated_signals: list[MarsRepeatedSignal] = Field(default_factory=list)
    conditional_unresolved: list[MarsSourceFact] = Field(default_factory=list)
    coverage: MarsSourceCoverage
    limitations: list[str] = Field(default_factory=list)
    synthesis: Optional[MarsProfileSynthesisResponse] = None


# --- Mars Deep Profile (M10.5 Phase 2A) — additive ownership presentation ---

FactorAvailability = Literal["available", "unavailable", "neutral_default"]
DeepContentKind = Literal["source", "synthesis"]
MarsPresentationLane = Literal[
    "core",
    "source_specific",
    "sensitive_source",
    "unresolved",
]


class DeepMarsAspectIdentity(BaseModel):
    factor_key: str
    aspect_type: str
    planet: str
    title: str
    orb_deg: Optional[float] = None


class DeepMarsConfiguration(BaseModel):
    """Concise Mars configuration header. No recalculation."""

    mars_sign: Optional[str] = None
    mars_house: Optional[int] = None
    house_available: bool
    house_unavailable_reason: Optional[str] = None
    mars_motion: Optional[str] = None
    birth_time_known: bool
    aspects: list[DeepMarsAspectIdentity] = Field(default_factory=list)


class DeepMarsFactRef(BaseModel):
    """Presentation-layer fact reference with derived visibility lane."""

    fact_id: str
    presentation_lane: MarsPresentationLane
    scope: MarsScope
    category: str
    activated: bool = False
    unresolved: bool = False


class DeepMarsNarrativeSubsection(BaseModel):
    key: str
    title: str
    text: str
    supporting_fact_ids: list[str] = Field(default_factory=list)


class DeepMarsFactorNarrative(BaseModel):
    """Deterministic human synthesis for a Mars factor. Not a source fact."""

    kind: DeepContentKind = "synthesis"
    core_theme: str
    summary: str
    subsections: list[DeepMarsNarrativeSubsection] = Field(default_factory=list)
    supporting_fact_ids: list[str] = Field(default_factory=list)
    conditional_fact_ids: list[str] = Field(default_factory=list)


class DeepMarsFactorBlock(BaseModel):
    """Canonical source ownership for one Mars factor layer.

    fact_ids = personal-visible matched facts
    work_fact_ids = activated WORK facts only
    narrative_eligible_fact_ids = future synthesis pool (core lane)
    unresolved_evidence_ids = unresolved chart-relevant source only
    """

    factor_type: FactorType
    factor_key: str
    title: str
    purpose: str
    availability: FactorAvailability
    unavailable_reason: Optional[str] = None
    content_kind: DeepContentKind = "source"
    ownership: Literal["canonical_source"] = "canonical_source"
    fact_ids: list[str] = Field(default_factory=list)
    work_fact_ids: list[str] = Field(default_factory=list)
    narrative_eligible_fact_ids: list[str] = Field(default_factory=list)
    unresolved_evidence_ids: list[str] = Field(default_factory=list)
    highlight_fact_ids: list[str] = Field(default_factory=list)
    fact_refs: list[DeepMarsFactRef] = Field(default_factory=list)
    provenance: str
    categories: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    narrative: Optional[DeepMarsFactorNarrative] = None


class DeepMarsAdditiveTheme(BaseModel):
    tag: str
    label: str = ""
    aspect_fact_ids: list[str] = Field(default_factory=list)


class DeepMarsReinforcingSignal(BaseModel):
    signal: str
    tag: str
    label: str = ""
    aspect_fact_ids: list[str] = Field(default_factory=list)
    base_fact_ids: list[str] = Field(default_factory=list)
    base_provenance_keys: list[str] = Field(default_factory=list)


class DeepMarsAspectInteraction(BaseModel):
    """Mars aspect modifier skeleton: ADD / REINFORCE; COMPLICATE empty in v1."""

    available: bool = False
    content_kind: DeepContentKind = "synthesis"
    adds: list[DeepMarsAdditiveTheme] = Field(default_factory=list)
    reinforcing: list[DeepMarsReinforcingSignal] = Field(default_factory=list)
    contrasting: list = Field(default_factory=list)
    statement: Optional[str] = None
    supporting_fact_ids: list[str] = Field(default_factory=list)
    provenance_keys: list[str] = Field(default_factory=list)


class DeepMarsAspectBlock(BaseModel):
    identity: DeepMarsAspectIdentity
    content_kind: DeepContentKind = "source"
    ownership: Literal["canonical_source"] = "canonical_source"
    fact_ids: list[str] = Field(default_factory=list)
    work_fact_ids: list[str] = Field(default_factory=list)
    narrative_eligible_fact_ids: list[str] = Field(default_factory=list)
    unresolved_evidence_ids: list[str] = Field(default_factory=list)
    highlight_fact_ids: list[str] = Field(default_factory=list)
    fact_refs: list[DeepMarsFactRef] = Field(default_factory=list)
    provenance: str
    categories: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    source_interpretation_available: bool = True
    interaction: DeepMarsAspectInteraction = Field(
        default_factory=DeepMarsAspectInteraction
    )


class DeepMarsIntegratedTakeaway(BaseModel):
    """Integrated Mars outcome item — human text optional until narrative attach."""

    kind: DeepContentKind = "synthesis"
    key: str
    basis: Literal[
        "base_character",
        "factor_modifier",
        "repeated_signal",
        "aspect_addition",
    ]
    signal: Optional[str] = None
    supporting_fact_ids: list[str] = Field(default_factory=list)
    provenance_keys: list[str] = Field(default_factory=list)
    text: Optional[str] = None


class MarsDeepProfile(BaseModel):
    """Factor-first personal Mars presentation (additive to work synthesis)."""

    configuration: DeepMarsConfiguration
    sign: DeepMarsFactorBlock
    house: DeepMarsFactorBlock
    motion: DeepMarsFactorBlock
    aspects: list[DeepMarsAspectBlock] = Field(default_factory=list)
    integrated: list[DeepMarsIntegratedTakeaway] = Field(default_factory=list)
    secondary_facts: list[MarsSourceFact] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


MarsProfileSynthesisResponse.model_rebuild()