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
