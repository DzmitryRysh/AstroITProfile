"""Mars Lesson 9 sign, house, retrograde-motion, and aspect source knowledge.

Sign / house / motion are Lesson 9. Aspects add Lesson 9 tense blockers plus
Bioastrology pair-level aptitude claims. No repeat specs, strength score,
or human copy. Direct Mars has no invented interpretation pack.
"""

from __future__ import annotations

from dataclasses import dataclass

MARS_CATEGORIES = frozenset(
    {
        "action_start",
        "initiative",
        "execution",
        "work_rhythm",
        "effort",
        "continuation",
        "obstacle",
        "conflict",
        "stuck_blocker",
        "work_conditions",
        "watchout",
        "compensation",
        "professional_association",
        "source_specific",
    }
)

MARS_SCOPES = frozenset(
    {
        "WORK_CORE",
        "WORK_DETAIL",
        "PERSONAL_MARS",
        "SOURCE_ONLY",
    }
)

MARS_POLARITIES = frozenset({"strength", "risk", "neutral", "conditional"})
WORK_PROFILE_SCOPES = frozenset({"WORK_CORE", "WORK_DETAIL"})

REF_ARIES = "lesson9_mars_sign_aries"
REF_TAURUS = "lesson9_mars_sign_taurus"
REF_GEMINI = "lesson9_mars_sign_gemini"
REF_CANCER = "lesson9_mars_sign_cancer"
REF_LEO = "lesson9_mars_sign_leo"
REF_VIRGO = "lesson9_mars_sign_virgo"
REF_LIBRA = "lesson9_mars_sign_libra"
REF_SCORPIO = "lesson9_mars_sign_scorpio"
REF_SAGITTARIUS = "lesson9_mars_sign_sagittarius"
REF_CAPRICORN = "lesson9_mars_sign_capricorn"
REF_AQUARIUS = "lesson9_mars_sign_aquarius"
REF_PISCES = "lesson9_mars_sign_pisces"


@dataclass(frozen=True)
class MarsSourceFactDef:
    id: str
    factor_type: str
    factor_key: str
    text: str
    source_reference: str
    category: str
    scope: str
    polarity: str
    tags: tuple[str, ...] = ()
    activation_condition: str | None = None
    unresolved: bool = False


def _f(
    fact_id: str,
    factor_key: str,
    category: str,
    text: str,
    polarity: str,
    scope: str,
    *tags: str,
    source_reference: str,
    factor_type: str = "sign",
    activation_condition: str | None = None,
    unresolved: bool = False,
) -> MarsSourceFactDef:
    return MarsSourceFactDef(
        id=fact_id,
        factor_type=factor_type,
        factor_key=factor_key,
        text=text,
        source_reference=source_reference,
        category=category,
        scope=scope,
        polarity=polarity,
        tags=tags,
        activation_condition=activation_condition,
        unresolved=unresolved,
    )


ARIES_PACK: tuple[MarsSourceFactDef, ...] = (
    _f("mars_aries_large_energy_reserve", "Aries", "effort",
       "Very large reserve of energy.",
       "strength", "WORK_CORE", source_reference=REF_ARIES),
    _f("mars_aries_lightning_fast_mobilization", "Aries", "action_start",
       "Lightning-fast mobilization; activity focuses into one point.",
       "strength", "WORK_CORE", "fast_start", source_reference=REF_ARIES),
    _f("mars_aries_acts_first_impulsive_will", "Aries", "action_start",
       "Acts first and thinks afterward; strong but poorly controlled will, "
       "expressed in impulses and bursts.",
       "strength", "WORK_CORE", source_reference=REF_ARIES),
    _f("mars_aries_high_involvement_hard_to_stay_detached", "Aries", "effort",
       "Very high involvement; difficult to act calmly and detached.",
       "strength", "WORK_CORE", source_reference=REF_ARIES),
    _f("mars_aries_inactive_then_one_assault", "Aries", "work_rhythm",
       "May stay inactive for a long time, then complete a large volume in one assault.",
       "conditional", "WORK_CORE", source_reference=REF_ARIES),
    _f("mars_aries_tolerates_large_physical_loads", "Aries", "effort",
       "Can tolerate large physical loads.",
       "strength", "WORK_CORE", source_reference=REF_ARIES),
    _f("mars_aries_overcome_life_difficulties", "Aries", "obstacle",
       "Source claims a strong ability to overcome life difficulties; not a validated competency.",
       "strength", "WORK_DETAIL", source_reference=REF_ARIES),
    _f("mars_aries_warrior_assault_attacks_first", "Aries", "conflict",
       "Warrior-assault style: attacks first, fast and powerfully.",
       "strength", "WORK_CORE", source_reference=REF_ARIES),
    _f("mars_aries_underestimates_difficulty_overestimates_capacity", "Aries", "watchout",
       "Underestimates difficulty and overestimates own capacity.",
       "risk", "WORK_CORE", source_reference=REF_ARIES),
    _f("mars_aries_aggression_rudeness_impatience", "Aries", "watchout",
       "Aggression / rudeness / impatience.",
       "risk", "WORK_CORE", source_reference=REF_ARIES),
    _f("mars_aries_lack_of_consideration_for_others", "Aries", "watchout",
       "Lack of consideration for others.",
       "risk", "WORK_CORE", source_reference=REF_ARIES),
    _f("mars_aries_force_or_pressure_others_to_work", "Aries", "conflict",
       "May force or pressure others to work.",
       "risk", "WORK_CORE", source_reference=REF_ARIES),
    _f("mars_aries_self_assertion_independent_action", "Aries", "initiative",
       "Strong drive toward self-assertion and doing things independently.",
       "strength", "WORK_CORE", "self_starting", source_reference=REF_ARIES),
    _f("mars_aries_comp_channel_activation_into_work_not_conflict", "Aries", "compensation",
       "Source compensation: channel activation into work or exercise rather than conflict; "
       "discharge excess aggressive impulse through work or sport.",
       "neutral", "WORK_DETAIL", source_reference=REF_ARIES),
    _f("mars_aries_comp_sport_competition_physical_work", "Aries", "compensation",
       "Source compensation: sport, competition, physical work.",
       "neutral", "WORK_DETAIL", source_reference=REF_ARIES),
    _f("mars_aries_comp_short_pause_before_acting", "Aries", "compensation",
       "Source compensation: a short pause before acting.",
       "neutral", "WORK_DETAIL", source_reference=REF_ARIES),
    _f("mars_aries_comp_divide_large_tasks_into_sprints", "Aries", "compensation",
       "Source compensation: divide large tasks into short sprints.",
       "neutral", "WORK_DETAIL", source_reference=REF_ARIES),
)

