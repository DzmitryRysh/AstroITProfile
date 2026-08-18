"""Mars source profile v1 — Lesson 9 SIGN activation only.

House, motion, and aspect knowledge are not implemented yet.
Those calculated layers are reported as unimplemented source coverage,
not as missing calculation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from typing import Optional

from app.services.mars_facts import (
    MarsSourceFactors,
    aspect_factor_key,
    compute_mars_source_factors,
)
from app.services.mars_source_knowledge import (
    ALL_MARS_SOURCE_FACTS,
    SUPPORTED_SIGN_KEYS,
    WORK_PROFILE_SCOPES,
    MarsSourceFactDef,
)


@dataclass(frozen=True)
class MarsSourceFact:
    id: str
    factor_type: str
    factor_key: str
    text: str
    source_reference: str
    category: str
    scope: str
    polarity: str
    tags: tuple[str, ...]
    activation_condition: str | None
    activated: bool
    unresolved: bool

    @property
    def provenance_key(self) -> str:
        return f"{self.factor_type}:{self.factor_key}"


@dataclass(frozen=True)
class MarsSourceCoverage:
    status: str
    covered_factors: tuple[str, ...]
    unimplemented_source_factors: tuple[str, ...]


@dataclass(frozen=True)
class MarsSourceProfile:
    calculated: MarsSourceFactors
    sign_facts: tuple[MarsSourceFact, ...]
    house_facts: tuple[MarsSourceFact, ...]
    motion_facts: tuple[MarsSourceFact, ...]
    aspect_facts: tuple[MarsSourceFact, ...]
    conditional_unresolved: tuple[MarsSourceFact, ...]
    coverage: MarsSourceCoverage
    limitations: tuple[str, ...]


def _to_fact(definition: MarsSourceFactDef, *, activated: bool) -> MarsSourceFact:
    return MarsSourceFact(
        id=definition.id,
        factor_type=definition.factor_type,
        factor_key=definition.factor_key,
        text=definition.text,
        source_reference=definition.source_reference,
        category=definition.category,
        scope=definition.scope,
        polarity=definition.polarity,
        tags=definition.tags,
        activation_condition=definition.activation_condition,
        activated=activated,
        unresolved=definition.unresolved,
    )


def _match_sign_definitions(sign: str) -> tuple[list[MarsSourceFact], list[MarsSourceFact]]:
    work_facts: list[MarsSourceFact] = []
    unresolved_facts: list[MarsSourceFact] = []
    for definition in ALL_MARS_SOURCE_FACTS:
        if definition.factor_type != "sign" or definition.factor_key != sign:
            continue
        if definition.unresolved:
            unresolved_facts.append(_to_fact(definition, activated=False))
            continue
        if definition.scope not in WORK_PROFILE_SCOPES:
            continue
        work_facts.append(_to_fact(definition, activated=True))
    return work_facts, unresolved_facts


def _coverage_and_limitations(
    factors: MarsSourceFactors,
) -> tuple[MarsSourceCoverage, list[str]]:
    covered: list[str] = []
    unimplemented: list[str] = []
    limitations = list(factors.limitations)

    if factors.mars_sign:
        sign_key = f"sign:{factors.mars_sign}"
        if factors.mars_sign in SUPPORTED_SIGN_KEYS:
            covered.append(sign_key)
        else:
            unimplemented.append(sign_key)
            limitations.append(
                f"Mars sign source knowledge for {factors.mars_sign} is not implemented yet."
            )

    if factors.mars_house is not None:
        unimplemented.append(f"house:{factors.mars_house}")
        limitations.append("Mars house source knowledge is not implemented yet.")

    if factors.mars_motion == "retrograde":
        unimplemented.append("motion:retrograde")
        limitations.append("Mars motion source knowledge is not implemented yet.")

    if factors.mars_aspects:
        for aspect in factors.mars_aspects:
            unimplemented.append(f"aspect:{aspect_factor_key(aspect)}")
        limitations.append("Mars aspect source knowledge is not implemented yet.")

    status = "complete" if not unimplemented else "partial"
    return (
        MarsSourceCoverage(
            status=status,
            covered_factors=tuple(covered),
            unimplemented_source_factors=tuple(unimplemented),
        ),
        limitations,
    )


def build_mars_source_profile_from_factors(
    factors: MarsSourceFactors,
) -> MarsSourceProfile:
    sign_facts: list[MarsSourceFact] = []
    unresolved: list[MarsSourceFact] = []
    if factors.mars_sign in SUPPORTED_SIGN_KEYS:
        sign_facts, unresolved = _match_sign_definitions(factors.mars_sign or "")

    coverage, limitations = _coverage_and_limitations(factors)
    return MarsSourceProfile(
        calculated=factors,
        sign_facts=tuple(sign_facts),
        house_facts=(),
        motion_facts=(),
        aspect_facts=(),
        conditional_unresolved=tuple(unresolved),
        coverage=coverage,
        limitations=tuple(limitations),
    )


def build_mars_source_profile(
    *,
    birth_date: date,
    birth_place: str,
    birth_time: Optional[time] = None,
) -> MarsSourceProfile:
    factors = compute_mars_source_factors(
        birth_date=birth_date,
        birth_place=birth_place,
        birth_time=birth_time,
    )
    return build_mars_source_profile_from_factors(factors)
