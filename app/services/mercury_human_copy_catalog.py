"""Mercury human presentation catalog — family coverage maintenance (S4.3).

SOURCE FACTS ARE IMMUTABLE EVIDENCE.

This module derives a presentation-maintenance catalog over ALL_SOURCE_FACTS.
It does not rewrite knowledge packs, change runtime UI fallback, or score people.

Runtime human display remains:
    HUMAN_COPY_OVERRIDES[id] if present else SourceFact.text

Review status is developer maintenance metadata only.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from app.services.mercury_human_copy import HUMAN_COPY_OVERRIDES
from app.services.mercury_human_copy_audit import detect_audit_reasons
from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS, SourceFactDef

STATUS_APPROVED_OVERRIDE = "approved_override"
STATUS_APPROVED_RAW = "approved_raw"
STATUS_NEEDS_REVIEW = "needs_review"
STATUS_UNREVIEWED = "unreviewed"

ALL_REVIEW_STATUSES: tuple[str, ...] = (
    STATUS_APPROVED_OVERRIDE,
    STATUS_APPROVED_RAW,
    STATUS_NEEDS_REVIEW,
    STATUS_UNREVIEWED,
)

# Explicit presentation decisions only (not overrides — those live in
# HUMAN_COPY_OVERRIDES). S4.3 seed + S4.4B Sagittarius family review.
APPROVED_RAW_FACT_IDS: frozenset[str] = frozenset(
    {
        # S4.3 seed
        "pluto_sq_strong_persuasiveness",
        "pluto_sq_powerful_words",
        "pluto_sq_debate_ability",
        "taurus_productive_thinking",
        "taurus_thorough_thinking",
        "taurus_measured_orderly_speech",
        "taurus_clearly_structured_speech",
        "taurus_thinks_before_speaking",
        "jupiter_sx_analysis_connects_with_synthesis",
        "uranus_cj_genius_potential",
        "uranus_cj_freshness_of_mind",
        "uranus_cj_openness_of_mind",
        "uranus_cj_spontaneous_creativity",
        "mars_tr_persuasive",
        "jupiter_sx_oratory_and_persuasion",
        # S4.4B Sagittarius approved_raw
        "sag_searches_higher_meaning_in_ordinary",
        "sag_bio_central_idea_grasping",
        "sag_bio_independent_research_learning",
        "sag_bio_learning_through_teaching",
        "sag_bio_monologue_learning",
        "sag_difficulty_theory_to_practice",
        "sag_theory_to_practice_gap_risk",
        "sag_learning_encyclopedias",
        "sag_learning_pass_knowledge_to_others",
        "sag_learning_setting_a_goal",
        "sag_learning_university_textbooks",
        "sag_teacher_like_with_siblings",
        "sag_tendency_to_attach_labels",
    }
)

# Explicit needs_review decisions. S4.4B holds framework/status statements
# for a later cross-family presentation policy.
NEEDS_REVIEW_FACT_IDS: frozenset[str] = frozenset(
    {
        "sag_bio_impartiality_disrupted",
        "sag_bio_learnability_disrupted",
        "sag_bio_major_exile",
    }
)

class HumanCopyCatalogError(ValueError):
    """Raised when presentation review registries are inconsistent."""


@dataclass(frozen=True)
class HumanCopyCatalogEntry:
    fact_id: str
    factor_type: str
    factor_key: str
    category: str
    polarity: str
    canonical_text: str
    human_text: str
    review_status: str
    uses_override: bool
    audit_reasons: tuple[str, ...]
    review_recommended: bool
    source_reference: str

    @property
    def family_key(self) -> str:
        return f"{self.factor_type}:{self.factor_key}"


@dataclass(frozen=True)
class HumanCopyFamilyCoverage:
    family_key: str
    factor_type: str
    factor_key: str
    total_facts: int
    approved_override: int
    approved_raw: int
    needs_review: int
    unreviewed: int
    review_recommended_unreviewed: int
    reviewed_count: int
    presentation_ready_count: int
    review_coverage: float
    presentation_ready_coverage: float


@dataclass(frozen=True)
class HumanCopyCatalogReport:
    total_facts: int
    entries: tuple[HumanCopyCatalogEntry, ...]
    approved_override_count: int
    approved_raw_count: int
    needs_review_count: int
    unreviewed_count: int
    reviewed_count: int
    presentation_ready_count: int
    review_coverage: float
    presentation_ready_coverage: float
    review_recommended_unreviewed_count: int
    families: tuple[HumanCopyFamilyCoverage, ...]


def validate_human_copy_registries(
    facts: Sequence[SourceFactDef] = ALL_SOURCE_FACTS,
    *,
    overrides: Mapping[str, str] | None = None,
    approved_raw: frozenset[str] | None = None,
    needs_review: frozenset[str] | None = None,
) -> None:
    """Fail loudly on conflicting or unknown presentation decisions."""
    catalog_ids = {fact.id for fact in facts}
    override_ids = set((overrides if overrides is not None else HUMAN_COPY_OVERRIDES).keys())
    raw_ids = set(approved_raw if approved_raw is not None else APPROVED_RAW_FACT_IDS)
    review_ids = set(needs_review if needs_review is not None else NEEDS_REVIEW_FACT_IDS)

    unknown_overrides = sorted(override_ids - catalog_ids)
    if unknown_overrides:
        raise HumanCopyCatalogError(
            f"Unknown HUMAN_COPY_OVERRIDES IDs: {unknown_overrides}"
        )

    unknown_raw = sorted(raw_ids - catalog_ids)
    if unknown_raw:
        raise HumanCopyCatalogError(
            f"Unknown APPROVED_RAW_FACT_IDS: {unknown_raw}"
        )

    unknown_needs = sorted(review_ids - catalog_ids)
    if unknown_needs:
        raise HumanCopyCatalogError(
            f"Unknown NEEDS_REVIEW_FACT_IDS: {unknown_needs}"
        )

    both_override_raw = sorted(override_ids & raw_ids)
    if both_override_raw:
        raise HumanCopyCatalogError(
            f"IDs cannot be override and approved_raw: {both_override_raw}"
        )

    both_override_needs = sorted(override_ids & review_ids)
    if both_override_needs:
        raise HumanCopyCatalogError(
            f"IDs cannot be override and needs_review: {both_override_needs}"
        )

    both_raw_needs = sorted(raw_ids & review_ids)
    if both_raw_needs:
        raise HumanCopyCatalogError(
            f"IDs cannot be approved_raw and needs_review: {both_raw_needs}"
        )


def derive_review_status(fact_id: str) -> str:
    """Derive review status from override + explicit decision registries."""
    if fact_id in HUMAN_COPY_OVERRIDES:
        return STATUS_APPROVED_OVERRIDE
    if fact_id in APPROVED_RAW_FACT_IDS:
        return STATUS_APPROVED_RAW
    if fact_id in NEEDS_REVIEW_FACT_IDS:
        return STATUS_NEEDS_REVIEW
    return STATUS_UNREVIEWED


def build_catalog_entry(fact: SourceFactDef) -> HumanCopyCatalogEntry:
    """Build one catalog entry for a canonical SourceFact."""
    status = derive_review_status(fact.id)
    uses_override = status == STATUS_APPROVED_OVERRIDE
    if uses_override:
        human_text = HUMAN_COPY_OVERRIDES[fact.id]
    else:
        human_text = fact.text
    reasons = detect_audit_reasons(fact.text)
    return HumanCopyCatalogEntry(
        fact_id=fact.id,
        factor_type=fact.factor_type,
        factor_key=fact.factor_key,
        category=fact.category,
        polarity=fact.polarity,
        canonical_text=fact.text,
        human_text=human_text,
        review_status=status,
        uses_override=uses_override,
        audit_reasons=reasons,
        review_recommended=bool(reasons),
        source_reference=fact.source_reference,
    )


def _coverage_ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _build_family_coverage(
    entries: Sequence[HumanCopyCatalogEntry],
) -> tuple[HumanCopyFamilyCoverage, ...]:
    by_family: dict[str, list[HumanCopyCatalogEntry]] = {}
    for entry in entries:
        by_family.setdefault(entry.family_key, []).append(entry)

    families: list[HumanCopyFamilyCoverage] = []
    for family_key in sorted(by_family):
        group = by_family[family_key]
        status_counts = Counter(item.review_status for item in group)
        approved_override = status_counts[STATUS_APPROVED_OVERRIDE]
        approved_raw = status_counts[STATUS_APPROVED_RAW]
        needs_review = status_counts[STATUS_NEEDS_REVIEW]
        unreviewed = status_counts[STATUS_UNREVIEWED]
        reviewed = approved_override + approved_raw + needs_review
        ready = approved_override + approved_raw
        recommended_unreviewed = sum(
            1
            for item in group
            if item.review_status == STATUS_UNREVIEWED and item.review_recommended
        )
        sample = group[0]
        total = len(group)
        families.append(
            HumanCopyFamilyCoverage(
                family_key=family_key,
                factor_type=sample.factor_type,
                factor_key=sample.factor_key,
                total_facts=total,
                approved_override=approved_override,
                approved_raw=approved_raw,
                needs_review=needs_review,
                unreviewed=unreviewed,
                review_recommended_unreviewed=recommended_unreviewed,
                reviewed_count=reviewed,
                presentation_ready_count=ready,
                review_coverage=_coverage_ratio(reviewed, total),
                presentation_ready_coverage=_coverage_ratio(ready, total),
            )
        )
    return tuple(families)


def build_human_copy_catalog(
    facts: Sequence[SourceFactDef] = ALL_SOURCE_FACTS,
) -> HumanCopyCatalogReport:
    """Build the full presentation catalog over canonical SourceFacts."""
    validate_human_copy_registries(facts)

    # Canonical SourceFact.id is the unit — one entry per fact, no alias inflation.
    entries = tuple(
        sorted(
            (build_catalog_entry(fact) for fact in facts),
            key=lambda item: (item.family_key, item.fact_id),
        )
    )
    status_counts = Counter(entry.review_status for entry in entries)
    approved_override = status_counts[STATUS_APPROVED_OVERRIDE]
    approved_raw = status_counts[STATUS_APPROVED_RAW]
    needs_review = status_counts[STATUS_NEEDS_REVIEW]
    unreviewed = status_counts[STATUS_UNREVIEWED]
    total = len(entries)
    reviewed = approved_override + approved_raw + needs_review
    ready = approved_override + approved_raw
    recommended_unreviewed = sum(
        1
        for entry in entries
        if entry.review_status == STATUS_UNREVIEWED and entry.review_recommended
    )

    return HumanCopyCatalogReport(
        total_facts=total,
        entries=entries,
        approved_override_count=approved_override,
        approved_raw_count=approved_raw,
        needs_review_count=needs_review,
        unreviewed_count=unreviewed,
        reviewed_count=reviewed,
        presentation_ready_count=ready,
        review_coverage=_coverage_ratio(reviewed, total),
        presentation_ready_coverage=_coverage_ratio(ready, total),
        review_recommended_unreviewed_count=recommended_unreviewed,
        families=_build_family_coverage(entries),
    )


def get_family_entries(
    report: HumanCopyCatalogReport,
    family_key: str,
) -> tuple[HumanCopyCatalogEntry, ...]:
    """Return catalog entries for one factor family, sorted by fact_id."""
    return tuple(
        entry
        for entry in report.entries
        if entry.family_key == family_key
    )


def least_reviewed_families(
    report: HumanCopyCatalogReport,
    *,
    limit: int = 10,
) -> tuple[HumanCopyFamilyCoverage, ...]:
    """Families with lowest review coverage (maintenance priority only)."""
    ordered = sorted(
        report.families,
        key=lambda family: (
            family.review_coverage,
            -family.unreviewed,
            -family.total_facts,
            family.family_key,
        ),
    )
    return tuple(ordered[: max(0, limit)])


def format_catalog_summary(report: HumanCopyCatalogReport, *, top_n: int = 10) -> str:
    """Concise developer maintenance summary."""
    lines = [
        "Mercury Human Presentation Catalog",
        "",
        f"Canonical facts: {report.total_facts}",
        f"Approved override: {report.approved_override_count}",
        f"Approved raw: {report.approved_raw_count}",
        f"Needs review: {report.needs_review_count}",
        f"Unreviewed: {report.unreviewed_count}",
        "",
        f"Reviewed coverage: {report.reviewed_count}/{report.total_facts} "
        f"({report.review_coverage:.1%})",
        f"Presentation-ready coverage: {report.presentation_ready_count}/"
        f"{report.total_facts} ({report.presentation_ready_coverage:.1%})",
        "",
        f"Families: {len(report.families)}",
        f"Review-recommended but unreviewed: "
        f"{report.review_recommended_unreviewed_count}",
        "",
        "Most incomplete families:",
    ]
    for family in least_reviewed_families(report, limit=top_n):
        lines.append(
            f"  {family.family_key} "
            f"reviewed={family.reviewed_count}/{family.total_facts} "
            f"({family.review_coverage:.0%}) "
            f"ready={family.presentation_ready_count} "
            f"unreviewed={family.unreviewed} "
            f"recommended={family.review_recommended_unreviewed}"
        )
    return "\n".join(lines)


def format_family_detail(
    report: HumanCopyCatalogReport,
    family_key: str,
) -> str:
    """Developer family review view."""
    family = next((item for item in report.families if item.family_key == family_key), None)
    entries = get_family_entries(report, family_key)
    if family is None or not entries:
        return f"Family not found or empty: {family_key}"

    lines = [
        f"Family: {family.family_key}",
        f"Total: {family.total_facts}",
        f"Approved override: {family.approved_override}",
        f"Approved raw: {family.approved_raw}",
        f"Needs review: {family.needs_review}",
        f"Unreviewed: {family.unreviewed}",
        f"Reviewed: {family.reviewed_count}/{family.total_facts} "
        f"({family.review_coverage:.0%})",
        f"Presentation-ready: {family.presentation_ready_count}/"
        f"{family.total_facts} ({family.presentation_ready_coverage:.0%})",
    ]

    def _section(title: str, items: Sequence[HumanCopyCatalogEntry]) -> None:
        lines.append("")
        lines.append(f"{title}:")
        if not items:
            lines.append("  (none)")
            return
        for entry in items:
            if entry.uses_override:
                lines.append(f"  [{entry.fact_id}]")
                lines.append(f"    canonical: {entry.canonical_text}")
                lines.append(f"    human: {entry.human_text}")
            else:
                reason_suffix = ""
                if entry.audit_reasons:
                    reason_suffix = f"\n    reasons: {', '.join(entry.audit_reasons)}"
                lines.append(f"  [{entry.fact_id}] {entry.canonical_text}{reason_suffix}")

    recommended = [
        e
        for e in entries
        if e.review_status == STATUS_UNREVIEWED and e.review_recommended
    ]
    clean_unreviewed = [
        e
        for e in entries
        if e.review_status == STATUS_UNREVIEWED and not e.review_recommended
    ]
    needs = [e for e in entries if e.review_status == STATUS_NEEDS_REVIEW]
    approved_raw = [e for e in entries if e.review_status == STATUS_APPROVED_RAW]
    approved_override = [
        e for e in entries if e.review_status == STATUS_APPROVED_OVERRIDE
    ]

    _section("UNREVIEWED / RECOMMENDED", recommended)
    _section("UNREVIEWED / CLEAN", clean_unreviewed)
    _section("NEEDS REVIEW", needs)
    _section("APPROVED RAW", approved_raw)
    _section("APPROVED OVERRIDE", approved_override)
    return "\n".join(lines)