TAURUS_PACK: tuple[MarsSourceFactDef, ...] = (
    _f("mars_taurus_will_through_stubborn_persistence", "Taurus", "continuation",
       "Will is expressed through resistance / stubborn persistence.",
       "strength", "WORK_CORE", source_reference=REF_TAURUS),
    _f("mars_taurus_acts_because_activity_is_enjoyable", "Taurus", "action_start",
       "Acts because the activity is enjoyable.",
       "strength", "WORK_CORE", source_reference=REF_TAURUS),
    _f("mars_taurus_constructive_tangible_result", "Taurus", "execution",
       "Constructive activity aimed at a tangible result.",
       "strength", "WORK_CORE", source_reference=REF_TAURUS),
    _f("mars_taurus_heavy_investment_in_creative_work", "Taurus", "effort",
       "Can invest heavily in creative work.",
       "strength", "WORK_CORE", source_reference=REF_TAURUS),
    _f("mars_taurus_capable_talented_worker", "Taurus", "execution",
       "Source describes a capable / talented worker; not a hiring or competency claim.",
       "strength", "WORK_DETAIL", source_reference=REF_TAURUS),
    _f("mars_taurus_defender_fortress_does_not_attack_first", "Taurus", "conflict",
       "Defender-fortress style; does not attack first. Reaction to aggression may be delayed; "
       "once pushed too far, the reaction may become very forceful.",
       "strength", "WORK_CORE", source_reference=REF_TAURUS),
    _f("mars_taurus_difficulty_activating_at_right_time", "Taurus", "stuck_blocker",
       "Main difficulty is activating at the right time.",
       "risk", "WORK_CORE", source_reference=REF_TAURUS),
    _f("mars_taurus_may_change_jobs_when_conditions_feel_wrong", "Taurus", "work_conditions",
       "May repeatedly change jobs because conditions feel wrong.",
       "risk", "WORK_CORE", source_reference=REF_TAURUS),
    _f("mars_taurus_comfort_affects_willingness_to_act", "Taurus", "work_conditions",
       "Comfort strongly affects willingness to act.",
       "conditional", "WORK_CORE", source_reference=REF_TAURUS),
    _f("mars_taurus_freeze_if_attacked_unprepared", "Taurus", "conflict",
       "May freeze when attacked unexpectedly unless prepared or expert.",
       "risk", "WORK_CORE", source_reference=REF_TAURUS),
    _f("mars_taurus_extreme_stubbornness_difficulty_switching", "Taurus", "continuation",
       "Extreme stubbornness / difficulty switching.",
       "risk", "WORK_CORE", source_reference=REF_TAURUS),
    _f("mars_taurus_hedonism_can_interfere_with_work", "Taurus", "watchout",
       "Hedonism can interfere with work.",
       "risk", "WORK_CORE", source_reference=REF_TAURUS),
    _f("mars_taurus_wait_for_mood_comfort_or_inspiration", "Taurus", "action_start",
       "May wait for mood, comfort, or inspiration before beginning.",
       "risk", "WORK_CORE", source_reference=REF_TAURUS),
    _f("mars_taurus_comp_start_with_one_small_physical_step", "Taurus", "compensation",
       "Source compensation: start with one small physical / action step rather than waiting "
       "for inspiration.",
       "neutral", "WORK_DETAIL", source_reference=REF_TAURUS),
    _f("mars_taurus_comp_create_comfortable_work_conditions", "Taurus", "compensation",
       "Source compensation: create comfortable work conditions.",
       "neutral", "WORK_DETAIL", source_reference=REF_TAURUS),
    _f("mars_taurus_comp_body_manual_practices", "Taurus", "compensation",
       "Source compensation: body / manual practices.",
       "neutral", "WORK_DETAIL", source_reference=REF_TAURUS),
    _f("mars_taurus_comp_delay_conflict_response_when_useful", "Taurus", "compensation",
       "Source compensation: delay conflict response when useful.",
       "neutral", "WORK_DETAIL", source_reference=REF_TAURUS),
)

GEMINI_PACK: tuple[MarsSourceFactDef, ...] = (
    _f("mars_gemini_adapts_to_different_work", "Gemini", "execution",
       "Physically not necessarily strongest, but adapts well to different work.",
       "strength", "WORK_CORE", source_reference=REF_GEMINI),
    _f("mars_gemini_information_oriented_action", "Gemini", "execution",
       "Activity is strongly information-oriented.",
       "strength", "WORK_CORE", source_reference=REF_GEMINI),
    _f("mars_gemini_orients_quickly_in_information_flows", "Gemini", "execution",
       "Quickly orients within flows of information. This is action-orientation, not fast thinking.",
       "strength", "WORK_CORE", source_reference=REF_GEMINI),
    _f("mars_gemini_high_mobility", "Gemini", "work_rhythm",
       "High mobility.",
       "strength", "WORK_CORE", source_reference=REF_GEMINI),
    _f("mars_gemini_action_through_words_persuasion", "Gemini", "execution",
       "May achieve action through words / persuasion.",
       "strength", "WORK_CORE", source_reference=REF_GEMINI),
    _f("mars_gemini_uses_contacts_to_get_things_done", "Gemini", "execution",
       "Often uses contacts and connections to get things done.",
       "strength", "WORK_CORE", source_reference=REF_GEMINI),
    _f("mars_gemini_conflict_through_information_and_facts", "Gemini", "conflict",
       "Conflict operates through information and knowledge; word / argument / fact can function "
       "as the main weapon.",
       "strength", "WORK_CORE", source_reference=REF_GEMINI),
    _f("mars_gemini_monotony_tension_fragmented_work", "Gemini", "work_rhythm",
       "Monotony creates tension; work may be done in fragments.",
       "risk", "WORK_CORE", source_reference=REF_GEMINI),
    _f("mars_gemini_superficiality_insufficient_concentration", "Gemini", "execution",
       "Superficiality / insufficient concentration.",
       "risk", "WORK_CORE", source_reference=REF_GEMINI),
    _f("mars_gemini_effort_scattered_across_many_tasks", "Gemini", "effort",
       "Effort scattered across many tasks.",
       "risk", "WORK_CORE", source_reference=REF_GEMINI),
    _f("mars_gemini_indecision_wants_more_information", "Gemini", "stuck_blocker",
       "Indecision before action because more thinking / information is wanted.",
       "risk", "WORK_CORE", source_reference=REF_GEMINI),
    _f("mars_gemini_chaotic_fussy_activity", "Gemini", "work_rhythm",
       "Chaotic / fussy activity.",
       "risk", "WORK_CORE", source_reference=REF_GEMINI),
    _f("mars_gemini_many_words_insufficient_action", "Gemini", "execution",
       "Many words but insufficient action.",
       "risk", "WORK_CORE", source_reference=REF_GEMINI),
    _f("mars_gemini_lying_distortion_of_facts_shadow", "Gemini", "watchout",
       "Source includes lying / distortion of facts as a shadow; not a deterministic accusation.",
       "risk", "WORK_CORE", source_reference=REF_GEMINI),
    _f("mars_gemini_loses_main_goal_among_contacts_tasks", "Gemini", "watchout",
       "May lose the main goal among contacts / tasks.",
       "risk", "WORK_CORE", source_reference=REF_GEMINI),
    _f("mars_gemini_unethical_information_pressure_gossip", "Gemini", "watchout",
       "Unethical information pressure / gossip / manipulation as a shadow; "
       "not a deterministic accusation.",
       "risk", "WORK_CORE", source_reference=REF_GEMINI),
    _f("mars_gemini_comp_conversation_helps_activate_work", "Gemini", "compensation",
       "Source compensation: conversation, contact, or reading may help activate work.",
       "neutral", "WORK_DETAIL", source_reference=REF_GEMINI),
    _f("mars_gemini_comp_short_focus_intervals", "Gemini", "compensation",
       "Source compensation: short focus intervals.",
       "neutral", "WORK_DETAIL", source_reference=REF_GEMINI),
    _f("mars_gemini_comp_lists_to_structure_action", "Gemini", "compensation",
       "Source compensation: lists to structure action.",
       "neutral", "WORK_DETAIL", source_reference=REF_GEMINI),
    _f("mars_gemini_comp_variety_and_communication_contexts", "Gemini", "compensation",
       "Source compensation: work contexts with variety and communication.",
       "neutral", "WORK_DETAIL", source_reference=REF_GEMINI),
    _f("mars_gemini_comp_conflict_reduce_verbal_sprawl", "Gemini", "compensation",
       "Source compensation: in conflict, reduce verbal sprawl to the core point.",
       "neutral", "WORK_DETAIL", source_reference=REF_GEMINI),
)

