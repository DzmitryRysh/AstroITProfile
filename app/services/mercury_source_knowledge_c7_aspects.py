"""Mercury Source Profile v2 — Aspect Batch C7 (Mars opposition / conjunction).

C7 completes the Mercury–Mars public family with two DISTINCT packs:

- opposition_Mars
- conjunction_Mars

No aliases. Do NOT reuse square_Mars catalog facts.
Do NOT treat square = opposition = conjunction.

Source may repeat atomic meanings across Mars tense/conjunction branches;
that is source repetition, not permission for aspect-type aliases.

Celebrity examples, secondary gain, compensation, and \"supergift\"
intentionally omitted (same C4–C6 precedent).

Female-chart younger-partner association is unresolved:
female_chart_context_unresolved — no gender resolver exists.

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


REF_MARS_OPP = "bioastrology_mercury_mars_opposition"
REF_MARS_CONJ = "bioastrology_mercury_mars_conjunction"
_FEMALE_CHART_UNRESOLVED = "female_chart_context_unresolved"


# ---------------------------------------------------------------------------
# Mercury opposition Mars — Bioastrology
# Canonical public catalog key: opposition_Mars
# Distinct from square_Mars and conjunction_Mars.
# ---------------------------------------------------------------------------
MARS_OPPOSITION_RESOLVED: tuple[SourceFactDef, ...] = (
    _f(
        "mars_opp_word_action_mismatch",
        "aspect",
        "opposition_Mars",
        "thinking",
        "Words diverge from actions.",
        "risk",
        "word_action_mismatch",
        source_reference=REF_MARS_OPP,
    ),
    _f(
        "mars_opp_action_interferes_with_thought_formulation",
        "aspect",
        "opposition_Mars",
        "thinking",
        "Action itself interferes with formulating thought.",
        "risk",
        "action_interferes_with_thought_formulation",
        source_reference=REF_MARS_OPP,
    ),
    _f(
        "mars_opp_aggressive_driving_accident_association",
        "aspect",
        "opposition_Mars",
        "source_specific",
        "The source associates this configuration with increased road-risk / "
        "aggressive-driving patterns "
        "(source-described association; not a prediction that a person will "
        "have an accident).",
        "risk",
        "source_aggressive_driving_accident_association",
        source_reference=REF_MARS_OPP,
    ),
    _f(
        "mars_opp_source_stuttering_association",
        "aspect",
        "opposition_Mars",
        "source_specific",
        "Source associates this opposition with stuttering "
        "(source-specific association; not a medical diagnosis, IQ claim, "
        "or hiring conclusion).",
        "risk",
        "source_stuttering_association",
        source_reference=REF_MARS_OPP,
    ),
    _f(
        "mars_opp_source_cognitive_slowdown_episode",
        "aspect",
        "opposition_Mars",
        "source_specific",
        "Source associates this opposition with episodes described as "
        "\"тупняки\" / cognitive slowdown episodes "
        "(source wording; not low intelligence, not a diagnosis).",
        "risk",
        "source_cognitive_slowdown_episode",
        source_reference=REF_MARS_OPP,
    ),
    _f(
        "mars_opp_social_conflict_contexts",
        "aspect",
        "opposition_Mars",
        "communication",
        "Source-described pattern of conflicts / squabbles in contexts such as "
        "social networks, the road, close environment, and neighbors "
        "(not equated with debate or argumentation ability).",
        "risk",
        "social_conflict_proneness",
        source_reference=REF_MARS_OPP,
    ),
    _f(
        "mars_opp_scattered_activity",
        "aspect",
        "opposition_Mars",
        "thinking",
        "Dispersion / scattering in activity.",
        "risk",
        "scattered_activity",
        source_reference=REF_MARS_OPP,
    ),
    _f(
        "mars_opp_goal_setting_difficulty",
        "aspect",
        "opposition_Mars",
        "thinking",
        "Difficulty with goal-setting "
        "(not equated with planning or forecasting).",
        "risk",
        "goal_setting_difficulty",
        source_reference=REF_MARS_OPP,
    ),
    _f(
        "mars_opp_radio_in_the_head",
        "aspect",
        "opposition_Mars",
        "thinking",
        "A non-stop \"radio\" in the head / continuing mental stream "
        "(not equated with fast_thinking, anxiety, ADHD, or mental illness).",
        "risk",
        "mental_noise",
        source_reference=REF_MARS_OPP,
    ),
    _f(
        "mars_opp_sense_of_humor",
        "aspect",
        "opposition_Mars",
        "communication",
        "Sense of humor.",
        "neutral",
        "sense_of_humor",
        source_reference=REF_MARS_OPP,
    ),
    _f(
        "mars_opp_critical_negative_tone",
        "aspect",
        "opposition_Mars",
        "communication",
        "Source describes a critical / negative verbal environment, which may "
        "be expressed by the native or directed toward them "
        "(bidirectional source wording; not a deterministic native accusation).",
        "risk",
        "critical_negative_tone",
        source_reference=REF_MARS_OPP,
    ),
    _f(
        "mars_opp_injury_fracture_association",
        "aspect",
        "opposition_Mars",
        "source_specific",
        "The source associates this opposition with general injury / fractures "
        "and threats involving head, fingers, and blood vessels "
        "(source-specific, non-diagnostic association; not medical advice and "
        "not a hiring conclusion).",
        "risk",
        "source_injury_fracture_association",
        source_reference=REF_MARS_OPP,
    ),
)

MARS_OPPOSITION_UNRESOLVED: tuple[SourceFactDef, ...] = (
    _f(
        "mars_opp_branch_female_chart_younger_partner",
        "aspect",
        "opposition_Mars",
        "source_specific",
        "The source describes an increased association with a younger partner / "
        "friend specifically for a female-chart context; that context is not "
        "resolved by the current profile "
        "(unresolved; no gender / sex resolver is applied).",
        "conditional",
        "source_female_chart_younger_partner_association",
        source_reference=REF_MARS_OPP,
        activation_condition=_FEMALE_CHART_UNRESOLVED,
        unresolved=True,
    ),
)

MARS_OPPOSITION: tuple[SourceFactDef, ...] = (
    MARS_OPPOSITION_RESOLVED + MARS_OPPOSITION_UNRESOLVED
)


# ---------------------------------------------------------------------------
# Mercury conjunction Mars — Bioastrology
# Canonical public catalog key: conjunction_Mars
# Distinct from square_Mars, trine_Mars, and opposition_Mars.
# ---------------------------------------------------------------------------
MARS_CONJUNCTION_RESOLVED: tuple[SourceFactDef, ...] = (
    _f(
        "mars_cj_action_overrides_free_curiosity",
        "aspect",
        "conjunction_Mars",
        "thinking",
        "The function \"do here and now\" absorbs / overrides basic curiosity "
        "and the ability to learn simply for the sake of learning "
        "(functional dominance; not global inability to learn or low intelligence).",
        "risk",
        "action_overrides_free_curiosity",
        source_reference=REF_MARS_CONJ,
    ),
    _f(
        "mars_cj_action_when_reflection_needed",
        "aspect",
        "conjunction_Mars",
        "thinking",
        "When communication / thinking is needed, the native may rush into action "
        "(not equated with generic impulsivity).",
        "risk",
        "action_when_reflection_needed",
        source_reference=REF_MARS_CONJ,
    ),
    _f(
        "mars_cj_reflection_when_action_needed",
        "aspect",
        "conjunction_Mars",
        "thinking",
        "When quick action is needed, thinking / doubting / scattering may start "
        "instead (not equated with generic indecision).",
        "risk",
        "reflection_when_action_needed",
        source_reference=REF_MARS_CONJ,
    ),
    _f(
        "mars_cj_sales",
        "aspect",
        "conjunction_Mars",
        "work_application",
        "Commercial / salesperson qualities "
        "(not equated with persuasion).",
        "strength",
        "sales",
        source_reference=REF_MARS_CONJ,
    ),
    _f(
        "mars_cj_convincing_voice",
        "aspect",
        "conjunction_Mars",
        "communication",
        "Loud, convincing voice "
        "(not equated with generic persuasion).",
        "strength",
        "convincing_voice",
        source_reference=REF_MARS_CONJ,
    ),
    _f(
        "mars_cj_speech_clarity",
        "aspect",
        "conjunction_Mars",
        "communication",
        "Clarity of speech.",
        "strength",
        "speech_clarity",
        source_reference=REF_MARS_CONJ,
    ),
    _f(
        "mars_cj_technical_mindset",
        "aspect",
        "conjunction_Mars",
        "thinking",
        "Technical / \"techie\" cast of mind "
        "(technical mindset; not equated with technical_ability).",
        "neutral",
        "technical_mindset",
        source_reference=REF_MARS_CONJ,
    ),
    _f(
        "mars_cj_aggressive_driving_accident_association",
        "aspect",
        "conjunction_Mars",
        "source_specific",
        "The source associates this configuration with increased road-risk / "
        "aggressive-driving patterns "
        "(source-described association; not a prediction that a person will "
        "have an accident; not equated with driving_ability).",
        "risk",
        "source_aggressive_driving_accident_association",
        source_reference=REF_MARS_CONJ,
    ),
    _f(
        "mars_cj_scattered_activity",
        "aspect",
        "conjunction_Mars",
        "thinking",
        "Scattered activity.",
        "risk",
        "scattered_activity",
        source_reference=REF_MARS_CONJ,
    ),
    _f(
        "mars_cj_goal_setting_difficulty",
        "aspect",
        "conjunction_Mars",
        "thinking",
        "Difficulty with goal-setting "
        "(not equated with planning).",
        "risk",
        "goal_setting_difficulty",
        source_reference=REF_MARS_CONJ,
    ),
    _f(
        "mars_cj_radio_in_the_head",
        "aspect",
        "conjunction_Mars",
        "thinking",
        "A non-stop \"radio\" in the head / continuing mental stream.",
        "risk",
        "mental_noise",
        source_reference=REF_MARS_CONJ,
    ),
    _f(
        "mars_cj_sense_of_humor",
        "aspect",
        "conjunction_Mars",
        "communication",
        "Sense of humor.",
        "neutral",
        "sense_of_humor",
        source_reference=REF_MARS_CONJ,
    ),
    _f(
        "mars_cj_critical_negative_irritability",
        "aspect",
        "conjunction_Mars",
        "communication",
        "Source describes criticality / negativity / irritability "
        "(source-described pattern; not a deterministic native accusation).",
        "risk",
        "critical_negative_tone",
        "irritability",
        source_reference=REF_MARS_CONJ,
    ),
    _f(
        "mars_cj_source_psychiatry_association",
        "aspect",
        "conjunction_Mars",
        "source_specific",
        "The source associates this conjunction with a psychiatry-related "
        "framework claim "
        "(source-specific, non-diagnostic; not a medical diagnosis, mental-illness "
        "label, or work-fitness conclusion).",
        "risk",
        "source_psychiatry_association",
        source_reference=REF_MARS_CONJ,
    ),
    _f(
        "mars_cj_injury_fracture_association",
        "aspect",
        "conjunction_Mars",
        "source_specific",
        "The source associates this conjunction with general injury / fractures "
        "and threats involving head, fingers, and blood vessels "
        "(source-specific, non-diagnostic association; not medical advice and "
        "not a hiring conclusion).",
        "risk",
        "source_injury_fracture_association",
        source_reference=REF_MARS_CONJ,
    ),
    _f(
        "mars_cj_source_speech_cognition_variability",
        "aspect",
        "conjunction_Mars",
        "source_specific",
        "Source describes \"strangeness\" in speech and intellect, ranging from "
        "acceleration / inattentiveness to episodes described as \"тупка\" "
        "(source wording; not IQ, ADHD, cognitive disorder, or diagnosis).",
        "risk",
        "source_speech_cognition_variability",
        source_reference=REF_MARS_CONJ,
    ),
    _f(
        "mars_cj_quarrelsome_interaction",
        "aspect",
        "conjunction_Mars",
        "communication",
        "Quarrelsomeness "
        "(not equated with debate ability).",
        "risk",
        "quarrelsome_interaction",
        source_reference=REF_MARS_CONJ,
    ),
    _f(
        "mars_cj_interlocutor_listening_difficulty",
        "aspect",
        "conjunction_Mars",
        "communication",
        "Difficulty hearing what the other person is saying "
        "(not a global poor-communication claim).",
        "risk",
        "interlocutor_listening_difficulty",
        source_reference=REF_MARS_CONJ,
    ),
    _f(
        "mars_cj_dialogue_building_difficulty",
        "aspect",
        "conjunction_Mars",
        "communication",
        "Difficulty building dialogue "
        "(not equated with argumentation).",
        "risk",
        "dialogue_building_difficulty",
        source_reference=REF_MARS_CONJ,
    ),
)

MARS_CONJUNCTION_UNRESOLVED: tuple[SourceFactDef, ...] = (
    _f(
        "mars_cj_branch_female_chart_younger_partner",
        "aspect",
        "conjunction_Mars",
        "source_specific",
        "The source describes an increased association with a younger partner / "
        "friend specifically for a female-chart context; that context is not "
        "resolved by the current profile "
        "(unresolved; no gender / sex resolver is applied).",
        "conditional",
        "source_female_chart_younger_partner_association",
        source_reference=REF_MARS_CONJ,
        activation_condition=_FEMALE_CHART_UNRESOLVED,
        unresolved=True,
    ),
)

MARS_CONJUNCTION: tuple[SourceFactDef, ...] = (
    MARS_CONJUNCTION_RESOLVED + MARS_CONJUNCTION_UNRESOLVED
)

C7_ASPECT_PACKS: tuple[SourceFactDef, ...] = MARS_OPPOSITION + MARS_CONJUNCTION

C7_SUPPORTED_ASPECT_KEYS = frozenset({"opposition_Mars", "conjunction_Mars"})
