"""Mercury Source Profile v2 — Aspect Batch C5 (Jupiter opposition / conjunction).

C5 finishes the Mercury–Jupiter public family with two DISTINCT packs:

- opposition_Jupiter
- conjunction_Jupiter

No aliases. Do NOT reuse square_Jupiter catalog facts.
Do NOT treat square = opposition = conjunction.

Compensation and "supergift" high-expression material intentionally omitted
(same C4 precedent: no dedicated compensation layer; no potential-only activation).

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


REF_JUPITER_OPP = "bioastrology_mercury_jupiter_opposition"
REF_JUPITER_CONJ = "bioastrology_mercury_jupiter_conjunction"


# ---------------------------------------------------------------------------
# Mercury opposition Jupiter — Bioastrology
# Canonical public catalog key: opposition_Jupiter
# Distinct from square_Jupiter and conjunction_Jupiter.
# ---------------------------------------------------------------------------
JUPITER_OPPOSITION: tuple[SourceFactDef, ...] = (
    _f(
        "jupiter_opp_knowledge_certainty_oscillation",
        "aspect",
        "opposition_Jupiter",
        "thinking",
        "\"I know everything\" alternates with \"I know nothing\".",
        "neutral",
        "knowledge_certainty_oscillation",
        source_reference=REF_JUPITER_OPP,
    ),
    _f(
        "jupiter_opp_practical_abstract_thinking_oscillation",
        "aspect",
        "opposition_Jupiter",
        "thinking",
        "Practical / commercial thinking can switch into abstract philosophizing "
        "about the fate of the world and searching for purpose.",
        "neutral",
        "practical_abstract_thinking_oscillation",
        source_reference=REF_JUPITER_OPP,
    ),
    _f(
        "jupiter_opp_external_ideology_narrowing",
        "aspect",
        "opposition_Jupiter",
        "thinking",
        "Risk of narrow thinking when the person's own ideas are overridden by "
        "fashion, a teacher, or religion.",
        "risk",
        "external_ideology_narrow_thinking",
        source_reference=REF_JUPITER_OPP,
    ),
    _f(
        "jupiter_opp_source_thinking_suppression",
        "aspect",
        "opposition_Jupiter",
        "source_specific",
        "Source-described family / authority theme: \"do not think\" / ability "
        "to think is devalued "
        "(source association; not a claim that this definitely occurred).",
        "risk",
        "source_thinking_suppression",
        source_reference=REF_JUPITER_OPP,
    ),
    _f(
        "jupiter_opp_source_voice_invalidation",
        "aspect",
        "opposition_Jupiter",
        "source_specific",
        "Source-described family / authority theme: \"nobody asked you\" "
        "(source association; not a claim that this definitely occurred).",
        "risk",
        "source_voice_invalidation",
        source_reference=REF_JUPITER_OPP,
    ),
    _f(
        "jupiter_opp_source_parental_thought_conformity",
        "aspect",
        "opposition_Jupiter",
        "source_specific",
        "Source-described family / authority theme: \"think only what the "
        "parents think\" "
        "(source association; not a claim that this definitely occurred).",
        "risk",
        "source_parental_thought_conformity",
        source_reference=REF_JUPITER_OPP,
    ),
    _f(
        "jupiter_opp_foreign_languages",
        "aspect",
        "opposition_Jupiter",
        "learning",
        "Aptitude / support for foreign languages.",
        "strength",
        "foreign_languages",
        source_reference=REF_JUPITER_OPP,
    ),
    _f(
        "jupiter_opp_legal_aptitude",
        "aspect",
        "opposition_Jupiter",
        "work_application",
        "Legal aptitude.",
        "strength",
        "legal_aptitude",
        source_reference=REF_JUPITER_OPP,
    ),
    _f(
        "jupiter_opp_oratory",
        "aspect",
        "opposition_Jupiter",
        "communication",
        "Oratory.",
        "strength",
        "oratory",
        source_reference=REF_JUPITER_OPP,
    ),
    _f(
        "jupiter_opp_persuasion",
        "aspect",
        "opposition_Jupiter",
        "communication",
        "Persuasion.",
        "strength",
        "persuasion",
        source_reference=REF_JUPITER_OPP,
    ),
    _f(
        "jupiter_opp_lifelong_learning",
        "aspect",
        "opposition_Jupiter",
        "learning",
        "Continuing need to learn and broaden horizons.",
        "strength",
        "lifelong_learning",
        source_reference=REF_JUPITER_OPP,
    ),
    _f(
        "jupiter_opp_prestigious_car_orientation",
        "aspect",
        "opposition_Jupiter",
        "environment",
        "Desire to drive and/or own a prestigious car.",
        "neutral",
        "prestigious_car_orientation",
        source_reference=REF_JUPITER_OPP,
    ),
    _f(
        "jupiter_opp_philosophy_interest",
        "aspect",
        "opposition_Jupiter",
        "learning",
        "Interest in philosophy.",
        "neutral",
        "philosophy_interest",
        source_reference=REF_JUPITER_OPP,
    ),
    _f(
        "jupiter_opp_science_interest",
        "aspect",
        "opposition_Jupiter",
        "learning",
        "Interest in science.",
        "neutral",
        "science_interest",
        source_reference=REF_JUPITER_OPP,
    ),
    _f(
        "jupiter_opp_esoteric_interest",
        "aspect",
        "opposition_Jupiter",
        "learning",
        "Interest in esoteric knowledge.",
        "neutral",
        "esoteric_interest",
        source_reference=REF_JUPITER_OPP,
    ),
    _f(
        "jupiter_opp_empty_talk_tendency",
        "aspect",
        "opposition_Jupiter",
        "communication",
        "Empty / excessive talking.",
        "risk",
        "empty_talk_tendency",
        source_reference=REF_JUPITER_OPP,
    ),
    _f(
        "jupiter_opp_source_school_grade_pressure",
        "aspect",
        "opposition_Jupiter",
        "source_specific",
        "Source associates this opposition with pressure / \"terrorism\" around "
        "school grades "
        "(source-described association; not a claim that this definitely happened).",
        "risk",
        "source_school_grade_pressure",
        source_reference=REF_JUPITER_OPP,
    ),
    _f(
        "jupiter_opp_road_inattentiveness_risk",
        "aspect",
        "opposition_Jupiter",
        "source_specific",
        "Source describes increased road inattentiveness risk "
        "(source-described risk; not a prediction that a person will have an accident).",
        "risk",
        "road_inattentiveness_risk",
        source_reference=REF_JUPITER_OPP,
    ),
    _f(
        "jupiter_opp_source_road_accident_risk",
        "aspect",
        "opposition_Jupiter",
        "source_specific",
        "Source describes increased road-accident risk "
        "(source-described risk; not a prediction that a person will have an accident).",
        "risk",
        "source_road_accident_risk",
        source_reference=REF_JUPITER_OPP,
    ),
    _f(
        "jupiter_opp_fact_evaluation_substitution",
        "aspect",
        "opposition_Jupiter",
        "thinking",
        "Source-described substitution of truth and facts with evaluation of facts.",
        "risk",
        "fact_evaluation_substitution",
        source_reference=REF_JUPITER_OPP,
    ),
    _f(
        "jupiter_opp_fact_image_substitution",
        "aspect",
        "opposition_Jupiter",
        "thinking",
        "Source-described substitution of truth and facts with an image of facts.",
        "risk",
        "fact_image_substitution",
        source_reference=REF_JUPITER_OPP,
    ),
    _f(
        "jupiter_opp_rightness_over_truth_orientation",
        "aspect",
        "opposition_Jupiter",
        "thinking",
        "Being right is prioritized over being truthful.",
        "risk",
        "rightness_over_truth_orientation",
        source_reference=REF_JUPITER_OPP,
    ),
    _f(
        "jupiter_opp_source_secondary_gain_being_right",
        "aspect",
        "opposition_Jupiter",
        "source_specific",
        "Source secondary-gain theme: a sense of one's own rightness "
        "(source-framework wording; not equated with confidence or expertise).",
        "risk",
        "source_secondary_gain_being_right",
        source_reference=REF_JUPITER_OPP,
    ),
)


# ---------------------------------------------------------------------------
# Mercury conjunction Jupiter — Bioastrology
# Canonical public catalog key: conjunction_Jupiter
# Distinct from square_Jupiter and opposition_Jupiter.
# Source relationship to Jupiter-dominant square is stated as text,
# not implemented by importing square catalog facts.
# ---------------------------------------------------------------------------
JUPITER_CONJUNCTION: tuple[SourceFactDef, ...] = (
    _f(
        "jupiter_cj_resembles_jupiter_dominant_square_less_intensity",
        "aspect",
        "conjunction_Jupiter",
        "source_specific",
        "Source states that conjunction resembles the Jupiter-dominant square "
        "expression, but with less pain / intensity "
        "(conjunction-specific relationship statement; not a catalog reuse of "
        "square_Jupiter facts).",
        "neutral",
        "source_conjunction_resembles_jupiter_dominant_square_less_intensity",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_intellectual_showing_off",
        "aspect",
        "conjunction_Jupiter",
        "communication",
        "Showing off intelligence / \"smarting off\" over small matters "
        "(source-described pattern; not a validated intelligence claim).",
        "risk",
        "intellectual_showing_off",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_philosophical_speech_display",
        "aspect",
        "conjunction_Jupiter",
        "communication",
        "Inserting philosophical language into speech.",
        "neutral",
        "philosophical_speech_display",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_foreign_word_display",
        "aspect",
        "conjunction_Jupiter",
        "communication",
        "Inserting foreign words into speech "
        "(display in speech; not equated with foreign-language aptitude).",
        "neutral",
        "foreign_word_display",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_intellectual_superiority_framing",
        "aspect",
        "conjunction_Jupiter",
        "source_specific",
        "Source describes an \"everyone around me is an idiot\" style of "
        "intellectual superiority "
        "(source-described pattern; not a deterministic accusation).",
        "risk",
        "intellectual_superiority_framing",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_traditional_learning_path_difficulty",
        "aspect",
        "conjunction_Jupiter",
        "learning",
        "Difficulty learning through traditional paths "
        "(not a global claim that all learning is difficult).",
        "risk",
        "traditional_learning_path_difficulty",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_teacher_conflicts",
        "aspect",
        "conjunction_Jupiter",
        "environment",
        "Conflicts with teachers "
        "(source-described pattern; not equated with debate ability).",
        "risk",
        "teacher_conflicts",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_self_elevation_over_teacher",
        "aspect",
        "conjunction_Jupiter",
        "learning",
        "Elevating oneself above the teacher "
        "(not equated with teaching ability).",
        "risk",
        "self_elevation_over_teacher",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_promise_execution_gap",
        "aspect",
        "conjunction_Jupiter",
        "communication",
        "Many promises, minimal execution.",
        "risk",
        "promise_execution_gap",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_exaggeration",
        "aspect",
        "conjunction_Jupiter",
        "communication",
        "Exaggeration.",
        "risk",
        "exaggeration",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_empty_promises",
        "aspect",
        "conjunction_Jupiter",
        "communication",
        "Empty promises "
        "(concrete source risk; not equated with generic dishonesty).",
        "risk",
        "empty_promises",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_evaluative_judgment_habit",
        "aspect",
        "conjunction_Jupiter",
        "thinking",
        "Habit of assigning ratings / judgments / evaluations "
        "(not equated with criticism or analytical thinking).",
        "neutral",
        "evaluative_judgment_habit",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_source_thinking_suppression",
        "aspect",
        "conjunction_Jupiter",
        "source_specific",
        "Source-described family / authority theme: \"do not think\" / thinking "
        "ability is devalued "
        "(source association; not a claim that this definitely occurred).",
        "risk",
        "source_thinking_suppression",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_source_voice_invalidation",
        "aspect",
        "conjunction_Jupiter",
        "source_specific",
        "Source-described family / authority theme: \"nobody asked you\" "
        "(source association; not a claim that this definitely occurred).",
        "risk",
        "source_voice_invalidation",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_source_parental_thought_conformity",
        "aspect",
        "conjunction_Jupiter",
        "source_specific",
        "Source-described family / authority theme: \"think only what the "
        "parents think\" "
        "(source association; not a claim that this definitely occurred).",
        "risk",
        "source_parental_thought_conformity",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_foreign_languages",
        "aspect",
        "conjunction_Jupiter",
        "learning",
        "Aptitude / support for foreign languages.",
        "strength",
        "foreign_languages",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_legal_aptitude",
        "aspect",
        "conjunction_Jupiter",
        "work_application",
        "Legal aptitude.",
        "strength",
        "legal_aptitude",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_oratory",
        "aspect",
        "conjunction_Jupiter",
        "communication",
        "Oratory.",
        "strength",
        "oratory",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_persuasion",
        "aspect",
        "conjunction_Jupiter",
        "communication",
        "Persuasion.",
        "strength",
        "persuasion",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_lifelong_learning",
        "aspect",
        "conjunction_Jupiter",
        "learning",
        "Continuing need to learn and expand horizons.",
        "strength",
        "lifelong_learning",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_prestigious_car_orientation",
        "aspect",
        "conjunction_Jupiter",
        "environment",
        "Desire to drive and/or own a prestigious car.",
        "neutral",
        "prestigious_car_orientation",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_philosophy_interest",
        "aspect",
        "conjunction_Jupiter",
        "learning",
        "Interest in philosophy.",
        "neutral",
        "philosophy_interest",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_science_interest",
        "aspect",
        "conjunction_Jupiter",
        "learning",
        "Interest in science.",
        "neutral",
        "science_interest",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_esoteric_interest",
        "aspect",
        "conjunction_Jupiter",
        "learning",
        "Interest in esoteric knowledge.",
        "neutral",
        "esoteric_interest",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_empty_talk_tendency",
        "aspect",
        "conjunction_Jupiter",
        "communication",
        "Empty / excessive talking.",
        "risk",
        "empty_talk_tendency",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_source_school_grade_pressure",
        "aspect",
        "conjunction_Jupiter",
        "source_specific",
        "Source associates this conjunction with pressure / \"terrorism\" around "
        "school grades "
        "(source-described association; not a claim that this definitely happened).",
        "risk",
        "source_school_grade_pressure",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_road_inattentiveness_risk",
        "aspect",
        "conjunction_Jupiter",
        "source_specific",
        "Source describes increased road inattentiveness risk "
        "(source-described risk; not a prediction that a person will have an accident).",
        "risk",
        "road_inattentiveness_risk",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_source_road_accident_risk",
        "aspect",
        "conjunction_Jupiter",
        "source_specific",
        "Source describes increased road-accident risk "
        "(source-described risk; not a prediction that a person will have an accident).",
        "risk",
        "source_road_accident_risk",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_fact_evaluation_substitution",
        "aspect",
        "conjunction_Jupiter",
        "thinking",
        "Source-described substitution of truth and facts with evaluation of facts.",
        "risk",
        "fact_evaluation_substitution",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_fact_image_substitution",
        "aspect",
        "conjunction_Jupiter",
        "thinking",
        "Source-described substitution of truth and facts with an image of facts.",
        "risk",
        "fact_image_substitution",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_rightness_over_truth_orientation",
        "aspect",
        "conjunction_Jupiter",
        "thinking",
        "Being right is prioritized over being truthful.",
        "risk",
        "rightness_over_truth_orientation",
        source_reference=REF_JUPITER_CONJ,
    ),
    _f(
        "jupiter_cj_source_secondary_gain_being_right",
        "aspect",
        "conjunction_Jupiter",
        "source_specific",
        "Source secondary-gain theme: own rightness "
        "(source-framework wording; not equated with confidence or expertise).",
        "risk",
        "source_secondary_gain_being_right",
        source_reference=REF_JUPITER_CONJ,
    ),
)

C5_ASPECT_PACKS: tuple[SourceFactDef, ...] = JUPITER_OPPOSITION + JUPITER_CONJUNCTION

C5_SUPPORTED_ASPECT_KEYS = frozenset({"opposition_Jupiter", "conjunction_Jupiter"})