CANCER_PACK: tuple[MarsSourceFactDef, ...] = (
    _f("mars_cancer_action_generated_through_emotion", "Cancer", "effort",
       "Energy / action is strongly generated through emotion and needs emotional stimulus.",
       "conditional", "WORK_CORE", source_reference=REF_CANCER),
    _f("mars_cancer_action_depends_on_mood", "Cancer", "action_start",
       "Ability to act depends on mood.",
       "conditional", "WORK_CORE", "mood_dependent_action", source_reference=REF_CANCER),
    _f("mars_cancer_works_best_in_familiar_safe_conditions", "Cancer", "work_conditions",
       "Works best in familiar / safe conditions.",
       "strength", "WORK_CORE", source_reference=REF_CANCER),
    _f("mars_cancer_adapts_under_pressure", "Cancer", "effort",
       "Can adapt under pressure.",
       "strength", "WORK_CORE", source_reference=REF_CANCER),
    _f("mars_cancer_soft_style_lacks_direct_forceful_push", "Cancer", "execution",
       "Lacks a direct forceful push; action style can be soft rather than forceful.",
       "neutral", "WORK_CORE", source_reference=REF_CANCER),
    _f("mars_cancer_conservative_habit_work", "Cancer", "execution",
       "Conservative in work; often acts through habit.",
       "strength", "WORK_CORE", source_reference=REF_CANCER),
    _f("mars_cancer_may_work_from_home", "Cancer", "work_conditions",
       "May naturally work from home.",
       "neutral", "WORK_CORE", source_reference=REF_CANCER),
    _f("mars_cancer_defends_emotional_attachments", "Cancer", "conflict",
       "Strongly defends people or things with emotional attachment.",
       "strength", "WORK_CORE", source_reference=REF_CANCER),
    _f("mars_cancer_intuition_for_danger_and_withdrawal", "Cancer", "obstacle",
       "Source describes strong intuition for danger and knowing when to withdraw; "
       "not a validated competency.",
       "strength", "WORK_DETAIL", source_reference=REF_CANCER),
    _f("mars_cancer_important_decisions_may_be_difficult", "Cancer", "stuck_blocker",
       "Important decisions may be difficult.",
       "risk", "WORK_CORE", source_reference=REF_CANCER),
    _f("mars_cancer_avoids_direct_confrontation", "Cancer", "conflict",
       "Avoids direct confrontation.",
       "risk", "WORK_CORE", source_reference=REF_CANCER),
    _f("mars_cancer_low_willingness_to_take_risks", "Cancer", "watchout",
       "Low willingness to take risks.",
       "risk", "WORK_CORE", source_reference=REF_CANCER),
    _f("mars_cancer_may_be_influenced_through_pity", "Cancer", "watchout",
       "May be influenced through pity.",
       "risk", "WORK_CORE", source_reference=REF_CANCER),
    _f("mars_cancer_passivity_waiting_for_others_conditions", "Cancer", "stuck_blocker",
       "Passivity / waiting for others to create conditions.",
       "risk", "WORK_CORE", source_reference=REF_CANCER),
    _f("mars_cancer_unstable_rhythm_activity_and_inactivity", "Cancer", "work_rhythm",
       "Unstable rhythm: activity alternates with inactivity.",
       "risk", "WORK_CORE", source_reference=REF_CANCER),
    _f("mars_cancer_argues_when_personally_affected", "Cancer", "conflict",
       "May argue mainly when personally / emotionally affected.",
       "conditional", "WORK_CORE", source_reference=REF_CANCER),
    _f("mars_cancer_may_provoke_or_display_toughness", "Cancer", "conflict",
       "May provoke or display toughness.",
       "risk", "WORK_CORE", source_reference=REF_CANCER),
    _f("mars_cancer_resentment_revenge_shadow", "Cancer", "watchout",
       "Resentment / revenge can appear as a shadow; not a deterministic accusation.",
       "risk", "WORK_CORE", source_reference=REF_CANCER),
    _f("mars_cancer_comp_psychologically_safe_work_conditions", "Cancer", "compensation",
       "Source compensation: create psychologically safe work conditions.",
       "neutral", "WORK_DETAIL", source_reference=REF_CANCER),
    _f("mars_cancer_comp_connect_action_to_personal_care", "Cancer", "compensation",
       "Source compensation: connect action to care / responsibility for something "
       "personally meaningful.",
       "neutral", "WORK_DETAIL", source_reference=REF_CANCER),
)

LEO_PACK: tuple[MarsSourceFactDef, ...] = (
    _f("mars_leo_i_will_do_it_myself", "Leo", "initiative",
       "Strong “I will do it myself” orientation.",
       "strength", "WORK_CORE", "self_starting", source_reference=REF_LEO),
    _f("mars_leo_prefers_others_not_interfere", "Leo", "work_conditions",
       "Prefers others not to interfere unnecessarily.",
       "strength", "WORK_CORE", source_reference=REF_LEO),
    _f("mars_leo_work_well_enough_to_be_appreciated", "Leo", "execution",
       "Aims to do work well enough to be appreciated.",
       "strength", "WORK_CORE", source_reference=REF_LEO),
    _f("mars_leo_slower_more_reliable_among_fire_signs", "Leo", "work_rhythm",
       "Among fire signs, slower but more reliable / constant execution.",
       "strength", "WORK_CORE", source_reference=REF_LEO),
    _f("mars_leo_willingly_assumes_responsibility", "Leo", "execution",
       "Willingly assumes responsibility.",
       "strength", "WORK_CORE", source_reference=REF_LEO),
    _f("mars_leo_work_should_feel_prestigious", "Leo", "work_conditions",
       "Work should feel prestigious according to personal criteria.",
       "conditional", "WORK_CORE", source_reference=REF_LEO),
    _f("mars_leo_authorship_creative_ownership", "Leo", "execution",
       "Likes authorship / creative ownership.",
       "strength", "WORK_CORE", source_reference=REF_LEO),
    _f("mars_leo_can_work_publicly", "Leo", "work_conditions",
       "Can work publicly.",
       "strength", "WORK_CORE", source_reference=REF_LEO),
    _f("mars_leo_not_easily_provoked_into_petty_conflict", "Leo", "conflict",
       "Not easily provoked into petty conflict.",
       "strength", "WORK_CORE", source_reference=REF_LEO),
    _f("mars_leo_conflict_dignity_and_distance", "Leo", "conflict",
       "Conflict style emphasizes dignity and distance.",
       "strength", "WORK_CORE", source_reference=REF_LEO),
    _f("mars_leo_fights_mainly_for_own_interests", "Leo", "conflict",
       "Tends to fight mainly for own interests.",
       "neutral", "WORK_CORE", source_reference=REF_LEO),
    _f("mars_leo_recognition_seeking_shadow", "Leo", "watchout",
       "May act for admiration and expect applause / recognition; source includes "
       "narcissistic recognition-seeking as a shadow, not a diagnosis.",
       "risk", "WORK_CORE", source_reference=REF_LEO),
    _f("mars_leo_little_energy_for_unloved_work", "Leo", "effort",
       "Little energy for work that feels unloved.",
       "risk", "WORK_CORE", source_reference=REF_LEO),
    _f("mars_leo_overconfidence_excessive_ambition", "Leo", "watchout",
       "Overconfidence / excessive ambition.",
       "risk", "WORK_CORE", source_reference=REF_LEO),
    _f("mars_leo_loses_energy_without_recognition", "Leo", "effort",
       "Can lose energy if recognition is absent.",
       "risk", "WORK_CORE", source_reference=REF_LEO),
    _f("mars_leo_dislikes_secondary_supporting_roles", "Leo", "work_conditions",
       "Dislikes secondary / supporting roles.",
       "risk", "WORK_CORE", source_reference=REF_LEO),
    _f("mars_leo_comp_challenge_activates_effort", "Leo", "compensation",
       "Source compensation: challenge can activate effort.",
       "neutral", "WORK_DETAIL", source_reference=REF_LEO),
    _f("mars_leo_comp_visible_authorship_leadership_contexts", "Leo", "compensation",
       "Source compensation: choose work with visible authorship, leadership, or creative "
       "expression where appropriate; not a career assignment.",
       "neutral", "WORK_DETAIL", source_reference=REF_LEO),
    _f("mars_leo_comp_internal_recognition", "Leo", "compensation",
       "Source compensation: develop internal recognition rather than depending only on "
       "external praise.",
       "neutral", "WORK_DETAIL", source_reference=REF_LEO),
    _f("mars_leo_comp_disagreement_is_not_loss_of_dignity", "Leo", "compensation",
       "Source compensation: do not equate disagreement with loss of dignity.",
       "neutral", "WORK_DETAIL", source_reference=REF_LEO),
)

