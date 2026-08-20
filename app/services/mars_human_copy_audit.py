"""Deterministic Mars human-copy readability audit.

SOURCE FACTS ARE IMMUTABLE EVIDENCE.

This module flags mechanical presentation/readability signals. It does not
rewrite facts, call an LLM, or change synthesis/UI behavior.
Occupation lists, source-bound medical language, and necessary conditionals
are reported as exceptions rather than auto-failed.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date, time

from app.services.mars_human_copy import HUMAN_COPY_OVERRIDES
from app.services.mars_profile_synthesis import build_mars_profile_synthesis
from app.services.mars_source_knowledge import ALL_MARS_SOURCE_FACTS, MarsSourceFactDef
from app.services.mars_source_profile import build_mars_source_profile

REASON_TECHNICAL_SCAFFOLDING = "technical_scaffolding"
REASON_SLASH_HEAVY = "slash_heavy"
REASON_REPEATED_EDITORIAL_PREFIX = "repeated_editorial_prefix"
REASON_PARENTHETICAL_HEAVY = "parenthetical_heavy"
REASON_OVERLY_LONG = "overly_long"
REASON_QUOTED_LITERALISM = "quoted_literalism"
REASON_TRANSLATION_ARTIFACT = "translation_artifact"
REASON_DETERMINISTIC_ACCUSATION = "deterministic_accusation"
REASON_COMPETENCE_INFLATION = "competence_inflation"

ALL_AUDIT_REASONS: tuple[str, ...] = (
    REASON_TECHNICAL_SCAFFOLDING,
    REASON_SLASH_HEAVY,
    REASON_REPEATED_EDITORIAL_PREFIX,
    REASON_PARENTHETICAL_HEAVY,
    REASON_OVERLY_LONG,
    REASON_QUOTED_LITERALISM,
    REASON_TRANSLATION_ARTIFACT,
    REASON_DETERMINISTIC_ACCUSATION,
    REASON_COMPETENCE_INFLATION,
)

TECHNICAL_SCAFFOLDING_PHRASES: tuple[str, ...] = (
    "Source affliction tendency",
    "activated via project",
    "hard_aspected",
    "activation proxy",
    "activation condition",
    "source describes",
    "Source describes",
    "Source-described",
    "source-described",
    "source association",
    "Source association",
    "Source compensation",
    "source-framework",
    "astrological configuration",
    "Possible expression cluster",
    "unresolved",
    "resolver",
)

EDITORIAL_PREFIXES: tuple[str, ...] = (
    "Source compensation:",
    "Source describes",
    "Source-described",
    "Source association",
    "Possible expression cluster A:",
    "Possible expression cluster B:",
)

SLASH_HEAVY_MIN_COUNT = 2
OVERLY_LONG_MIN_CHARS = 110
PARENTHETICAL_HEAVY_MIN_CHARS = 40

QUOTED_LITERAL_FRAGMENTS: tuple[str, ...] = (
    "measure seven times",
)

TRANSLATION_ARTIFACT_PHRASES: tuple[str, ...] = (
    "whiten oneself",
    "yin-like phase expression",
)

DETERMINISTIC_ACCUSATION_PHRASES: tuple[str, ...] = (
    "You are violent",
    "you are violent",
    "You will develop",
    "you will develop",
    "You are a liar",
    "this person is violent",
    "This person lies",
    "You are unreliable",
)

COMPETENCE_INFLATION_PHRASES: tuple[str, ...] = (
    "would be good at",
    "Would be good at",
    "should work as",
    "Should work as",
    "is qualified for",
    "Is qualified for",
    "strong technical skills",
    "Strong technical skills",
    "effective manager",
    "Effective manager",
    "is an effective manager",
)

# Occupation / medical / necessary-condition facts may keep slash lists or
# source-bounding language. Audit reports them; they are not auto-failed.
JUSTIFIED_EXCEPTION_FACT_IDS: frozenset[str] = frozenset()

_PAREN_RE = re.compile(r"\(([^)]*)\)")
_QUOTE_RE = re.compile(r'["“”]([^"“”]+)["“”]')

GOLDEN_PROFILE_NAMES: tuple[str, ...] = (
    "Avdey",
    "Vlad",
    "Dzmitry",
)


@dataclass(frozen=True)
class HumanCopyAuditCandidate:
    fact_id: str
    factor_type: str
    factor_key: str
    category: str
    polarity: str
    source_text: str
    display_text: str
    reasons: tuple[str, ...]
    human_override_exists: bool
    justified_exception: bool
    source_reference: str
    golden_profiles: tuple[str, ...] = ()
    golden_exposure_count: int = 0


@dataclass(frozen=True)
class HumanCopyAuditReport:
    total_source_facts: int
    human_override_count: int
    candidates: tuple[HumanCopyAuditCandidate, ...]
    candidates_already_overridden: tuple[HumanCopyAuditCandidate, ...]
    candidates_still_raw: tuple[HumanCopyAuditCandidate, ...]
    justified_exceptions: tuple[HumanCopyAuditCandidate, ...]
    reason_counts: Mapping[str, int]
    category_counts: Mapping[str, int]
    polarity_counts: Mapping[str, int]
    override_ids_missing_from_catalog: tuple[str, ...] = ()
    still_raw_by_presentation_review_priority: tuple[HumanCopyAuditCandidate, ...] = ()


def detect_audit_reasons(text: str, *, fact_id: str | None = None) -> tuple[str, ...]:
    """Return deterministic mechanical readability reasons for one text."""
    del fact_id  # reserved for justified-exception callers
    reasons: list[str] = []

    if any(phrase in text for phrase in TECHNICAL_SCAFFOLDING_PHRASES):
        reasons.append(REASON_TECHNICAL_SCAFFOLDING)

    if text.count("/") >= SLASH_HEAVY_MIN_COUNT:
        reasons.append(REASON_SLASH_HEAVY)

    if any(text.startswith(prefix) or prefix in text for prefix in EDITORIAL_PREFIXES):
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

    if any(phrase in text for phrase in DETERMINISTIC_ACCUSATION_PHRASES):
        reasons.append(REASON_DETERMINISTIC_ACCUSATION)

    if any(phrase in text for phrase in COMPETENCE_INFLATION_PHRASES):
        reasons.append(REASON_COMPETENCE_INFLATION)

    order = {name: index for index, name in enumerate(ALL_AUDIT_REASONS)}
    return tuple(sorted(set(reasons), key=lambda name: order[name]))


def is_justified_exception(fact: MarsSourceFactDef, reasons: Sequence[str]) -> bool:
    """Occupation lists, source-bound medical language, and necessary conditionals."""
    if fact.id in JUSTIFIED_EXCEPTION_FACT_IDS:
        return True
    if not reasons:
        return False
    occupation_like = (
        fact.category == "professional_association"
        or "occupation" in fact.id
        or "association with work involving" in fact.text.lower()
    )
    medical_source_bound = fact.scope == "SOURCE_ONLY" or "not a medical" in fact.text.lower()
    necessary_conditional = bool(fact.activation_condition) or fact.unresolved
    allowed = {REASON_SLASH_HEAVY, REASON_OVERLY_LONG, REASON_PARENTHETICAL_HEAVY}
    if set(reasons) <= allowed and (occupation_like or medical_source_bound or necessary_conditional):
        return True
    if occupation_like and REASON_SLASH_HEAVY in reasons:
        extra = set(reasons) - {REASON_SLASH_HEAVY, REASON_OVERLY_LONG}
        if not extra:
            return True
    return False


def _presentation_review_sort_key(
    candidate: HumanCopyAuditCandidate,
) -> tuple[int, int, int, int, str]:
    return (
        0 if not candidate.human_override_exists else 1,
        1 if candidate.justified_exception else 0,
        -candidate.golden_exposure_count,
        -len(candidate.reasons),
        candidate.fact_id,
    )


def build_golden_resolved_section_fact_ids() -> dict[str, frozenset[str]]:
    builders = {
        "Avdey": lambda: build_mars_source_profile(
            birth_date=date(1986, 7, 14),
            birth_time=time(7, 10),
            birth_place="Simferopol, Ukraine",
        ),
        "Vlad": lambda: build_mars_source_profile(
            birth_date=date(1986, 5, 16),
            birth_time=time(15, 0),
            birth_place="Dnipro, Ukraine",
        ),
        "Dzmitry": lambda: build_mars_source_profile(
            birth_date=date(1985, 11, 12),
            birth_time=time(14, 15),
            birth_place="Zhodino, Belarus",
        ),
    }
    exposure: dict[str, frozenset[str]] = {}
    for name in GOLDEN_PROFILE_NAMES:
        profile = builders[name]()
        synthesis = build_mars_profile_synthesis(profile)
        ids = frozenset(
            fact_id
            for section in synthesis.sections
            for fact_id in section.fact_ids
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
    fact: MarsSourceFactDef,
    *,
    exposure_by_profile: Mapping[str, frozenset[str]] | None = None,
) -> HumanCopyAuditCandidate | None:
    display = HUMAN_COPY_OVERRIDES.get(fact.id, fact.text)
    reasons = detect_audit_reasons(display, fact_id=fact.id)
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
        display_text=display,
        reasons=reasons,
        human_override_exists=fact.id in HUMAN_COPY_OVERRIDES,
        justified_exception=is_justified_exception(fact, reasons),
        source_reference=fact.source_reference,
        golden_profiles=profiles,
        golden_exposure_count=len(profiles),
    )


def run_human_copy_audit(
    facts: Sequence[MarsSourceFactDef] = ALL_MARS_SOURCE_FACTS,
    *,
    include_golden_exposure: bool = True,
    exposure_by_profile: Mapping[str, frozenset[str]] | None = None,
) -> HumanCopyAuditReport:
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

    candidates_sorted = tuple(sorted(candidates, key=_presentation_review_sort_key))
    already = tuple(c for c in candidates_sorted if c.human_override_exists)
    still_raw = tuple(c for c in candidates_sorted if not c.human_override_exists)
    justified = tuple(c for c in candidates_sorted if c.justified_exception)

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
        justified_exceptions=justified,
        reason_counts=dict(sorted(reason_counts.items())),
        category_counts=dict(sorted(category_counts.items())),
        polarity_counts=dict(sorted(polarity_counts.items())),
        override_ids_missing_from_catalog=missing_overrides,
        still_raw_by_presentation_review_priority=still_raw,
    )


def format_human_copy_audit_report(
    report: HumanCopyAuditReport,
    *,
    top_n: int = 20,
) -> str:
    lines = [
        "Mars Human Copy Audit",
        "",
        f"Source facts: {report.total_source_facts}",
        f"Curated overrides: {report.human_override_count}",
        f"Audit candidates: {len(report.candidates)}",
        f"Already overridden candidates: {len(report.candidates_already_overridden)}",
        f"Still raw candidates: {len(report.candidates_still_raw)}",
        f"Justified exceptions: {len(report.justified_exceptions)}",
        "",
        "Counts by reason:",
    ]
    for reason in ALL_AUDIT_REASONS:
        lines.append(f"  {reason}: {report.reason_counts.get(reason, 0)}")
    lines.append("")
    lines.append("Top still-raw candidates:")
    shown = report.still_raw_by_presentation_review_priority[:top_n]
    if not shown:
        lines.append("  (none)")
    for index, candidate in enumerate(shown, start=1):
        profiles = ", ".join(candidate.golden_profiles) or "(none)"
        exception = " justified" if candidate.justified_exception else ""
        lines.append(f"{index}. {candidate.fact_id}{exception}")
        lines.append(f"   reasons: {', '.join(candidate.reasons)}")
        lines.append(f"   profiles: {profiles}")
    return "\n".join(lines)
