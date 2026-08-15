"""Mercury Source Profile v2 — Aspect Batch C9 (Moon opposition / conjunction).

C9 completes the Mercury–Moon public family with two DISTINCT packs:

- opposition_Moon
- conjunction_Moon

No aliases. Do NOT reuse sextile_Moon or square_Moon catalog facts.
Do NOT alias conjunction <-> opposition.
Do NOT merge the richer Bioastrology square Moon body into square_Moon
(that enrichment is a separate later batch).

Conjunction non-intellectual-work / \"frozen opposition\" branch uses:
intellectual_work_context_unresolved — no intellectual-work resolver.

Celebrity examples, secondary gain, compensation, and \"supergift\"
intentionally omitted (same C4–C8 precedent).

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


REF_MOON_OPP = "bioastrology_mercury_moon_opposition"
REF_MOON_CONJ = "bioastrology_mercury_moon_conjunction"
_INTELLECTUAL_WORK_UNRESOLVED = "intellectual_work_context_unresolved"


# ---------------------------------------------------------------------------
# Mercury opposition Moon — Bioastrology
# Canonical public catalog key: opposition_Moon
# Distinct from square_Moon, sextile_Moon, and conjunction_Moon.
# ---------------------------------------------------------------------------
MOON_OPPOSITION: tuple[SourceFactDef, ...] = (
    _f(
        "moon_opp_comfort_novelty_oscillation",
        "aspect",
        "opposition_Moon",
        "thinking",
        "Permanent oscillation between two poles: comfort / familiarity feels "
        "good but soon becomes boring / restless; novelty / variety / information "
        "feels interesting but also uncomfortable, frightening, or irritating.",
        "risk",
        "comfort_novelty_oscillation",
        source_reference=REF_MOON_OPP,
    ),
    _f(
        "moon_opp_source_lying_association",
        "aspect",
        "opposition_Moon",
        "source_specific",
        "The source associates this opposition with lying "
        "(source-described behavioral association; not a deterministic accusation "
        "that a person lies).",
        "risk",
        "source_lying_association",
        source_reference=REF_MOON_OPP,
    ),
    _f(
        "moon_opp_source_theft_association",
        "aspect",
        "opposition_Moon",
        "source_specific",
        "The source associates this opposition with theft "
        "(source-described behavioral association; not a crime prediction or "
        "deterministic accusation).",
        "risk",
        "source_theft_association",
        source_reference=REF_MOON_OPP,
    ),
    _f(
        "moon_opp_fussiness_restlessness",
        "aspect",
        "opposition_Moon",
        "thinking",
        "The source associates this opposition with fussiness / restlessness.",
        "risk",
        "fussiness_restlessness",
        source_reference=REF_MOON_OPP,
    ),
    _f(
        "moon_opp_novelty_old_irritation",
        "aspect",
        "opposition_Moon",
        "thinking",
        "Need for novelty combined with irritation toward what is old / familiar.",
        "risk",
        "novelty_old_irritation",
        source_reference=REF_MOON_OPP,
    ),
    _f(
        "moon_opp_directionless_brownian_activity",
        "aspect",
        "opposition_Moon",
        "thinking",
        "Constant Brownian-like movement \"nowhere\": activity / movement without "
        "a stable destination "
        "(not equated with multitasking).",
        "risk",
        "directionless_brownian_activity",
        source_reference=REF_MOON_OPP,
    ),
    _f(
        "moon_opp_intrusiveness",
        "aspect",
        "opposition_Moon",
        "communication",
        "Intrusiveness / importunity "
        "(not equated with generic communication skill).",
        "risk",
        "intrusiveness",
        source_reference=REF_MOON_OPP,
    ),
    _f(
        "moon_opp_goal_concentration_difficulty",
        "aspect",
        "opposition_Moon",
        "thinking",
        "Difficulty maintaining concentration on a goal "
        "(not equated with goal_setting_difficulty, planning, or forecasting).",
        "risk",
        "goal_concentration_difficulty",
        source_reference=REF_MOON_OPP,
    ),
    _f(
        "moon_opp_detail_stream_essence_loss",
        "aspect",
        "opposition_Moon",
        "thinking",
        "Excessive focus on details and a stream of small questions while missing "
        "the essence / central idea "
        "(not equated with analytical_thinking, technical_ability, or "
        "evidence_requirement).",
        "risk",
        "detail_stream_essence_loss",
        source_reference=REF_MOON_OPP,
    ),
    _f(
        "moon_opp_source_mother_strange_infantile_perception",
        "aspect",
        "opposition_Moon",
        "source_specific",
        "Source-described perception of the mother as strange / infantile / "
        "\"crazy\" in the source's language "
        "(native's / source-described perception; not an objective fact about the "
        "mother; not a diagnosis).",
        "risk",
        "source_mother_strange_infantile_perception",
        source_reference=REF_MOON_OPP,
    ),
    _f(
        "moon_opp_source_mother_split_perception",
        "aspect",
        "opposition_Moon",
        "source_specific",
        "Source-described perception of the mother as split into two different "
        "personas "
        "(native's / source-described perception; not an objective fact about the "
        "mother).",
        "risk",
        "source_mother_split_perception",
        source_reference=REF_MOON_OPP,
    ),
    _f(
        "moon_opp_source_mother_intellectual_overload_emotional_devaluation",
        "aspect",
        "opposition_Moon",
        "source_specific",
        "Source-described perception that the mother loads the native with "
        "facts / study while emotionally rejecting or devaluing "
        "(native's / source-described perception; not an objective fact about the "
        "mother).",
        "risk",
        "source_mother_intellectual_overload_emotional_devaluation",
        source_reference=REF_MOON_OPP,
    ),
    _f(
        "moon_opp_source_spouse_home_irritation",
        "aspect",
        "opposition_Moon",
        "source_specific",
        "The source associates this opposition with irritation toward wife / "
        "spouse and toward one's own place of residence "
        "(source-specific relationship / home context; does not infer marital "
        "status; not equated with generic partner conflict).",
        "risk",
        "source_spouse_home_irritation",
        source_reference=REF_MOON_OPP,
    ),
)


# ---------------------------------------------------------------------------
# Mercury conjunction Moon — Bioastrology
# Canonical public catalog key: conjunction_Moon
# Distinct from opposition_Moon, square_Moon, and sextile_Moon.
# ---------------------------------------------------------------------------
MOON_CONJUNCTION_RESOLVED: tuple[SourceFactDef, ...] = (
    _f(
        "moon_cj_source_corpus_callosum_analogy",
        "aspect",
        "conjunction_Moon",
        "source_specific",
        "Source analogy: Moon–Mercury conjunction is compared to the corpus "
        "callosum connecting right and left cerebral hemispheres "
        "(source metaphor / analogy only; not a medical or neuroscientific "
        "diagnosis).",
        "neutral",
        "source_corpus_callosum_analogy",
        source_reference=REF_MOON_CONJ,
    ),
    _f(
        "moon_cj_neutral_aspect_source_classification",
        "aspect",
        "conjunction_Moon",
        "source_specific",
        "Source classifies this conjunction as neutral "
        "(source classification; not translated into \"good\" or \"bad\").",
        "neutral",
        "neutral_aspect_source_classification",
        source_reference=REF_MOON_CONJ,
    ),
    _f(
        "moon_cj_feelings_expressed_through_chatter",
        "aspect",
        "conjunction_Moon",
        "communication",
        "Feelings are expressed through chatter / talking.",
        "neutral",
        "feelings_expressed_through_chatter",
        source_reference=REF_MOON_CONJ,
    ),
    _f(
        "moon_cj_feelings_expressed_through_friendship",
        "aspect",
        "conjunction_Moon",
        "communication",
        "Feelings are expressed through friendship.",
        "neutral",
        "feelings_expressed_through_friendship",
        source_reference=REF_MOON_CONJ,
    ),
    _f(
        "moon_cj_feelings_expressed_through_trips",
        "aspect",
        "conjunction_Moon",
        "mobility",
        "Feelings are expressed through trips / movement "
        "(not equated with generic trips relevance from harmonious Moon).",
        "neutral",
        "feelings_expressed_through_trips",
        source_reference=REF_MOON_CONJ,
    ),
    _f(
        "moon_cj_psychological_right_hemisphere_learning_context",
        "aspect",
        "conjunction_Moon",
        "source_specific",
        "Learning / intellectual function works through psychological, "
        "right-hemisphere / feminine dynamics in the source wording "
        "(source-specific framing; not a diagnosis, not a gender-identity claim, "
        "not lower intelligence, not equated with intuition).",
        "neutral",
        "psychological_right_hemisphere_learning_context",
        source_reference=REF_MOON_CONJ,
    ),
    _f(
        "moon_cj_writing_ability",
        "aspect",
        "conjunction_Moon",
        "communication",
        "Writing abilities.",
        "strength",
        "writing",
        source_reference=REF_MOON_CONJ,
    ),
    _f(
        "moon_cj_poetic_ability",
        "aspect",
        "conjunction_Moon",
        "communication",
        "Poetic abilities.",
        "strength",
        "poetic_ability",
        source_reference=REF_MOON_CONJ,
    ),
    _f(
        "moon_cj_strong_sticky_memory",
        "aspect",
        "conjunction_Moon",
        "memory",
        "Sticky / strong memory.",
        "strength",
        "strong_memory",
        source_reference=REF_MOON_CONJ,
    ),
    _f(
        "moon_cj_softer_melodic_speech",
        "aspect",
        "conjunction_Moon",
        "communication",
        "Softer / melodic oral speech.",
        "strength",
        "soft_speech",
        source_reference=REF_MOON_CONJ,
    ),
    _f(
        "moon_cj_dexterity",
        "aspect",
        "conjunction_Moon",
        "work_application",
        "Dexterity.",
        "strength",
        "dexterity",
        source_reference=REF_MOON_CONJ,
    ),
)

MOON_CONJUNCTION_UNRESOLVED: tuple[SourceFactDef, ...] = (
    _f(
        "moon_cj_branch_non_intellectual_work_frozen_opposition",
        "aspect",
        "conjunction_Moon",
        "source_specific",
        "If the person is not engaged in substantial intellectual work, the "
        "source says the conjunction may bring more problems than benefits and "
        "may resemble an opposition \"frozen in time\": tension exists, but "
        "unlike opposition there is no oscillation between two poles "
        "(source relationship / context note; unresolved because intellectual-work "
        "context is not resolved by the current profile; no IQ, education, "
        "profession, or hiring inference; does not activate opposition_Moon).",
        "conditional",
        "frozen_opposition_without_oscillation",
        source_reference=REF_MOON_CONJ,
        activation_condition=_INTELLECTUAL_WORK_UNRESOLVED,
        unresolved=True,
    ),
)

MOON_CONJUNCTION: tuple[SourceFactDef, ...] = (
    MOON_CONJUNCTION_RESOLVED + MOON_CONJUNCTION_UNRESOLVED
)

C9_ASPECT_PACKS: tuple[SourceFactDef, ...] = MOON_OPPOSITION + MOON_CONJUNCTION

C9_SUPPORTED_ASPECT_KEYS = frozenset({"opposition_Moon", "conjunction_Moon"})
