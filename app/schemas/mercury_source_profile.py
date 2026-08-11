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
