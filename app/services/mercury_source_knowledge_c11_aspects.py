"""Mercury Source Profile v2 — Aspect Batch C11 (Sun conjunction).

C11 completes the only physically reachable natal Mercury–Sun major aspect:

- conjunction_Sun

Do NOT add sextile/square/trine/opposition Sun packs
(those remain IMPOSSIBLE_NATAL_GEOMETRY).

Combustion (orb strictly < 5°) is deterministic via:
sun_mercury_combustion_orb_lt_5

External affliction branch is unresolved:
external_affliction_context_unresolved — no affliction resolver.

Ancestry/genesis and celebrity examples intentionally omitted.

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


REF_SUN_CONJ = "bioastrology_mercury_sun_conjunction"
_COMBUSTION_ORB_LT_5 = "sun_mercury_combustion_orb_lt_5"
_EXTERNAL_AFFLICTION_UNRESOLVED = "external_affliction_context_unresolved"


# ---------------------------------------------------------------------------
# Mercury conjunction Sun — Bioastrology
# Canonical public catalog key: conjunction_Sun
# ---------------------------------------------------------------------------
SUN_CONJUNCTION_BASE: tuple[SourceFactDef, ...] = (
    _f(
        "sun_cj_identity_thought_fusion",
        "aspect",
        "conjunction_Sun",
        "thinking",
        "Identity / sense of self is closely tied to thinking "
        "(source Descartes-style framing: thinking as the ground of being; "
        "not equated with intelligence, confidence, or self-awareness).",
        "neutral",
        "identity_thought_fusion",
        source_reference=REF_SUN_CONJ,
    ),
    _f(
        "sun_cj_creative_phrasing",
        "aspect",
        "conjunction_Sun",
        "communication",
        "Creative phrases / creative wording "
        "(not equated with generic creativity).",
        "strength",
        "creative_phrasing",
        source_reference=REF_SUN_CONJ,
    ),
    _f(
        "sun_cj_oratory_mastery",
        "aspect",
        "conjunction_Sun",
        "communication",
        "Oratory mastery "
        "(source-described aptitude; not equated with persuasion, debate, or "
        "argumentation).",
        "strength",
        "source_oratory_aptitude",
        source_reference=REF_SUN_CONJ,
    ),
    _f(
        "sun_cj_sense_of_humor",
        "aspect",
        "conjunction_Sun",
        "communication",
        "Humor / sense of humor.",
        "strength",
        "sense_of_humor",
        source_reference=REF_SUN_CONJ,
    ),
    _f(
        "sun_cj_writing_ability",
        "aspect",
        "conjunction_Sun",
        "communication",
        "Writing ability.",
        "strength",
        "writing",
        source_reference=REF_SUN_CONJ,
    ),
    _f(
        "sun_cj_reasonableness",
        "aspect",
        "conjunction_Sun",
        "thinking",
        "Reasonableness.",
        "strength",
        "reasonableness",
        source_reference=REF_SUN_CONJ,
    ),
    _f(
        "sun_cj_enjoys_books",
        "aspect",
        "conjunction_Sun",
        "learning",
        "Enjoyment / pleasure from books "
        "(not equated with generic books aptitude).",
        "neutral",
        "enjoys_books",
        source_reference=REF_SUN_CONJ,
    ),
    _f(
        "sun_cj_enjoys_trips",
        "aspect",
        "conjunction_Sun",
        "mobility",
        "Enjoyment of trips "
        "(not equated with generic trips relevance).",
        "neutral",
        "enjoys_trips",
        source_reference=REF_SUN_CONJ,
    ),
    _f(
        "sun_cj_enjoys_communication",
        "aspect",
        "conjunction_Sun",
        "communication",
        "Enjoyment of communication "
        "(not equated with communication skill).",
        "neutral",
        "enjoys_communication",
        source_reference=REF_SUN_CONJ,
    ),
    _f(
        "sun_cj_enjoys_learning",
        "aspect",
        "conjunction_Sun",
        "learning",
        "Enjoyment of learning "
        "(not equated with lifelong_learning).",
        "neutral",
        "enjoys_learning",
        source_reference=REF_SUN_CONJ,
    ),
    _f(
        "sun_cj_source_intellectual_ability_contextual",
        "aspect",
        "conjunction_Sun",
        "source_specific",
        "Source describes +1 to intellectual abilities, with expression depending "
        "on sign and chart context "
        "(source-described contextual potential; not an IQ measurement, not "
        "technical_ability or analytical_thinking, not a hiring conclusion).",
        "strength",
        "source_intellectual_ability_contextual",
        source_reference=REF_SUN_CONJ,
    ),
)

SUN_CONJUNCTION_COMBUSTION: tuple[SourceFactDef, ...] = (
    _f(
        "sun_cj_combustion_excessive_speech",
        "aspect",
        "conjunction_Sun",
        "communication",
        "When the conjunction orb is strictly less than 5° (combustion), the "
        "source describes increased excessive speech / \"verbal diarrhea\" "
        "(not equated with fast_speech, oratory, or communication skill).",
        "risk",
        "excessive_speech",
        source_reference=REF_SUN_CONJ,
        activation_condition=_COMBUSTION_ORB_LT_5,
    ),
    _f(
        "sun_cj_combustion_identity_overattached_to_intellect_and_words",
        "aspect",
        "conjunction_Sun",
        "thinking",
        "When the conjunction orb is strictly less than 5° (combustion), the "
        "source describes excessive attachment of one's \"I\" / identity to "
        "intellect and words, including the identity equation "
        "\"I = what I say and think\".",
        "risk",
        "identity_overattached_to_intellect_and_words",
        source_reference=REF_SUN_CONJ,
        activation_condition=_COMBUSTION_ORB_LT_5,
    ),
    _f(
        "sun_cj_combustion_reduced_self_criticism",
        "aspect",
        "conjunction_Sun",
        "thinking",
        "When the conjunction orb is strictly less than 5° (combustion), the "
        "source describes absence / reduction of self-criticism.",
        "risk",
        "reduced_self_criticism",
        source_reference=REF_SUN_CONJ,
        activation_condition=_COMBUSTION_ORB_LT_5,
    ),
    _f(
        "sun_cj_combustion_identity_reduced_to_intellectual_expression",
        "aspect",
        "conjunction_Sun",
        "source_specific",
        "When the conjunction orb is strictly less than 5° (combustion), the "
        "source describes personality as reduced to its intellectual expression / "
        "an intellectual epiphenomenon "
        "(source wording; not a personality disorder, narcissism, low emotional "
        "intelligence, or mental-illness claim).",
        "risk",
        "identity_reduced_to_intellectual_expression",
        source_reference=REF_SUN_CONJ,
        activation_condition=_COMBUSTION_ORB_LT_5,
    ),
)

SUN_CONJUNCTION_EXTERNAL_AFFLICTION: tuple[SourceFactDef, ...] = (
    _f(
        "sun_cj_branch_external_affliction_gossip",
        "aspect",
        "conjunction_Sun",
        "source_specific",
        "If afflicted by other external factors, the source associates this "
        "conjunction with gossiping "
        "(source-described conditional association; unresolved; not a "
        "deterministic accusation).",
        "conditional",
        "source_gossip_association",
        source_reference=REF_SUN_CONJ,
        activation_condition=_EXTERNAL_AFFLICTION_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "sun_cj_branch_external_affliction_lying",
        "aspect",
        "conjunction_Sun",
        "source_specific",
        "If afflicted by other external factors, the source associates this "
        "conjunction with lying "
        "(source-described conditional association; unresolved; not a "
        "deterministic accusation that a person lies).",
        "conditional",
        "source_external_affliction_lying_association",
        source_reference=REF_SUN_CONJ,
        activation_condition=_EXTERNAL_AFFLICTION_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "sun_cj_branch_external_affliction_petty_theft",
        "aspect",
        "conjunction_Sun",
        "source_specific",
        "If afflicted by other external factors, the source associates this "
        "conjunction with petty theft "
        "(source-described conditional association; unresolved; not a crime "
        "prediction).",
        "conditional",
        "source_petty_theft_association",
        source_reference=REF_SUN_CONJ,
        activation_condition=_EXTERNAL_AFFLICTION_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "sun_cj_branch_external_affliction_shallow_smart_sounding_breadth",
        "aspect",
        "conjunction_Sun",
        "source_specific",
        "If afflicted by other external factors, the source associates this "
        "conjunction with speaking intelligently about everything without truly "
        "deep knowledge "
        "(source-described conditional association; unresolved; not a "
        "deterministic shallowness accusation).",
        "conditional",
        "source_broad_smart_sounding_shallow_knowledge",
        source_reference=REF_SUN_CONJ,
        activation_condition=_EXTERNAL_AFFLICTION_UNRESOLVED,
        unresolved=True,
    ),
)

SUN_CONJUNCTION: tuple[SourceFactDef, ...] = (
    SUN_CONJUNCTION_BASE
    + SUN_CONJUNCTION_COMBUSTION
    + SUN_CONJUNCTION_EXTERNAL_AFFLICTION
)

C11_ASPECT_PACKS: tuple[SourceFactDef, ...] = SUN_CONJUNCTION

C11_SUPPORTED_ASPECT_KEYS = frozenset({"conjunction_Sun"})