VIRGO_PACK: tuple[MarsSourceFactDef, ...] = (
    _f("mars_virgo_highly_productive_mars", "Virgo", "effort",
       "Source calls this a highly productive Mars; not a strength score or ranking.",
       "strength", "WORK_DETAIL", source_reference=REF_VIRGO),
    _f("mars_virgo_versatile_hands_on_worker", "Virgo", "execution",
       "Versatile hands-on worker.",
       "strength", "WORK_CORE", "hands_on_execution", source_reference=REF_VIRGO),
    _f("mars_virgo_multitasking_in_action", "Virgo", "execution",
       "Multitasking in action.",
       "strength", "WORK_CORE", source_reference=REF_VIRGO),
    _f("mars_virgo_needs_hands_occupied", "Virgo", "work_rhythm",
       "May need hands to remain occupied.",
       "conditional", "WORK_CORE", source_reference=REF_VIRGO),
    _f("mars_virgo_self_assertion_through_labor", "Virgo", "execution",
       "Self-assertion through labor.",
       "strength", "WORK_CORE", source_reference=REF_VIRGO),
    _f("mars_virgo_handles_routine_monotonous_work", "Virgo", "execution",
       "Handles routine and monotonous work well.",
       "strength", "WORK_CORE", "routine_execution", source_reference=REF_VIRGO),
    _f("mars_virgo_analyzes_previous_work_for_mistakes", "Virgo", "execution",
       "Analyzes previous work for mistakes. This is work review, not analytical thinking.",
       "strength", "WORK_CORE", source_reference=REF_VIRGO),
    _f("mars_virgo_self_criticism_generates_more_effort", "Virgo", "effort",
       "Self-criticism may generate more effort.",
       "conditional", "WORK_CORE", source_reference=REF_VIRGO),
    _f("mars_virgo_conflict_uses_facts_logic_details", "Virgo", "conflict",
       "Conflict style uses facts rather than physical force; argument relies on logic / details.",
       "strength", "WORK_CORE", source_reference=REF_VIRGO),
    _f("mars_virgo_absorbed_in_details_misses_main_task", "Virgo", "execution",
       "Strategic weakness: may become absorbed in details and miss the main task; "
       "detail fixation at the expense of the larger objective.",
       "risk", "WORK_CORE", source_reference=REF_VIRGO),
    _f("mars_virgo_critical_of_others_sensitive_to_criticism", "Virgo", "watchout",
       "Critical of others' work and sensitive to criticism of own work.",
       "risk", "WORK_CORE", source_reference=REF_VIRGO),
    _f("mars_virgo_resistance_to_new_methods", "Virgo", "watchout",
       "Resistance to new methods / change.",
       "risk", "WORK_CORE", source_reference=REF_VIRGO),
    _f("mars_virgo_self_criticism_not_good_enough", "Virgo", "watchout",
       "Self-criticism: “not good enough.”",
       "risk", "WORK_CORE", source_reference=REF_VIRGO),
    _f("mars_virgo_comp_divide_work_into_discrete_units", "Virgo", "compensation",
       "Source compensation: divide work into discrete units.",
       "neutral", "WORK_DETAIL", source_reference=REF_VIRGO),
    _f("mars_virgo_comp_identify_what_is_actually_important", "Virgo", "compensation",
       "Source compensation: repeatedly identify what is actually important.",
       "neutral", "WORK_DETAIL", source_reference=REF_VIRGO),
    _f("mars_virgo_comp_body_fine_motor_manual_practices", "Virgo", "compensation",
       "Source compensation: body / fine-motor / manual practices.",
       "neutral", "WORK_DETAIL", source_reference=REF_VIRGO),
    _f("mars_virgo_comp_good_enough_rather_than_perfect", "Virgo", "compensation",
       "Source compensation: practice “good enough” rather than perfect.",
       "neutral", "WORK_DETAIL", source_reference=REF_VIRGO),
)

LIBRA_PACK: tuple[MarsSourceFactDef, ...] = (
    _f("mars_libra_ability_to_manage_people", "Libra", "execution",
       "Source describes an ability to manage people; not a hiring or leadership assignment.",
       "strength", "WORK_DETAIL", source_reference=REF_LIBRA),
    _f("mars_libra_negotiation_dispute_management_orientation", "Libra", "execution",
       "Negotiation / dispute / management orientation.",
       "strength", "WORK_CORE", source_reference=REF_LIBRA),
    _f("mars_libra_responsible_decisions_can_be_difficult", "Libra", "stuck_blocker",
       "Responsible decisions can be difficult.",
       "risk", "WORK_CORE", source_reference=REF_LIBRA),
    _f("mars_libra_needs_partner_or_team_to_start", "Libra", "action_start",
       "May need partner / team support to start.",
       "conditional", "WORK_CORE", "needs_support_to_start", source_reference=REF_LIBRA),
    _f("mars_libra_enjoys_aesthetic_movement_dance", "Libra", "work_conditions",
       "Enjoys aesthetic movement / dance.",
       "neutral", "WORK_DETAIL", source_reference=REF_LIBRA),
    _f("mars_libra_paradoxical_conflict_advance_or_argue", "Libra", "conflict",
       "Paradoxical conflict response: may advance when retreat is better and argue when "
       "negotiation is better.",
       "risk", "WORK_CORE", source_reference=REF_LIBRA),
    _f("mars_libra_self_assertion_stays_verbal", "Libra", "execution",
       "Self-assertion may remain verbal rather than turning into action.",
       "risk", "WORK_CORE", source_reference=REF_LIBRA),
    _f("mars_libra_need_to_prove_strength", "Libra", "effort",
       "May feel a need to prove strength.",
       "conditional", "WORK_CORE", source_reference=REF_LIBRA),
    _f("mars_libra_dislikes_dirty_unpleasant_work", "Libra", "work_conditions",
       "Dislikes dirty / unpleasant work.",
       "risk", "WORK_CORE", source_reference=REF_LIBRA),
    _f("mars_libra_indecision_delayed_choice", "Libra", "stuck_blocker",
       "Indecision / delayed choice.",
       "risk", "WORK_CORE", "action_hesitation", source_reference=REF_LIBRA),
    _f("mars_libra_many_words_insufficient_action", "Libra", "execution",
       "Many words and insufficient action.",
       "risk", "WORK_CORE", source_reference=REF_LIBRA),
    _f("mars_libra_dependency_on_partner_opinion_for_action", "Libra", "action_start",
       "Dependency on partner / opinion for action.",
       "risk", "WORK_CORE", source_reference=REF_LIBRA),
    _f("mars_libra_comp_start_together_with_a_partner", "Libra", "compensation",
       "Source compensation: start together with a partner when useful.",
       "neutral", "WORK_DETAIL", source_reference=REF_LIBRA),
    _f("mars_libra_comp_train_quick_low_stakes_decisions", "Libra", "compensation",
       "Source compensation: train quick low-stakes decisions.",
       "neutral", "WORK_DETAIL", source_reference=REF_LIBRA),
    _f("mars_libra_comp_negotiation_diplomacy_contexts", "Libra", "compensation",
       "Source compensation: negotiation / diplomacy contexts; not a career assignment.",
       "neutral", "WORK_DETAIL", source_reference=REF_LIBRA),
    _f("mars_libra_comp_dance_aesthetic_physical_activity", "Libra", "compensation",
       "Source compensation: dance / aesthetic physical activity.",
       "neutral", "WORK_DETAIL", source_reference=REF_LIBRA),
)

