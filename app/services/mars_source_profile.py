"""Mars source profile v1 — Lesson 9 SIGN + HOUSE + RETROGRADE MOTION activation.

Direct Mars is a calculated state with no Lesson 9 interpretation pack.
Aspect knowledge is not implemented yet and is reported as unimplemented
source coverage, not as missing calculation.
Unknown birth time makes the house source layer unavailable.
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
    SUPPORTED_HOUSE_KEYS,
    SUPPORTED_MOTION_KEYS,
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


def _match_definitions(
    *,
    factor_type: str,
    factor_key: str,
) -> tuple[list[MarsSourceFact], list[MarsSourceFact]]:
    work_facts: list[MarsSourceFact] = []
    unresolved_facts: list[MarsSourceFact] = []
    for definition in ALL_MARS_SOURCE_FACTS:
        if definition.factor_type != factor_type or definition.factor_key != factor_key:
            continue
        if definition.unresolved:
            unresolved_facts.append(_to_fact(definition, activated=False))
            continue
        if definition.scope not in WORK_PROFILE_SCOPES:
            continue
        work_facts.append(_to_fact(definition, activated=True))
    return work_facts, unresolved_facts


DIRECT_MOTION_NO_PACK_LIMITATION = (
    "Direct Mars motion is a calculated state with no Lesson 9 "
    "source-specific interpretation pack."
)


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

    if factors.mars_house is None:
        if not factors.birth_time_known:
            limitations.append(
                "House source layer unavailable because birth time is unknown."
            )
    else:
        house_key = f"house:{factors.mars_house}"
        if str(factors.mars_house) in SUPPORTED_HOUSE_KEYS:
            covered.append(house_key)
        else:
            unimplemented.append(house_key)
            limitations.append(
                f"Mars house source knowledge for house {factors.mars_house} is not implemented yet."
            )

    if factors.mars_motion == "direct":
        limitations.append(DIRECT_MOTION_NO_PACK_LIMITATION)
    elif factors.mars_motion:
        motion_key = f"motion:{factors.mars_motion}"
        if factors.mars_motion in SUPPORTED_MOTION_KEYS:
            covered.append(motion_key)
        else:
            unimplemented.append(motion_key)
            limitations.append(
                f"Mars motion source knowledge for {factors.mars_motion} is not implemented yet."
            )

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
    house_facts: list[MarsSourceFact] = []
    motion_facts: list[MarsSourceFact] = []
    unresolved: list[MarsSourceFact] = []

    if factors.mars_sign in SUPPORTED_SIGN_KEYS:
        sign_facts, sign_unresolved = _match_definitions(
            factor_type="sign",
            factor_key=factors.mars_sign or "",
        )
        unresolved.extend(sign_unresolved)

    if factors.mars_house is not None:
        house_key = str(factors.mars_house)
        if house_key in SUPPORTED_HOUSE_KEYS:
            house_facts, house_unresolved = _match_definitions(
                factor_type="house",
                factor_key=house_key,
            )
            unresolved.extend(house_unresolved)

    if factors.mars_motion in SUPPORTED_MOTION_KEYS:
        motion_facts, motion_unresolved = _match_definitions(
            factor_type="motion",
            factor_key=factors.mars_motion or "",
        )
        unresolved.extend(motion_unresolved)

    coverage, limitations = _coverage_and_limitations(factors)
    return MarsSourceProfile(
        calculated=factors,
        sign_facts=tuple(sign_facts),
        house_facts=tuple(house_facts),
        motion_facts=tuple(motion_facts),
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
