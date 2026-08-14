"""Mercury Source Profile v2 — Aspect Batch C2 (verified square Mars / Saturn).

C2 adds Bioastrology source packs for:

- Mercury square Mars
- Mercury square Saturn

No aliases. No opposition/conjunction packs.
Strength-dependent winner branches are unresolved (no strength resolver).

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


REF_MARS_SQ = "bioastrology_mercury_mars_square"
REF_SATURN_SQ = "bioastrology_mercury_saturn_square"

# Shared activation label: include both competing winner branches; leave unresolved.
# No sign/house/dignity/orb/aspect-count heuristic selects a winner.
_STRENGTH_UNRESOLVED = "strength_unresolved"


# ---------------------------------------------------------------------------
# Mercury square Mars — Bioastrology
# Canonical public catalog key: square_Mars
# Do NOT alias to opposition/conjunction Mars.
# ---------------------------------------------------------------------------
MARS_SQUARE_COMMON: tuple[SourceFactDef, ...] = (
    _f(
        "mars_sq_learning_action_conflict",
        "aspect",
        "square_Mars",
        "thinking",
        "The principle of ease / openness / learnability conflicts with the "
        "principle of realization / starting / doing.",
        "risk",
        "learning_action_conflict",
        source_reference=REF_MARS_SQ,
    ),
    _f(
        "mars_sq_intellectual_terrorism_school_association",
        "aspect",
        "square_Mars",
        "source_specific",
        "Source frequently associates this square with intellectual terrorism / "
        "harsh intellectual pressure at school (source association; not a "
        "deterministic biography claim).",
        "risk",
        "source_intellectual_terrorism_school",
        source_reference=REF_MARS_SQ,
    ),
    _f(
        "mars_sq_aggressive_driving_accident_association",
        "aspect",
        "square_Mars",
        "source_specific",
        "The source associates this square with aggressive-driving / road-accident "
        "risk (source-described association; not a prediction or medical diagnosis).",
        "risk",
        "source_aggressive_driving_accident_association",
        source_reference=REF_MARS_SQ,
    ),
    _f(
        "mars_sq_social_network_quarrels",
        "aspect",
        "square_Mars",
        "communication",
        "Source-described pattern of quarrels / conflicts in social networks.",
        "risk",
        "social_network_conflict",
        source_reference=REF_MARS_SQ,
    ),
    _f(
        "mars_sq_road_quarrels",
        "aspect",
        "square_Mars",
        "communication",
        "Source-described pattern of quarrels / conflicts on the road.",
        "risk",
        "road_conflict",
        source_reference=REF_MARS_SQ,
    ),
    _f(
        "mars_sq_close_surroundings_neighbor_quarrels",
        "aspect",
        "square_Mars",
        "environment",
        "Source-described pattern of quarrels / conflicts with close surroundings "
        "/ neighbors.",
        "risk",
        "close_surroundings_conflict",
        source_reference=REF_MARS_SQ,
    ),
    _f(
        "mars_sq_scattered_activity",
        "aspect",
        "square_Mars",
        "thinking",
        "Scattered activity.",
        "risk",
        "scattered_activity",
        source_reference=REF_MARS_SQ,
    ),
    _f(
        "mars_sq_goal_setting_difficulty",
        "aspect",
        "square_Mars",
        "thinking",
        "Difficulty with goal-setting.",
        "risk",
        "goal_setting_difficulty",
        source_reference=REF_MARS_SQ,
    ),
    _f(
        "mars_sq_radio_in_the_head",
        "aspect",
        "square_Mars",
        "thinking",
        "Persistent \"radio in the head\" / ongoing mental noise.",
        "risk",
        "mental_noise",
        source_reference=REF_MARS_SQ,
    ),
    _f(
        "mars_sq_sense_of_humor",
        "aspect",
        "square_Mars",
        "communication",
        "Sense of humor.",
        "neutral",
        "sense_of_humor",
        source_reference=REF_MARS_SQ,
    ),
    _f(
        "mars_sq_critical_negative_tone",
        "aspect",
        "square_Mars",
        "communication",
        "Critical / negative tone: the source says either the native swears / "
        "criticizes, or criticism comes from outside.",
        "risk",
        "critical_negative_tone",
        source_reference=REF_MARS_SQ,
    ),
    _f(
        "mars_sq_injury_fracture_association",
        "aspect",
        "square_Mars",
        "source_specific",
        "The source associates this square with general injury / fractures and "
        "threats involving head, fingers, and blood vessels "
        "(source-specific, non-diagnostic association; not medical advice and "
        "not a hiring conclusion).",
        "risk",
        "source_injury_fracture_association",
        source_reference=REF_MARS_SQ,
    ),
)

MARS_SQUARE_MERCURY_WINS: tuple[SourceFactDef, ...] = (
    _f(
        "mars_sq_branch_mercury_weak_practical_persistence",
        "aspect",
        "square_Mars",
        "source_specific",
        "If the Mercury side dominates, the source describes weak practical "
        "persistence / substantial idleness from the practical perspective of "
        "patience and labor (unresolved; no strength resolver).",
        "conditional",
        "source_low_practical_persistence",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "mars_sq_branch_mercury_oratory",
        "aspect",
        "square_Mars",
        "source_specific",
        "If the Mercury side dominates, the source describes very strong / "
        "gifted oratory (source-described aptitude; unresolved).",
        "conditional",
        "source_oratory_aptitude",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "mars_sq_branch_mercury_philosophy",
        "aspect",
        "square_Mars",
        "source_specific",
        "If the Mercury side dominates, the source describes philosophy aptitude "
        "(source-described; unresolved).",
        "conditional",
        "source_philosophy_aptitude",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "mars_sq_branch_mercury_sales",
        "aspect",
        "square_Mars",
        "work_application",
        "If the Mercury side dominates, the source describes sales aptitude "
        "(unresolved; not equated with persuasion).",
        "conditional",
        "sales",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "mars_sq_branch_mercury_research_reading",
        "aspect",
        "square_Mars",
        "source_specific",
        "If the Mercury side dominates, the source describes researcher / heavy "
        "reader aptitude (source-described; unresolved).",
        "conditional",
        "source_research_reading_aptitude",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "mars_sq_branch_mercury_engineering",
        "aspect",
        "square_Mars",
        "source_specific",
        "If the Mercury side dominates, the source describes engineering aptitude "
        "(source-described; unresolved; not equated with technical_ability).",
        "conditional",
        "source_engineering_aptitude",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "mars_sq_branch_mercury_science",
        "aspect",
        "square_Mars",
        "source_specific",
        "If the Mercury side dominates, the source describes science aptitude "
        "(source-described; unresolved).",
        "conditional",
        "source_science_aptitude",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "mars_sq_branch_mercury_humor",
        "aspect",
        "square_Mars",
        "communication",
        "If the Mercury side dominates, the source describes humor "
        "(unresolved).",
        "conditional",
        "sense_of_humor",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "mars_sq_branch_mercury_difficulty_starting",
        "aspect",
        "square_Mars",
        "thinking",
        "If the Mercury side dominates: hard to START "
        "(unresolved; distinct from continuation difficulty).",
        "conditional",
        "difficulty_starting",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "mars_sq_branch_mercury_easier_continuation",
        "aspect",
        "square_Mars",
        "thinking",
        "If the Mercury side dominates: easier to CONTINUE "
        "(unresolved; distinct from starting difficulty).",
        "conditional",
        "easier_continuation",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "mars_sq_branch_mercury_low_manual_ability",
        "aspect",
        "square_Mars",
        "source_specific",
        "If the Mercury side dominates, the source describes poor manual ability "
        "(source uses harsh \"hands from the wrong place\" wording; framed as "
        "source-described pattern, not a deterministic insult; unresolved).",
        "conditional",
        "source_low_manual_ability",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
)

MARS_SQUARE_MARS_WINS: tuple[SourceFactDef, ...] = (
    _f(
        "mars_sq_branch_mars_hardworking",
        "aspect",
        "square_Mars",
        "thinking",
        "If the Mars side dominates: hardworking / labor-oriented (unresolved).",
        "conditional",
        "hardworking",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "mars_sq_branch_mars_irritability_aggression",
        "aspect",
        "square_Mars",
        "source_specific",
        "If the Mars side dominates, the source describes irritability / "
        "aggression (source-described pattern/risk; unresolved).",
        "conditional",
        "source_irritability_aggression",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "mars_sq_branch_mars_action_precedes_reflection",
        "aspect",
        "square_Mars",
        "thinking",
        "If the Mars side dominates: does many things and thoughts \"catch up "
        "afterward\" — action precedes reflection "
        "(unresolved; not equated with fast_thinking).",
        "conditional",
        "action_precedes_reflection",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "mars_sq_branch_mars_low_reflection",
        "aspect",
        "square_Mars",
        "thinking",
        "If the Mars side dominates: does not reflect much on this (unresolved).",
        "conditional",
        "low_reflection",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "mars_sq_branch_mars_difficulty_hearing_others",
        "aspect",
        "square_Mars",
        "communication",
        "If the Mars side dominates: does not hear other people well "
        "(unresolved; not a global poor-communication claim).",
        "conditional",
        "difficulty_hearing_others",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "mars_sq_branch_mars_lower_intellect_claim",
        "aspect",
        "square_Mars",
        "source_specific",
        "If the Mars side dominates, the source describes a lower intellectual "
        "level (source-described claim; not an objectively validated intelligence "
        "score; unresolved).",
        "conditional",
        "source_lower_intellect_claim",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "mars_sq_branch_mars_high_activity",
        "aspect",
        "square_Mars",
        "thinking",
        "If the Mars side dominates: nevertheless very active (unresolved).",
        "conditional",
        "high_activity",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "mars_sq_branch_mars_artistic_aptitude",
        "aspect",
        "square_Mars",
        "source_specific",
        "If the Mars side dominates, the source often associates artists "
        "(source-described association; unresolved).",
        "conditional",
        "source_artistic_aptitude",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "mars_sq_branch_mars_entrepreneurial_drive",
        "aspect",
        "square_Mars",
        "source_specific",
        "If the Mars side dominates, the source often associates strong-willed "
        "entrepreneurs (source-described association; unresolved).",
        "conditional",
        "source_entrepreneurial_drive",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "mars_sq_branch_mars_easy_starting",
        "aspect",
        "square_Mars",
        "thinking",
        "If the Mars side dominates: easy to START "
        "(unresolved; distinct from continuation difficulty).",
        "conditional",
        "easy_starting",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "mars_sq_branch_mars_difficulty_continuing",
        "aspect",
        "square_Mars",
        "thinking",
        "If the Mars side dominates: harder to CONTINUE "
        "(unresolved; distinct from starting ease).",
        "conditional",
        "difficulty_continuing",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "mars_sq_branch_mars_manual_hand_skill",
        "aspect",
        "square_Mars",
        "work_application",
        "If the Mars side dominates: strong / skillful / active hands "
        "(unresolved; not equated with technical_ability).",
        "conditional",
        "manual_dexterity_or_hand_skill",
        source_reference=REF_MARS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
)

MARS_SQUARE: tuple[SourceFactDef, ...] = (
    MARS_SQUARE_COMMON + MARS_SQUARE_MERCURY_WINS + MARS_SQUARE_MARS_WINS
)


# ---------------------------------------------------------------------------
# Mercury square Saturn — Bioastrology
# Canonical public catalog key: square_Saturn
# Do NOT alias to opposition/conjunction Saturn or to trine_Saturn.
# ---------------------------------------------------------------------------
SATURN_SQUARE_COMMON: tuple[SourceFactDef, ...] = (
    _f(
        "saturn_sq_cognitive_duty_result_conflict",
        "aspect",
        "square_Saturn",
        "thinking",
        "Thinking / learning / communication conflicts with focus, result, and "
        "external social \"must / should\" requirements.",
        "risk",
        "cognitive_duty_result_conflict",
        source_reference=REF_SATURN_SQ,
    ),
    _f(
        "saturn_sq_indirect_result_conceptualization",
        "aspect",
        "square_Saturn",
        "thinking",
        "Study and talking do not connect cleanly with result; the result may "
        "arise in a strange / indirect way that is then difficult to "
        "conceptualize or explain "
        "(distinct from lack of intelligence or global poor communication).",
        "risk",
        "indirect_result_conceptualization_difficulty",
        source_reference=REF_SATURN_SQ,
    ),
    _f(
        "saturn_sq_mental_dissatisfaction_learning_utility",
        "aspect",
        "square_Saturn",
        "learning",
        "Mental dissatisfaction: \"I know not what I need; when I begin learning "
        "something new, I quickly understand that it will not be useful to me.\"",
        "risk",
        "mental_dissatisfaction_learning_utility",
        source_reference=REF_SATURN_SQ,
    ),
    _f(
        "saturn_sq_thinking_pessimism",
        "aspect",
        "square_Saturn",
        "thinking",
        "Pessimism in thinking.",
        "risk",
        "thinking_pessimism",
        source_reference=REF_SATURN_SQ,
    ),
    _f(
        "saturn_sq_critical_attitude",
        "aspect",
        "square_Saturn",
        "communication",
        "Critical attitude.",
        "risk",
        "critical_attitude",
        source_reference=REF_SATURN_SQ,
    ),
    _f(
        "saturn_sq_distrust",
        "aspect",
        "square_Saturn",
        "thinking",
        "Distrust.",
        "risk",
        "distrust",
        source_reference=REF_SATURN_SQ,
    ),
    _f(
        "saturn_sq_verification_requirement",
        "aspect",
        "square_Saturn",
        "thinking",
        "\"Everything must be checked\" "
        "(verification requirement; not equated with evidence_requirement).",
        "neutral",
        "verification_requirement",
        source_reference=REF_SATURN_SQ,
    ),
    _f(
        "saturn_sq_mental_restructuring_difficulty",
        "aspect",
        "square_Saturn",
        "thinking",
        "Difficulty with mental restructuring / adaptation.",
        "risk",
        "mental_restructuring_difficulty",
        source_reference=REF_SATURN_SQ,
    ),
    _f(
        "saturn_sq_unlearning_difficulty",
        "aspect",
        "square_Saturn",
        "learning",
        "Once something is learned, it is difficult to forget / unlearn it "
        "(unlearning difficulty; not equated with strong_memory / sticky_memory).",
        "risk",
        "unlearning_difficulty",
        source_reference=REF_SATURN_SQ,
    ),
    _f(
        "saturn_sq_secondary_gain_local_smartest",
        "aspect",
        "square_Saturn",
        "source_specific",
        "Source secondary-gain theme: \"smartest person in the familiar pond\" / "
        "\"no need to study because I already know everything\" "
        "(source-specific framing; not equated with confidence or expertise).",
        "risk",
        "source_secondary_gain_local_smartest",
        source_reference=REF_SATURN_SQ,
    ),
)

SATURN_SQUARE_MERCURY_WINS: tuple[SourceFactDef, ...] = (
    _f(
        "saturn_sq_branch_mercury_strong_mental_focus",
        "aspect",
        "square_Saturn",
        "thinking",
        "If the Mercury side dominates: strong mental focus (unresolved).",
        "conditional",
        "strong_mental_focus",
        source_reference=REF_SATURN_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "saturn_sq_branch_mercury_prolific_writing",
        "aspect",
        "square_Saturn",
        "communication",
        "If the Mercury side dominates: prolific writing / strong writing "
        "tendency (unresolved).",
        "conditional",
        "source_prolific_writing",
        source_reference=REF_SATURN_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "saturn_sq_branch_mercury_analytical_qualities",
        "aspect",
        "square_Saturn",
        "thinking",
        "If the Mercury side dominates, the source describes extraordinary "
        "analytical qualities (unresolved).",
        "conditional",
        "analytical_thinking",
        source_reference=REF_SATURN_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "saturn_sq_branch_mercury_intellectual_profession",
        "aspect",
        "square_Saturn",
        "work_application",
        "If the Mercury side dominates: intellectual profession orientation "
        "(unresolved).",
        "conditional",
        "intellectual_profession_orientation",
        source_reference=REF_SATURN_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "saturn_sq_branch_mercury_detail_fixation",
        "aspect",
        "square_Saturn",
        "thinking",
        "If the Mercury side dominates: excessive fixation on details "
        "(unresolved).",
        "conditional",
        "excessive_detail_fixation",
        source_reference=REF_SATURN_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "saturn_sq_branch_mercury_technical_detail_fixation",
        "aspect",
        "square_Saturn",
        "thinking",
        "If the Mercury side dominates: excessive fixation on technique / "
        "technical details "
        "(unresolved; not equated with technical_ability).",
        "conditional",
        "excessive_technical_detail_fixation",
        source_reference=REF_SATURN_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "saturn_sq_branch_mercury_coherent_worlds",
        "aspect",
        "square_Saturn",
        "source_specific",
        "If the Mercury side dominates, the source says in the best expression "
        "this intelligence can build whole internally coherent \"worlds\" "
        "(source-specific; unresolved; not generic creativity).",
        "conditional",
        "source_internally_coherent_worlds",
        source_reference=REF_SATURN_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
)

SATURN_SQUARE_SATURN_WINS: tuple[SourceFactDef, ...] = (
    _f(
        "saturn_sq_branch_saturn_terse_communication",
        "aspect",
        "square_Saturn",
        "communication",
        "If the Saturn side dominates: few words / terse communication "
        "(unresolved; not equated with introversion).",
        "conditional",
        "terse_communication",
        source_reference=REF_SATURN_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "saturn_sq_branch_saturn_poor_abstract_thinking",
        "aspect",
        "square_Saturn",
        "thinking",
        "If the Saturn side dominates: abstract mind works poorly "
        "(unresolved; not a global low-intelligence claim).",
        "conditional",
        "poor_abstract_thinking",
        source_reference=REF_SATURN_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
)

SATURN_SQUARE: tuple[SourceFactDef, ...] = (
    SATURN_SQUARE_COMMON + SATURN_SQUARE_MERCURY_WINS + SATURN_SQUARE_SATURN_WINS
)

C2_ASPECT_PACKS: tuple[SourceFactDef, ...] = MARS_SQUARE + SATURN_SQUARE

C2_SUPPORTED_ASPECT_KEYS = frozenset({"square_Mars", "square_Saturn"})