SCORPIO_PACK: tuple[MarsSourceFactDef, ...] = (
    _f("mars_scorpio_powerful_under_overload_crisis", "Scorpio", "effort",
       "Action becomes powerful under overload / crisis / extreme conditions.",
       "strength", "WORK_CORE", "crisis_execution", source_reference=REF_SCORPIO),
    _f("mars_scorpio_willingness_to_take_risk", "Scorpio", "execution",
       "Willingness to take risk.",
       "strength", "WORK_CORE", source_reference=REF_SCORPIO),
    _f("mars_scorpio_very_high_endurance", "Scorpio", "effort",
       "Very high endurance.",
       "strength", "WORK_CORE", source_reference=REF_SCORPIO),
    _f("mars_scorpio_failures_crises_increase_activation", "Scorpio", "effort",
       "Failures / crises may increase activation.",
       "conditional", "WORK_CORE", source_reference=REF_SCORPIO),
    _f("mars_scorpio_acts_secretly_precisely_strategically", "Scorpio", "execution",
       "Can act secretly, precisely, and strategically.",
       "strength", "WORK_CORE", source_reference=REF_SCORPIO),
    _f("mars_scorpio_knows_how_to_wait", "Scorpio", "work_rhythm",
       "Knows how to wait.",
       "strength", "WORK_CORE", source_reference=REF_SCORPIO),
    _f("mars_scorpio_strategic_and_tactical_ability", "Scorpio", "execution",
       "Source describes strong strategic and tactical ability; not a validated competency.",
       "strength", "WORK_DETAIL", source_reference=REF_SCORPIO),
    _f("mars_scorpio_highly_driven_passionary_action", "Scorpio", "effort",
       "Highly driven / passionary action.",
       "strength", "WORK_CORE", source_reference=REF_SCORPIO),
    _f("mars_scorpio_conflict_exhausts_opponent", "Scorpio", "conflict",
       "Conflict strategy may focus on exhausting the opponent.",
       "neutral", "WORK_CORE", source_reference=REF_SCORPIO),
    _f("mars_scorpio_detects_weakness_reacts_quickly", "Scorpio", "conflict",
       "Detects weakness and reacts quickly.",
       "strength", "WORK_CORE", source_reference=REF_SCORPIO),
    _f("mars_scorpio_strikes_precisely_at_target", "Scorpio", "conflict",
       "Strikes precisely at the target.",
       "strength", "WORK_CORE", source_reference=REF_SCORPIO),
    _f("mars_scorpio_difficulty_living_in_calm_conditions", "Scorpio", "work_conditions",
       "Difficulty living in calm conditions.",
       "risk", "WORK_CORE", source_reference=REF_SCORPIO),
    _f("mars_scorpio_may_create_crisis_when_none_exists", "Scorpio", "watchout",
       "May create crisis when none exists.",
       "risk", "WORK_CORE", source_reference=REF_SCORPIO),
    _f("mars_scorpio_aggression_fixation", "Scorpio", "watchout",
       "Aggression / fixation; not a diagnosis.",
       "risk", "WORK_CORE", source_reference=REF_SCORPIO),
    _f("mars_scorpio_excessive_pressure_on_others", "Scorpio", "conflict",
       "Excessive pressure on others.",
       "risk", "WORK_CORE", source_reference=REF_SCORPIO),
    _f("mars_scorpio_drive_to_remake_others", "Scorpio", "watchout",
       "Drive to remake / change others.",
       "risk", "WORK_CORE", source_reference=REF_SCORPIO),
    _f("mars_scorpio_comp_sport_martial_arts_demanding_load", "Scorpio", "compensation",
       "Source compensation: sport / martial arts / demanding physical load.",
       "neutral", "WORK_DETAIL", source_reference=REF_SCORPIO),
    _f("mars_scorpio_comp_crisis_response_environments", "Scorpio", "compensation",
       "Source compensation: crisis-response professions / environments where appropriate; "
       "not a career assignment.",
       "neutral", "WORK_DETAIL", source_reference=REF_SCORPIO),
    _f("mars_scorpio_comp_not_every_obstacle_is_total_battle", "Scorpio", "compensation",
       "Source compensation: learn that not every obstacle requires total battle.",
       "neutral", "WORK_DETAIL", source_reference=REF_SCORPIO),
    _f("mars_scorpio_comp_redirect_pressure_practices", "Scorpio", "compensation",
       "Source compensation: body / psychological practices for redirecting pressure.",
       "neutral", "WORK_DETAIL", source_reference=REF_SCORPIO),
)

