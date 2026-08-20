"""Deterministic Mercury human-copy readability audit (S4.1).

SOURCE FACTS ARE IMMUTABLE EVIDENCE.

This module only flags mechanical presentation/readability signals on
canonical SourceFact.text. It does not rewrite facts, call an LLM, or
change synthesis/UI behavior.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, time

from app.schemas.mercury_source_profile import MercurySourceProfileRequest
from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_human_copy import HUMAN_COPY_OVERRIDES
from app.services.mercury_profile_synthesis import build_mercury_profile_synthesis
from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS, SourceFactDef
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
)

# --- Reason taxonomy (explicit mechanical signals only) ---

REASON_TECHNICAL_SCAFFOLDING = "technical_scaffolding"
REASON_CYRILLIC_SOURCE_NOTE = "cyrillic_source_note"
REASON_SLASH_HEAVY = "slash_heavy"
REASON_REPEATED_EDITORIAL_PREFIX = "repeated_editorial_prefix"
REASON_PARENTHETICAL_HEAVY = "parenthetical_heavy"
REASON_OVERLY_LONG = "overly_long"
REASON_QUOTED_LITERALISM = "quoted_literalism"
REASON_TRANSLATION_ARTIFACT = "translation_artifact"

ALL_AUDIT_REASONS: tuple[str, ...] = (
    REASON_TECHNICAL_SCAFFOLDING,
    REASON_CYRILLIC_SOURCE_NOTE,
    REASON_SLASH_HEAVY,
    REASON_REPEATED_EDITORIAL_PREFIX,
    REASON_PARENTHETICAL_HEAVY,
    REASON_OVERLY_LONG,
    REASON_QUOTED_LITERALISM,
    REASON_TRANSLATION_ARTIFACT,
)

# Explicit scaffolding phrases (case-sensitive substrings as written in packs).
TECHNICAL_SCAFFOLDING_PHRASES: tuple[str, ...] = (
    "Source affliction tendency",
    "activated via project",
    "hard_aspected proxy",
    "activation proxy",
    "source describes",
    "Source describes",
    "source association",
    "unresolved",
    "resolver",
)

EDITORIAL_PREFIXES: tuple[str, ...] = (
    "Development focus:",
    "Source describes",
    "Source affliction tendency",
)

# Slash-heavy: two or more "/" characters (one ordinary alternative slash is OK).
SLASH_HEAVY_MIN_COUNT = 2

# Overly long: review signal only (character threshold).
OVERLY_LONG_MIN_CHARS = 110

# Parenthetical-heavy: any single parenthetical body at/above this length.
PARENTHETICAL_HEAVY_MIN_CHARS = 40

# Quoted awkward literal fragments known from source packs.
QUOTED_LITERAL_FRAGMENTS: tuple[str, ...] = (
    "dust in eyes",
)

# Explicit known translation artifacts only — no NLP quality model.
TRANSLATION_ARTIFACT_PHRASES: tuple[str, ...] = (
    "whiten oneself",
)

_CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")
_PAREN_RE = re.compile(r"\(([^)]*)\)")
_QUOTE_RE = re.compile(r'["“”]([^"“”]+)["“”]')

DEVELOPMENT_FOCUS_PREFIX = "Development focus:"

GOLDEN_PROFILE_NAMES: tuple[str, ...] = (
    "Avdey",
    "Vlad",
    "Dzmitry",
    "Andrey",
    "Milka",
)


@dataclass(frozen=True)
class HumanCopyAuditCandidate:
    fact_id: str
    factor_type: str
    factor_key: str
    category: str
    polarity: str
    source_text: str
    reasons: tuple[str, ...]
    human_override_exists: bool
    source_reference: str
    golden_profiles: tuple[str, ...] = ()
    golden_exposure_count: int = 0


@dataclass(frozen=True)
class DevelopmentFocusItem:
    fact_id: str
    factor_type: str
    factor_key: str
    category: str
    polarity: str
    source_text: str
    human_override_exists: bool
    golden_profiles: tuple[str, ...]
    golden_exposure_count: int


@dataclass(frozen=True)
class HumanCopyAuditReport:
    total_source_facts: int
    human_override_count: int
    candidates: tuple[HumanCopyAuditCandidate, ...]
    candidates_already_overridden: tuple[HumanCopyAuditCandidate, ...]
    candidates_still_raw: tuple[HumanCopyAuditCandidate, ...]
    reason_counts: Mapping[str, int]
    category_counts: Mapping[str, int]
    polarity_counts: Mapping[str, int]
    development_focus_items: tuple[DevelopmentFocusItem, ...]
    override_ids_missing_from_catalog: tuple[str, ...] = ()
    # Internal maintenance ordering only — never a person score.
    still_raw_by_presentation_review_priority: tuple[HumanCopyAuditCandidate, ...] = ()


def detect_audit_reasons(text: str) -> tuple[str, ...]:
    """Return deterministic mechanical readability reasons for one source text."""
    reasons: list[str] = []

    if any(phrase in text for phrase in TECHNICAL_SCAFFOLDING_PHRASES):
        reasons.append(REASON_TECHNICAL_SCAFFOLDING)

    if _CYRILLIC_RE.search(text):
        reasons.append(REASON_CYRILLIC_SOURCE_NOTE)

    if text.count("/") >= SLASH_HEAVY_MIN_COUNT:
        reasons.append(REASON_SLASH_HEAVY)

    if text.startswith(DEVELOPMENT_FOCUS_PREFIX) or any(
        prefix != DEVELOPMENT_FOCUS_PREFIX and prefix in text
        for prefix in EDITORIAL_PREFIXES
    ):
        reasons.append(REASON_REPEATED_EDITORIAL_PREFIX)

    paren_bodies = _PAREN_RE.findall(text)
    if any(len(body) >= PARENTHETICAL_HEAVY_MIN_CHARS for body in paren_bodies):
        reasons.append(REASON_PARENTHETICAL_HEAVY)

    if len(text) >= OVERLY_LONG_MIN_CHARS:
        reasons.append(REASON_OVERLY_LONG)

    quoted_chunks = [chunk.lower() for chunk in _QUOTE_RE.findall(text)]
    if any(
        fragment in chunk
        for chunk in quoted_chunks
        for fragment in QUOTED_LITERAL_FRAGMENTS
    ):
        reasons.append(REASON_QUOTED_LITERALISM)

    if any(phrase in text for phrase in TRANSLATION_ARTIFACT_PHRASES):
        reasons.append(REASON_TRANSLATION_ARTIFACT)

    # Stable reason order matching taxonomy declaration.
    order = {name: index for index, name in enumerate(ALL_AUDIT_REASONS)}
    return tuple(sorted(set(reasons), key=lambda name: order[name]))


def _presentation_review_sort_key(
    candidate: HumanCopyAuditCandidate,
) -> tuple[int, int, int, str]:
    """Tuple sort for presentation maintenance — not a person score.

    Order:
      1. still RAW in human UI first
      2. higher golden exposure
      3. more audit reasons
      4. stable fact_id
    """
    return (
        0 if not candidate.human_override_exists else 1,
        -candidate.golden_exposure_count,
        -len(candidate.reasons),
        candidate.fact_id,
    )


def build_golden_resolved_section_fact_ids() -> dict[str, frozenset[str]]:
    """Map golden profile display name → resolved section SourceFact IDs."""
    builders = {
        "Avdey": lambda: build_mercury_source_profile(
            MercurySourceProfileRequest(
                birth_date=date(1986, 7, 14),
                birth_time=time(7, 10),
                birth_place="Simferopol, Ukraine",
            )
        ),
        "Vlad": lambda: build_mercury_source_profile(
            MercurySourceProfileRequest(
                birth_date=date(1986, 5, 16),
                birth_time=time(15, 0),
                birth_place="Dnipro, Ukraine",
            )
        ),
        "Dzmitry": lambda: build_mercury_source_profile(
            MercurySourceProfileRequest(
                birth_date=date(1985, 11, 12),
                birth_time=time(14, 15),
                birth_place="Zhodino, Belarus",
            )
        ),
        "Andrey": lambda: build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Cancer",
                mercury_element="water",
                mercury_motion="direct",
                mercury_house=5,
                aspects=[
                    MercuryAspect(planet="Uranus", type="trine", orb_deg=1.65),
                    MercuryAspect(planet="Pluto", type="square", orb_deg=2.68),
                ],
            )
        ),
        "Milka": lambda: build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=False,
                mercury_sign="Pisces",
                mercury_element="water",
                mercury_motion="direct",
                mercury_house=None,
                aspects=[],
            )
        ),
    }

    exposure: dict[str, frozenset[str]] = {}
    for name in GOLDEN_PROFILE_NAMES:
        profile = builders[name]()
        synthesis = build_mercury_profile_synthesis(profile)
        ids = frozenset(
            fact_id
            for section in synthesis.sections
            for fact_id in section.resolved_fact_ids
        )
        exposure[name] = ids
    return exposure


def _golden_profiles_for_fact(
    fact_id: str,
    exposure_by_profile: Mapping[str, frozenset[str]],
) -> tuple[str, ...]:
    return tuple(
        name
        for name in GOLDEN_PROFILE_NAMES
        if fact_id in exposure_by_profile.get(name, frozenset())
    )


def audit_source_fact(
    fact: SourceFactDef,
    *,
    exposure_by_profile: Mapping[str, frozenset[str]] | None = None,
) -> HumanCopyAuditCandidate | None:
    """Return a candidate when mechanical reasons fire; otherwise None."""
    reasons = detect_audit_reasons(fact.text)
    if not reasons:
        return None
    profiles: tuple[str, ...] = ()
    if exposure_by_profile is not None:
        profiles = _golden_profiles_for_fact(fact.id, exposure_by_profile)
    return HumanCopyAuditCandidate(
        fact_id=fact.id,
        factor_type=fact.factor_type,
        factor_key=fact.factor_key,
        category=fact.category,
        polarity=fact.polarity,
        source_text=fact.text,
        reasons=reasons,
        human_override_exists=fact.id in HUMAN_COPY_OVERRIDES,
        source_reference=fact.source_reference,
        golden_profiles=profiles,
        golden_exposure_count=len(profiles),
    )


def inventory_development_focus(
    facts: Sequence[SourceFactDef] = ALL_SOURCE_FACTS,
    *,
    exposure_by_profile: Mapping[str, frozenset[str]] | None = None,
) -> tuple[DevelopmentFocusItem, ...]:
    """Deterministic inventory of all 'Development focus:' source facts."""
    exposure = exposure_by_profile or {}
    items: list[DevelopmentFocusItem] = []
    for fact in facts:
        if not fact.text.startswith(DEVELOPMENT_FOCUS_PREFIX):
            continue
        profiles = _golden_profiles_for_fact(fact.id, exposure)
        items.append(
            DevelopmentFocusItem(
                fact_id=fact.id,
                factor_type=fact.factor_type,
                factor_key=fact.factor_key,
                category=fact.category,
                polarity=fact.polarity,
                source_text=fact.text,
                human_override_exists=fact.id in HUMAN_COPY_OVERRIDES,
                golden_profiles=profiles,
                golden_exposure_count=len(profiles),
            )
        )
    return tuple(sorted(items, key=lambda item: item.fact_id))


def run_human_copy_audit(
    facts: Sequence[SourceFactDef] = ALL_SOURCE_FACTS,
    *,
    include_golden_exposure: bool = True,
    exposure_by_profile: Mapping[str, frozenset[str]] | None = None,
) -> HumanCopyAuditReport:
    """Full structured audit over the canonical knowledge catalog."""
    catalog_ids = {fact.id for fact in facts}
    missing_overrides = tuple(
        sorted(fact_id for fact_id in HUMAN_COPY_OVERRIDES if fact_id not in catalog_ids)
    )

    exposure = exposure_by_profile
    if include_golden_exposure and exposure is None:
        exposure = build_golden_resolved_section_fact_ids()
    if exposure is None:
        exposure = {name: frozenset() for name in GOLDEN_PROFILE_NAMES}

    candidates: list[HumanCopyAuditCandidate] = []
    for fact in facts:
        candidate = audit_source_fact(fact, exposure_by_profile=exposure)
        if candidate is not None:
            candidates.append(candidate)

    candidates_sorted = tuple(
        sorted(candidates, key=_presentation_review_sort_key)
    )
    already = tuple(c for c in candidates_sorted if c.human_override_exists)
    still_raw = tuple(c for c in candidates_sorted if not c.human_override_exists)

    reason_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    polarity_counts: Counter[str] = Counter()
    for candidate in candidates_sorted:
        reason_counts.update(candidate.reasons)
        category_counts[candidate.category] += 1
        polarity_counts[candidate.polarity] += 1

    return HumanCopyAuditReport(
        total_source_facts=len(facts),
        human_override_count=len(HUMAN_COPY_OVERRIDES),
        candidates=candidates_sorted,
        candidates_already_overridden=already,
        candidates_still_raw=still_raw,
        reason_counts=dict(sorted(reason_counts.items())),
        category_counts=dict(sorted(category_counts.items())),
        polarity_counts=dict(sorted(polarity_counts.items())),
        development_focus_items=inventory_development_focus(
            facts, exposure_by_profile=exposure
        ),
        override_ids_missing_from_catalog=missing_overrides,
        still_raw_by_presentation_review_priority=still_raw,
    )


def format_human_copy_audit_report(
    report: HumanCopyAuditReport,
    *,
    top_n: int = 20,
    reason_filter: str | None = None,
    show_all: bool = False,
) -> str:
    """Developer-readable stdout report (not the source of truth)."""
    lines: list[str] = []
    lines.append("Mercury Human Copy Audit")
    lines.append("")
    lines.append(f"Source facts: {report.total_source_facts}")
    lines.append(f"Curated overrides: {report.human_override_count}")
    lines.append(f"Audit candidates: {len(report.candidates)}")
    lines.append(f"Already overridden candidates: {len(report.candidates_already_overridden)}")
    lines.append(f"Still raw candidates: {len(report.candidates_still_raw)}")
    if report.override_ids_missing_from_catalog:
        lines.append(
            "WARNING missing override IDs: "
            + ", ".join(report.override_ids_missing_from_catalog)
        )
    lines.append("")
    lines.append("Counts by reason:")
    for reason in ALL_AUDIT_REASONS:
        lines.append(f"  {reason}: {report.reason_counts.get(reason, 0)}")
    lines.append("")
    lines.append("Counts by category:")
    for category, count in report.category_counts.items():
        lines.append(f"  {category}: {count}")
    lines.append("")
    lines.append("Counts by polarity:")
    for polarity, count in report.polarity_counts.items():
        lines.append(f"  {polarity}: {count}")

    pool = report.still_raw_by_presentation_review_priority
    if reason_filter:
        pool = tuple(c for c in pool if reason_filter in c.reasons)
        lines.append("")
        lines.append(f"Filtered still-raw by reason={reason_filter}: {len(pool)}")

    lines.append("")
    lines.append("Top raw candidates by profile exposure:")
    shown = pool if show_all else pool[:top_n]
    if not shown:
        lines.append("  (none)")
    for index, candidate in enumerate(shown, start=1):
        profiles = ", ".join(candidate.golden_profiles) or "(none)"
        lines.append(f"{index}. {candidate.fact_id}")
        lines.append(f"   reasons: {', '.join(candidate.reasons)}")
        lines.append(
            f"   profiles: {profiles} "
            f"(exposure={candidate.golden_exposure_count})"
        )
        lines.append(
            f"   factor: {candidate.factor_type}:{candidate.factor_key} "
            f"| {candidate.category}/{candidate.polarity}"
        )

    if show_all and not reason_filter:
        lines.append("")
        lines.append("All candidates (including already overridden):")
        for index, candidate in enumerate(report.candidates, start=1):
            status = "overridden" if candidate.human_override_exists else "raw"
            lines.append(
                f"{index}. [{status}] {candidate.fact_id} :: "
                f"{', '.join(candidate.reasons)}"
            )

    focus = report.development_focus_items
    overridden_focus = sum(1 for item in focus if item.human_override_exists)
    raw_focus = len(focus) - overridden_focus
    exposed_focus = [item for item in focus if item.golden_exposure_count]
    lines.append("")
    lines.append("Development focus:")
    lines.append(f"  total facts: {len(focus)}")
    lines.append(f"  currently overridden: {overridden_focus}")
    lines.append(f"  still raw: {raw_focus}")
    lines.append(f"  golden-exposed: {len(exposed_focus)}")
    for item in focus:
        status = "override" if item.human_override_exists else "raw"
        profiles = ", ".join(item.golden_profiles) or "-"
        lines.append(
            f"  - [{status}] {item.fact_id} "
            f"({item.factor_type}:{item.factor_key}) profiles={profiles}"
        )

    return "\n".join(lines)
