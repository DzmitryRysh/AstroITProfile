"""Mercury Source Profile v2 — House Batch B2.

House 5 has Lesson 7 + Bioastrology (dual-source parity).
Houses 6 and 7 remain Lesson 7 only until their Bioastrology passes.

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


REF_H5_L7 = "lesson7_mercury_house_5"
REF_H5_BIO = "bioastrology_mercury_house_5"
REF_H6_L7 = "lesson7_mercury_house_6"
REF_H7_L7 = "lesson7_mercury_house_7"

# ---------------------------------------------------------------------------
# Mercury in House 5 — Lesson 7
# ---------------------------------------------------------------------------
HOUSE_5: tuple[SourceFactDef, ...] = (
    _f("h5_creativity_connected_with_intellectual_work", "house", "5", "thinking",
       "Creativity connected with intellectual / mental work.",
       "strength", "intellectual_creativity",
       source_reference=REF_H5_L7),
    _f("h5_creativity_connected_with_writing", "house", "5", "communication",
       "Creativity connected with writing.",
       "strength", "writing_based_creativity",
       source_reference=REF_H5_L7),
    _f("h5_creativity_connected_with_speech", "house", "5", "communication",
       "Creativity connected with speech.",
       "strength", "speech_based_creativity",
       source_reference=REF_H5_L7),
    _f("h5_romantic_beautiful_speech", "house", "5", "communication",
       "To make someone fall in love, one needs to speak beautifully "
       "(source-described romantic communication).",
       "neutral", "romantic_beautiful_speech",
       source_reference=REF_H5_L7),
    _f("h5_pleasure_from_studying", "house", "5", "learning",
       "Pleasure from studying / learning.",
       "strength", "learning_enjoyment",
       source_reference=REF_H5_L7),
    _f("h5_pleasure_from_books", "house", "5", "learning",
       "Pleasure from books.",
       "neutral", "book_enjoyment",
       source_reference=REF_H5_L7),
    _f("h5_entertainment_under_control_of_mind", "house", "5", "environment",
       "Entertainment remains under control of the mind.",
       "neutral", "mental_control_of_entertainment",
       source_reference=REF_H5_L7),
    _f("h5_rational_element_in_celebration", "house", "5", "environment",
       "Rational element exists in celebration / fun.",
       "neutral", "rationalized_entertainment",
       source_reference=REF_H5_L7),
    _f("h5_acquaintance_context_associations", "house", "5", "source_specific",
       "Source associates acquaintances with celebrations, theaters, cinema, shopping, "
       "and events; contextual associations, not personality skills.",
       "neutral", "acquaintance_context_associations",
       source_reference=REF_H5_L7),
    _f("h5_circumstances_public_speaking", "house", "5", "communication",
       "Circumstances make the native tell / speak about something publicly.",
       "neutral", "public_speaking_circumstance",
       source_reference=REF_H5_L7),
    _f("h5_occupation_associations", "house", "5", "source_specific",
       "Source-described occupation associations include art critic, teacher, advertiser, "
       "creative professional, and marketer; not career assignments.",
       "neutral", "occupation_associations",
       source_reference=REF_H5_L7),
    _f("h5_rationalism_in_love", "house", "5", "risk",
       "Rationalism in love.",
       "risk", "rationalism_in_love",
       source_reference=REF_H5_L7),
    _f("h5_cold_analysis_of_feelings", "house", "5", "risk",
       "Tendency to subject feelings to cold analysis.",
       "risk", "cold_analysis_of_feelings",
       source_reference=REF_H5_L7),
    _f("h5_romantic_talk_displaces_feelings", "house", "5", "risk",
       "Romantic topics in conversation can displace the feelings themselves.",
       "risk", "romantic_talk_displaces_feelings",
       source_reference=REF_H5_L7),
)

# ---------------------------------------------------------------------------
# Mercury in House 5 — Bioastrology (dual-source parity; HOUSE_5 L7 is frozen)
# ---------------------------------------------------------------------------
HOUSE_5_BIO: tuple[SourceFactDef, ...] = (
    _f("h5_bio_mercury_qualities_colored_by_children", "house", "5",
       "source_specific",
       "Mercury-related qualities may be colored by themes involving children.",
       "neutral",
       source_reference=REF_H5_BIO),
    _f("h5_bio_mercury_qualities_colored_by_creativity", "house", "5",
       "source_specific",
       "Mercury-related qualities may be colored by creative themes.",
       "neutral",
       source_reference=REF_H5_BIO),
    _f("h5_bio_mercury_qualities_colored_by_risk", "house", "5",
       "source_specific",
       "Mercury-related qualities may be colored by themes involving risk.",
       "neutral",
       source_reference=REF_H5_BIO),
    _f("h5_bio_entrepreneurial_qualities", "house", "5", "work_application",
       "May support entrepreneurial qualities.",
       "strength",
       source_reference=REF_H5_BIO),
    _f("h5_bio_sales_qualities", "house", "5", "work_application",
       "May support qualities associated with sales.",
       "strength", "sales",
       source_reference=REF_H5_BIO),
    _f("h5_bio_gift_for_writing", "house", "5", "communication",
       "May support a gift for writing.",
       "strength",
       source_reference=REF_H5_BIO),
    _f("h5_bio_books_as_hobby", "house", "5", "learning",
       "Books may be a prominent hobby interest.",
       "neutral",
       source_reference=REF_H5_BIO),
    _f("h5_bio_trips_as_hobby", "house", "5", "mobility",
       "Trips may be a prominent hobby interest.",
       "neutral",
       source_reference=REF_H5_BIO),
    _f("h5_bio_learning_as_hobby", "house", "5", "learning",
       "Learning may be a prominent hobby interest.",
       "neutral",
       source_reference=REF_H5_BIO),
    _f("h5_bio_favorable_acquaintances", "house", "5", "environment",
       "Favorable association with acquaintances.",
       "strength",
       source_reference=REF_H5_BIO),
    _f("h5_bio_parallel_romances", "house", "5", "source_specific",
       "There may be parallel romantic relationships.",
       "neutral",
       source_reference=REF_H5_BIO),
    _f("h5_bio_twins_association", "house", "5", "source_specific",
       "There may be an association with twins.",
       "neutral",
       source_reference=REF_H5_BIO),
    _f("h5_bio_multiple_children_association", "house", "5", "source_specific",
       "There may be an association with multiple children.",
       "neutral",
       source_reference=REF_H5_BIO),
)

# ---------------------------------------------------------------------------
# Mercury in House 6 — Lesson 7
# ---------------------------------------------------------------------------
HOUSE_6: tuple[SourceFactDef, ...] = (
    _f("h6_duties_performed_diligently", "house", "6", "work_application",
       "Duties are performed diligently.",
       "strength", "diligent_duty_execution",
       source_reference=REF_H6_L7),
    _f("h6_duties_performed_methodically", "house", "6", "work_application",
       "Duties are performed methodically.",
       "strength", "methodical_duty_execution",
       source_reference=REF_H6_L7),
    _f("h6_duties_performed_intelligently", "house", "6", "work_application",
       "Duties are performed intelligently.",
       "strength", "intelligent_duty_execution",
       source_reference=REF_H6_L7),
    _f("h6_duties_performed_rationally", "house", "6", "work_application",
       "Duties are performed rationally.",
       "strength", "rational_duty_execution",
       source_reference=REF_H6_L7),
    _f("h6_active_use_of_professional_contacts", "house", "6", "work_application",
       "Active use of connections / contacts in professional activity.",
       "strength", "professional_contact_use",
       source_reference=REF_H6_L7),
    _f("h6_work_involves_travel_or_moving", "house", "6", "mobility",
       "Work may involve a lot of travel / moving around.",
       "neutral", "work_travel",
       source_reference=REF_H6_L7),
    _f("h6_work_involves_processing_lots_of_information", "house", "6", "work_application",
       "Work may involve processing a lot of information.",
       "neutral", "high_information_workload",
       source_reference=REF_H6_L7),
    _f("h6_several_side_jobs", "house", "6", "work_application",
       "Several side jobs / multiple additional jobs.",
       "neutral", "multiple_side_jobs",
       source_reference=REF_H6_L7),
    _f("h6_occupation_associations", "house", "6", "source_specific",
       "Source-described occupation associations include consultant, dietitian, healer, "
       "doctor, communications worker, seller, journalist, commentator, and laboratory "
       "research; not career assignments.",
       "neutral", "occupation_associations",
       source_reference=REF_H6_L7),
    _f("h6_tendency_to_grab_several_tasks_at_once", "house", "6", "risk",
       "Tendency to grab several tasks at once (source-described risk of scattering "
       "across tasks, not positive multitasking).",
       "risk", "multiple_tasks_at_once_risk",
       source_reference=REF_H6_L7),
    _f("h6_preoccupation_with_small_matters", "house", "6", "risk",
       "Preoccupation with small matters.",
       "risk", "small_problem_preoccupation",
       source_reference=REF_H6_L7),
    _f("h6_may_invent_small_problems", "house", "6", "risk",
       "If small problems do not exist, the native may invent / create them.",
       "risk", "inventing_small_problems",
       source_reference=REF_H6_L7),
    _f("h6_dev_resolve_problem_decisively", "house", "6", "work_application",
       "Development focus: solve the problem quickly and permanently.",
       "neutral", "resolve_problem_decisively",
       source_reference=REF_H6_L7),
    _f("h6_dev_ignore_minor_problems", "house", "6", "work_application",
       "Development focus: ignore small problems.",
       "neutral", "ignore_minor_problems",
       source_reference=REF_H6_L7),
)

# ---------------------------------------------------------------------------
# Mercury in House 7 — Lesson 7
# ---------------------------------------------------------------------------
HOUSE_7: tuple[SourceFactDef, ...] = (
    _f("h7_many_contacts", "house", "7", "environment",
       "Many contacts.",
       "neutral", "many_contacts",
       source_reference=REF_H7_L7),
    _f("h7_conversation_partner_can_be_found", "house", "7", "communication",
       "In any circumstances a conversational partner can be found.",
       "strength", "conversation_partner_availability",
       source_reference=REF_H7_L7),
    _f("h7_master_of_dialogue", "house", "7", "communication",
       "Circumstances make the native a master of dialogue.",
       "strength", "dialogue_skill",
       source_reference=REF_H7_L7),
    _f("h7_master_of_compromise", "house", "7", "communication",
       "Circumstances make the native a master of compromise.",
       "strength", "compromise_skill",
       source_reference=REF_H7_L7),
    _f("h7_partner_may_be_communicative", "house", "7", "source_specific",
       "Source associates the partner with being communicative "
       "(partner association, not a native ability claim).",
       "neutral", "partner_communicative_association",
       source_reference=REF_H7_L7),
    _f("h7_partner_from_intellectual_profession", "house", "7", "source_specific",
       "Source associates the partner with an intellectual profession "
       "(partner association, not a native ability claim).",
       "neutral", "partner_intellectual_profession_association",
       source_reference=REF_H7_L7),
    _f("h7_partner_often_younger", "house", "7", "source_specific",
       "Source associates the partner with often being younger "
       "(partner association, not a native ability claim).",
       "neutral", "partner_often_younger_association",
       source_reference=REF_H7_L7),
    _f("h7_shared_topics_important_with_partner", "house", "7", "environment",
       "With a partner it is important to have shared topics.",
       "neutral", "shared_topics_in_partnership",
       source_reference=REF_H7_L7),
    _f("h7_intellectual_interest_important_with_partner", "house", "7", "environment",
       "With a partner it is important to have intellectual interest.",
       "neutral", "intellectual_interest_in_partnership",
       source_reference=REF_H7_L7),
    _f("h7_calculation_can_dominate_feelings_in_marriage", "house", "7", "risk",
       "Calculation / rationality can dominate feelings in marriage.",
       "risk", "calculation_dominates_feelings_in_marriage",
       source_reference=REF_H7_L7),
    _f("h7_relationships_built_more_on_reason", "house", "7", "risk",
       "Relationships may be built more on reason.",
       "risk", "relationships_built_on_reason",
       source_reference=REF_H7_L7),
    _f("h7_partner_intellectual_expectation_mutable_dependency", "house", "7", "source_specific",
       "If the partner does not meet intellectual expectations, marriage may be unstable; "
       "source especially notes this for mutable Mercury "
       "(mutable-Mercury dependency; no modality resolver is applied; not hard_aspected).",
       "conditional", "partner_intellectual_expectation_mutable_dependency",
       source_reference=REF_H7_L7, unresolved=True),
    _f("h7_possible_fictitious_formal_paper_marriage", "house", "7", "source_specific",
       "Possible fictitious / formal / paper marriage "
       "(source-described possible relationship scenario, not an accusation).",
       "neutral", "formal_paper_marriage_scenario",
       source_reference=REF_H7_L7),
    _f("h7_partner_may_be_two_faced", "house", "7", "source_specific",
       "Source says the partner may be two-faced "
       "(partner association, not a native character claim).",
       "risk", "partner_two_faced_association",
       source_reference=REF_H7_L7),
    _f("h7_partner_may_be_lying", "house", "7", "source_specific",
       "Source says the partner may be lying "
       "(partner association, not a native character claim).",
       "risk", "partner_lying_association",
       source_reference=REF_H7_L7),
    _f("h7_partner_argumentativeness_fire_element_dependency", "house", "7", "source_specific",
       "Source says the partner may be argumentative, especially in fire element "
       "(fire-element dependency; no element resolver is applied for this house fact; "
       "not hard_aspected).",
       "conditional", "partner_argumentativeness_fire_element_dependency",
       source_reference=REF_H7_L7, unresolved=True),
)

B2_HOUSE_PACKS: tuple[SourceFactDef, ...] = (
    HOUSE_5 + HOUSE_5_BIO + HOUSE_6 + HOUSE_7
)
B2_SUPPORTED_HOUSE_KEYS = frozenset({"5", "6", "7"})
