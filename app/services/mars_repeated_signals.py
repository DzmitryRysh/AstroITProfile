"""Mars repeated-signal specs and detection.

Same exact tag across >= 2 distinct calculated Mars provenance keys.
Does not import Mercury repeat specs. No approximate tag unions.
Square/opposition catalog twins on one planet count as one factor family.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

# Exact HOW-YOU-WORK tags that can co-occur on distinct natal factors.
# Rejected single-slot tags are documented in tests, not listed here.
MARS_REPEATED_SIGNAL_SPECS: tuple[dict, ...] = (
    {
        "signal": "hands_on_execution",
        "tag": "hands_on_execution",
        "min_factor_keys": 2,
    },
    {
        "signal": "crisis_execution",
        "tag": "crisis_execution",
        "min_factor_keys": 2,
    },
    {
        "signal": "mood_dependent_action",
        "tag": "mood_dependent_action",
        "min_factor_keys": 2,
    },
    {
        "signal": "effort_overload",
        "tag": "effort_overload",
        "min_factor_keys": 2,
    },
    {
        "signal": "action_hesitation",
        "tag": "action_hesitation",
        "min_factor_keys": 2,
    },
)


@dataclass(frozen=True)
class MarsRepeatedSignal:
    signal: str
    tag: str
    source_count: int
    sources: tuple[str, ...]
    fact_ids: tuple[str, ...]


def _provenance_key(fact) -> str:
    provenance = getattr(fact, "provenance_key", None)
    if provenance:
        return provenance
    return f"{fact.factor_type}:{fact.factor_key}"


def detect_mars_repeated_signals(facts) -> tuple[MarsRepeatedSignal, ...]:
    """Mercury-pattern detector: exact tag, distinct provenance keys, no score."""
    active = [
        item
        for item in facts
        if getattr(item, "activated", True) and not getattr(item, "unresolved", False)
    ]
    signals: list[MarsRepeatedSignal] = []
    for spec in MARS_REPEATED_SIGNAL_SPECS:
        tag = spec["tag"]
        by_factor: dict[str, list] = defaultdict(list)
        for fact in active:
            if tag in fact.tags:
                by_factor[_provenance_key(fact)].append(fact)
        if len(by_factor) < int(spec["min_factor_keys"]):
            continue
        sources = tuple(sorted(by_factor))
        fact_ids = tuple(sorted({fact.id for group in by_factor.values() for fact in group}))
        signals.append(
            MarsRepeatedSignal(
                signal=spec["signal"],
                tag=tag,
                source_count=len(sources),
                sources=sources,
                fact_ids=fact_ids,
            )
        )
    return tuple(signals)
