"""Mars human presentation catalog — coverage over all 504 canonical facts.

SOURCE FACTS ARE IMMUTABLE EVIDENCE.

This module derives presentation-maintenance metadata over ALL_MARS_SOURCE_FACTS.
It does not rewrite knowledge packs, change tags, or score people.

Runtime human display remains:
    HUMAN_COPY_OVERRIDES[id] if present else MarsSourceFact.text

Review status is developer maintenance metadata only.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from app.services.mars_human_copy import HUMAN_COPY_OVERRIDES
from app.services.mars_human_copy_audit import detect_audit_reasons
from app.services.mars_source_knowledge import ALL_MARS_SOURCE_FACTS, MarsSourceFactDef

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

FAMILY_BUCKETS: tuple[str, ...] = ("sign", "house", "motion", "l9", "bio")

# Explicit needs_review decisions only. M7 reviewed all 504 facts; remaining
# conditionals are preserved in copy without inventing resolvers.
NEEDS_REVIEW_FACT_IDS: frozenset[str] = frozenset()

# Remainder after overrides + needs_review: canonical English already usable.
APPROVED_RAW_FACT_IDS: frozenset[str] = frozenset(
    fact.id
    for fact in ALL_MARS_SOURCE_FACTS
    if fact.id not in HUMAN_COPY_OVERRIDES and fact.id not in NEEDS_REVIEW_FACT_IDS
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
    scope: str
    canonical_text: str
    human_text: str
    review_status: str
    uses_override: bool
    audit_reasons: tuple[str, ...]
    review_recommended: bool
    source_reference: str
    family_bucket: str

    @property
    def family_key(self) -> str:
        return f"{self.factor_type}:{self.factor_key}"


@dataclass(frozen=True)
class HumanCopyFamilyCoverage:
    family_key: str
    factor_type: str
    factor_key: str
    family_bucket: str
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
class HumanCopyBucketCoverage:
    bucket: str
    total_facts: int
    approved_override: int
    approved_raw: int
    needs_review: int
    unreviewed: int
    reviewed_count: int
    presentation_ready_count: int


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
    buckets: tuple[HumanCopyBucketCoverage, ...]


def family_bucket_for_fact(fact: MarsSourceFactDef) -> str:
    if fact.factor_type != "aspect":
        return fact.factor_type
    if fact.factor_key.startswith("pair_"):
        return "bio"
    return "l9"


def validate_human_copy_registries(
    facts: Sequence[MarsSourceFactDef] = ALL_MARS_SOURCE_FACTS,
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

    covered = override_ids | raw_ids | review_ids
    missing = sorted(catalog_ids - covered)
    if missing:
        raise HumanCopyCatalogError(
            f"Unreviewed Mars fact IDs (must be override, raw, or needs_review): {missing}"
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


def build_catalog_entry(fact: MarsSourceFactDef) -> HumanCopyCatalogEntry:
    """Build one catalog entry for a canonical MarsSourceFact."""
    status = derive_review_status(fact.id)
    uses_override = status == STATUS_APPROVED_OVERRIDE
    if uses_override:
        human_text = HUMAN_COPY_OVERRIDES[fact.id]
    else:
        human_text = fact.text
    reasons = detect_audit_reasons(human_text, fact_id=fact.id)
    return HumanCopyCatalogEntry(
        fact_id=fact.id,
        factor_type=fact.factor_type,
        factor_key=fact.factor_key,
        category=fact.category,
        polarity=fact.polarity,
        scope=fact.scope,
        canonical_text=fact.text,
        human_text=human_text,
        review_status=status,
        uses_override=uses_override,
        audit_reasons=reasons,
        review_recommended=bool(reasons),
        source_reference=fact.source_reference,
        family_bucket=family_bucket_for_fact(fact),
    )


def _coverage_ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _status_counts(entries: Sequence[HumanCopyCatalogEntry]) -> tuple[int, int, int, int]:
    status_counts = Counter(item.review_status for item in entries)
    return (
        status_counts[STATUS_APPROVED_OVERRIDE],
        status_counts[STATUS_APPROVED_RAW],
        status_counts[STATUS_NEEDS_REVIEW],
        status_counts[STATUS_UNREVIEWED],
    )


def _build_family_coverage(
    entries: Sequence[HumanCopyCatalogEntry],
) -> tuple[HumanCopyFamilyCoverage, ...]:
    by_family: dict[str, list[HumanCopyCatalogEntry]] = {}
    for entry in entries:
        by_family.setdefault(entry.family_key, []).append(entry)

    families: list[HumanCopyFamilyCoverage] = []
    for family_key in sorted(by_family):
        group = by_family[family_key]
        approved_override, approved_raw, needs_review, unreviewed = _status_counts(group)
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
                family_bucket=sample.family_bucket,
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


def _build_bucket_coverage(
    entries: Sequence[HumanCopyCatalogEntry],
) -> tuple[HumanCopyBucketCoverage, ...]:
    buckets: list[HumanCopyBucketCoverage] = []
    for bucket in FAMILY_BUCKETS:
        group = [item for item in entries if item.family_bucket == bucket]
        approved_override, approved_raw, needs_review, unreviewed = _status_counts(group)
        buckets.append(
            HumanCopyBucketCoverage(
                bucket=bucket,
                total_facts=len(group),
                approved_override=approved_override,
                approved_raw=approved_raw,
                needs_review=needs_review,
                unreviewed=unreviewed,
                reviewed_count=approved_override + approved_raw + needs_review,
                presentation_ready_count=approved_override + approved_raw,
            )
        )
    return tuple(buckets)


def build_human_copy_catalog(
    facts: Sequence[MarsSourceFactDef] = ALL_MARS_SOURCE_FACTS,
) -> HumanCopyCatalogReport:
    """Build the full presentation catalog over canonical Mars source facts."""
    validate_human_copy_registries(facts)

    entries = tuple(
        sorted(
            (build_catalog_entry(fact) for fact in facts),
            key=lambda item: (item.family_bucket, item.family_key, item.fact_id),
        )
    )
    approved_override, approved_raw, needs_review, unreviewed = _status_counts(entries)
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
        buckets=_build_bucket_coverage(entries),
    )


def get_family_entries(
    report: HumanCopyCatalogReport,
    family_key: str,
) -> tuple[HumanCopyCatalogEntry, ...]:
    return tuple(
        entry
        for entry in report.entries
        if entry.family_key == family_key
    )


def format_catalog_summary(report: HumanCopyCatalogReport) -> str:
    """Concise developer maintenance summary."""
    lines = [
        "Mars Human Presentation Catalog",
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
        "By family bucket:",
    ]
    for bucket in report.buckets:
        lines.append(
            f"  {bucket.bucket}: total={bucket.total_facts} "
            f"override={bucket.approved_override} "
            f"raw={bucket.approved_raw} "
            f"needs={bucket.needs_review} "
            f"unreviewed={bucket.unreviewed} "
            f"ready={bucket.presentation_ready_count}"
        )
    return "\n".join(lines)
