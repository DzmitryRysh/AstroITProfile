"""Mercury human presentation catalog — family coverage maintenance (S4.3).

SOURCE FACTS ARE IMMUTABLE EVIDENCE.

This module derives a presentation-maintenance catalog over ALL_SOURCE_FACTS.
It does not rewrite knowledge packs, change runtime UI fallback, or score people.

Runtime human display remains:
    HUMAN_COPY_OVERRIDES[id] if present else SourceFact.text

Review status is developer maintenance metadata only.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from app.services.mercury_human_copy import HUMAN_COPY_OVERRIDES
from app.services.mercury_human_copy_audit import detect_audit_reasons
from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS, SourceFactDef

STATUS_APPROVED_OVERRIDE = "approved_override"
STATUS_APPROVED_RAW = "approved_raw"
STATUS_NEEDS_REVIEW = "needs_review"
STATUS_UNREVIEWED = "unreviewed"

ALL_REVIEW_STATUSES: tuple[str, ...] = (
    STATUS_APPROVED_OVERRIDE,
    STATUS_APPROVED_RAW,
    STATUS_NEEDS_REVIEW,
    STATUS_UNREVIEWED,
)

# Explicit presentation decisions only (not overrides — those live in
# HUMAN_COPY_OVERRIDES). S4.3 seed + S4.4B–S4.5B + S4.7B–S4.11B + S4.14B
# + S4.16B–S4.17B.
APPROVED_RAW_FACT_IDS: frozenset[str] = frozenset(
    {
        # S4.3 seed
        "pluto_sq_strong_persuasiveness",
        "pluto_sq_powerful_words",
        "pluto_sq_debate_ability",
        "taurus_productive_thinking",
        "taurus_thorough_thinking",
        "taurus_measured_orderly_speech",
        "taurus_clearly_structured_speech",
        "taurus_thinks_before_speaking",
        "jupiter_sx_analysis_connects_with_synthesis",
        "uranus_cj_genius_potential",
        "uranus_cj_freshness_of_mind",
        "uranus_cj_openness_of_mind",
        "uranus_cj_spontaneous_creativity",
        "mars_tr_persuasive",
        "mars_tr_thinking_faster",
        "mars_tr_thinking_more_analytical",
        # M9.3 bridge-eligible analytical_thinking review
        "saturn_tr_analytical_ability",
        "pluto_sq_analytical_ability",
        "pluto_harm_analytical_quality",
        "jupiter_sx_oratory_and_persuasion",
        # S4.4B Sagittarius approved_raw
        "sag_searches_higher_meaning_in_ordinary",
        "sag_bio_central_idea_grasping",
        "sag_bio_independent_research_learning",
        "sag_bio_learning_through_teaching",
        "sag_bio_monologue_learning",
        "sag_difficulty_theory_to_practice",
        "sag_theory_to_practice_gap_risk",
        "sag_learning_encyclopedias",
        "sag_learning_pass_knowledge_to_others",
        "sag_learning_setting_a_goal",
        "sag_learning_university_textbooks",
        "sag_teacher_like_with_siblings",
        "sag_tendency_to_attach_labels",
        # S4.5B Taurus approved_raw
        "taurus_harmonious_thinking",
        "taurus_unhurried_thinking",
        "taurus_bio_unhurried_thinking_communication_learning",
        "taurus_bio_productive_thinking_communication_learning",
        "taurus_relies_on_common_sense",
        "taurus_values_factual_reliability",
        "taurus_bio_beautiful_handwriting",
        "taurus_bio_beautiful_voice",
        "taurus_bio_beautiful_speech",
        "taurus_bio_practice_based_learning",
        "taurus_applying_knowledge_in_practice",
        "taurus_comfortable_learning_environment",
        "taurus_learning_needs_time_without_pressure",
        "taurus_learning_repetition_persistence",
        "taurus_may_recheck_information",
        "taurus_slow_processing_long_retention",
        "taurus_difficulty_rapidly_changing_mental_direction",
        "taurus_risk_inertia",
        # S4.7B Capricorn approved_raw
        "capricorn_bio_calm_voice",
        "capricorn_bio_diploma_certificate_matters",
        "capricorn_bio_iron_argumentation",
        "capricorn_bio_learning_alone",
        "capricorn_bio_learning_long_systematic_courses",
        "capricorn_bio_learning_official_institutions",
        "capricorn_bio_learning_own_experience",
        "capricorn_bio_learning_practice",
        "capricorn_bio_logical_thinking",
        "capricorn_bio_needs_practical_usefulness_for_communication",
        "capricorn_bio_unemotional_style",
        "capricorn_l7_algorithms_help",
        "capricorn_l7_authoritative_opinion_reliance",
        "capricorn_l7_businesslike_thinking",
        "capricorn_l7_calm_speech",
        "capricorn_l7_common_sense_reliance",
        "capricorn_l7_concrete_thinking",
        "capricorn_l7_env_businesslike_siblings",
        "capricorn_l7_env_formal_communication",
        "capricorn_l7_env_limited_contact",
        "capricorn_l7_env_usefulness_selected",
        "capricorn_l7_focus_on_essence",
        "capricorn_l7_focus_on_principle",
        "capricorn_l7_formal_communication",
        "capricorn_l7_iron_logic",
        "capricorn_l7_lack_of_haste",
        "capricorn_l7_needs_sequence_of_actions",
        "capricorn_l7_needs_why_material_learned",
        "capricorn_l7_notes_help",
        "capricorn_l7_one_thing_at_a_time",
        "capricorn_l7_one_thought_at_a_time",
        "capricorn_l7_plans_help",
        "capricorn_l7_quiet_speech",
        "capricorn_l7_schedules_help",
        "capricorn_l7_schemes_help",
        "capricorn_l7_scientific_mindset",
        "capricorn_l7_speech_without_filler",
        "capricorn_l7_structure_helps",
        "capricorn_l7_structured_thinking",
        "capricorn_l7_stubbornness_in_views",
        "capricorn_l7_systems_help",
        "capricorn_l7_tables_help",
        # S4.7B Leo approved_raw
        "leo_l7_env_emphasizes_own_views",
        "leo_l7_env_idea_appropriation",
        "leo_l7_env_seeks_admiration",
        "leo_l7_env_seeks_recognition",
        "leo_l7_learning_bright_presentation",
        "leo_l7_learning_creative_reformulation",
        "leo_l7_learning_performing",
        "leo_l7_learning_standing_out",
        "leo_l7_monologue_communication",
        "leo_l7_monologue_thinking",
        "leo_l7_persist_in_views_while_knowing_wrong",
        "leo_l7_prepared_phrases_appearance_of_competence",
        "leo_l7_seeks_applause",
        "leo_l7_tracks_audience_effect",
        "leo_l7_transforms_others_idea_into_own",
        "leo_l7_unwillingness_to_admit_wrong",
        "leo_leadership_communication_potential",
        "leo_learns_through_impressions",
        "leo_learns_through_independent_investigation",
        "leo_may_discount_others_opinions",
        "leo_nonstandard_speech_thinking",
        "leo_playful_competition_motivates_learning",
        "leo_pr_ability",
        "leo_praise_motivates_learning",
        "leo_risk_intellectual_superficiality",
        "leo_sales_ability",
        "leo_strong_creative_quality",
        "leo_strong_debate_potential",
        "leo_strong_oratory_potential",
        "leo_thinks_from_own_position",
        "leo_visible_status_motivates_learning",
        "leo_wants_to_demonstrate_results",
        # S4.8B Aquarius approved_raw
        "aquarius_bio_creative_thinking",
        "aquarius_bio_curiosity",
        "aquarius_bio_erudition",
        "aquarius_bio_extemporaneous_many_topics",
        "aquarius_bio_interest_science_fiction",
        "aquarius_bio_interest_technology",
        "aquarius_bio_knowledge_fragment_synthesis",
        "aquarius_bio_learning_audio",
        "aquarius_bio_learning_books",
        "aquarius_bio_learning_group_communication",
        "aquarius_bio_learning_lectures",
        "aquarius_bio_learning_video",
        "aquarius_l7_abstraction_ability",
        "aquarius_l7_book_learning",
        "aquarius_l7_cycles_many_options_quickly",
        "aquarius_l7_democratic_communication",
        "aquarius_l7_discussion_learning",
        "aquarius_l7_env_broad_social_circle",
        "aquarius_l7_env_friendly_siblings",
        "aquarius_l7_env_futuristic_environment",
        "aquarius_l7_env_unpredictable_siblings",
        "aquarius_l7_env_unusual_environment",
        "aquarius_l7_extemporaneous_many_topics",
        "aquarius_l7_gadgets_can_help",
        "aquarius_l7_global_thinking",
        "aquarius_l7_good_memory",
        "aquarius_l7_group_learning",
        "aquarius_l7_idealistic_thinking",
        "aquarius_l7_independent_learning",
        "aquarius_l7_independent_thinking",
        "aquarius_l7_lecture_learning",
        "aquarius_l7_planning_can_help",
        "aquarius_l7_processes_large_data_quickly",
        "aquarius_l7_spans_knowledge_areas",
        "aquarius_l7_speech_varies_with_mood",
        # S4.8B Gemini approved_raw
        "gemini_bio_curiosity_motivated_learning",
        "gemini_bio_demonstrative_teacher_potential",
        "gemini_bio_intellectual_multitasking",
        "gemini_bio_rationalism",
        "gemini_bio_reliance_on_facts",
        "gemini_bio_strong_memory",
        "gemini_bio_strong_student_potential",
        "gemini_l7_env_constantly_renews",
        "gemini_l7_env_contact_quantity_over_quality",
        "gemini_l7_env_sibling_easy",
        "gemini_l7_env_sibling_superficial",
        "gemini_l7_highly_contact_oriented_thinking",
        "gemini_l7_learns_easily_in_dialogue",
        "gemini_l7_logical_thinking",
        "gemini_l7_may_fail_to_see_whole",
        "gemini_l7_particular_to_general",
        "gemini_l7_quantity_may_dominate_quality",
        "gemini_l7_quick_understanding_may_cause_laziness",
        "gemini_l7_quick_understanding_may_lose_interest",
        "gemini_l7_risk_boredom_prolonged_one_subject",
        "gemini_l7_simplifies_abstractions",
        "gemini_l7_strong_commercial_ability",
        "gemini_l7_strong_negotiation_ability",
        "gemini_l7_support_books",
        "gemini_l7_support_groups",
        "gemini_l7_support_lectures",
        "gemini_l7_support_multi_person_communication",
        "gemini_l7_support_teachers",
        "gemini_l7_understands_quickly",
        # S4.9B Pisces approved_raw
        "pisces_bio_context_dependent_memory",
        "pisces_bio_learning_audio",
        "pisces_bio_learning_books",
        "pisces_bio_learning_flow_state",
        "pisces_bio_public_speaking_requires_preparation",
        "pisces_bio_public_speaking_requires_training",
        "pisces_bio_selective_memory",
        "pisces_l7_calm_communication",
        "pisces_l7_creative_reinterpretation_learning",
        "pisces_l7_emotional_speech",
        "pisces_l7_env_adapts_to_collective_stereotypes",
        "pisces_l7_env_avoids_polemics",
        "pisces_l7_env_possible_misunderstanding",
        "pisces_l7_env_sibling_illusions",
        "pisces_l7_env_soulful_siblings",
        "pisces_l7_harmonious_communication",
        "pisces_l7_image_based_perception",
        "pisces_l7_learning_images",
        "pisces_l7_learning_intuitive_impression",
        "pisces_l7_learning_listening",
        "pisces_l7_learning_photos",
        "pisces_l7_learning_solitude",
        "pisces_l7_learning_video",
        "pisces_l7_overall_impression_over_isolated_fact",
        "pisces_l7_speaks_through_parables",
        "pisces_l7_speaks_through_riddles",
        "pisces_l7_speech_may_lack_central_idea",
        "pisces_l7_unclear_speech",
        "pisces_l7_unconventional_learning",
        # S4.9B Aries approved_raw
        "aries_bio_learns_through_disputes",
        "aries_bio_learns_through_practical_implementation",
        "aries_bio_monologue_communication",
        "aries_bio_strong_through_speed_not_depth",
        "aries_bio_strong_through_speed_not_endurance",
        "aries_bio_tends_not_to_hear_others",
        "aries_l7_communication_as_polemics",
        "aries_l7_detects_logic_weak_points",
        "aries_l7_difficult_to_reach_through_dialogue",
        "aries_l7_difficulty_hearing_others",
        "aries_l7_env_contacts_impulsive",
        "aries_l7_env_sees_opponent_in_others",
        "aries_l7_env_sibling_argumentative",
        "aries_l7_env_sibling_competitive",
        "aries_l7_fast_thinking",
        "aries_l7_hurried_thinking",
        "aries_l7_inattentive_thinking",
        "aries_l7_mediation_difficult",
        "aries_l7_ordinary_communication_becomes_argument",
        "aries_l7_perceives_interlocutors_as_opponents",
        "aries_l7_primarily_hears_self",
        "aries_l7_questioner_and_answerer",
        "aries_l7_ready_answer",
        "aries_l7_repeats_own_position",
        "aries_l7_retains_existing_formulation",
        "aries_l7_risk_haste_errors",
        # S4.10B Scorpio approved_raw
        "scorpio_bio_learning_group_discussion",
        "scorpio_bio_learning_independent_research",
        "scorpio_bio_quiet_calm_voice",
        "scorpio_bio_strong_memory",
        "scorpio_l7_ability_to_see_the_essence",
        "scorpio_l7_categorical_thinking",
        "scorpio_l7_caustic_speech",
        "scorpio_l7_detective_like_thinking",
        "scorpio_l7_env_hidden_sibling_tension",
        "scorpio_l7_env_sibling_competition",
        "scorpio_l7_env_sibling_verbal_jabs",
        "scorpio_l7_expects_listener_to_infer",
        "scorpio_l7_extraction_of_nonverbal_information",
        "scorpio_l7_fast_replies",
        "scorpio_l7_high_analytical_ability",
        "scorpio_l7_independent_learning",
        "scorpio_l7_many_probing_questions",
        "scorpio_l7_maximalist_thinking",
        "scorpio_l7_research_oriented_mind",
        "scorpio_l7_says_very_little_explicitly",
        "scorpio_l7_sharp_replies",
        "scorpio_l7_sticky_memory",
        "scorpio_l7_tendency_to_dig_to_core",
        "scorpio_l7_tense_communication",
        "scorpio_l7_verbal_jabs",
        "scorpio_l7_very_deep_memory",
        # S4.10B Libra approved_raw
        "libra_bio_beautiful_handwriting",
        "libra_bio_beauty_of_words",
        "libra_bio_learning_books",
        "libra_bio_learning_contrasts",
        "libra_bio_learning_dialogue",
        "libra_l7_appeal_to_fairness",
        "libra_l7_assimilation_through_discussion",
        "libra_l7_delicate_communication",
        "libra_l7_difficulty_making_decisions",
        "libra_l7_env_search_for_common_language",
        "libra_l7_env_sibling_diplomacy",
        "libra_l7_env_sibling_dispute_avoidance",
        "libra_l7_env_tendency_to_form_relationships",
        "libra_l7_evaluates_via_aesthetic_beauty",
        "libra_l7_evaluates_via_completeness",
        "libra_l7_high_receptivity",
        "libra_l7_high_speed_of_comprehension",
        "libra_l7_information_synthesis",
        "libra_l7_learning_through_contradiction_comparison",
        "libra_l7_peaceful_communication",
        "libra_l7_says_what_interlocutor_wants",
        "libra_l7_skill_with_compliments",
        "libra_l7_view_issue_from_multiple_sides",
        # S4.11B Cancer approved_raw
        "cancer_bio_also_accepts_books",
        "cancer_bio_attachment_to_classics_opinions",
        "cancer_bio_attachment_to_parents_opinions",
        "cancer_bio_image_based_emotional_memory",
        "cancer_bio_learns_through_audio",
        "cancer_bio_learns_through_impressions",
        "cancer_bio_learns_through_lectures",
        "cancer_bio_learns_through_video",
        "cancer_bio_living_image_in_web_of_facts",
        "cancer_bio_may_lose_debates_lacking_force",
        "cancer_bio_speech_may_be_unstable",
        "cancer_l7_deep_associative_connections",
        "cancer_l7_env_authorities_important",
        "cancer_l7_env_emotional_attachment_siblings",
        "cancer_l7_env_traditions_important",
        "cancer_l7_excellent_imagination",
        "cancer_l7_good_improvisation",
        "cancer_l7_intuitive_args_hard_to_explain",
        "cancer_l7_learning_through_authorities",
        "cancer_l7_learning_through_traditions",
        "cancer_l7_mind_attached_to_past",
        "cancer_l7_need_emotional_feedback",
        "cancer_l7_risk_difficulty_concentrating",
        "cancer_l7_risk_emotionality_interferes_learning",
        "cancer_l7_risk_mental_drifting",
        "cancer_l7_sensitivity_to_dialogue_atmosphere",
        "cancer_l7_speech_can_become_tangled",
        "cancer_l7_speech_expresses_emotion",
        "cancer_l7_sticky_memory_emotions",
        "cancer_l7_sticky_memory_images",
        "cancer_l7_sticky_memory_smells",
        "cancer_l7_thought_hard_to_express",
        # S4.11B Virgo approved_raw
        "virgo_bio_deliberately_correct_speech",
        "virgo_bio_grounded_thinking",
        "virgo_bio_independent_analysis_learning",
        "virgo_bio_learning_on_the_fly",
        "virgo_bio_strong_attention",
        "virgo_bio_strong_erudition",
        "virgo_l7_analytical_thinking",
        "virgo_l7_dispersion_into_small_details",
        "virgo_l7_env_limited_social_circle",
        "virgo_l7_env_low_emotionality_siblings",
        "virgo_l7_limited_contact_circle",
        "virgo_l7_practical_learning",
        "virgo_l7_precision_of_formulations",
        "virgo_l7_selective_thinking",
        "virgo_l7_strong_tactical_thinking",
        "virgo_l7_strongest_logic_after_preparation",
        "virgo_l7_tendency_to_clarify_details",
        "virgo_l7_weaker_strategic_overview",
        # S4.14B motion:retrograde approved_raw
        "rx_nonstandard_solutions",
        "rx_processing_takes_longer",
        "rx_repeated_internal_processing",
        "rx_revisit_previously_learned",
        "rx_tendency_to_relearn",
        "rx_tendency_to_rewrite",
        "rx_unexpected_conclusions",
        "rx_written_easier_than_spontaneous",
        # S4.16B house:2 approved_raw
        "h2_profit_through_public_speaking",
        # S4.17B house:3 approved_raw
        "h3_reads_a_lot",
        # S4.33B house:1 Lesson 7 approved_raw
        "h1_l7_impression_of_fussiness",
        "h1_l7_undirected_activity",
        "h1_l7_starts_but_does_not_complete_tasks",
        "h1_l7_logic_displaces_intuition",
        "h1_l7_youthfulness_leads_to_lack_of_respect",
        # S4.33 remaining House approved_raw (H2–H12)
        "h2_bio_consultant_qualities",
        "h2_bio_intellect_becomes_practical_applied",
        "h2_bio_intellect_oriented_toward_health",
        "h2_bio_intellect_oriented_toward_money",
        "h2_bio_sales_qualities",
        "h2_bio_two_or_three_parallel_income_sources",
        "h3_bio_circumstances_force_lifelong_communication_learning",
        "h3_bio_interest_trainings_seminars",
        "h3_bio_learning_for_learning_lifestyle",
        "h3_bio_multiple_educations",
        "h4_bio_family_intellectual_interest",
        "h4_bio_home_intellectual_interest",
        "h4_bio_home_requires_serving_working",
        "h4_bio_home_requires_writing_study_reading",
        "h4_bio_interest_in_medicine",
        "h4_bio_politics_intellectual_interest",
        "h4_bio_psychology_intellectual_interest",
        "h4_bio_relocation",
        "h5_bio_books_as_hobby",
        "h5_bio_entrepreneurial_qualities",
        "h5_bio_gift_for_writing",
        "h5_bio_learning_as_hobby",
        "h5_bio_mercury_qualities_colored_by_children",
        "h5_bio_mercury_qualities_colored_by_creativity",
        "h5_bio_mercury_qualities_colored_by_risk",
        "h5_bio_multiple_children_association",
        "h5_bio_parallel_romances",
        "h5_bio_sales_qualities",
        "h5_bio_trips_as_hobby",
        "h5_bio_twins_association",
        "h5_romantic_talk_displaces_feelings",
        "h6_bio_consultant_qualities",
        "h6_bio_increased_concerns_hassles",
        "h6_bio_interest_in_medicine",
        "h6_bio_ongoing_professional_education",
        "h6_bio_others_assign_work",
        "h6_bio_professional_retraining",
        "h6_bio_sales_qualities",
        "h6_bio_several_pets",
        "h6_bio_two_parallel_jobs_or_projects",
        "h6_work_involves_processing_lots_of_information",
        "h7_bio_communication_learning_through_partners_public",
        "h7_bio_consultant_qualities",
        "h7_bio_lawyer_qualities",
        "h7_bio_partner_younger",
        "h7_bio_politician_qualities",
        "h7_conversation_partner_can_be_found",
        "h7_intellectual_interest_important_with_partner",
        "h7_relationships_built_more_on_reason",
        "h7_shared_topics_important_with_partner",
        "h8_bio_analytical_ability",
        "h8_bio_communication_learning_demanded_in_crises",
        "h8_bio_communication_learning_demanded_in_finance",
        "h8_bio_communication_learning_demanded_in_magic",
        "h8_bio_communication_learning_demanded_in_psychology",
        "h8_bio_detective_ability",
        "h8_bio_interest_in_energies",
        "h8_bio_interest_in_sex",
        "h8_bio_investments_other_people_money",
        "h8_bio_power_of_word",
        "h8_bio_solitary_critical_learning_method",
        "h9_bio_communication_learning_realized_through_philosophical_concepts",
        "h9_bio_communication_learning_realized_through_scientific_theories",
        "h9_bio_communication_learning_realized_through_travel",
        "h9_bio_increased_courses",
        "h9_bio_increased_trainings",
        "h9_bio_increased_university_contexts",
        "h9_bio_learning_through_direct_teacher_dialogue",
        "h9_bio_mentor_talent",
        "h9_bio_not_heard_in_ordinary_situations",
        "h9_bio_strong_intellect",
        "h9_bio_teacher_talent",
        "h9_bio_trainer_talent",
        "h9_casual_communication_less_natural",
        "h9_consume_too_much_high_level_info",
        "h9_cycle_on_unnecessary_information",
        "h9_need_to_monitor_speech",
        "h10_bio_communication_learning_demanded_in_business",
        "h10_bio_communication_learning_demanded_in_career",
        "h10_bio_communication_learning_strengthened_overall",
        "h10_bio_consultant_qualities",
        "h10_bio_intellect_becomes_conservative",
        "h10_bio_intellect_becomes_grounded",
        "h10_bio_intellect_becomes_socially_conditioned",
        "h10_bio_parallel_work_business_directions",
        "h10_bio_politician_role",
        "h10_bio_sales_qualities",
        "h10_bio_scientist_role",
        "h10_bio_work_with_siblings",
        "h10_bio_work_with_younger_people",
        "h10_career_requires_communication_tools",
        "h10_career_requires_large_information_volumes",
        "h10_frequent_change_of_work",
        "h10_information_load_can_be_difficult",
        "h10_may_change_professions_until_interesting_prestigious",
        "h11_bio_communication_learning_realized_through_clubs",
        "h11_bio_communication_learning_realized_through_collectives",
        "h11_bio_communication_learning_realized_through_forums",
        "h11_bio_communication_learning_realized_through_gatherings",
        "h11_bio_communication_learning_realized_through_internet",
        "h11_bio_intellect_becomes_scientific",
        "h11_bio_intellect_becomes_technological",
        "h11_bio_learning_in_group_or_collective",
        "h11_bio_learning_oriented_toward_high_technologies",
        "h11_bio_learning_with_equals_or_peers",
        "h11_bio_learning_with_friends",
        "h11_bio_many_discussed_plans",
        "h11_bio_many_discussed_projects",
        "h11_friends_are_sources_of_knowledge",
        "h11_groups_are_sources_of_knowledge",
        "h12_bio_circumstances_make_person_solitary",
        "h12_bio_communication_learning_hidden_from_broad_public",
        "h12_bio_doctor_qualities",
        "h12_bio_intuitive_revelations_insights",
        "h12_bio_learning_from_own_experience",
        "h12_bio_mystic_qualities",
        "h12_bio_psychologist_qualities",
        "h12_bio_source_broad_intellectual_capacity",
    }
)

# Explicit needs_review decisions. S4.12B resolved 18 of 19 sign policy
# facts via HUMAN_COPY_OVERRIDES. Remaining conditional dependencies:
# cancer_bio_depends_on_moon_sign — Moon-sign context not resolved in
# this prototype; reconsider only when a Moon-sign resolver exists.
# h4_weak_mercury_others_speak_instead — Mercury-strength context not
# resolved in this prototype; not equated with hard_aspected.
NEEDS_REVIEW_FACT_IDS: frozenset[str] = frozenset(
    {
        "cancer_bio_depends_on_moon_sign",
        "h4_weak_mercury_others_speak_instead",
    }
)

class HumanCopyCatalogError(ValueError):
    """Raised when presentation review registries are inconsistent."""


@dataclass(frozen=True)
class HumanCopyCatalogEntry:
    fact_id: str
    factor_type: str
    factor_key: str
    category: str
    polarity: str
    canonical_text: str
    human_text: str
    review_status: str
    uses_override: bool
    audit_reasons: tuple[str, ...]
    review_recommended: bool
    source_reference: str

    @property
    def family_key(self) -> str:
        return f"{self.factor_type}:{self.factor_key}"


@dataclass(frozen=True)
class HumanCopyFamilyCoverage:
    family_key: str
    factor_type: str
    factor_key: str
    total_facts: int
    approved_override: int
    approved_raw: int
    needs_review: int
    unreviewed: int
    review_recommended_unreviewed: int
    reviewed_count: int
    presentation_ready_count: int
    review_coverage: float
    presentation_ready_coverage: float


@dataclass(frozen=True)
class HumanCopyCatalogReport:
    total_facts: int
    entries: tuple[HumanCopyCatalogEntry, ...]
    approved_override_count: int
    approved_raw_count: int
    needs_review_count: int
    unreviewed_count: int
    reviewed_count: int
    presentation_ready_count: int
    review_coverage: float
    presentation_ready_coverage: float
    review_recommended_unreviewed_count: int
    families: tuple[HumanCopyFamilyCoverage, ...]


def validate_human_copy_registries(
    facts: Sequence[SourceFactDef] = ALL_SOURCE_FACTS,
    *,
    overrides: Mapping[str, str] | None = None,
    approved_raw: frozenset[str] | None = None,
    needs_review: frozenset[str] | None = None,
) -> None:
    """Fail loudly on conflicting or unknown presentation decisions."""
    catalog_ids = {fact.id for fact in facts}
    override_ids = set((overrides if overrides is not None else HUMAN_COPY_OVERRIDES).keys())
    raw_ids = set(approved_raw if approved_raw is not None else APPROVED_RAW_FACT_IDS)
    review_ids = set(needs_review if needs_review is not None else NEEDS_REVIEW_FACT_IDS)

    unknown_overrides = sorted(override_ids - catalog_ids)
    if unknown_overrides:
        raise HumanCopyCatalogError(
            f"Unknown HUMAN_COPY_OVERRIDES IDs: {unknown_overrides}"
        )

    unknown_raw = sorted(raw_ids - catalog_ids)
    if unknown_raw:
        raise HumanCopyCatalogError(
            f"Unknown APPROVED_RAW_FACT_IDS: {unknown_raw}"
        )

    unknown_needs = sorted(review_ids - catalog_ids)
    if unknown_needs:
        raise HumanCopyCatalogError(
            f"Unknown NEEDS_REVIEW_FACT_IDS: {unknown_needs}"
        )

    both_override_raw = sorted(override_ids & raw_ids)
    if both_override_raw:
        raise HumanCopyCatalogError(
            f"IDs cannot be override and approved_raw: {both_override_raw}"
        )

    both_override_needs = sorted(override_ids & review_ids)
    if both_override_needs:
        raise HumanCopyCatalogError(
            f"IDs cannot be override and needs_review: {both_override_needs}"
        )

    both_raw_needs = sorted(raw_ids & review_ids)
    if both_raw_needs:
        raise HumanCopyCatalogError(
            f"IDs cannot be approved_raw and needs_review: {both_raw_needs}"
        )


def derive_review_status(fact_id: str) -> str:
    """Derive review status from override + explicit decision registries."""
    if fact_id in HUMAN_COPY_OVERRIDES:
        return STATUS_APPROVED_OVERRIDE
    if fact_id in APPROVED_RAW_FACT_IDS:
        return STATUS_APPROVED_RAW
    if fact_id in NEEDS_REVIEW_FACT_IDS:
        return STATUS_NEEDS_REVIEW
    return STATUS_UNREVIEWED


def build_catalog_entry(fact: SourceFactDef) -> HumanCopyCatalogEntry:
    """Build one catalog entry for a canonical SourceFact."""
    status = derive_review_status(fact.id)
    uses_override = status == STATUS_APPROVED_OVERRIDE
    if uses_override:
        human_text = HUMAN_COPY_OVERRIDES[fact.id]
    else:
        human_text = fact.text
    reasons = detect_audit_reasons(fact.text)
    return HumanCopyCatalogEntry(
        fact_id=fact.id,
        factor_type=fact.factor_type,
        factor_key=fact.factor_key,
        category=fact.category,
        polarity=fact.polarity,
        canonical_text=fact.text,
        human_text=human_text,
        review_status=status,
        uses_override=uses_override,
        audit_reasons=reasons,
        review_recommended=bool(reasons),
        source_reference=fact.source_reference,
    )


def _coverage_ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def _build_family_coverage(
    entries: Sequence[HumanCopyCatalogEntry],
) -> tuple[HumanCopyFamilyCoverage, ...]:
    by_family: dict[str, list[HumanCopyCatalogEntry]] = {}
    for entry in entries:
        by_family.setdefault(entry.family_key, []).append(entry)

    families: list[HumanCopyFamilyCoverage] = []
    for family_key in sorted(by_family):
        group = by_family[family_key]
        status_counts = Counter(item.review_status for item in group)
        approved_override = status_counts[STATUS_APPROVED_OVERRIDE]
        approved_raw = status_counts[STATUS_APPROVED_RAW]
        needs_review = status_counts[STATUS_NEEDS_REVIEW]
        unreviewed = status_counts[STATUS_UNREVIEWED]
        reviewed = approved_override + approved_raw + needs_review
        ready = approved_override + approved_raw
        recommended_unreviewed = sum(
            1
            for item in group
            if item.review_status == STATUS_UNREVIEWED and item.review_recommended
        )
        sample = group[0]
        total = len(group)
        families.append(
            HumanCopyFamilyCoverage(
                family_key=family_key,
                factor_type=sample.factor_type,
                factor_key=sample.factor_key,
                total_facts=total,
                approved_override=approved_override,
                approved_raw=approved_raw,
                needs_review=needs_review,
                unreviewed=unreviewed,
                review_recommended_unreviewed=recommended_unreviewed,
                reviewed_count=reviewed,
                presentation_ready_count=ready,
                review_coverage=_coverage_ratio(reviewed, total),
                presentation_ready_coverage=_coverage_ratio(ready, total),
            )
        )
    return tuple(families)


def build_human_copy_catalog(
    facts: Sequence[SourceFactDef] = ALL_SOURCE_FACTS,
) -> HumanCopyCatalogReport:
    """Build the full presentation catalog over canonical SourceFacts."""
    validate_human_copy_registries(facts)

    # Canonical SourceFact.id is the unit — one entry per fact, no alias inflation.
    entries = tuple(
        sorted(
            (build_catalog_entry(fact) for fact in facts),
            key=lambda item: (item.family_key, item.fact_id),
        )
    )
    status_counts = Counter(entry.review_status for entry in entries)
    approved_override = status_counts[STATUS_APPROVED_OVERRIDE]
    approved_raw = status_counts[STATUS_APPROVED_RAW]
    needs_review = status_counts[STATUS_NEEDS_REVIEW]
    unreviewed = status_counts[STATUS_UNREVIEWED]
    total = len(entries)
    reviewed = approved_override + approved_raw + needs_review
    ready = approved_override + approved_raw
    recommended_unreviewed = sum(
        1
        for entry in entries
        if entry.review_status == STATUS_UNREVIEWED and entry.review_recommended
    )

    return HumanCopyCatalogReport(
        total_facts=total,
        entries=entries,
        approved_override_count=approved_override,
        approved_raw_count=approved_raw,
        needs_review_count=needs_review,
        unreviewed_count=unreviewed,
        reviewed_count=reviewed,
        presentation_ready_count=ready,
        review_coverage=_coverage_ratio(reviewed, total),
        presentation_ready_coverage=_coverage_ratio(ready, total),
        review_recommended_unreviewed_count=recommended_unreviewed,
        families=_build_family_coverage(entries),
    )


def get_family_entries(
    report: HumanCopyCatalogReport,
    family_key: str,
) -> tuple[HumanCopyCatalogEntry, ...]:
    """Return catalog entries for one factor family, sorted by fact_id."""
    return tuple(
        entry
        for entry in report.entries
        if entry.family_key == family_key
    )


def least_reviewed_families(
    report: HumanCopyCatalogReport,
    *,
    limit: int = 10,
) -> tuple[HumanCopyFamilyCoverage, ...]:
    """Families with lowest review coverage (maintenance priority only)."""
    ordered = sorted(
        report.families,
        key=lambda family: (
            family.review_coverage,
            -family.unreviewed,
            -family.total_facts,
            family.family_key,
        ),
    )
    return tuple(ordered[: max(0, limit)])


def format_catalog_summary(report: HumanCopyCatalogReport, *, top_n: int = 10) -> str:
    """Concise developer maintenance summary."""
    lines = [
        "Mercury Human Presentation Catalog",
        "",
        f"Canonical facts: {report.total_facts}",
        f"Approved override: {report.approved_override_count}",
        f"Approved raw: {report.approved_raw_count}",
        f"Needs review: {report.needs_review_count}",
        f"Unreviewed: {report.unreviewed_count}",
        "",
        f"Reviewed coverage: {report.reviewed_count}/{report.total_facts} "
        f"({report.review_coverage:.1%})",
        f"Presentation-ready coverage: {report.presentation_ready_count}/"
        f"{report.total_facts} ({report.presentation_ready_coverage:.1%})",
        "",
        f"Families: {len(report.families)}",
        f"Review-recommended but unreviewed: "
        f"{report.review_recommended_unreviewed_count}",
        "",
        "Most incomplete families:",
    ]
    for family in least_reviewed_families(report, limit=top_n):
        lines.append(
            f"  {family.family_key} "
            f"reviewed={family.reviewed_count}/{family.total_facts} "
            f"({family.review_coverage:.0%}) "
            f"ready={family.presentation_ready_count} "
            f"unreviewed={family.unreviewed} "
            f"recommended={family.review_recommended_unreviewed}"
        )
    return "\n".join(lines)


def format_family_detail(
    report: HumanCopyCatalogReport,
    family_key: str,
) -> str:
    """Developer family review view."""
    family = next((item for item in report.families if item.family_key == family_key), None)
    entries = get_family_entries(report, family_key)
    if family is None or not entries:
        return f"Family not found or empty: {family_key}"

    lines = [
        f"Family: {family.family_key}",
        f"Total: {family.total_facts}",
        f"Approved override: {family.approved_override}",
        f"Approved raw: {family.approved_raw}",
        f"Needs review: {family.needs_review}",
        f"Unreviewed: {family.unreviewed}",
        f"Reviewed: {family.reviewed_count}/{family.total_facts} "
        f"({family.review_coverage:.0%})",
        f"Presentation-ready: {family.presentation_ready_count}/"
        f"{family.total_facts} ({family.presentation_ready_coverage:.0%})",
    ]

    def _section(title: str, items: Sequence[HumanCopyCatalogEntry]) -> None:
        lines.append("")
        lines.append(f"{title}:")
        if not items:
            lines.append("  (none)")
            return
        for entry in items:
            if entry.uses_override:
                lines.append(f"  [{entry.fact_id}]")
                lines.append(f"    canonical: {entry.canonical_text}")
                lines.append(f"    human: {entry.human_text}")
            else:
                reason_suffix = ""
                if entry.audit_reasons:
                    reason_suffix = f"\n    reasons: {', '.join(entry.audit_reasons)}"
                lines.append(f"  [{entry.fact_id}] {entry.canonical_text}{reason_suffix}")

    recommended = [
        e
        for e in entries
        if e.review_status == STATUS_UNREVIEWED and e.review_recommended
    ]
    clean_unreviewed = [
        e
        for e in entries
        if e.review_status == STATUS_UNREVIEWED and not e.review_recommended
    ]
    needs = [e for e in entries if e.review_status == STATUS_NEEDS_REVIEW]
    approved_raw = [e for e in entries if e.review_status == STATUS_APPROVED_RAW]
    approved_override = [
        e for e in entries if e.review_status == STATUS_APPROVED_OVERRIDE
    ]

    _section("UNREVIEWED / RECOMMENDED", recommended)
    _section("UNREVIEWED / CLEAN", clean_unreviewed)
    _section("NEEDS REVIEW", needs)
    _section("APPROVED RAW", approved_raw)
    _section("APPROVED OVERRIDE", approved_override)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# S4.6 — Sign family review queue (maintenance workload only)
# ---------------------------------------------------------------------------

# Zodiac display order for all-12 sign reports (not priority order).
ZODIAC_SIGN_ORDER: tuple[str, ...] = (
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
)

SIGN_FAMILY_KEYS: tuple[str, ...] = tuple(
    f"sign:{name}" for name in ZODIAC_SIGN_ORDER
)

@dataclass(frozen=True)
class SignReviewQueueEntry:
    """One Mercury sign family in the human-copy review queue.

    estimated_review_load is an explicit workload tuple — not a quality score:
      (unreviewed, review_recommended_unreviewed, needs_review)
    """

    family_key: str
    sign_name: str
    total_facts: int
    approved_override: int
    approved_raw: int
    needs_review: int
    unreviewed: int
    review_recommended_unreviewed: int
    reviewed_count: int
    presentation_ready_count: int
    review_coverage: float
    presentation_ready_coverage: float
    is_review_complete: bool
    is_presentation_ready_complete: bool
    estimated_review_load: tuple[int, int, int]


@dataclass(frozen=True)
class NeedsReviewBacklogItem:
    fact_id: str
    family_key: str
    canonical_text: str


@dataclass(frozen=True)
class SuggestedSignReviewBatch:
    batch_index: int
    family_keys: tuple[str, ...]
    sign_names: tuple[str, ...]
    unreviewed_workload: int
    review_recommended_workload: int


@dataclass(frozen=True)
class SignReviewQueueReport:
    all_sign_families: tuple[SignReviewQueueEntry, ...]
    completed_families: tuple[SignReviewQueueEntry, ...]
    incomplete_queue: tuple[SignReviewQueueEntry, ...]
    suggested_batches: tuple[SuggestedSignReviewBatch, ...]
    needs_review_backlog: tuple[NeedsReviewBacklogItem, ...]
    sign_total_facts: int
    sign_reviewed_facts: int
    sign_presentation_ready_facts: int
    sign_unreviewed_facts: int
    sign_needs_review_facts: int
    review_complete_family_count: int
    presentation_ready_complete_family_count: int


def _sign_review_priority_key(entry: SignReviewQueueEntry) -> tuple:
    """Maintenance workload priority — not astrology importance.

    Order incomplete families by:
      1. higher unreviewed
      2. higher review_recommended_unreviewed
      3. lower presentation_ready_coverage
      4. stable family_key
    """
    return (
        -entry.unreviewed,
        -entry.review_recommended_unreviewed,
        entry.presentation_ready_coverage,
        entry.family_key,
    )


def _family_to_sign_queue_entry(family: HumanCopyFamilyCoverage) -> SignReviewQueueEntry:
    return SignReviewQueueEntry(
        family_key=family.family_key,
        sign_name=family.factor_key,
        total_facts=family.total_facts,
        approved_override=family.approved_override,
        approved_raw=family.approved_raw,
        needs_review=family.needs_review,
        unreviewed=family.unreviewed,
        review_recommended_unreviewed=family.review_recommended_unreviewed,
        reviewed_count=family.reviewed_count,
        presentation_ready_count=family.presentation_ready_count,
        review_coverage=family.review_coverage,
        presentation_ready_coverage=family.presentation_ready_coverage,
        is_review_complete=family.unreviewed == 0,
        is_presentation_ready_complete=(
            family.presentation_ready_count == family.total_facts
        ),
        estimated_review_load=(
            family.unreviewed,
            family.review_recommended_unreviewed,
            family.needs_review,
        ),
    )


def _pack_sign_batches(
    incomplete: Sequence[SignReviewQueueEntry],
) -> tuple[SuggestedSignReviewBatch, ...]:
    """Workload-balance incomplete signs: heaviest remaining + lightest remaining.

    Maintenance batching only — not astrology similarity / element / modality.

    Algorithm:
      1. Start from the already priority-sorted incomplete queue
         (non-increasing unreviewed workload).
      2. Pair the highest remaining workload family with the lowest remaining
         workload family (front + back of the remaining list).
      3. Remove both; emit that pair as one batch (heaviest first).
      4. Repeat.
      5. If an odd count remains, the final middle family is a singleton batch.
    """
    remaining = list(incomplete)
    chunks: list[tuple[SignReviewQueueEntry, ...]] = []
    while remaining:
        if len(remaining) == 1:
            chunks.append((remaining.pop(0),))
            break
        heaviest = remaining.pop(0)
        lightest = remaining.pop(-1)
        chunks.append((heaviest, lightest))

    batches: list[SuggestedSignReviewBatch] = []
    for batch_index, members in enumerate(chunks, start=1):
        batches.append(
            SuggestedSignReviewBatch(
                batch_index=batch_index,
                family_keys=tuple(member.family_key for member in members),
                sign_names=tuple(member.sign_name for member in members),
                unreviewed_workload=sum(member.unreviewed for member in members),
                review_recommended_workload=sum(
                    member.review_recommended_unreviewed for member in members
                ),
            )
        )
    return tuple(batches)


def build_sign_review_queue(
    report: HumanCopyCatalogReport | None = None,
) -> SignReviewQueueReport:
    """Build deterministic Mercury sign-family human-copy review queue."""
    catalog = report if report is not None else build_human_copy_catalog()
    sign_families = {
        family.family_key: family
        for family in catalog.families
        if family.factor_type == "sign"
    }
    missing = [key for key in SIGN_FAMILY_KEYS if key not in sign_families]
    if missing:
        raise HumanCopyCatalogError(f"Missing sign families in catalog: {missing}")

    all_entries = tuple(
        _family_to_sign_queue_entry(sign_families[key]) for key in SIGN_FAMILY_KEYS
    )
    completed = tuple(entry for entry in all_entries if entry.is_review_complete)
    incomplete = tuple(
        sorted(
            (entry for entry in all_entries if not entry.is_review_complete),
            key=_sign_review_priority_key,
        )
    )
    backlog = tuple(
        NeedsReviewBacklogItem(
            fact_id=entry.fact_id,
            family_key=entry.family_key,
            canonical_text=entry.canonical_text,
        )
        for entry in catalog.entries
        if entry.review_status == STATUS_NEEDS_REVIEW and entry.factor_type == "sign"
    )
    backlog = tuple(sorted(backlog, key=lambda item: (item.family_key, item.fact_id)))

    return SignReviewQueueReport(
        all_sign_families=all_entries,
        completed_families=completed,
        incomplete_queue=incomplete,
        suggested_batches=_pack_sign_batches(incomplete),
        needs_review_backlog=backlog,
        sign_total_facts=sum(entry.total_facts for entry in all_entries),
        sign_reviewed_facts=sum(entry.reviewed_count for entry in all_entries),
        sign_presentation_ready_facts=sum(
            entry.presentation_ready_count for entry in all_entries
        ),
        sign_unreviewed_facts=sum(entry.unreviewed for entry in all_entries),
        sign_needs_review_facts=sum(entry.needs_review for entry in all_entries),
        review_complete_family_count=sum(
            1 for entry in all_entries if entry.is_review_complete
        ),
        presentation_ready_complete_family_count=sum(
            1 for entry in all_entries if entry.is_presentation_ready_complete
        ),
    )


def format_sign_review_queue(queue: SignReviewQueueReport) -> str:
    """Developer-readable Mercury sign human-copy review queue."""
    lines = [
        "MERCURY SIGN HUMAN-COPY REVIEW QUEUE",
        "",
        "Priority = maintenance workload only "
        "(unreviewed, recommended-unreviewed, ready-coverage). "
        "Not astrology importance.",
        "",
        f"Sign families: {len(queue.all_sign_families)}",
        f"Review-complete: {queue.review_complete_family_count}",
        f"Presentation-ready-complete: "
        f"{queue.presentation_ready_complete_family_count}",
        f"Sign facts: {queue.sign_total_facts}",
        f"Sign reviewed facts: {queue.sign_reviewed_facts}",
        f"Sign presentation-ready facts: {queue.sign_presentation_ready_facts}",
        f"Sign unreviewed facts: {queue.sign_unreviewed_facts}",
        f"Sign needs_review facts: {queue.sign_needs_review_facts}",
        "",
        "Completed:",
    ]
    if not queue.completed_families:
        lines.append("  (none)")
    else:
        for entry in queue.completed_families:
            ready_note = (
                "ready-complete"
                if entry.is_presentation_ready_complete
                else (
                    f"ready {entry.presentation_ready_count}/"
                    f"{entry.total_facts}"
                )
            )
            lines.append(
                f"  {entry.sign_name:<12} "
                f"{entry.reviewed_count}/{entry.total_facts} reviewed   "
                f"{ready_note}"
            )

    lines.append("")
    lines.append("Remaining queue:")
    if not queue.incomplete_queue:
        lines.append("  (none)")
    else:
        for index, entry in enumerate(queue.incomplete_queue, start=1):
            lines.append(f"{index}. {entry.sign_name}")
            lines.append(f"   family: {entry.family_key}")
            lines.append(f"   total: {entry.total_facts}")
            lines.append(f"   unreviewed: {entry.unreviewed}")
            lines.append(
                f"   recommended-unreviewed: {entry.review_recommended_unreviewed}"
            )
            lines.append(f"   needs_review: {entry.needs_review}")
            lines.append(
                f"   reviewed: {entry.reviewed_count}/{entry.total_facts} "
                f"({entry.review_coverage:.0%})"
            )
            lines.append(
                f"   ready: {entry.presentation_ready_count}/{entry.total_facts} "
                f"({entry.presentation_ready_coverage:.0%})"
            )
            lines.append(
                f"   estimated_review_load: "
                f"unreviewed={entry.estimated_review_load[0]}, "
                f"recommended={entry.estimated_review_load[1]}, "
                f"needs_review={entry.estimated_review_load[2]}"
            )

    lines.append("")
    lines.append(
        "Suggested workload-balanced review batches "
        "(heaviest + lightest remaining; not semantic / astrology groups):"
    )
    if not queue.suggested_batches:
        lines.append("  (none)")
    else:
        for batch in queue.suggested_batches:
            names = " + ".join(batch.sign_names)
            lines.append(
                f"  Batch {batch.batch_index}: {names} "
                f"(unreviewed={batch.unreviewed_workload}, "
                f"recommended={batch.review_recommended_workload})"
            )

    lines.append("")
    lines.append("Needs-review backlog (sign families):")
    if not queue.needs_review_backlog:
        lines.append("  (none)")
    else:
        for item in queue.needs_review_backlog:
            sign = item.family_key.split(":", 1)[-1]
            lines.append(f"  {sign} · {item.fact_id}")
            lines.append(f"    {item.canonical_text}")

    return "\n".join(lines)
