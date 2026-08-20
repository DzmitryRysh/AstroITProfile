"""Mercury Source Profile v2 — Aspect Batch C12 (Venus reachable family).

C12 completes the physically reachable natal Mercury–Venus major aspects:

- sextile_Venus
- conjunction_Venus

square/trine/opposition Venus remain IMPOSSIBLE_NATAL_GEOMETRY — do not add packs.

Source presents sextile and conjunction under one combined Bioastrology section.
Both share the same source body; conjunction alone adds stronger rigid automatism.

NO ASPECT_PACK_ALIAS between them.

Ancestry/genesis and celebrity/profession examples intentionally omitted.

SOURCE FIRST → SYNTHESIS SECOND.
Local SourceFactDef/_f avoid circular import with mercury_source_knowledge.py.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceFactDef:
    id: str
    factor_type: str
    factor_key: str
    category: str
    text: str
    polarity: str
    tags: tuple[str, ...] = ()
    source_reference: str = ""
    activation_condition: str | None = None
    unresolved: bool = False


def _f(
    id: str,
    factor_type: str,
    factor_key: str,
    category: str,
    text: str,
    polarity: str,
    *tags: str,
    source_reference: str,
    activation_condition: str | None = None,
    unresolved: bool = False,
) -> SourceFactDef:
    return SourceFactDef(
        id=id,
        factor_type=factor_type,
        factor_key=factor_key,
        category=category,
        text=text,
        polarity=polarity,
        tags=tags,
        source_reference=source_reference,
        activation_condition=activation_condition,
        unresolved=unresolved,
    )


REF_VENUS_SX_CJ = "bioastrology_mercury_venus_sextile_conjunction"


def _common_body(factor_key: str, id_prefix: str) -> tuple[SourceFactDef, ...]:
    """Shared Bioastrology Mercury–Venus sextile/conjunction atoms for one factor pack."""
    return (
        _f(
            f"{id_prefix}_predominantly_harmonious_source_classification",
            "aspect",
            factor_key,
            "source_specific",
            "Source classifies this Mercury–Venus configuration as predominantly "
            "harmonious and bringing more benefit than harm "
            "(source classification; not an always-positive guarantee, not a hiring "
            "or objective performance score).",
            "neutral",
            "predominantly_harmonious_source_classification",
            source_reference=REF_VENUS_SX_CJ,
        ),
        _f(
            f"{id_prefix}_concrete_thinking",
            "aspect",
            factor_key,
            "thinking",
            "Venus makes thinking more concrete / subject-oriented "
            "(not equated with analytical_thinking or technical_ability).",
            "strength",
            "concrete_thinking",
            source_reference=REF_VENUS_SX_CJ,
        ),
        _f(
            f"{id_prefix}_practical_thinking",
            "aspect",
            factor_key,
            "thinking",
            "Venus makes thinking more practical "
            "(not equated with analytical_thinking, planning, or financial_skill).",
            "strength",
            "practical_thinking",
            source_reference=REF_VENUS_SX_CJ,
        ),
        _f(
            f"{id_prefix}_beautiful_handwriting",
            "aspect",
            factor_key,
            "communication",
            "Handwriting becomes more beautiful.",
            "strength",
            "beautiful_handwriting",
            source_reference=REF_VENUS_SX_CJ,
        ),
        _f(
            f"{id_prefix}_beautiful_speech",
            "aspect",
            factor_key,
            "communication",
            "Speech becomes more beautiful "
            "(not equated with soft_speech, persuasion, oratory, or "
            "communication_skill).",
            "strength",
            "beautiful_speech",
            source_reference=REF_VENUS_SX_CJ,
        ),
        _f(
            f"{id_prefix}_grounding_venus_from_esoteric_drift",
            "aspect",
            factor_key,
            "thinking",
            "Mercury allows Venus to avoid drifting into \"esoteric thickets\" "
            "(source grounding; not equated with anti-spirituality, skepticism, "
            "evidence_requirement, or analytical_thinking).",
            "strength",
            "grounding_venus_from_esoteric_drift",
            source_reference=REF_VENUS_SX_CJ,
        ),
        _f(
            f"{id_prefix}_source_dependency_avoidance_venus_context",
            "aspect",
            factor_key,
            "source_specific",
            "Mercury allows Venus to avoid falling into dependencies "
            "(source-described tendency in Venus context; not a clinical claim "
            "that a person cannot develop addiction/dependency).",
            "strength",
            "source_dependency_avoidance_venus_context",
            source_reference=REF_VENUS_SX_CJ,
        ),
        _f(
            f"{id_prefix}_verbalizes_financial_motives",
            "aspect",
            factor_key,
            "communication",
            "Ability to verbalize / speak out financial motives "
            "(not equated with financial literacy or persuasion).",
            "strength",
            "verbalizes_financial_motives",
            source_reference=REF_VENUS_SX_CJ,
        ),
        _f(
            f"{id_prefix}_verbalizes_romantic_motives",
            "aspect",
            factor_key,
            "communication",
            "Ability to verbalize / speak out romantic / love motives "
            "(not equated with relationship skill, emotional intelligence, or "
            "persuasion).",
            "strength",
            "verbalizes_romantic_motives",
            source_reference=REF_VENUS_SX_CJ,
        ),
        _f(
            f"{id_prefix}_financial_reasonableness",
            "aspect",
            factor_key,
            "thinking",
            "Reasonableness in finances "
            "(context-specific; not equated with generic reasonableness or "
            "financial success).",
            "strength",
            "financial_reasonableness",
            source_reference=REF_VENUS_SX_CJ,
        ),
        _f(
            f"{id_prefix}_relationship_reasonableness",
            "aspect",
            factor_key,
            "thinking",
            "Reasonableness in relationships "
            "(context-specific; not equated with generic reasonableness or "
            "relationship skill).",
            "strength",
            "relationship_reasonableness",
            source_reference=REF_VENUS_SX_CJ,
        ),
        _f(
            f"{id_prefix}_commercial_talent",
            "aspect",
            factor_key,
            "work_application",
            "Commercial talent "
            "(source-described; not equated with sales, persuasion, negotiation, "
            "entrepreneurship, or income).",
            "strength",
            "commercial_talent",
            source_reference=REF_VENUS_SX_CJ,
        ),
        _f(
            f"{id_prefix}_writing_ability",
            "aspect",
            factor_key,
            "communication",
            "Writing abilities.",
            "strength",
            "writing",
            source_reference=REF_VENUS_SX_CJ,
        ),
        _f(
            f"{id_prefix}_copywriting_ability",
            "aspect",
            factor_key,
            "communication",
            "Copywriting abilities "
            "(not equated with persuasion, sales, marketing, or oratory).",
            "strength",
            "copywriting_ability",
            source_reference=REF_VENUS_SX_CJ,
        ),
        _f(
            f"{id_prefix}_reasonable_emotional_switching",
            "aspect",
            factor_key,
            "source_specific",
            "Reasonable switching in feelings — for example, not remaining stuck "
            "on a toxic partner "
            "(source-described tendency; does not assert that a current partner "
            "exists, is toxic, or diagnose attachment/mental-health conditions; "
            "not equated with adaptability or emotional_intelligence).",
            "strength",
            "reasonable_emotional_switching",
            source_reference=REF_VENUS_SX_CJ,
        ),
        _f(
            f"{id_prefix}_understands_information_flows",
            "aspect",
            factor_key,
            "thinking",
            "Ability to understand information flows "
            "(not equated with analytical_thinking, insight, systems_thinking, "
            "or technical_ability).",
            "strength",
            "understands_information_flows",
            source_reference=REF_VENUS_SX_CJ,
        ),
        _f(
            f"{id_prefix}_clear_self_expression",
            "aspect",
            factor_key,
            "communication",
            "Ability to express oneself understandably / clearly "
            "(not equated with persuasion, oratory, argumentation, or "
            "communication_skill).",
            "strength",
            "clear_self_expression",
            source_reference=REF_VENUS_SX_CJ,
        ),
    )


# ---------------------------------------------------------------------------
# Mercury sextile Venus — Bioastrology
# Canonical public catalog key: sextile_Venus
# ---------------------------------------------------------------------------
VENUS_SEXTILE: tuple[SourceFactDef, ...] = _common_body("sextile_Venus", "ven_sx")

# ---------------------------------------------------------------------------
# Mercury conjunction Venus — Bioastrology
# Canonical public catalog key: conjunction_Venus
# Shared body + conjunction-specific automatism (NO alias to sextile).
# ---------------------------------------------------------------------------
VENUS_CONJUNCTION_AUTOMATISM: tuple[SourceFactDef, ...] = (
    _f(
        "ven_cj_love_thought_commercial_automatism",
        "aspect",
        "conjunction_Venus",
        "source_specific",
        "Conjunction difference: stronger / more rigid automatism — affection/"
        "value response and thinking become more automatically linked "
        "(source illustration: love → think; think → look for a way to love or "
        "sell). Source-described mechanism; not equated with sales, persuasion, "
        "romantic obsession, commercialism, or love addiction.",
        "neutral",
        "love_thought_commercial_automatism",
        source_reference=REF_VENUS_SX_CJ,
    ),
)

VENUS_CONJUNCTION: tuple[SourceFactDef, ...] = (
    _common_body("conjunction_Venus", "ven_cj") + VENUS_CONJUNCTION_AUTOMATISM
)

C12_ASPECT_PACKS: tuple[SourceFactDef, ...] = VENUS_SEXTILE + VENUS_CONJUNCTION

C12_SUPPORTED_ASPECT_KEYS = frozenset({"sextile_Venus", "conjunction_Venus"})
