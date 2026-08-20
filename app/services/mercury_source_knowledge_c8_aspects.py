"""Mercury Source Profile v2 — Aspect Batch C8 (Uranus square / opposition).

C8 completes the Mercury–Uranus public family with two DISTINCT packs:

- square_Uranus
- opposition_Uranus

No aliases. Do NOT reuse conjunction_Uranus or trine_Uranus catalog facts.
Do NOT treat conjunction \"resembles square\" as catalog identity.

Winner branches on square use existing strength_unresolved
(Mercury-wins / Uranus-wins). Engine cannot resolve winner.

Celebrity examples, secondary gain, compensation, and \"supergift\"
intentionally omitted (same C4–C7 precedent).

Header-like square fragment \"function of communication and learning\"
omitted (no independent semantic predicate).

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


REF_URANUS_SQ = "bioastrology_mercury_uranus_square"
REF_URANUS_OPP = "bioastrology_mercury_uranus_opposition"
_STRENGTH_UNRESOLVED = "strength_unresolved"


# ---------------------------------------------------------------------------
# Mercury square Uranus — Bioastrology
# Canonical public catalog key: square_Uranus
# Distinct from conjunction_Uranus, trine_Uranus, opposition_Uranus.
# ---------------------------------------------------------------------------
URANUS_SQUARE_COMMON: tuple[SourceFactDef, ...] = (
    _f(
        "uranus_sq_source_genius_fresh_open_mind",
        "aspect",
        "square_Uranus",
        "source_specific",
        "Source describes + genius / freshness / openness of mind "
        "(source-described claim; not an objectively validated intelligence score).",
        "strength",
        "source_genius_fresh_open_mind",
        source_reference=REF_URANUS_SQ,
    ),
    _f(
        "uranus_sq_distractibility",
        "aspect",
        "square_Uranus",
        "risk",
        "Distractibility / defocus.",
        "risk",
        "distractibility",
        source_reference=REF_URANUS_SQ,
    ),
    _f(
        "uranus_sq_source_adhd_association",
        "aspect",
        "square_Uranus",
        "source_specific",
        "Source associates this square with ADHD "
        "(source-specific association; not a medical diagnosis, not a hiring conclusion).",
        "risk",
        "source_adhd_association",
        source_reference=REF_URANUS_SQ,
    ),
    _f(
        "uranus_sq_strange_concept_drift",
        "aspect",
        "square_Uranus",
        "risk",
        "Drifting into strange concepts.",
        "risk",
        "strange_concept_drift",
        source_reference=REF_URANUS_SQ,
    ),
    _f(
        "uranus_sq_impractical_thinking",
        "aspect",
        "square_Uranus",
        "risk",
        "Impracticality of thinking "
        "(not equated with planning difficulty, technical ability, or intelligence).",
        "risk",
        "impractical_thinking",
        source_reference=REF_URANUS_SQ,
    ),
    _f(
        "uranus_sq_boredom_with_here_and_now",
        "aspect",
        "square_Uranus",
        "risk",
        "Boredom with thinking about \"here and now\".",
        "risk",
        "boredom_with_here_and_now",
        source_reference=REF_URANUS_SQ,
    ),
    _f(
        "uranus_sq_driving_accident_risk",
        "aspect",
        "square_Uranus",
        "source_specific",
        "The source associates this configuration with increased traffic-accident risk "
        "(source-described association; not a prediction that a person will have an "
        "accident; not equated with driving_ability; source does not state aggressive driving).",
        "risk",
        "driving_accident_risk",
        source_reference=REF_URANUS_SQ,
    ),
    _f(
        "uranus_sq_fast_sometimes_disfluent_speech",
        "aspect",
        "square_Uranus",
        "communication",
        "Fast speech that may sometimes become stumbling / crumpled "
        "(not equated with fast_thinking, oratory, or poor intelligence).",
        "neutral",
        "fast_speech",
        "speech_disfluency_or_compression",
        source_reference=REF_URANUS_SQ,
    ),
    _f(
        "uranus_sq_technical_talents",
        "aspect",
        "square_Uranus",
        "work_application",
        "Source describes + technical talents.",
        "strength",
        "technical_ability",
        source_reference=REF_URANUS_SQ,
    ),
    _f(
        "uranus_sq_rebellious_free_thinking",
        "aspect",
        "square_Uranus",
        "thinking",
        "Source describes + rebellious free thinking "
        "(not equated with generic nonstandard_thinking).",
        "strength",
        "rebellious_free_thinking",
        source_reference=REF_URANUS_SQ,
    ),
    _f(
        "uranus_sq_interest_ability_psychology",
        "aspect",
        "square_Uranus",
        "source_specific",
        "Source describes + interest / ability in psychology "
        "(source-described claim; not a scientifically validated professional competency).",
        "neutral",
        "source_psychology_interest_ability",
        source_reference=REF_URANUS_SQ,
    ),
    _f(
        "uranus_sq_interest_ability_numerology",
        "aspect",
        "square_Uranus",
        "source_specific",
        "Source describes + interest / ability in numerology "
        "(source-described claim; not a scientifically validated professional competency).",
        "neutral",
        "source_numerology_interest_ability",
        source_reference=REF_URANUS_SQ,
    ),
    _f(
        "uranus_sq_interest_ability_astrology",
        "aspect",
        "square_Uranus",
        "source_specific",
        "Source describes + interest / ability in astrology "
        "(source-described claim; not a scientifically validated professional competency).",
        "neutral",
        "source_astrology_interest_ability",
        source_reference=REF_URANUS_SQ,
    ),
    _f(
        "uranus_sq_claircognizance",
        "aspect",
        "square_Uranus",
        "source_specific",
        "Source describes + claircognizance "
        "(source-framework claim; not scientifically established perception, "
        "not a diagnostic/hiring fact).",
        "neutral",
        "source_claircognizance",
        source_reference=REF_URANUS_SQ,
    ),
    _f(
        "uranus_sq_sense_of_humor",
        "aspect",
        "square_Uranus",
        "communication",
        "Source describes + sense of humor.",
        "neutral",
        "sense_of_humor",
        source_reference=REF_URANUS_SQ,
    ),
    _f(
        "uranus_sq_piercing_persuasiveness_madman_framing",
        "aspect",
        "square_Uranus",
        "communication",
        "Source describes + \"piercing persuasiveness of the madman's words\" "
        "(source framing of unusual persuasiveness; \"madman\" is source wording, "
        "not a psychiatric diagnosis).",
        "strength",
        "persuasion",
        source_reference=REF_URANUS_SQ,
    ),
)

URANUS_SQUARE_MERCURY_WINS: tuple[SourceFactDef, ...] = (
    _f(
        "uranus_sq_branch_mercury_stream_of_consciousness_speech",
        "aspect",
        "square_Uranus",
        "communication",
        "If the Mercury side dominates, the source describes streams / flow of "
        "consciousness in speech (unresolved; no strength resolver).",
        "conditional",
        "stream_of_consciousness_speech",
        source_reference=REF_URANUS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "uranus_sq_branch_mercury_speech_overproduction",
        "aspect",
        "square_Uranus",
        "communication",
        "If the Mercury side dominates, the source describes excess of the speech "
        "function (unresolved; no strength resolver).",
        "conditional",
        "speech_overproduction",
        source_reference=REF_URANUS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "uranus_sq_branch_mercury_freak_or_professional_manipulator",
        "aspect",
        "square_Uranus",
        "source_specific",
        "If the Mercury side dominates, the source describes the person as either "
        "a \"freak\" or a \"professional manipulator\" "
        "(source wording; unresolved conditional; not an unconditional character "
        "verdict or hiring conclusion).",
        "conditional",
        "source_freak_or_professional_manipulator_label",
        source_reference=REF_URANUS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "uranus_sq_branch_mercury_speech_insensitive_to_interlocutor",
        "aspect",
        "square_Uranus",
        "communication",
        "If the Mercury side dominates, speech is insensitive to the emotions and "
        "reactions of the interlocutor (unresolved; no strength resolver; not equated "
        "with persuasion, argumentation, or debate).",
        "conditional",
        "speech_insensitive_to_interlocutor_reaction",
        source_reference=REF_URANUS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "uranus_sq_branch_mercury_oratory_aptitude",
        "aspect",
        "square_Uranus",
        "source_specific",
        "If the Mercury side dominates, the source says this can be ideal for orators "
        "(source-described aptitude; unresolved; not a hiring recommendation).",
        "conditional",
        "source_oratory_aptitude",
        source_reference=REF_URANUS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "uranus_sq_branch_mercury_investigative_aptitude",
        "aspect",
        "square_Uranus",
        "source_specific",
        "If the Mercury side dominates, the source says this can be ideal for "
        "investigators (source-described aptitude; unresolved; not a hiring "
        "recommendation).",
        "conditional",
        "source_investigative_aptitude",
        source_reference=REF_URANUS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
)

URANUS_SQUARE_URANUS_WINS: tuple[SourceFactDef, ...] = (
    _f(
        "uranus_sq_branch_uranus_ordinary_thinking_pulverized",
        "aspect",
        "square_Uranus",
        "source_specific",
        "If the Uranus side dominates, ordinary / primitive thinking is "
        "\"ground into powder\" by energies of distant cosmos "
        "(source wording; unresolved; no strength resolver; not an IQ claim).",
        "conditional",
        "source_ordinary_thinking_pulverized_by_distant_cosmos",
        source_reference=REF_URANUS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "uranus_sq_branch_uranus_philosophical_concept_focus",
        "aspect",
        "square_Uranus",
        "thinking",
        "If the Uranus side dominates, thoughts center around philosophical concepts "
        "(unresolved; not equated with abstract_thinking).",
        "conditional",
        "philosophical_concept_focus",
        source_reference=REF_URANUS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "uranus_sq_branch_uranus_psychological_concept_focus",
        "aspect",
        "square_Uranus",
        "thinking",
        "If the Uranus side dominates, thoughts center around psychological concepts "
        "(unresolved).",
        "conditional",
        "psychological_concept_focus",
        source_reference=REF_URANUS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "uranus_sq_branch_uranus_believes_no_one",
        "aspect",
        "square_Uranus",
        "thinking",
        "If the Uranus side dominates, the native believes no one "
        "(unresolved; distinct from generic distrust tag elsewhere).",
        "conditional",
        "believes_no_one",
        source_reference=REF_URANUS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "uranus_sq_branch_uranus_independent_research",
        "aspect",
        "square_Uranus",
        "thinking",
        "If the Uranus side dominates, prefers independently digging into / "
        "researching reality (unresolved; not equated with analytical_thinking).",
        "conditional",
        "independent_research",
        source_reference=REF_URANUS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "uranus_sq_branch_uranus_skeptical_questioning",
        "aspect",
        "square_Uranus",
        "thinking",
        "If the Uranus side dominates, puts everything into question and doubt "
        "(unresolved; not equated with evidence_requirement).",
        "conditional",
        "skeptical_questioning",
        source_reference=REF_URANUS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "uranus_sq_branch_uranus_blunt_truth_without_regard_for_consequences",
        "aspect",
        "square_Uranus",
        "communication",
        "If the Uranus side dominates, habit of \"cutting the truth straight\" "
        "without regard for consequences "
        "(unresolved; not equated with argumentation or debate; not the same as "
        "generic blunt_truth_speech aptitude).",
        "conditional",
        "blunt_truth_without_regard_for_consequences",
        source_reference=REF_URANUS_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
)

URANUS_SQUARE: tuple[SourceFactDef, ...] = (
    URANUS_SQUARE_COMMON + URANUS_SQUARE_MERCURY_WINS + URANUS_SQUARE_URANUS_WINS
)


# ---------------------------------------------------------------------------
# Mercury opposition Uranus — Bioastrology
# Canonical public catalog key: opposition_Uranus
# Distinct from square_Uranus, conjunction_Uranus, trine_Uranus.
# No winner branches in supplied opposition main body.
# ---------------------------------------------------------------------------
URANUS_OPPOSITION_CORE: tuple[SourceFactDef, ...] = (
    _f(
        "uranus_opp_ordinary_learning_vs_uranian_creative_detachment_conflict",
        "aspect",
        "opposition_Uranus",
        "thinking",
        "The function of communication / learning \"fights\" the function of "
        "detachment, creativity, and science-fiction / fantasy orientation "
        "(opposition-specific polarity between functions; not flattened to "
        "learning_difficulty, creativity, or communication_problem).",
        "risk",
        "ordinary_learning_vs_uranian_creative_detachment_conflict",
        source_reference=REF_URANUS_OPP,
    ),
    _f(
        "uranus_opp_ordinary_vs_transcendent_thinking_oscillation",
        "aspect",
        "opposition_Uranus",
        "source_specific",
        "The mind becomes bored and continually dives between "
        "(1) \"I should learn something ordinary and just chat\" and "
        "(2) leaving ordinary reality to metaphorically \"talk with God\" and "
        "operate at \"ultra-high frequencies unavailable to mere mortals\" "
        "(source metaphorical language; not proof of superior intelligence, "
        "not a psychiatric diagnosis, not an objective supernatural ability).",
        "risk",
        "ordinary_vs_transcendent_thinking_oscillation",
        source_reference=REF_URANUS_OPP,
    ),
)

URANUS_OPPOSITION_COMMON: tuple[SourceFactDef, ...] = (
    _f(
        "uranus_opp_source_genius_fresh_open_mind",
        "aspect",
        "opposition_Uranus",
        "source_specific",
        "Source describes + genius / freshness / openness of mind "
        "(source-described claim; not an objectively validated intelligence score).",
        "strength",
        "source_genius_fresh_open_mind",
        source_reference=REF_URANUS_OPP,
    ),
    _f(
        "uranus_opp_distractibility",
        "aspect",
        "opposition_Uranus",
        "risk",
        "Distractibility / defocus.",
        "risk",
        "distractibility",
        source_reference=REF_URANUS_OPP,
    ),
    _f(
        "uranus_opp_source_adhd_association",
        "aspect",
        "opposition_Uranus",
        "source_specific",
        "Source associates this opposition with ADHD "
        "(source-specific association; not a medical diagnosis, not a hiring conclusion).",
        "risk",
        "source_adhd_association",
        source_reference=REF_URANUS_OPP,
    ),
    _f(
        "uranus_opp_strange_concept_drift",
        "aspect",
        "opposition_Uranus",
        "risk",
        "Drifting into strange concepts.",
        "risk",
        "strange_concept_drift",
        source_reference=REF_URANUS_OPP,
    ),
    _f(
        "uranus_opp_impractical_thinking",
        "aspect",
        "opposition_Uranus",
        "risk",
        "Impracticality of thinking "
        "(not equated with planning difficulty, technical ability, or intelligence).",
        "risk",
        "impractical_thinking",
        source_reference=REF_URANUS_OPP,
    ),
    _f(
        "uranus_opp_boredom_with_here_and_now",
        "aspect",
        "opposition_Uranus",
        "risk",
        "Boredom with thinking about \"here and now\".",
        "risk",
        "boredom_with_here_and_now",
        source_reference=REF_URANUS_OPP,
    ),
    _f(
        "uranus_opp_driving_accident_risk",
        "aspect",
        "opposition_Uranus",
        "source_specific",
        "The source associates this configuration with increased traffic-accident risk "
        "(source-described association; not a prediction that a person will have an "
        "accident; not equated with driving_ability; source does not state aggressive driving).",
        "risk",
        "driving_accident_risk",
        source_reference=REF_URANUS_OPP,
    ),
    _f(
        "uranus_opp_fast_sometimes_disfluent_speech",
        "aspect",
        "opposition_Uranus",
        "communication",
        "Fast speech that may sometimes become stumbling / crumpled "
        "(not equated with fast_thinking, oratory, or poor intelligence).",
        "neutral",
        "fast_speech",
        "speech_disfluency_or_compression",
        source_reference=REF_URANUS_OPP,
    ),
    _f(
        "uranus_opp_technical_talents",
        "aspect",
        "opposition_Uranus",
        "work_application",
        "Source describes + technical talents.",
        "strength",
        "technical_ability",
        source_reference=REF_URANUS_OPP,
    ),
    _f(
        "uranus_opp_rebellious_free_thinking",
        "aspect",
        "opposition_Uranus",
        "thinking",
        "Source describes + rebellious free thinking "
        "(not equated with generic nonstandard_thinking).",
        "strength",
        "rebellious_free_thinking",
        source_reference=REF_URANUS_OPP,
    ),
    _f(
        "uranus_opp_interest_ability_psychology",
        "aspect",
        "opposition_Uranus",
        "source_specific",
        "Source describes + interest / ability in psychology "
        "(source-described claim; not a scientifically validated professional competency).",
        "neutral",
        "source_psychology_interest_ability",
        source_reference=REF_URANUS_OPP,
    ),
    _f(
        "uranus_opp_interest_ability_numerology",
        "aspect",
        "opposition_Uranus",
        "source_specific",
        "Source describes + interest / ability in numerology "
        "(source-described claim; not a scientifically validated professional competency).",
        "neutral",
        "source_numerology_interest_ability",
        source_reference=REF_URANUS_OPP,
    ),
    _f(
        "uranus_opp_interest_ability_astrology",
        "aspect",
        "opposition_Uranus",
        "source_specific",
        "Source describes + interest / ability in astrology "
        "(source-described claim; not a scientifically validated professional competency).",
        "neutral",
        "source_astrology_interest_ability",
        source_reference=REF_URANUS_OPP,
    ),
    _f(
        "uranus_opp_claircognizance",
        "aspect",
        "opposition_Uranus",
        "source_specific",
        "Source describes + claircognizance "
        "(source-framework claim; not scientifically established perception, "
        "not a diagnostic/hiring fact).",
        "neutral",
        "source_claircognizance",
        source_reference=REF_URANUS_OPP,
    ),
    _f(
        "uranus_opp_sense_of_humor",
        "aspect",
        "opposition_Uranus",
        "communication",
        "Source describes + sense of humor.",
        "neutral",
        "sense_of_humor",
        source_reference=REF_URANUS_OPP,
    ),
    _f(
        "uranus_opp_piercing_persuasiveness_madman_framing",
        "aspect",
        "opposition_Uranus",
        "communication",
        "Source describes + \"piercing persuasiveness of the madman's words\" "
        "(source framing of unusual persuasiveness; \"madman\" is source wording, "
        "not a psychiatric diagnosis).",
        "strength",
        "persuasion",
        source_reference=REF_URANUS_OPP,
    ),
)

URANUS_OPPOSITION: tuple[SourceFactDef, ...] = (
    URANUS_OPPOSITION_CORE + URANUS_OPPOSITION_COMMON
)

C8_ASPECT_PACKS: tuple[SourceFactDef, ...] = URANUS_SQUARE + URANUS_OPPOSITION

C8_SUPPORTED_ASPECT_KEYS = frozenset({"square_Uranus", "opposition_Uranus"})
