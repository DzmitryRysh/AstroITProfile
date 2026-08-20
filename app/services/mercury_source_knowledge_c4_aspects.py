"""Mercury Source Profile v2 — Aspect Batch C4 (verified Jupiter square).

C4 adds Bioastrology source pack for:

- Mercury square Jupiter

No aliases. No opposition/conjunction Jupiter packs.
Do NOT reuse harmonious Jupiter (sextile/trine) facts.

Strength-dependent winner branches are unresolved (no strength resolver).
Compensation and \"supergift\" high-expression material intentionally omitted
pending safer dedicated representation.

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


REF_JUPITER_SQ = "bioastrology_mercury_jupiter_square"
_STRENGTH_UNRESOLVED = "strength_unresolved"


# ---------------------------------------------------------------------------
# Mercury square Jupiter — Bioastrology
# Canonical public catalog key: square_Jupiter
# Do NOT alias to opposition/conjunction Jupiter or to sextile/trine Jupiter.
# ---------------------------------------------------------------------------
JUPITER_SQUARE_COMMON: tuple[SourceFactDef, ...] = (
    _f(
        "jupiter_sq_tense_constructive_context",
        "aspect",
        "square_Jupiter",
        "thinking",
        "Source pair context: even tense Jupiter–Mercury interaction can be "
        "psychologically rather constructive because Jupiter expands Mercury's "
        "mental quality.",
        "neutral",
        "jupiter_mercury_tense_constructive_context",
        source_reference=REF_JUPITER_SQ,
    ),
    _f(
        "jupiter_sq_thinking_strengthened_through_resistance",
        "aspect",
        "square_Jupiter",
        "thinking",
        "Source pair context: doubt and resistance can strengthen thinking.",
        "neutral",
        "thinking_strengthened_through_resistance",
        source_reference=REF_JUPITER_SQ,
    ),
    _f(
        "jupiter_sq_student_teacher_cognitive_conflict",
        "aspect",
        "square_Jupiter",
        "thinking",
        "The student / analyst principle fights with the fashion / wisdom / "
        "teacher principle.",
        "risk",
        "student_teacher_cognitive_conflict",
        source_reference=REF_JUPITER_SQ,
    ),
    _f(
        "jupiter_sq_source_thinking_suppression",
        "aspect",
        "square_Jupiter",
        "source_specific",
        "Source-described family / authority theme: \"don't think\" / thinking "
        "ability is humiliated "
        "(source association; not a claim that this definitely occurred).",
        "risk",
        "source_thinking_suppression",
        source_reference=REF_JUPITER_SQ,
    ),
    _f(
        "jupiter_sq_source_voice_invalidation",
        "aspect",
        "square_Jupiter",
        "source_specific",
        "Source-described family / authority theme: \"nobody asked you\" "
        "(source association; not a claim that this definitely occurred).",
        "risk",
        "source_voice_invalidation",
        source_reference=REF_JUPITER_SQ,
    ),
    _f(
        "jupiter_sq_source_parental_thought_conformity",
        "aspect",
        "square_Jupiter",
        "source_specific",
        "Source-described family / authority theme: \"think only what your "
        "parents think\" "
        "(source association; not a claim that this definitely occurred).",
        "risk",
        "source_parental_thought_conformity",
        source_reference=REF_JUPITER_SQ,
    ),
    _f(
        "jupiter_sq_prestigious_car_orientation",
        "aspect",
        "square_Jupiter",
        "environment",
        "Desire / need to drive and/or own a prestigious car.",
        "neutral",
        "prestigious_car_orientation",
        source_reference=REF_JUPITER_SQ,
    ),
    _f(
        "jupiter_sq_empty_talk_tendency",
        "aspect",
        "square_Jupiter",
        "communication",
        "Empty ringing talk / verbal diarrhea "
        "(source-described empty-talk tendency; not sanitized as mere talkativeness).",
        "risk",
        "empty_talk_tendency",
        source_reference=REF_JUPITER_SQ,
    ),
    _f(
        "jupiter_sq_source_school_grade_pressure",
        "aspect",
        "square_Jupiter",
        "source_specific",
        "Source associates this square with pressure / \"terrorism\" around "
        "school grades "
        "(source-described association; not a claim that this definitely happened).",
        "risk",
        "source_school_grade_pressure",
        source_reference=REF_JUPITER_SQ,
    ),
    _f(
        "jupiter_sq_fact_evaluation_substitution",
        "aspect",
        "square_Jupiter",
        "thinking",
        "Source-described substitution of truth and facts with evaluation of facts.",
        "risk",
        "fact_evaluation_substitution",
        source_reference=REF_JUPITER_SQ,
    ),
    _f(
        "jupiter_sq_fact_image_substitution",
        "aspect",
        "square_Jupiter",
        "thinking",
        "Source-described substitution of truth and facts with an image of facts.",
        "risk",
        "fact_image_substitution",
        source_reference=REF_JUPITER_SQ,
    ),
    _f(
        "jupiter_sq_rightness_over_truth_orientation",
        "aspect",
        "square_Jupiter",
        "thinking",
        "Being right becomes more important than being truthful.",
        "risk",
        "rightness_over_truth_orientation",
        source_reference=REF_JUPITER_SQ,
    ),
    _f(
        "jupiter_sq_source_secondary_gain_being_right",
        "aspect",
        "square_Jupiter",
        "source_specific",
        "Source secondary-gain theme: own rightness / being right "
        "(source-framework wording; not equated with confidence or expertise).",
        "risk",
        "source_secondary_gain_being_right",
        source_reference=REF_JUPITER_SQ,
    ),
)

JUPITER_SQUARE_JUPITER_WINS: tuple[SourceFactDef, ...] = (
    _f(
        "jupiter_sq_branch_jupiter_omniscience_illusion",
        "aspect",
        "square_Jupiter",
        "source_specific",
        "If Jupiter dominates this square: illusion of knowing everything "
        "(source-described; not expertise; unresolved).",
        "conditional",
        "source_omniscience_illusion",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "jupiter_sq_branch_jupiter_tranquilizing_obviousness",
        "aspect",
        "square_Jupiter",
        "source_specific",
        "If Jupiter dominates this square: \"tranquilizing obviousness\" "
        "(source-specific concept; not a clinical claim; unresolved).",
        "conditional",
        "source_tranquilizing_obviousness",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "jupiter_sq_branch_jupiter_oratory_with_demagogy",
        "aspect",
        "square_Jupiter",
        "source_specific",
        "If Jupiter dominates this square: brilliant oratory with a share of "
        "demagogy "
        "(mixed source character; not equated with clean persuasion; unresolved).",
        "conditional",
        "source_oratory_with_demagogy",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "jupiter_sq_branch_jupiter_managerial_intellectual",
        "aspect",
        "square_Jupiter",
        "source_specific",
        "If Jupiter dominates this square: managerial intellectual qualities "
        "(source-described aptitude; not a validated hiring competency; unresolved).",
        "conditional",
        "source_managerial_intellectual_aptitude",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "jupiter_sq_branch_jupiter_legal_intellectual",
        "aspect",
        "square_Jupiter",
        "source_specific",
        "If Jupiter dominates this square: legal intellectual qualities "
        "(source-described aptitude; not a validated hiring competency; unresolved).",
        "conditional",
        "source_legal_intellectual_aptitude",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "jupiter_sq_branch_jupiter_governmental_intellectual",
        "aspect",
        "square_Jupiter",
        "source_specific",
        "If Jupiter dominates this square: state / government intellectual "
        "qualities "
        "(source-described aptitude; not a validated hiring competency; unresolved).",
        "conditional",
        "source_governmental_intellectual_aptitude",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "jupiter_sq_branch_jupiter_blind_opinion_conviction",
        "aspect",
        "square_Jupiter",
        "thinking",
        "If Jupiter dominates this square: blind conviction in opinions and "
        "ideas (unresolved).",
        "conditional",
        "blind_opinion_conviction",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "jupiter_sq_branch_jupiter_ideological_speech_thinking",
        "aspect",
        "square_Jupiter",
        "communication",
        "If Jupiter dominates this square: ideological coloring of speech and "
        "thinking (unresolved).",
        "conditional",
        "ideological_speech_thinking",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "jupiter_sq_branch_jupiter_devaluation_unfamiliar_concepts",
        "aspect",
        "square_Jupiter",
        "thinking",
        "If Jupiter dominates this square: devaluation of other people's / "
        "unfamiliar concepts and teachings (unresolved).",
        "conditional",
        "devaluation_of_unfamiliar_concepts",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "jupiter_sq_branch_jupiter_moralizing",
        "aspect",
        "square_Jupiter",
        "communication",
        "If Jupiter dominates this square: moralizing (unresolved).",
        "conditional",
        "moralizing_tendency",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "jupiter_sq_branch_jupiter_detail_attention_deficit",
        "aspect",
        "square_Jupiter",
        "thinking",
        "If Jupiter dominates this square: lack of attention to detail "
        "(unresolved; not equated with general inattentiveness).",
        "conditional",
        "detail_attention_deficit",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "jupiter_sq_branch_jupiter_mentorizing",
        "aspect",
        "square_Jupiter",
        "communication",
        "If Jupiter dominates this square: mentoring / lecturing tendency "
        "(unresolved; not equated with teaching ability).",
        "conditional",
        "mentorizing_tendency",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "jupiter_sq_branch_jupiter_snobbery",
        "aspect",
        "square_Jupiter",
        "source_specific",
        "If Jupiter dominates this square: snobbery "
        "(source-described tendency; unresolved).",
        "conditional",
        "source_snobbery_tendency",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "jupiter_sq_branch_jupiter_intellectual_superiority_attitude",
        "aspect",
        "square_Jupiter",
        "source_specific",
        "If Jupiter dominates this square, the source describes an "
        "\"everyone around is an idiot\" superiority / devaluation attitude "
        "(source-described pattern; not a deterministic accusation; unresolved).",
        "conditional",
        "source_intellectual_superiority_attitude",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
)

JUPITER_SQUARE_MERCURY_WINS: tuple[SourceFactDef, ...] = (
    _f(
        "jupiter_sq_branch_mercury_faltering_intellect",
        "aspect",
        "square_Jupiter",
        "source_specific",
        "If Mercury dominates this square: stumbling / faltering intellect "
        "(source-specific framing; not low intelligence, learning disability, "
        "or diagnosis; unresolved).",
        "conditional",
        "source_faltering_intellect",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "jupiter_sq_branch_mercury_lying_tendency",
        "aspect",
        "square_Jupiter",
        "source_specific",
        "If Mercury dominates this square, the source describes a lying "
        "tendency "
        "(source-described pattern; not a deterministic statement that the "
        "person lies; unresolved).",
        "conditional",
        "source_lying_tendency",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "jupiter_sq_branch_mercury_fabrication_tendency",
        "aspect",
        "square_Jupiter",
        "source_specific",
        "If Mercury dominates this square: stories / fabrication / tall tales "
        "(source-described; kept distinct from lying; unresolved).",
        "conditional",
        "source_fabrication_tendency",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "jupiter_sq_branch_mercury_inattentiveness",
        "aspect",
        "square_Jupiter",
        "thinking",
        "If Mercury dominates this square: inattentiveness "
        "(unresolved; not an ADHD inference).",
        "conditional",
        "inattentiveness",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "jupiter_sq_branch_mercury_profanity",
        "aspect",
        "square_Jupiter",
        "communication",
        "If Mercury dominates this square: frequent profanity (unresolved).",
        "conditional",
        "profanity_tendency",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "jupiter_sq_branch_mercury_shouting",
        "aspect",
        "square_Jupiter",
        "communication",
        "If Mercury dominates this square: habit of shouting (unresolved).",
        "conditional",
        "shouting_tendency",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "jupiter_sq_branch_mercury_argumentative_behavior",
        "aspect",
        "square_Jupiter",
        "communication",
        "If Mercury dominates this square: habit of arguing "
        "(unresolved; behavioral conflict, not debate/argumentation ability).",
        "conditional",
        "argumentative_behavior",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "jupiter_sq_branch_mercury_authority_rejection",
        "aspect",
        "square_Jupiter",
        "thinking",
        "If Mercury dominates this square: frequent rejection of authorities "
        "(unresolved).",
        "conditional",
        "authority_rejection",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "jupiter_sq_branch_mercury_rejection_higher_wisdom",
        "aspect",
        "square_Jupiter",
        "source_specific",
        "If Mercury dominates this square: rejection of esotericism / aspects "
        "of higher wisdom "
        "(source-framework claim; esotericism not treated as scientifically "
        "validated knowledge; unresolved).",
        "conditional",
        "source_rejection_of_higher_wisdom",
        source_reference=REF_JUPITER_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
)

JUPITER_SQUARE: tuple[SourceFactDef, ...] = (
    JUPITER_SQUARE_COMMON
    + JUPITER_SQUARE_JUPITER_WINS
    + JUPITER_SQUARE_MERCURY_WINS
)

C4_ASPECT_PACKS: tuple[SourceFactDef, ...] = JUPITER_SQUARE

C4_SUPPORTED_ASPECT_KEYS = frozenset({"square_Jupiter"})