SAGITTARIUS_PACK: tuple[MarsSourceFactDef, ...] = (
    _f("mars_sagittarius_warrior_for_an_idea", "Sagittarius", "execution",
       "Fights for an idea / belief / ideal / social status; warrior for an idea.",
       "strength", "WORK_CORE", source_reference=REF_SAGITTARIUS),
    _f("mars_sagittarius_work_involving_knowledge_prestige", "Sagittarius", "work_conditions",
       "Attracted to work involving knowledge / prestige.",
       "strength", "WORK_CORE", source_reference=REF_SAGITTARIUS),
    _f("mars_sagittarius_nonstandard_travel_esoteric_associations", "Sagittarius",
       "professional_association",
       "Source associates nonstandard work, travel, and esoteric / hypnotic domains; "
       "not career assignments.",
       "neutral", "WORK_DETAIL", source_reference=REF_SAGITTARIUS),
    _f("mars_sagittarius_avoids_petty_fights_prefers_worthy_opposition", "Sagittarius",
       "conflict",
       "Avoids petty fights and prefers meaningful / worthy opposition.",
       "strength", "WORK_CORE", source_reference=REF_SAGITTARIUS),
    _f("mars_sagittarius_action_tied_to_morality_principles", "Sagittarius", "execution",
       "Action tied to morality / principles.",
       "strength", "WORK_CORE", source_reference=REF_SAGITTARIUS),
    _f("mars_sagittarius_strong_push_through_obstacles_when_meaningful", "Sagittarius",
       "obstacle",
       "Very strong push through obstacles when the goal is meaningful.",
       "strength", "WORK_CORE", source_reference=REF_SAGITTARIUS),
    _f("mars_sagittarius_protective_toward_weaker_people", "Sagittarius", "conflict",
       "Protective / patronizing orientation toward weaker people.",
       "neutral", "WORK_CORE", source_reference=REF_SAGITTARIUS),
    _f("mars_sagittarius_unstable_business_activity_field_changes", "Sagittarius",
       "work_rhythm",
       "Unstable business activity / major changes of field.",
       "risk", "WORK_CORE", source_reference=REF_SAGITTARIUS),
    _f("mars_sagittarius_active_periods_alternate_with_inactivity", "Sagittarius",
       "work_rhythm",
       "Active periods may alternate with inactivity.",
       "risk", "WORK_CORE", source_reference=REF_SAGITTARIUS),
    _f("mars_sagittarius_without_meaningful_goal_may_not_act", "Sagittarius", "stuck_blocker",
       "Without a meaningful goal, may not act.",
       "risk", "WORK_CORE", source_reference=REF_SAGITTARIUS),
    _f("mars_sagittarius_arrogance_authoritarianism", "Sagittarius", "watchout",
       "Arrogance / authoritarianism.",
       "risk", "WORK_CORE", source_reference=REF_SAGITTARIUS),
    _f("mars_sagittarius_unrealistic_optimism_fantasy", "Sagittarius", "watchout",
       "Unrealistic optimism / fantasy.",
       "risk", "WORK_CORE", source_reference=REF_SAGITTARIUS),
    _f("mars_sagittarius_hidden_pride_dislikes_accepting_help", "Sagittarius", "watchout",
       "Hidden pride; dislikes accepting help.",
       "risk", "WORK_CORE", source_reference=REF_SAGITTARIUS),
    _f("mars_sagittarius_lack_of_measure_overexertion", "Sagittarius", "effort",
       "Lack of measure may lead to overexertion.",
       "risk", "WORK_CORE", source_reference=REF_SAGITTARIUS),
    _f("mars_sagittarius_comp_identify_large_meaningful_goal", "Sagittarius", "compensation",
       "Source compensation: identify a large meaningful goal.",
       "neutral", "WORK_DETAIL", source_reference=REF_SAGITTARIUS),
    _f("mars_sagittarius_comp_divide_large_path_into_stages", "Sagittarius", "compensation",
       "Source compensation: divide the large path into stages.",
       "neutral", "WORK_DETAIL", source_reference=REF_SAGITTARIUS),
    _f("mars_sagittarius_comp_teaching_mentoring_international", "Sagittarius",
       "compensation",
       "Source compensation: teaching / mentoring / international contexts as source "
       "associations; not career assignments.",
       "neutral", "WORK_DETAIL", source_reference=REF_SAGITTARIUS),
    _f("mars_sagittarius_comp_learn_to_accept_help", "Sagittarius", "compensation",
       "Source compensation: learn to accept help.",
       "neutral", "WORK_DETAIL", source_reference=REF_SAGITTARIUS),
)

CAPRICORN_PACK: tuple[MarsSourceFactDef, ...] = (
    _f("mars_capricorn_economical_endurance", "Capricorn", "effort",
       "Endurance: energy is spent economically, as if it does not run out.",
       "strength", "WORK_CORE", source_reference=REF_CAPRICORN),
    _f("mars_capricorn_plans_then_executes", "Capricorn", "execution",
       "No chaotic action: first plans, then executes.",
       "strength", "WORK_CORE", "planned_execution", source_reference=REF_CAPRICORN),
    _f("mars_capricorn_unassessed_as_unjustified_risk", "Capricorn", "execution",
       "Any unread / insufficiently assessed situation is treated as unjustified risk.",
       "strength", "WORK_CORE", source_reference=REF_CAPRICORN),
    _f("mars_capricorn_patience_unhurried", "Capricorn", "work_rhythm",
       "Large reserve of patience. Does not hurry unnecessarily.",
       "strength", "WORK_CORE", source_reference=REF_CAPRICORN),
    _f("mars_capricorn_maximum_task_concentration", "Capricorn", "execution",
       "Maximum concentration on the task. Does not get distracted.",
       "strength", "WORK_CORE", "task_concentration", source_reference=REF_CAPRICORN),
    _f("mars_capricorn_strategy_and_tactics", "Capricorn", "execution",
       "Combines strategy and tactics; action is calculated.",
       "strength", "WORK_CORE", "strategic_action", source_reference=REF_CAPRICORN),
    _f("mars_capricorn_professionalism_orientation", "Capricorn", "execution",
       "Strives to develop maximum professionalism.",
       "strength", "WORK_CORE", source_reference=REF_CAPRICORN),
    _f("mars_capricorn_cold_strategist_no_anger_attack", "Capricorn", "conflict",
       "Cold-blooded strategist. Does not attack in anger — plans and waits.",
       "strength", "WORK_CORE", source_reference=REF_CAPRICORN),
    _f("mars_capricorn_conservative_proven_methods", "Capricorn", "execution",
       "Conservative: relies on what has already been developed / proven.",
       "strength", "WORK_CORE", source_reference=REF_CAPRICORN),
    _f("mars_capricorn_people_as_material_for_victory", "Capricorn", "watchout",
       "May use people coldly as material for achieving victory; not a deterministic accusation.",
       "risk", "WORK_CORE", source_reference=REF_CAPRICORN),
    _f("mars_capricorn_coldness_people_as_resource", "Capricorn", "watchout",
       "Interpersonal coldness / hardness; using people as resources.",
       "risk", "WORK_CORE", source_reference=REF_CAPRICORN),
    _f("mars_capricorn_fear_of_change", "Capricorn", "watchout",
       "Fear of change: only proven / reliable methods.",
       "risk", "WORK_CORE", source_reference=REF_CAPRICORN),
    _f("mars_capricorn_tension_stiffness", "Capricorn", "watchout",
       "Stiffness / difficulty relaxing.",
       "risk", "WORK_CORE", source_reference=REF_CAPRICORN),
    _f("mars_capricorn_comp_long_term_step_by_step", "Capricorn", "compensation",
       "Source compensation: build long-term plans and follow them step by step.",
       "neutral", "WORK_DETAIL", source_reference=REF_CAPRICORN),
    _f("mars_capricorn_comp_discipline_strategy_contexts", "Capricorn", "compensation",
       "Source compensation: work requiring discipline and strategy; not a career assignment.",
       "neutral", "WORK_DETAIL", source_reference=REF_CAPRICORN),
    _f("mars_capricorn_comp_human_factor", "Capricorn", "compensation",
       "Source compensation: remember the human factor; people are not material.",
       "neutral", "WORK_DETAIL", source_reference=REF_CAPRICORN),
    _f("mars_capricorn_comp_rest_without_guilt", "Capricorn", "compensation",
       "Source compensation: allow rest without guilt.",
       "neutral", "WORK_DETAIL", source_reference=REF_CAPRICORN),
)

