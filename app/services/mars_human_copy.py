"""Mars human presentation copy — curated overrides only.

SOURCE FACTS ARE IMMUTABLE EVIDENCE.

This layer supplies optional human-facing display text keyed by stable
MarsSourceFact.id. It does not rewrite knowledge packs, change tags, or feed
repeat detection.
"""

from __future__ import annotations

from collections.abc import Iterable

from app.services.mars_source_profile import MarsSourceFact


def _tense(planet: str, slug: str, text: str) -> dict[str, str]:
    return {
        f"mars_square_{planet}_l9_{slug}": text,
        f"mars_opposition_{planet}_l9_{slug}": text,
    }


HUMAN_COPY_OVERRIDES: dict[str, str] = {
    # --- Aries ---
    "mars_aries_overcome_life_difficulties": (
        "May show a strong drive to push through life difficulties."
    ),
    "mars_aries_aggression_rudeness_impatience": (
        "May show aggression, rudeness, or impatience."
    ),
    "mars_aries_comp_channel_activation_into_work_not_conflict": (
        "Channeling activation into work or exercise rather than conflict can help; "
        "excess aggressive impulse may discharge through work or sport."
    ),
    "mars_aries_comp_sport_competition_physical_work": (
        "Sport, competition, or physical work can be a useful outlet."
    ),
    "mars_aries_comp_short_pause_before_acting": (
        "A short pause before acting can help."
    ),
    "mars_aries_comp_divide_large_tasks_into_sprints": (
        "Dividing large tasks into short sprints can help."
    ),
    # --- Taurus ---
    "mars_taurus_capable_talented_worker": (
        "May come across as a capable, talented worker; this is not a hiring claim."
    ),
    "mars_taurus_extreme_stubbornness_difficulty_switching": (
        "Stubbornness can become extreme, with difficulty switching course."
    ),
    "mars_taurus_comp_start_with_one_small_physical_step": (
        "Starting with one small physical step, rather than waiting for inspiration, can help."
    ),
    "mars_taurus_comp_create_comfortable_work_conditions": (
        "Creating comfortable work conditions can help."
    ),
    "mars_taurus_comp_body_manual_practices": (
        "Body-based or manual practices can help."
    ),
    "mars_taurus_comp_delay_conflict_response_when_useful": (
        "Delaying a conflict response can help when that is useful."
    ),
    # --- Gemini ---
    "mars_gemini_conflict_through_information_and_facts": (
        "Conflict may operate through information and knowledge; words, arguments, "
        "or facts can function as the main weapon."
    ),
    "mars_gemini_lying_distortion_of_facts_shadow": (
        "Lying or distortion of facts can appear as a shadow pattern."
    ),
    "mars_gemini_unethical_information_pressure_gossip": (
        "Unethical information pressure, gossip, or manipulation can appear as a shadow pattern."
    ),
    "mars_gemini_comp_conversation_helps_activate_work": (
        "Conversation, contact, or reading may help activate work."
    ),
    "mars_gemini_comp_short_focus_intervals": (
        "Short focus intervals can help."
    ),
    "mars_gemini_comp_lists_to_structure_action": (
        "Lists can help structure action."
    ),
    "mars_gemini_comp_variety_and_communication_contexts": (
        "Work with variety and communication can help."
    ),
    "mars_gemini_comp_conflict_reduce_verbal_sprawl": (
        "In conflict, reducing verbal sprawl to the core point can help."
    ),
    # --- Cancer ---
    "mars_cancer_intuition_for_danger_and_withdrawal": (
        "May have a strong feel for danger and for when to withdraw."
    ),
    "mars_cancer_resentment_revenge_shadow": (
        "Resentment or revenge can appear as a shadow pattern."
    ),
    "mars_cancer_passivity_waiting_for_others_conditions": (
        "Passivity can appear as waiting for others to create the conditions."
    ),
    "mars_cancer_comp_psychologically_safe_work_conditions": (
        "Psychologically safe work conditions can help."
    ),
    "mars_cancer_comp_connect_action_to_personal_care": (
        "Connecting action to care or responsibility for something personally meaningful can help."
    ),
    # --- Leo ---
    "mars_leo_i_will_do_it_myself": (
        "A strong “I will do it myself” orientation."
    ),
    "mars_leo_recognition_seeking_shadow": (
        "May act for admiration and expect applause or recognition; "
        "narcissistic recognition-seeking can appear as a shadow pattern, not a diagnosis."
    ),
    "mars_leo_comp_challenge_activates_effort": (
        "Challenge can activate effort."
    ),
    "mars_leo_comp_visible_authorship_leadership_contexts": (
        "Work with visible authorship, leadership, or creative expression can help "
        "where it fits; this is not a career assignment."
    ),
    "mars_leo_comp_internal_recognition": (
        "Developing internal recognition, rather than depending only on external praise, can help."
    ),
    "mars_leo_comp_disagreement_is_not_loss_of_dignity": (
        "Not treating disagreement as a loss of dignity can help."
    ),
    # --- Virgo ---
    "mars_virgo_highly_productive_mars": (
        "This action style is often highly productive; this is not a ranking."
    ),
    "mars_virgo_self_criticism_not_good_enough": (
        "Self-criticism may take the form of “not good enough.”"
    ),
    "mars_virgo_comp_divide_work_into_discrete_units": (
        "Dividing work into discrete units can help."
    ),
    "mars_virgo_comp_identify_what_is_actually_important": (
        "Repeatedly identifying what is actually important can help."
    ),
    "mars_virgo_comp_body_fine_motor_manual_practices": (
        "Fine-motor or manual practices can help."
    ),
    "mars_virgo_comp_good_enough_rather_than_perfect": (
        "Practicing “good enough” rather than perfect can help."
    ),
    # --- Libra ---
    "mars_libra_ability_to_manage_people": (
        "May have a people-management orientation in action; this is not a hiring or leadership assignment."
    ),
    "mars_libra_negotiation_dispute_management_orientation": (
        "May orient toward negotiation, dispute handling, or management."
    ),
    "mars_libra_comp_start_together_with_a_partner": (
        "Starting together with a partner can help when that is useful."
    ),
    "mars_libra_comp_train_quick_low_stakes_decisions": (
        "Training quick, low-stakes decisions can help."
    ),
    "mars_libra_comp_negotiation_diplomacy_contexts": (
        "Negotiation or diplomacy contexts can help; this is not a career assignment."
    ),
    "mars_libra_comp_dance_aesthetic_physical_activity": (
        "Dance or other aesthetic physical activity can help."
    ),
    # --- Scorpio ---
    "mars_scorpio_strategic_and_tactical_ability": (
        "May show strong strategic and tactical ability; this is not a validated competency."
    ),
    "mars_scorpio_aggression_fixation": (
        "Aggression or fixation can appear; this is not a diagnosis."
    ),
    "mars_scorpio_comp_sport_martial_arts_demanding_load": (
        "Sport, martial arts, or a demanding physical load can help."
    ),
    "mars_scorpio_comp_crisis_response_environments": (
        "Crisis-response environments can fit this action style where appropriate; "
        "this is not a career assignment."
    ),
    "mars_scorpio_comp_not_every_obstacle_is_total_battle": (
        "Learning that not every obstacle requires a total battle can help."
    ),
    "mars_scorpio_comp_redirect_pressure_practices": (
        "Body or psychological practices for redirecting pressure can help."
    ),
    # --- Sagittarius ---
    "mars_sagittarius_nonstandard_travel_esoteric_associations": (
        "There may be an association with nonstandard work, travel, or esoteric domains; "
        "this is not a career assignment."
    ),
    "mars_sagittarius_comp_identify_large_meaningful_goal": (
        "Identifying a large, meaningful goal can help."
    ),
    "mars_sagittarius_comp_divide_large_path_into_stages": (
        "Dividing a large path into stages can help."
    ),
    "mars_sagittarius_comp_teaching_mentoring_international": (
        "Teaching, mentoring, or international contexts may help; this is not a career assignment."
    ),
    "mars_sagittarius_comp_learn_to_accept_help": (
        "Learning to accept help can help."
    ),
    # --- Capricorn ---
    "mars_capricorn_people_as_material_for_victory": (
        "May use people coldly as material for achieving victory."
    ),
    "mars_capricorn_comp_long_term_step_by_step": (
        "Building long-term plans and following them step by step can help."
    ),
    "mars_capricorn_comp_discipline_strategy_contexts": (
        "Work that requires discipline and strategy can help; this is not a career assignment."
    ),
    "mars_capricorn_comp_human_factor": (
        "Remembering the human factor can help; people are not material."
    ),
    "mars_capricorn_comp_rest_without_guilt": (
        "Allowing rest without guilt can help."
    ),
    # --- Aquarius ---
    "mars_aquarius_poorly_suited_to_manual_work": (
        "May be poorly suited to manual work; this is not a competency ranking."
    ),
    "mars_aquarius_new_technologies_internet_associations": (
        "There may be an association with work involving new technologies or the internet; "
        "this is not a career assignment."
    ),
    "mars_aquarius_unpredictability_unreliability": (
        "Unpredictability or unreliability can appear; this is not a hiring verdict."
    ),
    "mars_aquarius_source_democracy_liberalism_irresponsibility": (
        "The source includes a politically loaded claim linking democracy and liberalism "
        "with irresponsibility shifted onto others. This remains source-only and is not "
        "a work, civic, or product claim."
    ),
    "mars_aquarius_comp_invention_reform_technology_social_projects": (
        "Invention, reform, technology, or social projects can help; these are not career assignments."
    ),
    "mars_aquarius_comp_carry_ideas_through_to_implementation": (
        "Carrying ideas through to implementation can help."
    ),
    "mars_aquarius_comp_plan_future_strategy": (
        "Planning future strategy can help."
    ),
    # --- Pisces ---
    "mars_pisces_strong_plasticity_of_movement": (
        "Movement may be unusually plastic or fluid; this is not a diagnosis or ranking."
    ),
    "mars_pisces_lying_as_shadow": (
        "Lying can appear as a shadow pattern."
    ),
    "mars_pisces_fears_illusions_escape_from_ordinary_reality": (
        "Fears, illusions, or escape from ordinary reality can interfere with action; "
        "this is not a diagnosis."
    ),
    "mars_pisces_cunning_as_shadow_strategy": (
        "Cunning can appear as a shadow strategy."
    ),
    "mars_pisces_weak_neptune_chaos_wasted_effort": (
        "If Neptune is weak in the source’s terms, effort may become chaotic, wasted, "
        "or unclear in direction."
    ),
    "mars_pisces_weak_neptune_grounding_recommendation": (
        "If Neptune is weak in the source’s terms, grounding through the body and daily "
        "routine is recommended."
    ),
    "mars_pisces_comp_connect_work_to_higher_meaning": (
        "Connecting work to a higher meaning can help."
    ),
    "mars_pisces_comp_choreography_cinema_music_water": (
        "Choreography, cinema, music, or water-related activity may help; "
        "this is not a career assignment."
    ),
    "mars_pisces_comp_external_structure_deadlines_reality_anchors": (
        "External structure — a plan, clear deadlines, and reality anchors — can help."
    ),
    "mars_pisces_indirect_partisan_conflict_style": (
        "Conflict style may be indirect and partisan rather than open confrontation."
    ),
    # --- House 1 ---
    "mars_h1_source_analytical_abilities": (
        "In this action context, there may be analytical abilities; this is not Mercury "
        "analytical thinking and not a validated competency."
    ),
    "mars_h1_metal_solder_forge_hand_work": (
        "In this area, there may be an inclination toward metalwork, soldering, forging, "
        "or other hand work; this is not a certified skill claim."
    ),
    "mars_h1_aggression_rudeness_recklessness_under_defeat": (
        "Under defeat, aggression, rudeness, lack of restraint, or recklessness may appear."
    ),
    "mars_h1_weak_long_term_strategy": (
        "Long-term strategy may be weak, with difficulty planning far ahead."
    ),
    "mars_h1_source_athletic_lean_muscular_appearance": (
        "The source associates this placement with an athletic, lean, or muscular appearance; "
        "this is not a body or hiring claim."
    ),
    "mars_h1_source_close_ascendant_surgical_birth": (
        "The source associates a close-to-Ascendant placement with a surgical-birth claim; "
        "this is not a medical diagnosis."
    ),
    # --- House 2 ---
    "mars_h2_occupation_associations": (
        "There may be an association with work involving dentistry, cutting or sewing, "
        "firefighting, business, the military, or engineering."
    ),
    "mars_h2_push_for_discounts": (
        "May push for discounts; this is not a validated negotiation competency."
    ),
    "mars_h2_strong_harmonious_positive_budget_through_activity": (
        "If Mars is strong or harmonious in the source’s terms, activity and dynamism may "
        "more often support a positive budget."
    ),
    # --- House 3 ---
    "mars_h3_occupation_associations": (
        "There may be an association with work involving journalism, commentary, literature, "
        "teaching, or driving."
    ),
    "mars_h3_strong_persuasion_in_conversation": (
        "Conversation may be strongly persuasive; this is not a validated persuasion competency."
    ),
    "mars_h3_source_transport_accidents_injuries": (
        "The source associates this placement with transport accidents or injuries; "
        "this is not a prediction or diagnosis."
    ),
    "mars_h3_harmonious_mars_fast_driving": (
        "If Mars is harmonious in the source’s terms, this may show simply as fast driving; "
        "this is not a driving skill."
    ),
    # --- House 4 ---
    "mars_h4_source_fire_destruction_risk": (
        "The source associates this placement with fire or destruction risk; this is not a prediction."
    ),
    "mars_h4_source_household_injury_theft_tragedy": (
        "The source associates this placement with household injury, theft, or tragedy; "
        "this is not a prediction or diagnosis."
    ),
    "mars_h4_strong_affliction_domestic_tyranny": (
        "If Mars is strongly afflicted in the source’s terms, domestic tyranny may appear; "
        "this is not an accusation."
    ),
    # --- House 5 ---
    "mars_h5_occupation_associations": (
        "There may be an association with work involving business, casinos, fitness, sport, "
        "art expertise, teaching, or profit from entertainment, creative, sport, or stage fields."
    ),
    "mars_h5_hobby_may_develop_into_profession": (
        "A hobby may develop into a profession; this is not a career assignment."
    ),
    # --- House 6 ---
    "mars_h6_duties_constant_overload": (
        "Duties may create constant overload and little breathing room."
    ),
    "mars_h6_workplace_conflict_pushes_line": (
        "Workplace conflict may involve pushing one's own line or arguing."
    ),
    "mars_h6_chronic_workplace_conflict": (
        "There may be chronic workplace conflict."
    ),
    "mars_h6_rarely_leads": (
        "In work settings, may rarely lead."
    ),
    "mars_h6_personal_work_done_well": (
        "Personal, hands-on execution may be done especially well; this is not a validated competency."
    ),
    "mars_h6_occupation_associations": (
        "There may be an association with work involving surgery, dentistry, massage, mechanics, "
        "manual labor, the military, or firefighting."
    ),
    "mars_h6_source_illness_activity_imbalance": (
        "The source associates this placement with illness from too little or too much "
        "physical activity; this is not a medical diagnosis."
    ),
    "mars_h6_source_acute_inflammatory_illness": (
        "The source associates this placement with acute or inflammatory illness or fever; "
        "this is not a medical diagnosis."
    ),
    # --- House 7 ---
    "mars_h7_occupation_associations": (
        "There may be an association with work involving negotiations, consulting, or dance teaching."
    ),
    "mars_h7_sparring_sport_dance_association": (
        "There may be an association with sparring-type sport or dance; this is not a skill certification."
    ),
    "mars_h7_perceived_as_aggressive_or_rough": (
        "Others may perceive the person as aggressive or rough."
    ),
    "mars_h7_affliction_early_marriage_divorce": (
        "If Mars is afflicted in the source’s terms, early marriage or early divorce may be "
        "associated; this is not a relationship prediction."
    ),
    # --- House 8 ---
    "mars_h8_occupation_associations": (
        "There may be an association with work involving business, politics, surgery, security, "
        "emergency response, finance, sport, or fund and asset management."
    ),
    "mars_h8_mysticism_magic_energy_work_associations": (
        "There may be an association with mysticism, magic, or energy-work domains; "
        "these are not validated practices or job-fit claims."
    ),
    "mars_h8_property_conflicts_may_resolve_dramatically": (
        "Property conflicts may resolve dramatically or violently; this is not a violence prediction."
    ),
    "mars_h8_aggression_over_others_money_inheritance": (
        "Conflict may become intense around others’ money or inheritance."
    ),
    "mars_h8_extreme_risk_situations": (
        "There may be exposure to extreme-risk situations; this is risk exposure, not a "
        "risk-tolerance score."
    ),
    "mars_h8_source_injury_fire_aggression_danger": (
        "The source associates this placement with injury, fire, or aggression danger; "
        "this is not a prediction or diagnosis."
    ),
    # --- House 9 ---
    "mars_h9_occupation_associations": (
        "There may be an association with work involving the military, coaching, agitation, "
        "guiding, teaching, politics, PR, law, or media."
    ),
    "mars_h9_work_abroad_association": (
        "There may be an association with work abroad; this is not a career assignment."
    ),
    "mars_h9_international_trade_goods_mechanisms": (
        "There may be an association with international trade in manufactured goods or mechanisms; "
        "this is not a trade-skill claim."
    ),
    "mars_h9_ideological_fanaticism": (
        "Ideological fanaticism can appear; this is not a diagnosis."
    ),
    # --- House 10 ---
    "mars_h10_source_leadership_association": (
        "There may be a leadership association; this is not a validated leadership competency."
    ),
    "mars_h10_occupation_associations": (
        "There may be an association with military or technical careers, business, smithing, "
        "surgery, emergency response, or dance."
    ),
    "mars_h10_may_pursue_power_at_others_expense": (
        "May pursue power aggressively or at others’ expense."
    ),
    "mars_h10_rootless_solitary_struggle_pattern": (
        "A rootless, solitary struggle pattern can appear."
    ),
    # --- House 11 ---
    "mars_h11_occupation_associations": (
        "There may be an association with instrumentation, mechanics, electronics, or social activity."
    ),
    "mars_h11_ignite_enthusiasm_in_groups": (
        "May ignite enthusiasm in groups; this is not a validated leadership competency."
    ),
    # --- House 12 ---
    "mars_h12_source_strategic_talent": (
        "There may be a strategic talent in this context; this is not a validated job competence."
    ),
    "mars_h12_occupation_associations": (
        "There may be an association with intelligence or scouting, analysis, trading, "
        "investing, or brokerage."
    ),
    "mars_h12_samurai_path_service_to_ideal": (
        "There may be a “samurai path” of service to an ideal."
    ),
    "mars_h12_attraction_to_weapons_strength_sports": (
        "The source associates an attraction to weapons or strength sports; "
        "this is not a hiring or violence claim."
    ),
    "mars_h12_others_may_perceive_as_lazy": (
        "Others may perceive the person as lazy."
    ),
    "mars_h12_source_hidden_violence": (
        "The source associates this placement with hidden violence; this is not a prediction "
        "or accusation."
    ),
    "mars_h12_affliction_criminal_fraud_activity": (
        "If Mars is afflicted in the source’s terms, criminal or fraud activity may be "
        "associated; this is not a legal or hiring allegation."
    ),
    # --- Motion ---
    "mars_rx_works_inwardly_yin_phase": (
        "Action may work more inwardly, in a quieter phase; this is a modifier, not a "
        "performance verdict."
    ),
    "mars_rx_braking_inhibition": (
        "Action may involve periods of internal braking or inhibition."
    ),
    "mars_rx_indecision": (
        "Indecision may stall decisions; this is a modifier, not an inability to act."
    ),
    "mars_rx_doing_and_redoing": (
        "May revisit or redo actions before moving forward."
    ),
    "mars_rx_suppressed_will_internal_tension": (
        "Will may feel suppressed, with internal tension; this is not low energy and not aggression."
    ),
    "mars_rx_push_pull_dynamics": (
        "Action may move in a push-pull pattern."
    ),
    "mars_rx_repeated_hesitation_measure_seven_times": (
        "Decision-making may involve repeated hesitation and difficulty making the final cut."
    ),
    "mars_rx_unusual_muscular_activity": (
        "The source associates this motion with unusual muscular activity; this is not a "
        "medical or body claim."
    ),
    "mars_rx_sexual_temperament_suppression": (
        "The source associates this motion with suppression of sexual temperament; "
        "this is not a diagnosis."
    ),
    "mars_rx_auto_aggression": (
        "The source associates this motion with auto-aggression; this is not a prediction, "
        "diagnosis, or accusation."
    ),
    # --- Lesson 9 Moon clusters ---
    **_tense(
        "moon",
        "cluster_a_internal_fears",
        "One possible expression is internal fear.",
    ),
    **_tense(
        "moon",
        "cluster_a_constraint_stiffness",
        "One possible expression is constraint or stiffness.",
    ),
    **_tense(
        "moon",
        "cluster_a_action_depending_on_mood",
        "One possible expression is action that depends on mood.",
    ),
    **_tense(
        "moon",
        "cluster_b_overstrain",
        "Another possible expression is overstrain.",
    ),
    **_tense(
        "moon",
        "cluster_b_heavy_work_overwork",
        "Another possible expression is heavy work or overwork.",
    ),
    **_tense(
        "moon",
        "cluster_b_hyperactivity",
        "Another possible expression is hyperactivity.",
    ),
    **_tense(
        "moon",
        "cluster_b_constant_tension",
        "Another possible expression is constant tension.",
    ),
    **_tense(
        "moon",
        "cluster_b_burnout",
        "Another possible expression is burnout.",
    ),
    **_tense(
        "jupiter",
        "ideal_or_not_try_pattern",
        "If the work cannot be done ideally, there may be little willingness to try; "
        "this is not a diagnosis.",
    ),
    **_tense(
        "neptune",
        "without_inspiration_passivity_laziness_hide",
        "Without inspiration, passivity, laziness, or a desire to hide may appear; "
        "this is not a diagnosis.",
    ),
    **_tense(
        "neptune",
        "feeling_powerless",
        "A feeling of powerlessness may appear; this is not a diagnosis.",
    ),
    **_tense(
        "uranus",
        "inner_rebellion_against_doing_like_everyone",
        "There may be an inner rebellion against doing things like everyone else.",
    ),
    # --- Bio pair aptitudes ---
    "mars_sun_bio_manual_work_aptitude": (
        "The source associates this pairing with manual-work aptitude, not technical ability."
    ),
    "mars_sun_bio_selling_persuasion_aptitude": (
        "The source associates this pairing with selling or persuasion aptitude."
    ),
    "mars_sun_bio_anti_crisis_aptitude": (
        "The source associates this pairing with anti-crisis aptitude, not generic risk tolerance."
    ),
    "mars_sun_bio_skilled_action_in_chaos_uncertainty": (
        "The source associates this pairing with skilled action in chaos or uncertainty."
    ),
    "mars_mercury_bio_selling_persuasion_aptitude": (
        "The source associates this pairing with selling or persuasion aptitude."
    ),
    "mars_mercury_bio_mobile_quick_intellect_predisposition": (
        "The source associates this pairing with a mobile, quick intellect predisposition; "
        "this is not a Mercury thinking claim."
    ),
    "mars_mercury_bio_technical_analytical_it_engineering_aptitude": (
        "The source associates this pairing with technical, analytical, or IT-engineering aptitude."
    ),
    "mars_mercury_bio_vocal_musical_aptitude": (
        "The source associates this pairing with vocal or musical aptitude."
    ),
    "mars_mercury_bio_sense_of_humor": (
        "The source associates this pairing with a sense of humor."
    ),
    "mars_venus_bio_design_aptitude": (
        "The source associates this pairing with design aptitude, including photography, "
        "clothing, websites, architecture, and similar work."
    ),
    "mars_jupiter_bio_philosopher_aptitude": (
        "The source associates this pairing with philosopher aptitude."
    ),
    "mars_jupiter_bio_teacher_mentor_aptitude": (
        "The source associates this pairing with teacher or mentor aptitude."
    ),
    "mars_jupiter_bio_ideological_manager_aptitude": (
        "The source associates this pairing with ideological-manager aptitude."
    ),
    "mars_jupiter_bio_sets_goals": (
        "The source associates this pairing with an aptitude for setting goals."
    ),
    "mars_jupiter_bio_invents_strategies": (
        "The source associates this pairing with an aptitude for inventing strategies; "
        "this is not strategic execution style."
    ),
    "mars_jupiter_bio_inspires": (
        "The source associates this pairing with an aptitude to inspire."
    ),
    "mars_jupiter_bio_moral_material_value_orientation": (
        "The source associates this pairing with a particular moral or material-value "
        "orientation; this is not a moral verdict."
    ),
    "mars_saturn_bio_design_aptitude": (
        "The source associates this pairing with design aptitude."
    ),
    "mars_saturn_bio_manual_work_aptitude": (
        "The source associates this pairing with manual-work aptitude."
    ),
    "mars_saturn_bio_management_organizational_aptitude": (
        "The source associates this pairing with management or organizational aptitude."
    ),
    "mars_uranus_bio_technical_analytical_it_engineering_aptitude": (
        "The source associates this pairing with technical, analytical, or IT-engineering aptitude."
    ),
    "mars_uranus_bio_psychology_aptitude": (
        "The source associates this pairing with psychology aptitude, not diagnostic ability."
    ),
    "mars_uranus_bio_planning_forecasting_aptitude": (
        "The source associates this pairing with planning or forecasting aptitude; "
        "this is not strategic execution."
    ),
    "mars_uranus_bio_astrology_forecasting": (
        "The source includes astrology forecasting among associated aptitudes."
    ),
    "mars_uranus_bio_hypnosis_extrasensory": (
        "The source associates this pairing with hypnosis or extrasensory claims; "
        "this is not a validated competency or diagnosis."
    ),
    "mars_neptune_bio_design_aptitude": (
        "The source associates this pairing with design aptitude."
    ),
    "mars_neptune_bio_psychology_aptitude": (
        "The source associates this pairing with psychology aptitude, not diagnostic ability."
    ),
    "mars_neptune_bio_hypnosis_extrasensory": (
        "The source associates this pairing with hypnosis or extrasensory claims; "
        "this is not a validated competency or diagnosis."
    ),
    "mars_neptune_bio_medical_healing": (
        "The source associates this pairing with medical or healing claims; "
        "this is not a medical qualification or diagnosis."
    ),
    "mars_pluto_bio_selling_persuasion_aptitude": (
        "The source associates this pairing with selling or persuasion aptitude."
    ),
    "mars_pluto_bio_anti_crisis_aptitude": (
        "The source associates this pairing with anti-crisis aptitude, not generic risk tolerance."
    ),
    "mars_pluto_bio_skilled_action_in_chaos_uncertainty": (
        "The source associates this pairing with skilled action in chaos or uncertainty."
    ),
    "mars_pluto_bio_management_organizational_aptitude": (
        "The source associates this pairing with management or organizational aptitude."
    ),
    "mars_pluto_bio_psychology_aptitude": (
        "The source associates this pairing with psychology aptitude, not diagnostic ability."
    ),
    "mars_pluto_bio_hypnosis_extrasensory": (
        "The source associates this pairing with hypnosis or extrasensory claims; "
        "this is not a validated competency or diagnosis."
    ),
    "mars_pluto_bio_medical_healing": (
        "The source associates this pairing with medical or healing claims; "
        "this is not a medical qualification or diagnosis."
    ),
}


def get_human_fact_text(fact: MarsSourceFact) -> str:
    """Return curated human copy when present; otherwise raw canonical text."""
    override = HUMAN_COPY_OVERRIDES.get(fact.id)
    if override is not None:
        return override
    return fact.text


def presentation_overrides_for_facts(facts: Iterable[MarsSourceFact]) -> dict[str, str]:
    """Map fact IDs present in `facts` to curated overrides only."""
    return {
        fact.id: HUMAN_COPY_OVERRIDES[fact.id]
        for fact in facts
        if fact.id in HUMAN_COPY_OVERRIDES
    }


def presentation_text_for_fact_id(fact_id: str, canonical_text: str) -> str:
    return HUMAN_COPY_OVERRIDES.get(fact_id, canonical_text)
