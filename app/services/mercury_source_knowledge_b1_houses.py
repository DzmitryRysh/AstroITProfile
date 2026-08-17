"""Mercury Source Profile v2 — House Batch B1.

House 2 has Lesson 7 + Bioastrology (dual-source parity).
House 3 has Lesson 7 + Bioastrology (dual-source parity).
House 4 remains Lesson 7 only until its Bioastrology pass.

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


REF_H2_L7 = "lesson7_mercury_house_2"
REF_H2_BIO = "bioastrology_mercury_house_2"
REF_H3_L7 = "lesson7_mercury_house_3"
REF_H3_BIO = "bioastrology_mercury_house_3"
REF_H4_L7 = "lesson7_mercury_house_4"

# ---------------------------------------------------------------------------
# Mercury in House 2 — Lesson 7
# ---------------------------------------------------------------------------
HOUSE_2: tuple[SourceFactDef, ...] = (
    _f("h2_profit_through_public_speaking", "house", "2", "work_application",
       "Profit may come through public speaking.",
       "strength", "public_speaking_income",
       source_reference=REF_H2_L7),
    _f("h2_profit_through_literary_text_activity", "house", "2", "work_application",
       "Profit may come through literary / text-related activity.",
       "strength", "writing_income",
       source_reference=REF_H2_L7),
    _f("h2_literary_text_work_examples", "house", "2", "source_specific",
       "Source examples within literary/text work include speechwriting, editing, and "
       "copywriting; source-described work associations, not certified skill assignments.",
       "neutral", "literary_text_work_associations",
       source_reference=REF_H2_L7),
    _f("h2_talking_genre_profession_association", "house", "2", "source_specific",
       "Source associates speaking / \"talking genre\" professions (source-described "
       "association, not a career assignment).",
       "neutral", "talking_genre_profession_association",
       source_reference=REF_H2_L7),
    _f("h2_trade_income_association", "house", "2", "work_application",
       "Source associates income/activity with trade.",
       "neutral", "trade_income",
       source_reference=REF_H2_L7),
    _f("h2_import_export_trade_association", "house", "2", "work_application",
       "Source especially associates trade with import-export trade.",
       "neutral", "import_export_trade",
       source_reference=REF_H2_L7),
    _f("h2_advertising_income_association", "house", "2", "work_application",
       "Source associates income/activity with advertising.",
       "neutral", "advertising_income",
       source_reference=REF_H2_L7),
    _f("h2_financial_scheme_creation", "house", "2", "work_application",
       "Maximum money can come through creating cleverly thought-out financial schemes.",
       "strength", "financial_scheme_creation",
       source_reference=REF_H2_L7),
    _f("h2_financial_mechanism_design", "house", "2", "work_application",
       "Maximum money can come through creating cleverly thought-out financial mechanisms.",
       "strength", "financial_mechanism_design",
       source_reference=REF_H2_L7),
    _f("h2_objects_attract_through_usefulness", "house", "2", "environment",
       "Objects / things attract through usefulness.",
       "neutral", "usefulness_preference",
       source_reference=REF_H2_L7),
    _f("h2_objects_attract_through_applicability", "house", "2", "environment",
       "Objects / things attract through applicability.",
       "neutral", "applicability_preference",
       source_reference=REF_H2_L7),
    _f("h2_objects_attract_through_interestingness", "house", "2", "environment",
       "Objects / things attract through interestingness.",
       "neutral", "intellectual_interest_in_objects",
       source_reference=REF_H2_L7),
    _f("h2_likes_stationery", "house", "2", "source_specific",
       "Likes stationery.",
       "neutral", "likes_stationery",
       source_reference=REF_H2_L7),
    _f("h2_likes_expensive_pens", "house", "2", "source_specific",
       "Likes expensive pens.",
       "neutral", "likes_expensive_pens",
       source_reference=REF_H2_L7),
    _f("h2_likes_notebooks", "house", "2", "source_specific",
       "Likes notebooks.",
       "neutral", "likes_notebooks",
       source_reference=REF_H2_L7),
    _f("h2_likes_writing_paper_letters", "house", "2", "source_specific",
       "Likes writing paper letters.",
       "neutral", "likes_writing_paper_letters",
       source_reference=REF_H2_L7),
    _f("h2_accumulates_collects_books", "house", "2", "source_specific",
       "Accumulates / collects books.",
       "neutral", "collects_books",
       source_reference=REF_H2_L7),
    _f("h2_money_loss_carelessness", "house", "2", "risk",
       "Source-described money-loss risk in House 2 context: carelessness / lack of caution.",
       "risk", "money_loss_carelessness",
       source_reference=REF_H2_L7),
    _f("h2_money_loss_superficiality", "house", "2", "risk",
       "Source-described money-loss risk in House 2 context: superficiality.",
       "risk", "money_loss_superficiality",
       source_reference=REF_H2_L7),
    _f("h2_money_loss_overconfidence", "house", "2", "risk",
       "Source-described money-loss risk in House 2 context: excessive self-confidence.",
       "risk", "money_loss_overconfidence",
       source_reference=REF_H2_L7),
)

# ---------------------------------------------------------------------------
# Mercury in House 2 — Bioastrology (dual-source parity; HOUSE_2 L7 is frozen)
# ---------------------------------------------------------------------------
HOUSE_2_BIO: tuple[SourceFactDef, ...] = (
    _f("h2_bio_intellect_becomes_practical_applied", "house", "2", "thinking",
       "Over time, intellect may become more practical and applied.",
       "neutral",
       source_reference=REF_H2_BIO),
    _f("h2_bio_intellect_oriented_toward_money", "house", "2", "thinking",
       "Over time, intellect may become more oriented toward money.",
       "neutral",
       source_reference=REF_H2_BIO),
    _f("h2_bio_intellect_oriented_toward_health", "house", "2", "thinking",
       "Over time, intellect may become more oriented toward health.",
       "neutral",
       source_reference=REF_H2_BIO),
    _f("h2_bio_favorable_earning_through_information", "house", "2", "work_application",
       "Favorable earning potential through information.",
       "strength",
       source_reference=REF_H2_BIO),
    _f("h2_bio_two_or_three_parallel_income_sources", "house", "2", "work_application",
       "There may be two or three parallel sources of income.",
       "neutral",
       source_reference=REF_H2_BIO),
    _f("h2_bio_intellectual_transport_profession", "house", "2", "work_application",
       "Favorable association with intellectual and transport-related professions.",
       "strength", "intellectual_work", "transport_profession",
       source_reference=REF_H2_BIO),
    _f("h2_bio_consultant_qualities", "house", "2", "work_application",
       "May support qualities associated with consulting.",
       "strength", "consulting",
       source_reference=REF_H2_BIO),
    _f("h2_bio_sales_qualities", "house", "2", "work_application",
       "May support qualities associated with sales.",
       "strength", "sales",
       source_reference=REF_H2_BIO),
)

# ---------------------------------------------------------------------------
# Mercury in House 3 — Lesson 7
# ---------------------------------------------------------------------------
HOUSE_3: tuple[SourceFactDef, ...] = (
    _f("h3_extreme_curiosity", "house", "3", "thinking",
       "Extreme / very strong curiosity.",
       "strength", "extreme_curiosity",
       source_reference=REF_H3_L7),
    _f("h3_constant_drive_toward_learning", "house", "3", "learning",
       "Constant drive toward learning.",
       "strength", "constant_drive_toward_learning",
       source_reference=REF_H3_L7),
    _f("h3_knowledge_grasped_on_the_fly", "house", "3", "learning",
       "Knowledge is grasped \"on the fly\".",
       "strength", "quick_learning",
       source_reference=REF_H3_L7),
    _f("h3_ability_to_switch_between_activities", "house", "3", "thinking",
       "Ability to switch between activities.",
       "strength", "activity_switching",
       source_reference=REF_H3_L7),
    _f("h3_ability_to_distribute_attention", "house", "3", "focus",
       "Ability to distribute attention.",
       "strength", "distributed_attention",
       source_reference=REF_H3_L7),
    _f("h3_writes_essays_well", "house", "3", "communication",
       "Writes essays well.",
       "strength", "essay_writing",
       source_reference=REF_H3_L7),
    _f("h3_learns_languages", "house", "3", "learning",
       "Learns languages.",
       "strength", "languages_learning",
       source_reference=REF_H3_L7),
    _f("h3_excellent_written_expression", "house", "3", "communication",
       "Excellent ability to express thoughts in writing.",
       "strength", "written_expression",
       source_reference=REF_H3_L7),
    _f("h3_skilled_storyteller", "house", "3", "communication",
       "Skilled storyteller.",
       "strength", "storytelling",
       source_reference=REF_H3_L7),
    _f("h3_arguments_readily_available", "house", "3", "communication",
       "Arguments are readily available / \"always ready\".",
       "strength", "argument_readiness",
       source_reference=REF_H3_L7),
    _f("h3_wide_circle_of_acquaintances", "house", "3", "environment",
       "Wide circle of acquaintances.",
       "neutral", "wide_contact_circle",
       source_reference=REF_H3_L7),
    _f("h3_need_for_dialogue", "house", "3", "communication",
       "Need for dialogue.",
       "neutral", "dialogue_need",
       source_reference=REF_H3_L7),
    _f("h3_need_for_feedback", "house", "3", "communication",
       "Need for feedback.",
       "neutral", "feedback_need",
       source_reference=REF_H3_L7),
    _f("h3_ability_to_ask_right_questions", "house", "3", "communication",
       "Ability to ask the right questions.",
       "strength", "question_asking",
       source_reference=REF_H3_L7),
    _f("h3_ability_to_solve_tactical_tasks", "house", "3", "thinking",
       "Ability to solve tactical tasks.",
       "strength", "tactical_problem_solving",
       source_reference=REF_H3_L7),
    _f("h3_intellectual_success_depends_on_concentration", "house", "3", "source_specific",
       "Intellectual success occurs if concentration succeeds / if the native can concentrate "
       "(source dependency; no concentration-ability resolver is applied).",
       "conditional", "intellectual_success_depends_on_concentration",
       source_reference=REF_H3_L7, unresolved=True),
    _f("h3_group_learning_easier", "house", "3", "learning",
       "Group learning is easier.",
       "strength", "group_learning",
       source_reference=REF_H3_L7),
    _f("h3_reads_a_lot", "house", "3", "learning",
       "Reads a lot.",
       "neutral", "reading",
       source_reference=REF_H3_L7),
    _f("h3_attends_courses", "house", "3", "learning",
       "Attends courses.",
       "neutral", "course_learning",
       source_reference=REF_H3_L7),
    _f("h3_attends_lectures", "house", "3", "learning",
       "Attends lectures.",
       "neutral", "lecture_learning",
       source_reference=REF_H3_L7),
    _f("h3_events_often_begin_with_receiving_news", "house", "3", "source_specific",
       "Events often begin with receiving news (source examples: call, letter).",
       "neutral", "events_triggered_by_information",
       source_reference=REF_H3_L7),
    _f("h3_many_unnecessary_contacts", "house", "3", "risk",
       "Very many connections, most often unnecessary.",
       "risk", "many_unnecessary_contacts",
       source_reference=REF_H3_L7),
)

# ---------------------------------------------------------------------------
# Mercury in House 3 — Bioastrology (dual-source parity; HOUSE_3 L7 is frozen)
# ---------------------------------------------------------------------------
HOUSE_3_BIO: tuple[SourceFactDef, ...] = (
    _f("h3_bio_strengthens_mercury_functions", "house", "3", "thinking",
       "Strengthens Mercury functions overall.",
       "strength", "amplifier",
       source_reference=REF_H3_BIO),
    _f("h3_bio_emphasizes_mercury_aspects", "house", "3", "thinking",
       "Emphasizes Mercury aspects.",
       "neutral", "amplifier", "aspect_emphasis",
       source_reference=REF_H3_BIO),
    _f("h3_bio_emphasizes_mercury_sign", "house", "3", "thinking",
       "Emphasizes the Mercury sign.",
       "neutral", "amplifier", "sign_emphasis",
       source_reference=REF_H3_BIO),
    _f("h3_bio_eventfulness_books", "house", "3", "environment",
       "Increased eventfulness connected with books.",
       "neutral", "books",
       source_reference=REF_H3_BIO),
    _f("h3_bio_eventfulness_trips", "house", "3", "mobility",
       "Increased eventfulness connected with trips.",
       "neutral", "trips", "mobility",
       source_reference=REF_H3_BIO),
    _f("h3_bio_eventfulness_social_networks", "house", "3", "environment",
       "Increased eventfulness connected with social networks.",
       "neutral", "social_networks",
       source_reference=REF_H3_BIO),
    _f("h3_bio_circumstances_force_lifelong_communication_learning", "house", "3",
       "learning",
       "Circumstances may push the person to communicate and learn throughout "
       "life, even if naturally quiet.",
       "neutral",
       source_reference=REF_H3_BIO),
    _f("h3_bio_multiple_educations", "house", "3", "learning",
       "There may be multiple educations.",
       "neutral",
       source_reference=REF_H3_BIO),
    _f("h3_bio_learning_for_learning_lifestyle", "house", "3", "learning",
       "Learning may become a lifestyle pursued for its own sake.",
       "neutral",
       source_reference=REF_H3_BIO),
    _f("h3_bio_interest_trainings_seminars", "house", "3", "learning",
       "May show strong interest in trainings and seminars.",
       "strength",
       source_reference=REF_H3_BIO),
)

# ---------------------------------------------------------------------------
# Mercury in House 4 — Lesson 7
# ---------------------------------------------------------------------------
HOUSE_4: tuple[SourceFactDef, ...] = (
    _f("h4_intellectual_family_from_childhood", "house", "4", "environment",
       "From childhood, intellectual family.",
       "strength", "intellectual_family_environment",
       source_reference=REF_H4_L7),
    _f("h4_family_contains_a_lot_of_communication", "house", "4", "environment",
       "Family contains a lot of communication.",
       "neutral", "family_high_communication",
       source_reference=REF_H4_L7),
    _f("h4_home_communication_students_neighbors_household", "house", "4", "communication",
       "Communication happens at home with students, neighbors, and household / family members.",
       "neutral", "home_communication_contexts",
       source_reference=REF_H4_L7),
    _f("h4_home_based_study", "house", "4", "learning",
       "Home-based study.",
       "strength", "home_learning",
       source_reference=REF_H4_L7),
    _f("h4_home_library", "house", "4", "learning",
       "Home library.",
       "neutral", "home_library",
       source_reference=REF_H4_L7),
    _f("h4_guests_at_home", "house", "4", "environment",
       "Guests at home.",
       "neutral", "frequent_home_guests",
       source_reference=REF_H4_L7),
    _f("h4_home_pass_through_yard_traffic", "house", "4", "environment",
       "Home may function like a \"pass-through yard\" / many people coming through.",
       "neutral", "high_home_traffic",
       source_reference=REF_H4_L7),
    _f("h4_interest_in_family_ancestral_history", "house", "4", "learning",
       "Interest in family / ancestral history.",
       "neutral", "family_history_interest",
       source_reference=REF_H4_L7),
    _f("h4_weak_mercury_others_speak_instead", "house", "4", "source_specific",
       "If Mercury is weak, others will speak rather than the native "
       "(Mercury-strength dependency; no Mercury-strength resolver is applied; "
       "not equated with hard_aspected).",
       "conditional", "mercury_strength_dependency",
       source_reference=REF_H4_L7, unresolved=True),
    _f("h4_home_phone_withdrawal_from_live_communication", "house", "4", "risk",
       "Comes home and sits on the phone; this acts as withdrawal from live communication.",
       "risk", "home_phone_withdrawal_from_live_communication",
       source_reference=REF_H4_L7),
)

B1_HOUSE_PACKS: tuple[SourceFactDef, ...] = (
    HOUSE_2 + HOUSE_2_BIO + HOUSE_3 + HOUSE_3_BIO + HOUSE_4
)
B1_SUPPORTED_HOUSE_KEYS = frozenset({"2", "3", "4"})