AQUARIUS_PACK: tuple[MarsSourceFactDef, ...] = (
    _f("mars_aquarius_effort_toward_large_global_problems", "Aquarius", "effort",
       "Effort directed toward large / global problems.",
       "strength", "WORK_CORE", source_reference=REF_AQUARIUS),
    _f("mars_aquarius_poorly_suited_to_manual_work", "Aquarius", "execution",
       "Source says poorly suited to manual work; not a competency ranking.",
       "neutral", "WORK_CORE", source_reference=REF_AQUARIUS),
    _f("mars_aquarius_new_technologies_internet_associations", "Aquarius",
       "professional_association",
       "Source associates earning / work with new technologies and internet; "
       "not a career assignment.",
       "neutral", "WORK_DETAIL", source_reference=REF_AQUARIUS),
    _f("mars_aquarius_motivation_directing_organizing_others", "Aquarius", "execution",
       "Motivation may include directing / organizing others.",
       "conditional", "WORK_CORE", source_reference=REF_AQUARIUS),
    _f("mars_aquarius_participation_in_organizations", "Aquarius", "work_conditions",
       "Participation in organizations / social activity.",
       "strength", "WORK_CORE", source_reference=REF_AQUARIUS),
    _f("mars_aquarius_reformer_style", "Aquarius", "execution",
       "Reformer style.",
       "strength", "WORK_CORE", source_reference=REF_AQUARIUS),
    _f("mars_aquarius_action_intensifies_when_freedom_restricted", "Aquarius", "effort",
       "Action intensifies when freedom is restricted.",
       "conditional", "WORK_CORE", source_reference=REF_AQUARIUS),
    _f("mars_aquarius_eccentric_arbitrary_action", "Aquarius", "execution",
       "Eccentric / arbitrary action.",
       "risk", "WORK_CORE", source_reference=REF_AQUARIUS),
    _f("mars_aquarius_unpredictability_unreliability", "Aquarius", "watchout",
       "Unpredictability / unreliability; not a hiring verdict.",
       "risk", "WORK_CORE", source_reference=REF_AQUARIUS),
    _f("mars_aquarius_destruction_without_creation", "Aquarius", "watchout",
       "Destruction without creation.",
       "risk", "WORK_CORE", source_reference=REF_AQUARIUS),
    _f("mars_aquarius_prefers_instructing_over_manual_execution", "Aquarius", "execution",
       "May prefer instructing others over doing manual execution.",
       "risk", "WORK_CORE", source_reference=REF_AQUARIUS),
    _f("mars_aquarius_may_fail_to_recognize_own_limits", "Aquarius", "watchout",
       "May fail to recognize own limits.",
       "risk", "WORK_CORE", source_reference=REF_AQUARIUS),
    _f("mars_aquarius_source_democracy_liberalism_irresponsibility", "Aquarius",
       "source_specific",
       "Source contains a politically loaded statement equating democracy / liberalism with "
       "irresponsibility transferred onto others. Canonical preservation only; not a work, "
       "civic, or hiring claim.",
       "risk", "SOURCE_ONLY", source_reference=REF_AQUARIUS),
    _f("mars_aquarius_comp_invention_reform_technology_social_projects", "Aquarius",
       "compensation",
       "Source compensation: invention / reform / technology / social projects; "
       "not career assignments.",
       "neutral", "WORK_DETAIL", source_reference=REF_AQUARIUS),
    _f("mars_aquarius_comp_carry_ideas_through_to_implementation", "Aquarius",
       "compensation",
       "Source compensation: carry ideas through to implementation.",
       "neutral", "WORK_DETAIL", source_reference=REF_AQUARIUS),
    _f("mars_aquarius_comp_plan_future_strategy", "Aquarius", "compensation",
       "Source compensation: plan future strategy.",
       "neutral", "WORK_DETAIL", source_reference=REF_AQUARIUS),
)

PISCES_PACK: tuple[MarsSourceFactDef, ...] = (
    _f("mars_pisces_action_driven_by_new_feelings_experience", "Pisces", "action_start",
       "Action may be driven by search for new feelings / experience.",
       "conditional", "WORK_CORE", source_reference=REF_PISCES),
    _f("mars_pisces_acts_for_ideal_higher_meaning", "Pisces", "execution",
       "Acts for an ideal / higher meaning.",
       "strength", "WORK_CORE", source_reference=REF_PISCES),
    _f("mars_pisces_dislikes_routine_without_meaning", "Pisces", "work_conditions",
       "Dislikes routine without meaning.",
       "risk", "WORK_CORE", source_reference=REF_PISCES),
    _f("mars_pisces_can_work_alone_comfortably", "Pisces", "work_conditions",
       "Can work alone comfortably.",
       "strength", "WORK_CORE", source_reference=REF_PISCES),
    _f("mars_pisces_strong_plasticity_of_movement", "Pisces", "source_specific",
       "Source describes very strong plasticity of movement; not a diagnosis or ranking.",
       "neutral", "WORK_DETAIL", source_reference=REF_PISCES),
    _f("mars_pisces_chasing_mirages_unrealistic_aims", "Pisces", "watchout",
       "Chasing mirages / unrealistic aims.",
       "risk", "WORK_CORE", source_reference=REF_PISCES),
    _f("mars_pisces_chaotic_action", "Pisces", "work_rhythm",
       "Chaotic action.",
       "risk", "WORK_CORE", source_reference=REF_PISCES),
    _f("mars_pisces_lying_as_shadow", "Pisces", "watchout",
       "Source includes lying as a shadow; not a deterministic accusation.",
       "risk", "WORK_CORE", source_reference=REF_PISCES),
    _f("mars_pisces_loss_of_concentration", "Pisces", "execution",
       "Loss of concentration.",
       "risk", "WORK_CORE", source_reference=REF_PISCES),
    _f("mars_pisces_fears_illusions_escape_from_ordinary_reality", "Pisces", "stuck_blocker",
       "Fears / illusions / escape from ordinary reality; not a diagnosis.",
       "risk", "WORK_CORE", source_reference=REF_PISCES),
    _f("mars_pisces_without_structure_effort_diffuses", "Pisces", "effort",
       "Without structure, effort may diffuse and become ineffective.",
       "risk", "WORK_CORE", source_reference=REF_PISCES),
    _f("mars_pisces_low_direct_aggression", "Pisces", "conflict",
       "Relatively low direct aggression.",
       "neutral", "WORK_CORE", source_reference=REF_PISCES),
    _f("mars_pisces_indecision", "Pisces", "stuck_blocker",
       "Indecision.",
       "risk", "WORK_CORE", "action_hesitation", source_reference=REF_PISCES),
    _f("mars_pisces_indirect_partisan_conflict_style", "Pisces", "conflict",
       "Indirect “partisan” conflict style rather than open confrontation.",
       "neutral", "WORK_CORE", source_reference=REF_PISCES),
    _f("mars_pisces_energy_moves_into_imagination", "Pisces", "effort",
       "Energy can move into imagination rather than practical action.",
       "risk", "WORK_CORE", source_reference=REF_PISCES),
    _f("mars_pisces_cunning_as_shadow_strategy", "Pisces", "watchout",
       "Source includes cunning as a shadow strategy; not a deterministic accusation.",
       "risk", "WORK_CORE", source_reference=REF_PISCES),
    _f("mars_pisces_weak_neptune_chaos_wasted_effort", "Pisces", "effort",
       "Source condition “with weak Neptune”: chaos / wasted effort / unclear direction. "
       "No Neptune-strength resolver is applied.",
       "conditional", "WORK_DETAIL",
       source_reference=REF_PISCES,
       activation_condition="neptune_strength_unresolved",
       unresolved=True),
    _f("mars_pisces_weak_neptune_grounding_recommendation", "Pisces", "compensation",
       "Source condition “with weak Neptune”: grounding through body / daily routine is "
       "recommended. No Neptune-strength resolver is applied.",
       "neutral", "WORK_DETAIL",
       source_reference=REF_PISCES,
       activation_condition="neptune_strength_unresolved",
       unresolved=True),
    _f("mars_pisces_comp_connect_work_to_higher_meaning", "Pisces", "compensation",
       "Source compensation: connect work to higher meaning.",
       "neutral", "WORK_DETAIL", source_reference=REF_PISCES),
    _f("mars_pisces_comp_choreography_cinema_music_water", "Pisces", "compensation",
       "Source compensation: choreography / cinema / music / water-related activity as "
       "source associations; not career assignments.",
       "neutral", "WORK_DETAIL", source_reference=REF_PISCES),
    _f("mars_pisces_comp_external_structure_deadlines_reality_anchors", "Pisces",
       "compensation",
       "Source compensation: external structure — plan, clear deadlines, reality anchors.",
       "neutral", "WORK_DETAIL", source_reference=REF_PISCES),
)

