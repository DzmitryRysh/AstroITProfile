"""Mercury Source Profile v2 — Aspect Batch C6 (Saturn opposition / conjunction).

C6 completes the Mercury–Saturn public family with two DISTINCT packs:

- opposition_Saturn
- conjunction_Saturn

No aliases. Do NOT reuse square_Saturn catalog facts.
Do NOT treat square = opposition = conjunction.

Source may repeat atomic meanings across Saturn tense/conjunction branches;
that is source repetition, not permission for aspect-type aliases.

Compensation, secondary-gain celebrities, and \"supergift\" intentionally omitted
(same C4/C5 precedent).

Conjunction includes ONE unresolved conditional for source
\"with a strong creative core\" — no creative-core resolver exists.

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


REF_SATURN_OPP = "bioastrology_mercury_saturn_opposition"
REF_SATURN_CONJ = "bioastrology_mercury_saturn_conjunction"
_CREATIVE_CORE_UNRESOLVED = "creative_core_strength_unresolved"


# ---------------------------------------------------------------------------
# Mercury opposition Saturn — Bioastrology
# Canonical public catalog key: opposition_Saturn
# Distinct from square_Saturn and conjunction_Saturn.
# ---------------------------------------------------------------------------
SATURN_OPPOSITION: tuple[SourceFactDef, ...] = (
    _f(
        "saturn_opp_curiosity_vs_social_requirement_conflict",
        "aspect",
        "opposition_Saturn",
        "thinking",
        "Tug-of-war between \"curious / I can learn\" and "
        "\"I must / it will be useful in society / it fits frameworks and evaluations.\"",
        "risk",
        "curiosity_vs_social_requirement_conflict",
        source_reference=REF_SATURN_OPP,
    ),
    _f(
        "saturn_opp_youth_to_later_professionalism_pattern",
        "aspect",
        "opposition_Saturn",
        "source_specific",
        "Source-described age pattern: mental slowness / \"тупка\" in youth, "
        "but high professionalism at 30+ "
        "(source-described pattern; not a deterministic real-person claim or hiring conclusion).",
        "neutral",
        "youth_to_later_professionalism_pattern",
        source_reference=REF_SATURN_OPP,
    ),
    _f(
        "saturn_opp_mercury_saturn_house_axis_tension",
        "aspect",
        "opposition_Saturn",
        "source_specific",
        "Source-described house-axis / context pattern: difficulty achieving a "
        "result in Mercury's house, while Saturn's house resembles a \"barracks\" "
        "with a shortage of fresh information "
        "(source context statement; no Saturn-house resolver is applied).",
        "risk",
        "mercury_saturn_house_axis_result_information_tension",
        source_reference=REF_SATURN_OPP,
    ),
    _f(
        "saturn_opp_everyday_scatter_work_hyperfocus_contrast",
        "aspect",
        "opposition_Saturn",
        "source_specific",
        "Source allows a possible contrast: everyday mental dullness / "
        "absent-mindedness (\"бытовая тупость\"), but extreme focus and "
        "\"genius\" in work "
        "(source-described possible contrast; not a diagnosis, IQ claim, or hiring quality).",
        "neutral",
        "everyday_scatter_work_hyperfocus_contrast",
        source_reference=REF_SATURN_OPP,
    ),
    _f(
        "saturn_opp_organization",
        "aspect",
        "opposition_Saturn",
        "work_application",
        "Ability to organize.",
        "strength",
        "organization",
        source_reference=REF_SATURN_OPP,
    ),
    _f(
        "saturn_opp_planning",
        "aspect",
        "opposition_Saturn",
        "work_application",
        "Ability to plan.",
        "strength",
        "planning",
        source_reference=REF_SATURN_OPP,
    ),
    _f(
        "saturn_opp_forecasting",
        "aspect",
        "opposition_Saturn",
        "work_application",
        "Ability to forecast.",
        "strength",
        "forecasting",
        source_reference=REF_SATURN_OPP,
    ),
    _f(
        "saturn_opp_point_by_point_speech",
        "aspect",
        "opposition_Saturn",
        "communication",
        "Clear point-by-point speech.",
        "strength",
        "point_by_point_speech",
        source_reference=REF_SATURN_OPP,
    ),
    _f(
        "saturn_opp_articulation",
        "aspect",
        "opposition_Saturn",
        "communication",
        "Good articulation.",
        "strength",
        "articulation",
        source_reference=REF_SATURN_OPP,
    ),
    _f(
        "saturn_opp_logic",
        "aspect",
        "opposition_Saturn",
        "thinking",
        "Strong logic.",
        "strength",
        "logic",
        source_reference=REF_SATURN_OPP,
    ),
    _f(
        "saturn_opp_argumentation",
        "aspect",
        "opposition_Saturn",
        "communication",
        "Strong argumentation.",
        "strength",
        "argumentation",
        source_reference=REF_SATURN_OPP,
    ),
    _f(
        "saturn_opp_driving_ability",
        "aspect",
        "opposition_Saturn",
        "mobility",
        "Skilled-driver pattern: automatically absorbs rules and feels the flow.",
        "strength",
        "driving_ability",
        source_reference=REF_SATURN_OPP,
    ),
    _f(
        "saturn_opp_mental_dissatisfaction_learning_utility",
        "aspect",
        "opposition_Saturn",
        "learning",
        "Mental dissatisfaction: \"I know not what I need, and when I start "
        "learning something new I quickly understand it will not be useful to me.\"",
        "risk",
        "mental_dissatisfaction_learning_utility",
        source_reference=REF_SATURN_OPP,
    ),
    _f(
        "saturn_opp_thinking_pessimism",
        "aspect",
        "opposition_Saturn",
        "thinking",
        "Pessimism of mind.",
        "risk",
        "thinking_pessimism",
        source_reference=REF_SATURN_OPP,
    ),
    _f(
        "saturn_opp_critical_attitude",
        "aspect",
        "opposition_Saturn",
        "communication",
        "Critical attitude.",
        "risk",
        "critical_attitude",
        source_reference=REF_SATURN_OPP,
    ),
    _f(
        "saturn_opp_distrust",
        "aspect",
        "opposition_Saturn",
        "thinking",
        "Distrust.",
        "risk",
        "distrust",
        source_reference=REF_SATURN_OPP,
    ),
    _f(
        "saturn_opp_verification_requirement",
        "aspect",
        "opposition_Saturn",
        "thinking",
        "\"Everything must be checked\" "
        "(verification requirement; not equated with evidence_requirement).",
        "neutral",
        "verification_requirement",
        source_reference=REF_SATURN_OPP,
    ),
    _f(
        "saturn_opp_mental_restructuring_difficulty",
        "aspect",
        "opposition_Saturn",
        "thinking",
        "Difficulty with mental restructuring / adaptation.",
        "risk",
        "mental_restructuring_difficulty",
        source_reference=REF_SATURN_OPP,
    ),
    _f(
        "saturn_opp_unlearning_difficulty",
        "aspect",
        "opposition_Saturn",
        "learning",
        "Once something is learned, it is difficult to forget / unlearn it "
        "(unlearning difficulty; not equated with strong_memory / sticky_memory).",
        "risk",
        "unlearning_difficulty",
        source_reference=REF_SATURN_OPP,
    ),
)


# ---------------------------------------------------------------------------
# Mercury conjunction Saturn — Bioastrology
# Canonical public catalog key: conjunction_Saturn
# Distinct from square_Saturn and opposition_Saturn.
# ---------------------------------------------------------------------------
SATURN_CONJUNCTION_RESOLVED: tuple[SourceFactDef, ...] = (
    _f(
        "saturn_cj_narrow_prescribed_thinking",
        "aspect",
        "conjunction_Saturn",
        "thinking",
        "Control / correctness / professionalism completely absorbs freedom of "
        "thinking and pushes the mind into a narrow tunnel of "
        "\"acceptable / proper / prescribed\" "
        "(source wording: \"узкий тоннель\").",
        "risk",
        "narrow_prescribed_thinking",
        source_reference=REF_SATURN_CONJ,
    ),
    _f(
        "saturn_cj_everyday_scatter_work_hyperfocus_contrast",
        "aspect",
        "conjunction_Saturn",
        "source_specific",
        "Source also describes a possible contrast: everyday mental dullness / "
        "absent-mindedness (\"бытовая тупость\"), but extreme focus and "
        "\"genius\" in work "
        "(source-described possible contrast; not a diagnosis, IQ claim, or hiring quality).",
        "neutral",
        "everyday_scatter_work_hyperfocus_contrast",
        source_reference=REF_SATURN_CONJ,
    ),
    _f(
        "saturn_cj_mental_dissatisfaction_learning_utility",
        "aspect",
        "conjunction_Saturn",
        "learning",
        "Mental dissatisfaction: \"I know not what I need, and when I start "
        "learning something new I quickly understand it will not be useful to me.\"",
        "risk",
        "mental_dissatisfaction_learning_utility",
        source_reference=REF_SATURN_CONJ,
    ),
    _f(
        "saturn_cj_thinking_pessimism",
        "aspect",
        "conjunction_Saturn",
        "thinking",
        "Pessimism of mind.",
        "risk",
        "thinking_pessimism",
        source_reference=REF_SATURN_CONJ,
    ),
    _f(
        "saturn_cj_critical_attitude",
        "aspect",
        "conjunction_Saturn",
        "communication",
        "Critical attitude.",
        "risk",
        "critical_attitude",
        source_reference=REF_SATURN_CONJ,
    ),
    _f(
        "saturn_cj_distrust",
        "aspect",
        "conjunction_Saturn",
        "thinking",
        "Distrust.",
        "risk",
        "distrust",
        source_reference=REF_SATURN_CONJ,
    ),
    _f(
        "saturn_cj_verification_requirement",
        "aspect",
        "conjunction_Saturn",
        "thinking",
        "\"Everything must be checked\" "
        "(verification requirement; not equated with evidence_requirement).",
        "neutral",
        "verification_requirement",
        source_reference=REF_SATURN_CONJ,
    ),
    _f(
        "saturn_cj_mental_restructuring_difficulty",
        "aspect",
        "conjunction_Saturn",
        "thinking",
        "Difficulty with mental restructuring / adaptation.",
        "risk",
        "mental_restructuring_difficulty",
        source_reference=REF_SATURN_CONJ,
    ),
    _f(
        "saturn_cj_unlearning_difficulty",
        "aspect",
        "conjunction_Saturn",
        "learning",
        "Once something is learned, it is difficult to forget / unlearn it "
        "(unlearning difficulty; not equated with strong_memory / sticky_memory).",
        "risk",
        "unlearning_difficulty",
        source_reference=REF_SATURN_CONJ,
    ),
    _f(
        "saturn_cj_organization",
        "aspect",
        "conjunction_Saturn",
        "work_application",
        "Ability to organize.",
        "strength",
        "organization",
        source_reference=REF_SATURN_CONJ,
    ),
    _f(
        "saturn_cj_planning",
        "aspect",
        "conjunction_Saturn",
        "work_application",
        "Ability to plan.",
        "strength",
        "planning",
        source_reference=REF_SATURN_CONJ,
    ),
    _f(
        "saturn_cj_forecasting",
        "aspect",
        "conjunction_Saturn",
        "work_application",
        "Ability to forecast.",
        "strength",
        "forecasting",
        source_reference=REF_SATURN_CONJ,
    ),
    _f(
        "saturn_cj_point_by_point_speech",
        "aspect",
        "conjunction_Saturn",
        "communication",
        "Clear point-by-point speech.",
        "strength",
        "point_by_point_speech",
        source_reference=REF_SATURN_CONJ,
    ),
    _f(
        "saturn_cj_articulation",
        "aspect",
        "conjunction_Saturn",
        "communication",
        "Good articulation.",
        "strength",
        "articulation",
        source_reference=REF_SATURN_CONJ,
    ),
    _f(
        "saturn_cj_logic",
        "aspect",
        "conjunction_Saturn",
        "thinking",
        "Strong logic.",
        "strength",
        "logic",
        source_reference=REF_SATURN_CONJ,
    ),
    _f(
        "saturn_cj_argumentation",
        "aspect",
        "conjunction_Saturn",
        "communication",
        "Strong argumentation.",
        "strength",
        "argumentation",
        source_reference=REF_SATURN_CONJ,
    ),
    _f(
        "saturn_cj_driving_ability",
        "aspect",
        "conjunction_Saturn",
        "mobility",
        "Skilled-driver pattern: automatically absorbs rules and feels the flow.",
        "strength",
        "driving_ability",
        source_reference=REF_SATURN_CONJ,
    ),
)

SATURN_CONJUNCTION_UNRESOLVED: tuple[SourceFactDef, ...] = (
    _f(
        "saturn_cj_branch_creative_core_deep_analytical_focus",
        "aspect",
        "conjunction_Saturn",
        "source_specific",
        "If a strong creative core is present, the source describes incredible "
        "mental focus and digging / deep analytical intelligence, achieving "
        "very strong results through prolonged immersion in a subject "
        "(unresolved; no creative-core strength resolver is applied; not an "
        "always-on claim).",
        "conditional",
        "deep_analytical_focus",
        source_reference=REF_SATURN_CONJ,
        activation_condition=_CREATIVE_CORE_UNRESOLVED,
        unresolved=True,
    ),
)

SATURN_CONJUNCTION: tuple[SourceFactDef, ...] = (
    SATURN_CONJUNCTION_RESOLVED + SATURN_CONJUNCTION_UNRESOLVED
)

C6_ASPECT_PACKS: tuple[SourceFactDef, ...] = SATURN_OPPOSITION + SATURN_CONJUNCTION

C6_SUPPORTED_ASPECT_KEYS = frozenset({"opposition_Saturn", "conjunction_Saturn"})
