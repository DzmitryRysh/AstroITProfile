"""Mercury Source Profile v2 — Aspect Batch C14 (Pluto reachable family completion).

C14 completes the final reachable natal Mercury–Pluto major aspects:

- opposition_Pluto
- conjunction_Pluto

Existing: square_Pluto, trine_Pluto, sextile_Pluto (alias -> trine).

NO alias between opposition and conjunction.
Conjunction \"similar to square with strong Pluto\" is a source relationship only —
NOT catalog identity and NOT pluto_strength_unresolved activation.

Secondary gain, compensation, supergift, and celebrity examples omitted.

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


REF_PLUTO_OPP = "bioastrology_mercury_pluto_opposition"
REF_PLUTO_CJ = "bioastrology_mercury_pluto_conjunction"


def _build_pluto_common_body(
    *,
    factor_key: str,
    prefix: str,
    source_ref: str,
) -> tuple[SourceFactDef, ...]:
    """Shared Bioastrology Mercury–Pluto opposition/conjunction tense body."""
    return (
        _f(
            f"{prefix}_source_toxic_conflict_atmosphere_association",
            "aspect",
            factor_key,
            "source_specific",
            "Source associates +1 to a general atmosphere of poisonous / toxic "
            "conflict around the person, where the person may be either source or "
            "victim "
            "(source-described association; not a deterministic accusation that "
            "the person is toxic or causes conflict).",
            "conditional",
            "source_toxic_conflict_atmosphere_association",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_source_road_accident_risk_association",
            "aspect",
            factor_key,
            "source_specific",
            "Source associates +1 to road accidents "
            "(source-described association; not a prediction of an accident; not "
            "driving_ability or driving-fitness judgment).",
            "conditional",
            "source_road_accident_risk_association",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_aggressive_driving_tendency_source_claim",
            "aspect",
            factor_key,
            "mobility",
            "Source describes +1 to aggressive driving "
            "(source-described tendency claim; not a factual claim about a real "
            "person's driving; not driving_ability).",
            "risk",
            "aggressive_driving_tendency_source_claim",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_neighbor_conflict_source_association",
            "aspect",
            factor_key,
            "environment",
            "Source associates +1 to problems with neighbors "
            "(source-described association; does not assert actual current "
            "conflict).",
            "conditional",
            "neighbor_conflict_source_association",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_sibling_conflict_source_association",
            "aspect",
            factor_key,
            "environment",
            "Source associates +1 to problems with brothers / sisters "
            "(source-described association; does not assert actual current "
            "conflict).",
            "conditional",
            "sibling_conflict_source_association",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_travel_crisis_source_association",
            "aspect",
            factor_key,
            "mobility",
            "Source associates +1 to crises / problems during trips, ranging from "
            "dislike of travel to liking travel but repeatedly having something go "
            "wrong on the road "
            "(not equated with likes_travel, dislikes_travel, or foreign_languages).",
            "conditional",
            "travel_crisis_source_association",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_dangerous_curiosity_source_claim",
            "aspect",
            factor_key,
            "thinking",
            "Source describes +1 to dangerous curiosity "
            "(not equated with generic curiosity, research, or risk_taking).",
            "risk",
            "dangerous_curiosity",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_pessimism",
            "aspect",
            factor_key,
            "thinking",
            "Source describes +1 to pessimism.",
            "risk",
            "pessimism",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_fatalistic_doom_source_claim",
            "aspect",
            factor_key,
            "source_specific",
            "Source describes +1 to a fatalistic sense of doom "
            "(source Dostoevsky-on-the-tongue metaphor; not a clinical diagnosis).",
            "risk",
            "fatalistic_doom_source_claim",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_sharp_hurtful_speech_source_claim",
            "aspect",
            factor_key,
            "communication",
            "Source describes a \"razor effect on the tongue with snake venom\": "
            "it is easy to hurt / offend others with words "
            "(not equated with persuasion, oratory, or argumentation).",
            "risk",
            "sharp_hurtful_speech_source_claim",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_high_word_impact_source_claim",
            "aspect",
            factor_key,
            "communication",
            "Source describes that words have a high degree of resonance / impact "
            "(not equated with persuasion, oratory, or argumentation).",
            "neutral",
            "high_word_impact_source_claim",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_sarcasm",
            "aspect",
            factor_key,
            "communication",
            "Source describes +1 sarcasm.",
            "neutral",
            "sarcasm",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_sense_of_humor",
            "aspect",
            factor_key,
            "communication",
            "Source describes +1 excellent sense of humor.",
            "strength",
            "sense_of_humor",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_destructive_penetrating_winning_thought_speech_drive",
            "aspect",
            factor_key,
            "source_specific",
            "Source describes a thinking/speech imperative: if you think and speak, "
            "destroy, dig and win, otherwise you will be \"stupid\" "
            "(source-described cognitive/verbal drive framing; not a literal "
            "statement that the user becomes stupid; not equated with aggression, "
            "competition, or technical_ability).",
            "risk",
            "destructive_penetrating_winning_thought_speech_drive",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_source_negative_thought_word_manifestation_association",
            "aspect",
            factor_key,
            "source_specific",
            "Source uses the phrase \"my tongue is my enemy, I think something bad "
            "and it immediately comes true\" "
            "(source-described subjective association / metaphor; not a claim that "
            "negative thoughts paranormally cause events).",
            "conditional",
            "source_negative_thought_word_manifestation_association",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_persuasion",
            "aspect",
            factor_key,
            "communication",
            "Source describes +1 persuasiveness.",
            "strength",
            "persuasion",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_insight",
            "aspect",
            factor_key,
            "thinking",
            "Source describes +1 insight / penetrative perception "
            "(\"проницательность\").",
            "strength",
            "insight",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_powerful_words",
            "aspect",
            factor_key,
            "communication",
            "Source describes +1 power of word.",
            "strength",
            "powerful_words",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_blunt_truth_telling",
            "aspect",
            factor_key,
            "communication",
            "Source describes ability to \"cut the truth\" "
            "(not equated with honesty, evidence, or debate).",
            "strength",
            "blunt_truth_telling",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_penetrating_naming",
            "aspect",
            factor_key,
            "communication",
            "Source describes ability to call things by their piercing / true names "
            "(not equated with honesty, evidence, or debate).",
            "strength",
            "penetrating_naming",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_source_nlp_aptitude",
            "aspect",
            factor_key,
            "source_specific",
            "Source describes talent of an NLP practitioner "
            "(source-described aptitude; not a certified NLP credential, not a "
            "manipulation diagnosis, and not a hiring competency).",
            "neutral",
            "source_nlp_aptitude",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_debate",
            "aspect",
            factor_key,
            "communication",
            "Source describes ability to conduct debates.",
            "strength",
            "debate",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_argumentation",
            "aspect",
            factor_key,
            "communication",
            "Source describes ability to find weighty / strong arguments "
            "(not equated with evidence_requirement).",
            "strength",
            "argumentation",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_technical_ability",
            "aspect",
            factor_key,
            "work_application",
            "Source describes +1 to technical talents.",
            "strength",
            "technical_ability",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_source_diagnostic_aptitude",
            "aspect",
            factor_key,
            "source_specific",
            "Source describes an ability to \"diagnose\" / identify what is wrong "
            "(source wording; not a medical diagnosis capability, psychiatric "
            "competence, or clinical qualification).",
            "neutral",
            "source_diagnostic_aptitude",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_vulnerability_detection",
            "aspect",
            factor_key,
            "work_application",
            "Source describes ability to see vulnerabilities "
            "(not equated with cybersecurity ability automatically).",
            "strength",
            "vulnerability_detection",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_analytical_thinking",
            "aspect",
            factor_key,
            "thinking",
            "Source describes +1 analyticality.",
            "strength",
            "analytical_thinking",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_source_psychological_aptitude",
            "aspect",
            factor_key,
            "source_specific",
            "Source describes psychological abilities "
            "(source-described aptitude; not licensed psychologist competence).",
            "neutral",
            "source_psychological_aptitude",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_source_hypnotic_aptitude",
            "aspect",
            factor_key,
            "source_specific",
            "Source describes hypnotic abilities "
            "(source-described aptitude; not a mind-control claim).",
            "neutral",
            "source_hypnotic_aptitude",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_source_technical_hacking_aptitude",
            "aspect",
            factor_key,
            "source_specific",
            "Source describes ability to hack technology / equipment "
            "(source-described ability association; not an instruction for "
            "offensive cyber activity; not equated with general technical_ability).",
            "neutral",
            "source_technical_hacking_aptitude",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_source_system_hacking_aptitude",
            "aspect",
            factor_key,
            "source_specific",
            "Source describes ability to hack systems "
            "(source-described ability association; does not infer illegal conduct; "
            "not equated with general technical_ability).",
            "neutral",
            "source_system_hacking_aptitude",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_source_mind_hacking_metaphor",
            "aspect",
            factor_key,
            "source_specific",
            "Source literally says \"hack another person's brain\" "
            "(source metaphor for psychological penetration / influence; not "
            "literal mind control; not equated with hypnosis or persuasion "
            "automatically).",
            "neutral",
            "source_mind_hacking_metaphor",
            source_reference=source_ref,
        ),
        _f(
            f"{prefix}_fast_learning_through_critique",
            "aspect",
            factor_key,
            "learning",
            "Source describes +1 to fast learning through criticism of existing "
            "concepts and orders "
            "(not equated with lifelong_learning, learning_speed, or "
            "critical_thinking automatically).",
            "strength",
            "fast_learning_through_critique",
            source_reference=source_ref,
        ),
    )


# ---------------------------------------------------------------------------
# Mercury opposition Pluto — Bioastrology
# Canonical: opposition_Pluto
# ---------------------------------------------------------------------------
PLUTO_OPPOSITION_UNIQUE: tuple[SourceFactDef, ...] = (
    _f(
        "plu_opp_thinking_pluto_cold_war_source_metaphor",
        "aspect",
        "opposition_Pluto",
        "source_specific",
        "Source describes the function of thinking, communication and learning as "
        "conducting a \"cold war\" with the energy of an atomic bomb "
        "(source metaphor / aspect-mechanism classification; not literal atomic "
        "energy; not equated with conflict_skill, aggression, technical_ability, "
        "or debate).",
        "neutral",
        "thinking_pluto_cold_war_source_metaphor",
        source_reference=REF_PLUTO_OPP,
    ),
    _f(
        "plu_opp_learning_openness_omniscience_rejection_oscillation",
        "aspect",
        "opposition_Pluto",
        "thinking",
        "Source describes oscillation between poles: "
        "\"I am open, positive, I want to learn\" and "
        "\"I already know everything, everyone around is stupid, all information "
        "is nonsense and lies\" "
        "(source-described polarity / oscillation; not a deterministic claim that "
        "the person thinks everyone is stupid, rejects all information, or "
        "believes everything is a lie).",
        "risk",
        "learning_openness_omniscience_rejection_oscillation",
        source_reference=REF_PLUTO_OPP,
    ),
)

PLUTO_OPPOSITION: tuple[SourceFactDef, ...] = (
    PLUTO_OPPOSITION_UNIQUE
    + _build_pluto_common_body(
        factor_key="opposition_Pluto",
        prefix="plu_opp",
        source_ref=REF_PLUTO_OPP,
    )
)


# ---------------------------------------------------------------------------
# Mercury conjunction Pluto — Bioastrology
# Canonical: conjunction_Pluto — distinct from square_Pluto
# ---------------------------------------------------------------------------
PLUTO_CONJUNCTION_UNIQUE: tuple[SourceFactDef, ...] = (
    _f(
        "plu_cj_thinking_pluto_full_absorption_source_metaphor",
        "aspect",
        "conjunction_Pluto",
        "source_specific",
        "Source describes the function of thinking, communication and learning as "
        "completely absorbed by \"atomic bomb energy\" "
        "(source metaphor / mechanism; not interpreted as obsession, mental "
        "illness, aggression, or compulsion).",
        "neutral",
        "thinking_pluto_full_absorption_source_metaphor",
        source_reference=REF_PLUTO_CJ,
    ),
    _f(
        "plu_cj_resembles_square_pluto_stronger_source_relationship",
        "aspect",
        "conjunction_Pluto",
        "source_specific",
        "Source says conjunction is \"similar to square with strong Pluto\" "
        "(descriptive source relationship only; not catalog identity with "
        "square_Pluto; does not activate square strength branches; does not mark "
        "Pluto as calculated stronger).",
        "neutral",
        "resembles_square_pluto_stronger_source_relationship",
        source_reference=REF_PLUTO_CJ,
    ),
)

PLUTO_CONJUNCTION: tuple[SourceFactDef, ...] = (
    PLUTO_CONJUNCTION_UNIQUE
    + _build_pluto_common_body(
        factor_key="conjunction_Pluto",
        prefix="plu_cj",
        source_ref=REF_PLUTO_CJ,
    )
)

C14_ASPECT_PACKS: tuple[SourceFactDef, ...] = PLUTO_OPPOSITION + PLUTO_CONJUNCTION

C14_SUPPORTED_ASPECT_KEYS = frozenset({"opposition_Pluto", "conjunction_Pluto"})