SIGN_PACKS: dict[str, tuple[MarsSourceFactDef, ...]] = {
    "Aries": ARIES_PACK,
    "Taurus": TAURUS_PACK,
    "Gemini": GEMINI_PACK,
    "Cancer": CANCER_PACK,
    "Leo": LEO_PACK,
    "Virgo": VIRGO_PACK,
    "Libra": LIBRA_PACK,
    "Scorpio": SCORPIO_PACK,
    "Sagittarius": SAGITTARIUS_PACK,
    "Capricorn": CAPRICORN_PACK,
    "Aquarius": AQUARIUS_PACK,
    "Pisces": PISCES_PACK,
}

SUPPORTED_SIGN_KEYS: frozenset[str] = frozenset(SIGN_PACKS)
EXPECTED_SIGN_SOURCE_REFERENCES: dict[str, str] = {
    "Aries": REF_ARIES,
    "Taurus": REF_TAURUS,
    "Gemini": REF_GEMINI,
    "Cancer": REF_CANCER,
    "Leo": REF_LEO,
    "Virgo": REF_VIRGO,
    "Libra": REF_LIBRA,
    "Scorpio": REF_SCORPIO,
    "Sagittarius": REF_SAGITTARIUS,
    "Capricorn": REF_CAPRICORN,
    "Aquarius": REF_AQUARIUS,
    "Pisces": REF_PISCES,
}

from app.services.mars_source_knowledge_houses import (  # noqa: E402
    EXPECTED_HOUSE_SOURCE_REFERENCES,
    HOUSE_PACKS,
    SUPPORTED_HOUSE_KEYS,
)
from app.services.mars_source_knowledge_motion import (  # noqa: E402
    EXPECTED_MOTION_SOURCE_REFERENCES,
    MOTION_PACKS,
    SUPPORTED_MOTION_KEYS,
)
from app.services.mars_source_knowledge_aspects_l9 import (  # noqa: E402
    EXPECTED_L9_ASPECT_SOURCE_REFERENCES,
    L9_ASPECT_PACKS,
    L9_TENSE_PLANETS,
    MARS_MAJOR_ASPECT_TYPES,
    MARS_TENSE_ASPECT_TYPES,
)
from app.services.mars_source_knowledge_aspects_bio import (  # noqa: E402
    BIO_MOON_NOT_EXTRACTED_LIMITATION,
    BIO_PAIR_PACKS,
    BIO_PAIR_PLANETS,
    EXPECTED_BIO_ASPECT_SOURCE_REFERENCES,
)

ALL_MARS_SOURCE_FACTS: tuple[MarsSourceFactDef, ...] = (
    tuple(fact for pack in SIGN_PACKS.values() for fact in pack)
    + tuple(fact for pack in HOUSE_PACKS.values() for fact in pack)
    + tuple(fact for pack in MOTION_PACKS.values() for fact in pack)
    + tuple(fact for pack in L9_ASPECT_PACKS.values() for fact in pack)
    + tuple(fact for pack in BIO_PAIR_PACKS.values() for fact in pack)
)


def _expected_aspect_source_reference(fact: MarsSourceFactDef) -> str:
    if fact.factor_key.startswith("pair_"):
        planet = fact.factor_key.removeprefix("pair_")
        if planet not in BIO_PAIR_PLANETS:
            raise ValueError(f"Unknown Mars Bio pair key: {fact.factor_key}")
        if not fact.id.startswith(f"mars_{planet.lower()}_bio_"):
            raise ValueError(f"Bio aspect id must start with mars_{planet.lower()}_bio_: {fact.id}")
        return EXPECTED_BIO_ASPECT_SOURCE_REFERENCES[planet]
    if fact.factor_key not in L9_ASPECT_PACKS:
        raise ValueError(f"Unknown Mars aspect key: {fact.factor_key}")
    aspect_type, planet = fact.factor_key.split("_", 1)
    if aspect_type not in MARS_TENSE_ASPECT_TYPES or planet not in L9_TENSE_PLANETS:
        raise ValueError(f"Lesson 9 aspect key must be square/opposition to a target: {fact.factor_key}")
    if not fact.id.startswith(f"mars_{aspect_type}_{planet.lower()}_l9_"):
        raise ValueError(
            f"Lesson 9 aspect id must start with mars_{aspect_type}_{planet.lower()}_l9_: {fact.id}"
        )
    return EXPECTED_L9_ASPECT_SOURCE_REFERENCES[planet]


def mars_aspect_has_source_coverage(*, aspect_type: str, planet: str) -> bool:
    if aspect_type in MARS_TENSE_ASPECT_TYPES and planet in L9_TENSE_PLANETS:
        return True
    if aspect_type in MARS_MAJOR_ASPECT_TYPES and planet in BIO_PAIR_PLANETS:
        return True
    return False


def validate_mars_source_facts(
    facts: tuple[MarsSourceFactDef, ...] = ALL_MARS_SOURCE_FACTS,
) -> None:
    ids = [fact.id for fact in facts]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate Mars source fact ids")
    for fact in facts:
        if not fact.id.startswith("mars_"):
            raise ValueError(f"Mars fact id must start with mars_: {fact.id}")
        if fact.factor_type == "sign":
            if fact.factor_key not in SUPPORTED_SIGN_KEYS:
                raise ValueError(f"Unknown Mars sign key: {fact.factor_key}")
            expected_ref = EXPECTED_SIGN_SOURCE_REFERENCES[fact.factor_key]
        elif fact.factor_type == "house":
            if fact.factor_key not in SUPPORTED_HOUSE_KEYS:
                raise ValueError(f"Unknown Mars house key: {fact.factor_key}")
            if not fact.id.startswith(f"mars_h{fact.factor_key}_"):
                raise ValueError(f"House fact id must start with mars_h{fact.factor_key}_: {fact.id}")
            expected_ref = EXPECTED_HOUSE_SOURCE_REFERENCES[fact.factor_key]
        elif fact.factor_type == "motion":
            if fact.factor_key not in SUPPORTED_MOTION_KEYS:
                raise ValueError(f"Unknown Mars motion key: {fact.factor_key}")
            if fact.factor_key == "retrograde" and not fact.id.startswith("mars_rx_"):
                raise ValueError(f"Retrograde fact id must start with mars_rx_: {fact.id}")
            expected_ref = EXPECTED_MOTION_SOURCE_REFERENCES[fact.factor_key]
        elif fact.factor_type == "aspect":
            expected_ref = _expected_aspect_source_reference(fact)
        else:
            raise ValueError(f"Unsupported Mars factor_type on {fact.id}: {fact.factor_type}")
        if fact.category not in MARS_CATEGORIES:
            raise ValueError(f"Invalid Mars category on {fact.id}: {fact.category}")
        if fact.scope not in MARS_SCOPES:
            raise ValueError(f"Invalid Mars scope on {fact.id}: {fact.scope}")
        if fact.polarity not in MARS_POLARITIES:
            raise ValueError(f"Invalid Mars polarity on {fact.id}: {fact.polarity}")
        if fact.source_reference != expected_ref:
            raise ValueError(
                f"Wrong source_reference on {fact.id}: {fact.source_reference}"
            )


validate_mars_source_facts()
