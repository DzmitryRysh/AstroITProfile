"""Schemas for the Thinking → Execution presentation bridge (M9)."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.mercury_work_profile import MercuryWorkProfileRequest

BridgeKind = Literal["reinforcement", "friction", "contrast"]


class ThinkingToExecutionRequest(MercuryWorkProfileRequest):
    display_name: Optional[str] = None
    sex: Optional[str] = None


class CrossProfilePattern(BaseModel):
    id: str
    title: str
    kind: BridgeKind
    presentation_text: str
    mercury_semantic: str
    mars_semantic: str
    mercury_support: list[str] = Field(default_factory=list)
    mars_support: list[str] = Field(default_factory=list)
    mercury_provenance: list[str] = Field(default_factory=list)
    mars_provenance: list[str] = Field(default_factory=list)
    why_this_appears: str


class ThinkingToExecutionSynthesis(BaseModel):
    patterns: list[CrossProfilePattern] = Field(default_factory=list)
