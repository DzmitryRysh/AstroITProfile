"""Mercury Source Profile v2 — Aspect Batch C13 (Neptune reachable family).

C13 completes all five reachable natal Mercury–Neptune major aspects:

- trine_Neptune (canonical harmonious body)
- sextile_Neptune -> trine_Neptune (source-justified alias: combined trine/sextile)
- square_Neptune
- opposition_Neptune
- conjunction_Neptune

Do NOT alias opposition/conjunction to square.
Do NOT treat conjunction \"resembles square with Neptune stronger\" as catalog identity.

Square strength branches use existing strength_unresolved.
Diction/pronunciation under multiple affliction uses:
multiple_affliction_context_unresolved

Genealogy, celebrity examples, secondary gain, compensation, and \"supergift\"
intentionally omitted.

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


REF_NEPTUNE_HARM = "bioastrology_mercury_neptune_harmonious"
REF_NEPTUNE_SQ = "bioastrology_mercury_neptune_square"
REF_NEPTUNE_OPP = "bioastrology_mercury_neptune_opposition"
REF_NEPTUNE_CJ = "bioastrology_mercury_neptune_conjunction"
_STRENGTH_UNRESOLVED = "strength_unresolved"
_MULTIPLE_AFFLICTION_UNRESOLVED = "multiple_affliction_context_unresolved"


def _tense_common_body(
    factor_key: str,
    id_prefix: str,
    source_reference: str,
) -> tuple[SourceFactDef, ...]:
    """Shared tense Mercury–Neptune body for square / opposition / conjunction."""
    return (
        _f(
            f"{id_prefix}_distractibility",
            "aspect",
            factor_key,
            "thinking",
            "Distractibility "
            "(source-described tendency; not a medical attention diagnosis).",
            "risk",
            "distractibility",
            source_reference=source_reference,
        ),
        _f(
            f"{id_prefix}_memory_problems",
            "aspect",
            factor_key,
            "memory",
            "Memory problems "
            "(source-described tendency; not a neurological disorder claim).",
            "risk",
            "source_memory_problems",
            source_reference=source_reference,
        ),
        _f(
            f"{id_prefix}_difficulty_routine_work",
            "aspect",
            factor_key,
            "work_application",
            "Difficulty performing routine work.",
            "risk",
            "difficulty_routine_work",
            source_reference=source_reference,
        ),
        _f(
            f"{id_prefix}_difficulty_learning_simple_from_books",
            "aspect",
            factor_key,
            "learning",
            "Difficulty learning simple / basic things from books.",
            "risk",
            "difficulty_learning_simple_from_books",
            source_reference=source_reference,
        ),
        _f(
            f"{id_prefix}_mystifies_simple_obvious_matters",
            "aspect",
            factor_key,
            "thinking",
            "Tendency to make simple matters confusing by mystifying the obvious.",
            "risk",
            "mystifies_simple_obvious_matters",
            source_reference=source_reference,
        ),
        _f(
            f"{id_prefix}_relative_ease_with_complex_material",
            "aspect",
            factor_key,
            "learning",
            "Source describes a contrast: basic / routine learning may be difficult "
            "while complex material may be grasped more easily "
            "(source-described learning pattern; not an IQ measurement, genius claim, "
            "or hiring competence conclusion).",
            "neutral",
            "relative_ease_with_complex_material",
            source_reference=source_reference,
        ),
        _f(
            f"{id_prefix}_learns_via_stories_video_solitude",
            "aspect",
            factor_key,
            "learning",
            "Preference / ease of learning through stories and video in solitude.",
            "neutral",
            "learns_via_stories_video_solitude",
            source_reference=source_reference,
        ),
        _f(
            f"{id_prefix}_branch_multiple_affliction_diction_pronunciation",
            "aspect",
            factor_key,
            "communication",
            "If under multiple affliction, the source associates diction / "
            "pronunciation problems "
            "(source-described conditional; unresolved; not a speech-disorder "
            "diagnosis; multiple affliction is not calculated).",
            "conditional",
            "source_diction_pronunciation_multiple_affliction",
            source_reference=source_reference,
            activation_condition=_MULTIPLE_AFFLICTION_UNRESOLVED,
            unresolved=True,
        ),
        _f(
            f"{id_prefix}_source_theft_risk_association",
            "aspect",
            factor_key,
            "source_specific",
            "Source associates this Mercury–Neptune pattern with theft risk "
            "(source-described association; not a deterministic accusation that "
            "a person steals; not a crime prediction).",
            "conditional",
            "source_theft_risk_association",
            source_reference=source_reference,
        ),
        _f(
            f"{id_prefix}_source_road_accident_risk_association",
            "aspect",
            factor_key,
            "source_specific",
            "Source associates this Mercury–Neptune pattern with road-accident risk "
            "(source-described association; not a prediction of an accident; not "
            "driving_ability or driving-fitness judgment).",
            "conditional",
            "source_road_accident_risk_association",
            source_reference=source_reference,
        ),
        _f(
            f"{id_prefix}_source_plagiarism_association",
            "aspect",
            factor_key,
            "source_specific",
            "Source associates the pattern with plagiarism, including potentially "
            "unintentional plagiarism "
            "(source-described association; not an accusation that the native "
            "plagiarizes).",
            "conditional",
            "source_plagiarism_association",
            source_reference=source_reference,
        ),
        _f(
            f"{id_prefix}_source_female_logic_label",
            "aspect",
            factor_key,
            "source_specific",
            "Source uses the label \"female logic\" for this pattern "
            "(source wording only; not a claim about women, gender, or gendered "
            "cognition).",
            "neutral",
            "source_female_logic_label",
            source_reference=source_reference,
        ),
        _f(
            f"{id_prefix}_thinking_doubt_tendency",
            "aspect",
            factor_key,
            "thinking",
            "Tendency toward doubt while thinking.",
            "risk",
            "thinking_doubt_tendency",
            source_reference=source_reference,
        ),
        _f(
            f"{id_prefix}_speech_complicating",
            "aspect",
            factor_key,
            "communication",
            "Speech tendency to complicate.",
            "risk",
            "speech_complicating",
            source_reference=source_reference,
        ),
        _f(
            f"{id_prefix}_speech_confusing",
            "aspect",
            factor_key,
            "communication",
            "Speech tendency to confuse.",
            "risk",
            "speech_confusing",
            source_reference=source_reference,
        ),
        _f(
            f"{id_prefix}_source_lying_distortion_association",
            "aspect",
            factor_key,
            "source_specific",
            "Source associates speech with lying / distortion "
            "(source-described communication tendency/association; not a "
            "deterministic accusation that a person lies).",
            "conditional",
            "source_lying_distortion_association",
            source_reference=source_reference,
        ),
    )


# ---------------------------------------------------------------------------
# Mercury trine/sextile Neptune — Bioastrology harmonious
# Canonical: trine_Neptune
# Alias: sextile_Neptune -> trine_Neptune
# ---------------------------------------------------------------------------
NEPTUNE_HARMONIOUS: tuple[SourceFactDef, ...] = (
    _f(
        "nep_harm_communication_learning_imagination_integration",
        "aspect",
        "trine_Neptune",
        "thinking",
        "Communication and learning integrate smoothly / harmoniously with "
        "imagination / subtle intuitive perception.",
        "strength",
        "communication_learning_imagination_integration",
        source_reference=REF_NEPTUNE_HARM,
    ),
    _f(
        "nep_harm_literary_talent",
        "aspect",
        "trine_Neptune",
        "communication",
        "Literary talent "
        "(not equated with generic writing ability).",
        "strength",
        "literary_talent",
        source_reference=REF_NEPTUNE_HARM,
    ),
    _f(
        "nep_harm_excellent_memory",
        "aspect",
        "trine_Neptune",
        "memory",
        "Excellent memory.",
        "strength",
        "strong_memory",
        source_reference=REF_NEPTUNE_HARM,
    ),
    _f(
        "nep_harm_foreign_languages",
        "aspect",
        "trine_Neptune",
        "learning",
        "Inclination / talent for foreign languages.",
        "strength",
        "foreign_languages",
        source_reference=REF_NEPTUNE_HARM,
    ),
    _f(
        "nep_harm_source_right_hemisphere_development",
        "aspect",
        "trine_Neptune",
        "source_specific",
        "Source describes strongly developed \"right hemisphere\" "
        "(source terminology; not a neuroscience diagnosis or validated "
        "cognitive measurement).",
        "neutral",
        "source_right_hemisphere_development",
        source_reference=REF_NEPTUNE_HARM,
    ),
    _f(
        "nep_harm_intuition",
        "aspect",
        "trine_Neptune",
        "thinking",
        "Intuition.",
        "strength",
        "intuition",
        source_reference=REF_NEPTUNE_HARM,
    ),
    _f(
        "nep_harm_read_between_the_lines",
        "aspect",
        "trine_Neptune",
        "thinking",
        "Ability to read between the lines.",
        "strength",
        "read_between_the_lines",
        source_reference=REF_NEPTUNE_HARM,
    ),
    _f(
        "nep_harm_source_nlp_aptitude",
        "aspect",
        "trine_Neptune",
        "source_specific",
        "NLP aptitude "
        "(source-described aptitude; not a certified NLP credential, not a "
        "manipulation diagnosis, and not a hiring competency).",
        "neutral",
        "source_nlp_aptitude",
        source_reference=REF_NEPTUNE_HARM,
    ),
    _f(
        "nep_harm_source_hypnotic_aptitude",
        "aspect",
        "trine_Neptune",
        "source_specific",
        "Hypnosis aptitude "
        "(source-described aptitude; not a clinical hypnosis credential).",
        "neutral",
        "source_hypnotic_aptitude",
        source_reference=REF_NEPTUNE_HARM,
    ),
    _f(
        "nep_harm_source_psychological_aptitude",
        "aspect",
        "trine_Neptune",
        "source_specific",
        "Psychological aptitude "
        "(source-described aptitude; not a licensed psychology credential).",
        "neutral",
        "source_psychological_aptitude",
        source_reference=REF_NEPTUNE_HARM,
    ),
    _f(
        "nep_harm_source_extrasensory_aptitude",
        "aspect",
        "trine_Neptune",
        "source_specific",
        "Extrasensory aptitude "
        "(source-described aptitude; not equated with claircognizance, "
        "intuition, or insight automatically).",
        "neutral",
        "source_extrasensory_aptitude",
        source_reference=REF_NEPTUNE_HARM,
    ),
)


# ---------------------------------------------------------------------------
# Mercury square Neptune — Bioastrology
# Canonical: square_Neptune
# ---------------------------------------------------------------------------
NEPTUNE_SQUARE_COMMON: tuple[SourceFactDef, ...] = (
    _f(
        "nep_sq_communication_learning_vs_imagination_conflict",
        "aspect",
        "square_Neptune",
        "thinking",
        "Communication / learning openly conflicts with mythology, imagination "
        "and subtle intuitive perception.",
        "risk",
        "communication_learning_vs_imagination_conflict",
        source_reference=REF_NEPTUNE_SQ,
    ),
) + _tense_common_body("square_Neptune", "nep_sq", REF_NEPTUNE_SQ)

NEPTUNE_SQUARE_MERCURY_STRONGER: tuple[SourceFactDef, ...] = (
    _f(
        "nep_sq_branch_mercury_atomistic_overrides_holistic",
        "aspect",
        "square_Neptune",
        "thinking",
        "If Mercury is stronger, atomistic / reductionist thinking overrides "
        "holistic perception (unresolved; no strength resolver).",
        "conditional",
        "atomistic_overrides_holistic",
        source_reference=REF_NEPTUNE_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "nep_sq_branch_mercury_dry_emotionally_callous_thinking",
        "aspect",
        "square_Neptune",
        "thinking",
        "If Mercury is stronger, dry / emotionally callous thinking style "
        "(unresolved; no strength resolver).",
        "conditional",
        "dry_emotionally_callous_thinking",
        source_reference=REF_NEPTUNE_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "nep_sq_branch_mercury_blind_thinking_source_framing",
        "aspect",
        "square_Neptune",
        "thinking",
        "If Mercury is stronger, \"blind\" thinking in the source's framing "
        "(unresolved; no strength resolver).",
        "conditional",
        "blind_thinking_source_framing",
        source_reference=REF_NEPTUNE_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "nep_sq_branch_mercury_strange_speech_inconsistency",
        "aspect",
        "square_Neptune",
        "communication",
        "If Mercury is stronger, strange inconsistency in speech "
        "(unresolved; no strength resolver).",
        "conditional",
        "strange_speech_inconsistency",
        source_reference=REF_NEPTUNE_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "nep_sq_branch_mercury_lack_of_depth_zest",
        "aspect",
        "square_Neptune",
        "thinking",
        "If Mercury is stronger, lack of depth / \"zest\" "
        "(unresolved; no strength resolver).",
        "conditional",
        "lack_of_depth_zest",
        source_reference=REF_NEPTUNE_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "nep_sq_branch_mercury_thinking_too_primitive_superficial",
        "aspect",
        "square_Neptune",
        "thinking",
        "If Mercury is stronger, thinking may become too primitive / superficial "
        "in the source's framing (unresolved; no strength resolver).",
        "conditional",
        "thinking_too_primitive_superficial",
        source_reference=REF_NEPTUNE_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
)

NEPTUNE_SQUARE_NEPTUNE_STRONGER: tuple[SourceFactDef, ...] = (
    _f(
        "nep_sq_branch_neptune_holistic_overrides_atomistic",
        "aspect",
        "square_Neptune",
        "thinking",
        "If Neptune is stronger, holistic perception overrides atomistic / "
        "reductionist thinking (unresolved; no strength resolver).",
        "conditional",
        "holistic_overrides_atomistic",
        source_reference=REF_NEPTUNE_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "nep_sq_branch_neptune_soulful_speech",
        "aspect",
        "square_Neptune",
        "communication",
        "If Neptune is stronger, soulful speech "
        "(unresolved; no strength resolver).",
        "conditional",
        "soulful_speech",
        source_reference=REF_NEPTUNE_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "nep_sq_branch_neptune_musical_speech",
        "aspect",
        "square_Neptune",
        "communication",
        "If Neptune is stronger, musical speech "
        "(unresolved; not equated with beautiful_speech; no strength resolver).",
        "conditional",
        "musical_speech",
        source_reference=REF_NEPTUNE_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "nep_sq_branch_neptune_engaging_storyteller_speech",
        "aspect",
        "square_Neptune",
        "communication",
        "If Neptune is stronger, engaging storyteller speech "
        "(unresolved; not equated with persuasion; no strength resolver).",
        "conditional",
        "engaging_storyteller_speech",
        source_reference=REF_NEPTUNE_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "nep_sq_branch_neptune_speech_lacks_details",
        "aspect",
        "square_Neptune",
        "communication",
        "If Neptune is stronger, speech may lack details "
        "(unresolved; no strength resolver).",
        "conditional",
        "speech_lacks_details",
        source_reference=REF_NEPTUNE_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "nep_sq_branch_neptune_speech_lacks_consistency",
        "aspect",
        "square_Neptune",
        "communication",
        "If Neptune is stronger, speech may lack consistency "
        "(unresolved; no strength resolver).",
        "conditional",
        "speech_lacks_consistency",
        source_reference=REF_NEPTUNE_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "nep_sq_branch_neptune_speech_lacks_oratorical_elegance",
        "aspect",
        "square_Neptune",
        "communication",
        "If Neptune is stronger, speech may lack oratorical elegance "
        "(unresolved; no strength resolver).",
        "conditional",
        "speech_lacks_oratorical_elegance",
        source_reference=REF_NEPTUNE_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "nep_sq_branch_neptune_unusually_deep_voluminous_thinking",
        "aspect",
        "square_Neptune",
        "thinking",
        "If Neptune is stronger, thinking described by source as unusually deep / "
        "voluminous (unresolved; not equated with analytical_thinking; no "
        "strength resolver).",
        "conditional",
        "unusually_deep_voluminous_thinking",
        source_reference=REF_NEPTUNE_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
    _f(
        "nep_sq_branch_neptune_many_vivid_mental_images",
        "aspect",
        "square_Neptune",
        "thinking",
        "If Neptune is stronger, many vivid mental images "
        "(unresolved; not equated with insight; no strength resolver).",
        "conditional",
        "many_vivid_mental_images",
        source_reference=REF_NEPTUNE_SQ,
        activation_condition=_STRENGTH_UNRESOLVED,
        unresolved=True,
    ),
)

NEPTUNE_SQUARE: tuple[SourceFactDef, ...] = (
    NEPTUNE_SQUARE_COMMON
    + NEPTUNE_SQUARE_MERCURY_STRONGER
    + NEPTUNE_SQUARE_NEPTUNE_STRONGER
)


# ---------------------------------------------------------------------------
# Mercury opposition Neptune — Bioastrology
# Canonical: opposition_Neptune — distinct from square
# ---------------------------------------------------------------------------
NEPTUNE_OPPOSITION_UNIQUE: tuple[SourceFactDef, ...] = (
    _f(
        "nep_opp_cold_war_communication_learning_vs_imagination",
        "aspect",
        "opposition_Neptune",
        "thinking",
        "Communication / learning is in a \"cold war\" with mythology, "
        "imagination and subtle intuitive perception.",
        "risk",
        "cold_war_communication_learning_vs_imagination",
        source_reference=REF_NEPTUNE_OPP,
    ),
    _f(
        "nep_opp_oscillation_all_knowing_vs_mass_of_facts",
        "aspect",
        "opposition_Neptune",
        "thinking",
        "Oscillation between feeling naturally all-knowing / wise and getting "
        "buried in a mass of facts.",
        "risk",
        "oscillation_all_knowing_vs_mass_of_facts",
        source_reference=REF_NEPTUNE_OPP,
    ),
    _f(
        "nep_opp_creator_researcher_vs_plagiarist_imitator_polarity",
        "aspect",
        "opposition_Neptune",
        "source_specific",
        "Source polarity: at one end creator / researcher, at the other "
        "plagiarist / imitator who knows a little about many things but lacks "
        "depth of competence "
        "(source-described polarity; not a factual judgment of the user's "
        "competence; not a hiring / work-fitness conclusion).",
        "conditional",
        "source_creator_researcher_vs_plagiarist_imitator_polarity",
        source_reference=REF_NEPTUNE_OPP,
    ),
)

NEPTUNE_OPPOSITION: tuple[SourceFactDef, ...] = (
    NEPTUNE_OPPOSITION_UNIQUE + _tense_common_body("opposition_Neptune", "nep_opp", REF_NEPTUNE_OPP)
)


# ---------------------------------------------------------------------------
# Mercury conjunction Neptune — Bioastrology
# Canonical: conjunction_Neptune — distinct from square (no catalog reuse)
# ---------------------------------------------------------------------------
NEPTUNE_CONJUNCTION_UNIQUE: tuple[SourceFactDef, ...] = (
    _f(
        "nep_cj_absorbed_by_intuitive_understanding",
        "aspect",
        "conjunction_Neptune",
        "thinking",
        "Communication and learning are described as being absorbed by intuitive "
        "understanding / deep intuitive penetration.",
        "neutral",
        "absorbed_by_intuitive_understanding",
        source_reference=REF_NEPTUNE_CJ,
    ),
    _f(
        "nep_cj_source_resembles_square_neptune_stronger",
        "aspect",
        "conjunction_Neptune",
        "source_specific",
        "Source says conjunction resembles the square with Neptune stronger "
        "(descriptive source relationship only; not catalog identity with "
        "square_Neptune; does not mark Neptune as calculated stronger).",
        "neutral",
        "source_resembles_square_neptune_stronger",
        source_reference=REF_NEPTUNE_CJ,
    ),
)

NEPTUNE_CONJUNCTION: tuple[SourceFactDef, ...] = (
    NEPTUNE_CONJUNCTION_UNIQUE
    + _tense_common_body("conjunction_Neptune", "nep_cj", REF_NEPTUNE_CJ)
)

C13_ASPECT_PACKS: tuple[SourceFactDef, ...] = (
    NEPTUNE_HARMONIOUS + NEPTUNE_SQUARE + NEPTUNE_OPPOSITION + NEPTUNE_CONJUNCTION
)

C13_SUPPORTED_ASPECT_KEYS = frozenset(
    {
        "trine_Neptune",
        "sextile_Neptune",
        "square_Neptune",
        "opposition_Neptune",
        "conjunction_Neptune",
    }
)
