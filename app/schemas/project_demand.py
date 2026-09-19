"""Schemas for Project Demand v1.

Project Demand describes what contribution patterns THIS WORK requires.
It is independent of astrology, people, Contribution Profile states, and
Team Gap / Team Function workflow coverage.

Parallel domains (intentionally not interchangeable):
  Team Gap        → Team Function × Workflow Coverage
  Project Demand  → Contribution Dimension × work demand levels
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

# Exact Contribution Profile dimension keys (parity enforced in tests).
ProjectDemandDimensionKey = Literal[
    "investigation",
    "structuring",
    "validation",
    "execution_momentum",
    "hands_on_delivery",
]

# Work-need levels — not person evidence states (primary/strong/supporting/conditional).
ProjectDemandLevel = Literal[
    "critical",
    "important",
    "useful",
    "not_required",
]

PROJECT_DEMAND_DIMENSION_ORDER: tuple[ProjectDemandDimensionKey, ...] = (
    "investigation",
    "structuring",
    "validation",
    "execution_momentum",
    "hands_on_delivery",
)

ProjectDemandCreatedFrom = Literal["explicit"]
ProjectDemandDimensionSource = Literal["user"]


class ProjectDemandDimensionInput(BaseModel):
    dimension: ProjectDemandDimensionKey
    demand_level: ProjectDemandLevel
    rationale: str = Field(..., min_length=1)

    @field_validator("rationale")
    @classmethod
    def rationale_must_be_nonblank(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("rationale must be a non-empty human explanation")
        return trimmed


class ProjectDemandRequest(BaseModel):
    """Explicit complete Project Demand input. Stateless. No natal fields."""

    label: str = Field(..., min_length=1)
    description: Optional[str] = None
    dimensions: list[ProjectDemandDimensionInput] = Field(..., min_length=5, max_length=5)
    assumptions: list[str] = Field(default_factory=list)

    @field_validator("label")
    @classmethod
    def label_must_be_nonblank(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("label must be a non-empty project label")
        return trimmed

    @field_validator("description")
    @classmethod
    def description_trim(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None

    @field_validator("assumptions")
    @classmethod
    def assumptions_trim(cls, values: list[str]) -> list[str]:
        cleaned: list[str] = []
        for item in values:
            trimmed = item.strip()
            if trimmed:
                cleaned.append(trimmed)
        return cleaned

    @model_validator(mode="after")
    def validate_complete_dimension_set(self) -> "ProjectDemandRequest":
        keys = [item.dimension for item in self.dimensions]
        required = set(PROJECT_DEMAND_DIMENSION_ORDER)
        actual = set(keys)
        if len(keys) != len(actual):
            raise ValueError(
                "dimensions must not contain duplicates; "
                "each supported dimension must appear exactly once"
            )
        missing = required - actual
        if missing:
            raise ValueError(
                "dimensions must include every supported dimension exactly once; "
                f"missing: {', '.join(sorted(missing))}"
            )
        # Unknown keys are already blocked by ProjectDemandDimensionKey Literal.
        if actual != required:
            raise ValueError(
                "dimensions must be exactly the five supported Contribution keys"
            )
        return self


class ProjectDemandDimension(BaseModel):
    dimension: ProjectDemandDimensionKey
    demand_level: ProjectDemandLevel
    rationale: str
    source: ProjectDemandDimensionSource = "user"


class ProjectDemand(BaseModel):
    """Canonical Project Demand snapshot. Deterministic. Not a persisted entity."""

    label: str
    description: Optional[str] = None
    dimensions: list[ProjectDemandDimension]
    assumptions: list[str] = Field(default_factory=list)
    created_from: ProjectDemandCreatedFrom = "explicit"
    notes: list[str] = Field(default_factory=list)
