"""Mercury human presentation copy — curated overrides only.

SOURCE FACTS ARE IMMUTABLE EVIDENCE.

This layer supplies optional human-facing display text keyed by stable
SourceFact.id. It does not rewrite knowledge packs, change tags, or feed
repeat/contrast detection.
"""

from __future__ import annotations

from collections.abc import Iterable

from app.schemas.mercury_source_profile import SourceFact

# Curated human-facing overrides. Keys are stable SourceFact.id values.
# S4.0–S4.9B + S4.10B Scorpio/Libra family review. Presentation only.
HUMAN_COPY_OVERRIDES: dict[str, str] = {
    # --- S4.0 pilot ---
    "pluto_sq_conflictual_communication": (
        "Communication can become highly conflictual and toxic."
    ),
    "pluto_sq_pessimistic_fatalistic_tone": (
        "Communication can take on a pessimistic or fatalistic tone."
    ),
    "pluto_sq_extremely_sharp_speech": (
        "Speech can become razor-sharp, venomous, and highly hurtful."
    ),
    "pluto_sq_words_can_hurt": (
        "Words can have strong impact and can hurt deeply."
    ),
    "pluto_sq_destroy_dig_defeat_through_speech": (
        "Thinking and speech can become destructive and focused on "
        "defeating the other side."
    ),
    "leo_l7_self_justifying_speech": (
        "Speech may be used to justify or exonerate oneself."
    ),
    "leo_afflicted_superior_manner": (
        "Communication can become overly authoritative or condescending."
    ),
    "leo_afflicted_expecting_admiration": (
        "Communication may come with an expectation of admiration or visible "
        "approval."
    ),
    "leo_l7_dev_distinguish_real_vs_dust": (
        "Development focus: distinguish real knowledge from impressive "
        "appearances."
    ),
    "leo_l7_dev_move_beyond_monologue": (
        "Development focus: move beyond one-way communication."
    ),
    "h1_support_intellectual_work": (
        "May support intellectual work and transport-related professions."
    ),
    # --- S4.2 golden-exposure batch ---
    "pluto_sq_core_conflict": (
        "Thinking, communication, and learning can conflict strongly with "
        "intense drives for power, depth, and control."
    ),
    "leo_afflicted_lying_distortion": (
        "Communication may involve lying, distortion, or misrepresentation."
    ),
    "leo_afflicted_appearance_of_competence": (
        "May present an appearance of competence instead of real "
        "professionalism."
    ),
    "leo_afflicted_ego_interferes_with_facts": (
        "Ego can interfere with objective perception of facts."
    ),
    "leo_afflicted_extreme_stubbornness": (
        "Thinking can become extremely stubborn."
    ),
    "leo_afflicted_putting_on_a_show": (
        "Communication may become performative or aimed at creating a false "
        "impression."
    ),
    "taurus_bio_afflicted_cognitive_sluggishness": (
        "Thinking can become cognitively sluggish."
    ),
    "taurus_bio_afflicted_reduced_muted_intuition": (
        "Intuition may become reduced or muted."
    ),
    "taurus_bio_afflicted_weak_abstract_thinking": (
        "Abstract thinking may be weak or largely absent."
    ),
    "cancer_bio_afflicted_disregard_for_facts": (
        "May disregard facts."
    ),
    "cancer_bio_afflicted_everyday_momentary_thinking": (
        "Thinking can become stuck in everyday, momentary concerns."
    ),
    "cancer_bio_afflicted_habit_bound_momentary_reasoning": (
        "Reasoning can become habit-bound and momentary."
    ),
    "cancer_bio_afflicted_losing_central_meaning": (
        "Can lose the central meaning of what is being discussed."
    ),
    "cancer_bio_afflicted_losing_the_thread": (
        "Can lose the thread of an argument."
    ),
    "cancer_bio_afflicted_scatter_distractibility": (
        "Attention can become scattered or distractible."
    ),
    "cancer_bio_afflicted_thinking_trapped_by_habits": (
        "Thinking can become trapped by habits."
    ),
    "cancer_bio_afflicted_thinking_trapped_by_outdated_beliefs": (
        "Thinking can become trapped by outdated beliefs."
    ),
    "cancer_bio_afflicted_loss_of_focus": (
        "Can lose focus."
    ),
    "leo_l7_throwing_dust_in_eyes": (
        "Communication may sometimes create a misleading impression that "
        "obscures what is really going on."
    ),
    "leo_l7_lying_source_claim": (
        "Communication may include a tendency toward lying."
    ),
    "leo_l7_dev_creative_vision": (
        "Growth area: develop a broader creative vision."
    ),
    "leo_l7_dev_creativity": (
        "Growth area: strengthen creative expression."
    ),
    "leo_l7_dev_hear_others_opinions": (
        "Growth area: listen more carefully to other people's perspectives."
    ),
    "uranus_cj_adhd_like_attention_scatter": (
        "Attention can become scattered or distractible."
    ),
    "pisces_l7_dev_distinguish_own_vs_suggested": (
        "Growth area: distinguish one's own thoughts from suggested or "
        "imposed illusions."
    ),
    # --- S4.2.1 live-UI polish (Vlad + one Avdey wording tweak above) ---
    "moon_sq_felt_and_thought_may_diverge": (
        "What is felt may differ from what is thought or said."
    ),
    "taurus_practical_concrete_orientation": (
        "Practical, concrete thinking."
    ),
    "taurus_conversation_needs_practical_purpose": (
        "Prefers conversations with a practical or result-oriented purpose."
    ),
    "taurus_calm_authoritative_communication": (
        "Communication tends to be calm and authoritative."
    ),
    "taurus_bio_slowness_dispute_disadvantage": (
        "A slower response pace can be a disadvantage in fast-moving "
        "arguments."
    ),
    # --- S4.2.2 Dzmitry live-UI polish ---
    "sag_thinks_in_categories_globally": (
        "Thinks in broad categories and on a large scale."
    ),
    "sag_asks_why_what_for": (
        "Naturally asks why things matter and what they are for."
    ),
    "sag_sees_elevated_misses_simple": (
        "May focus on larger meaning while overlooking simpler details."
    ),
    "sag_nonstandard_in_intellectual_matters": (
        "Approaches intellectual questions in unconventional ways."
    ),
    "sag_bio_imagination": (
        "Shows a tendency toward imaginative thinking."
    ),
    "sag_bio_large_scale_thinking": (
        "Thinking tends to operate on a large scale."
    ),
    "sag_bio_global_thinking": (
        "Thinking tends to take a global perspective."
    ),
    "sag_bio_categorical_thinking": (
        "Thinking can become categorical."
    ),
    "sag_bio_thinking_connected_with_opinions_more_than_facts": (
        "Thinking may lean more on opinions than on facts."
    ),
    "sag_bio_thinking_connected_with_image_of_facts": (
        "Thinking may focus more on how facts are framed or represented "
        "than on raw factual material."
    ),
    "uranus_cj_function_overridden_by_rebellious_superconsciousness": (
        "Communication and learning can be strongly reshaped by "
        "unconventional, technically oriented thinking."
    ),
    "uranus_cj_rebellious_free_thinking": (
        "Thinking can be rebellious and free-spirited."
    ),
    "sag_speaks_like_preacher_agitator_philosopher": (
        "Communication can take on the tone of a preacher, agitator, or "
        "philosopher."
    ),
    "sag_speech_maintains_authority": (
        "Speech may be used to maintain authority."
    ),
    "sag_tends_to_teach_lecture": (
        "May slip into teaching or lecturing others."
    ),
    "sag_broadcasts_from_above": (
        "May communicate from a position of authority rather than as an "
        "equal dialogue partner."
    ),
    "sag_love_of_pompous_wording": (
        "May favor pompous or high-flown language."
    ),
    "sag_intolerance_of_others_opinions": (
        "May become intolerant of other people's opinions and ideas."
    ),
    "sag_tells_others_about_achievements": (
        "May enjoy talking about personal achievements and exploits."
    ),
    "sag_bio_prolific_writing_tendency": (
        "May have a strong tendency toward prolific writing."
    ),
    "mars_tr_easier_to_argue_debate": (
        "Finds it easier to argue or debate."
    ),
    "mars_tr_speech_clearer_more_forceful": (
        "Speech can become louder, clearer, and more forceful."
    ),
    "jupiter_sx_native_and_foreign_languages": (
        "Communication may have a strong connection with foreign languages."
    ),
    # --- S4.4B Sagittarius family review (24) ---
    "sag_bio_afflicted_accuracy_problems": (
        "Accuracy problems can appear."
    ),
    "sag_bio_afflicted_coarse_rude_communication": (
        "Communication can become coarse or rude."
    ),
    "sag_bio_afflicted_common_sense_detachment": (
        "Thinking may detach from common sense."
    ),
    "sag_bio_afflicted_dubious_philosophy_drift": (
        "May drift toward dubious or murky philosophies."
    ),
    "sag_bio_afflicted_illusions": (
        "May become prone to illusions."
    ),
    "sag_bio_afflicted_labeling": (
        "May tend toward labeling others."
    ),
    "sag_bio_afflicted_memory_problems": (
        "Memory problems can appear."
    ),
    "sag_bio_afflicted_practice_detachment": (
        "Religious or philosophical frameworks may detach thinking from "
        "practice."
    ),
    "sag_bio_afflicted_strange_religion_drift": (
        "May drift toward strange religions."
    ),
    "sag_bio_expert_aptitude": (
        "May show aptitude for expert-level work."
    ),
    "sag_bio_foreign_language_aptitude": (
        "May show aptitude for foreign languages."
    ),
    "sag_bio_humanities_aptitude": (
        "May show aptitude for the humanities."
    ),
    "sag_bio_pr_aptitude": (
        "May show aptitude for PR."
    ),
    "sag_bio_teacher_instructor_quality": (
        "May show teacher or instructor qualities."
    ),
    "sag_bio_authority_learning_motivation": (
        "Learning may be motivated by authority."
    ),
    "sag_bio_fashion_learning_motivation": (
        "Learning may be motivated by the chance to become fashionable."
    ),
    "sag_bio_status_display_learning_motivation": (
        "Learning may be motivated by the chance to display status."
    ),
    "sag_bio_universal_wisdom_learning_motivation": (
        "Learning may be motivated by a sense of touching higher or "
        "universal wisdom."
    ),
    "sag_bio_fitting_facts_under_philosophy_ideology": (
        "May fit or pull facts under a philosophy or ideology."
    ),
    "sag_calculation_errors_neglect_precision": (
        "May make calculation errors or neglect precision."
    ),
    "sag_learning_practical_life_motive": (
        "Finding a practical life motive for why the learning matters "
        "supports learning."
    ),
    "sag_lecturing_labeling_siblings": (
        "May lecture or label siblings."
    ),
    "sag_seeks_socially_significant_fashionable": (
        "May seek socially significant or fashionable people or themes in "
        "the environment."
    ),
    "sag_bio_occupation_associations": (
        "Occupational themes associated with this placement can include "
        "science, expertise, writing, politics, and propaganda-oriented "
        "journalism — not career assignments."
    ),
    # --- S4.5B Taurus family review (8) ---
    "taurus_abstraction_harder_than_concrete": (
        "Abstraction can be harder than concrete or practical material."
    ),
    "taurus_bio_strong_attention": (
        "May show increased or strong attention."
    ),
    "taurus_bio_visual_scheme_learning": (
        "Learns best through visual schemes or diagrams."
    ),
    "taurus_slower_switching_topics": (
        "May switch more slowly between topics or tasks."
    ),
    "taurus_tangible_benefit_motivates_learning": (
        "Tangible benefit or practical motivation supports learning."
    ),
    "taurus_bio_aesthetic_learning_motivation": (
        "Learning may be motivated by material that feels beautiful or "
        "aesthetically attractive."
    ),
    "taurus_bio_money_learning_motivation": (
        "Learning may be motivated by money."
    ),
    "taurus_bio_vocal_artistic_aptitude": (
        "May show vocal or artistic aptitude."
    ),
    # --- S4.7B Capricorn family review (34) ---
    "capricorn_bio_afflicted_closedness": (
        "Communication or manner may become closed."
    ),
    "capricorn_bio_afflicted_difficulty_tuning_into_others_thoughts": (
        "May have difficulty tuning into other people's thoughts."
    ),
    "capricorn_bio_afflicted_difficulty_understanding_others_thinking": (
        "May have difficulty understanding other people's thinking."
    ),
    "capricorn_bio_afflicted_duty_rule_bound_thinking": (
        'Thinking can become duty- or rule-bound ("must," "should," '
        '"proper," "obliged").'
    ),
    "capricorn_bio_afflicted_old_dogma_fixation": (
        "Thinking can fixate on old dogma."
    ),
    "capricorn_bio_afflicted_professional_vs_everyday_orientation": (
        "Professional-domain knowledge can coexist with poor orientation "
        "in everyday domains."
    ),
    "capricorn_bio_afflicted_rigid_thinking": (
        "Thinking can become rigid."
    ),
    "capricorn_bio_afflicted_severe_lack_of_imagination": (
        "Imagination may be severely limited."
    ),
    "capricorn_bio_afflicted_unsociability": (
        "May become unsociable."
    ),
    "capricorn_bio_clear_thinking_communication_learning": (
        "Thinking, communication, and learning are described as clear."
    ),
    "capricorn_bio_commanding_tone": (
        "May use a commanding tone."
    ),
    "capricorn_bio_difficult_casual_chat": (
        'Difficult to chat casually or "about life."'
    ),
    "capricorn_bio_forecasting": "Forecasting ability.",
    "capricorn_bio_logic": "Logical ability.",
    "capricorn_bio_memory": "Memory capacity.",
    "capricorn_bio_motivation_build_structure": (
        "Learning may be motivated by building structure."
    ),
    "capricorn_bio_motivation_logical_interconnections": (
        "Learning may be motivated by building logical interconnections."
    ),
    "capricorn_bio_occupation_associations": (
        "Occupational themes associated with this placement include "
        "leadership, science, and entrepreneurship; these are not career "
        "assignments."
    ),
    "capricorn_bio_planning": "Planning ability.",
    "capricorn_bio_sober_cold_style": (
        "Sober or cool communication style."
    ),
    "capricorn_bio_structured": (
        "Structured thinking, communication, and learning."
    ),
    "capricorn_bio_table_template_oriented": (
        "Oriented toward tables and templates."
    ),
    "capricorn_bio_technical_aptitude": "Technical aptitude.",
    "capricorn_l7_beautiful_voice": "May have a beautiful voice.",
    "capricorn_l7_chopped_concise_phrases": (
        "Phrases can be clipped and concise."
    ),
    "capricorn_l7_develop_fundamentality": (
        "Growth area: develop a more fundamental and well-grounded approach."
    ),
    "capricorn_l7_env_concrete_without_water": (
        "Sibling and environmental communication tends to be concrete and "
        "free of filler."
    ),
    "capricorn_l7_limited_contact": (
        "Limited contact or restrained sociability."
    ),
    "capricorn_l7_metrics_help": (
        "Clear indicators or metrics help learning."
    ),
    "capricorn_l7_rely_on_proven_experience": (
        "Growth area: rely on proven experience."
    ),
    "capricorn_l7_sarcasm_when_imagination_lacking": (
        "When imagination is lacking, humor may take a sarcastic form."
    ),
    "capricorn_l7_slow_deliberate_perception": (
        "Information perception is slow and deliberate."
    ),
    "capricorn_l7_strong_critic": "May be a strong critic.",
    "capricorn_l7_systematize": "Growth area: systematize.",
    # --- S4.7B Leo family review (9) ---
    "leo_dialogue_difficulty": (
        "Real two-way dialogue can be difficult."
    ),
    "leo_expressive_visible_thinking": (
        "Thinking, communication, and learning are highly expressive and "
        "visible."
    ),
    "leo_l7_creativity": "Creative ability.",
    "leo_l7_difficulty_opinion_receptivity": (
        "May have difficulty being receptive to other people's opinions."
    ),
    "leo_l7_dignified_lordly_speech": (
        "Dignified or lordly speech style."
    ),
    "leo_l7_env_lordly_sibling_position": (
        'May take an "above" or lordly position with siblings.'
    ),
    "leo_l7_nonstandardness": "Nonstandard quality.",
    "leo_l7_self_praise_learning_motivation": (
        "Self-praise or self-encouragement can motivate learning."
    ),
    "leo_l7_verbal_escape_skill": (
        "May be able to wriggle out of situations verbally."
    ),
    # --- S4.8B Aquarius family review (33) ---
    "aquarius_bio_afflicted_anomalous_rhythms": (
        "Mental activity may follow irregular or unusual rhythms."
    ),
    "aquarius_bio_afflicted_broad_fragmentary_general_knowledge": (
        "Knowledge can become broad but fragmentary."
    ),
    "aquarius_bio_afflicted_idea_waves_then_irritation_slowdown": (
        "Waves of many ideas may be followed by irritation or mental "
        "slowdown."
    ),
    "aquarius_bio_afflicted_instability_of_learning": (
        "Learning can become unstable."
    ),
    "aquarius_bio_afflicted_instability_of_thinking": (
        "Thinking can become unstable."
    ),
    "aquarius_bio_afflicted_insufficient_depth_despite_breadth": (
        "Breadth may come with insufficient depth."
    ),
    "aquarius_bio_afflicted_irregular_broken_speech_tempo": (
        "Speech tempo may become irregular or broken."
    ),
    "aquarius_bio_afflicted_loss_of_focus": "May lose focus.",
    "aquarius_bio_artistic_aptitude": "May show artistic aptitude.",
    "aquarius_bio_continual_learning_courses": (
        "Continual learning; may enjoy courses."
    ),
    "aquarius_bio_creativity": "Creative ability.",
    "aquarius_bio_forecasting": "Forecasting ability.",
    "aquarius_bio_insights": "May show insight.",
    "aquarius_bio_interest_in_future": "Interest in the future.",
    "aquarius_bio_inventor_aptitude": (
        "May show aptitude for invention."
    ),
    "aquarius_bio_motivation_extraordinary_new_information": (
        "Learning may be motivated by extraordinary or unusual new "
        "information."
    ),
    "aquarius_bio_motivation_fresh_information": (
        "Learning may be motivated by a constant need for fresh information."
    ),
    "aquarius_bio_motivation_natural_curiosity": (
        "Learning may be motivated by natural curiosity."
    ),
    "aquarius_bio_planning": "Planning ability.",
    "aquarius_bio_strong_firm_memory": "Strong or firm memory.",
    "aquarius_bio_technical_scientific_aptitude": (
        "May show technical or scientific aptitude."
    ),
    "aquarius_bio_uranian_freedom_equality_fraternity_coloring": (
        "Thinking, communication, and learning may be colored by themes of "
        "freedom, equality, and fraternity."
    ),
    "aquarius_l7_anomalous_mental_rhythm": (
        "Anomalous or irregular rhythm of mental activity."
    ),
    "aquarius_l7_calculator_in_the_head": (
        "May have a calculator-like way of handling mental calculations."
    ),
    "aquarius_l7_develop_concreteness_in_decisions": (
        "Growth area: make decisions more concrete and specific."
    ),
    "aquarius_l7_develop_concreteness_in_wording": (
        "Growth area: make wording more concrete and specific."
    ),
    "aquarius_l7_engage_through_genuine_interest": (
        "Growth area: engage through genuine interest."
    ),
    "aquarius_l7_gets_bored_quickly": "May get bored quickly.",
    "aquarius_l7_informal_communication": (
        "Familiar or informal communication."
    ),
    "aquarius_l7_lack_of_patience": "May show a lack of patience.",
    "aquarius_l7_lack_of_systematicity": (
        "May have difficulty staying systematic."
    ),
    "aquarius_l7_quirky_speech_manner": (
        "Quirky or unusual speech manner."
    ),
    "aquarius_l7_scattering_dispersion": (
        "Attention or interests may become scattered."
    ),
    # --- S4.8B Gemini family review (20) ---
    "gemini_bio_afflicted_excessive_verbal_output": (
        "Communication may become excessively verbal."
    ),
    "gemini_bio_afflicted_lying": (
        "Communication may involve lying."
    ),
    "gemini_bio_afflicted_words_exceed_actions": (
        "Words may greatly outnumber actions."
    ),
    "gemini_bio_communicator_ability": "Communicator ability.",
    "gemini_bio_driving_ability": (
        "May show driving ability or potential."
    ),
    "gemini_bio_extraordinary_speed": (
        "Thinking, communication, and learning can be extraordinarily fast."
    ),
    "gemini_bio_foreign_language_polyglot": (
        "May show potential for foreign languages or multilingualism."
    ),
    "gemini_bio_informational_omnivorousness": (
        "May have a broad appetite for information."
    ),
    "gemini_bio_learns_from_many_sources": (
        "Learns from many kinds of sources."
    ),
    "gemini_bio_oratory_talent": (
        "May show oratory talent or potential."
    ),
    "gemini_bio_salesperson_ability": "Sales ability.",
    "gemini_bio_slight_technical_orientation": (
        "Slight technical orientation."
    ),
    "gemini_bio_writing_talent": (
        "May show writing talent or potential."
    ),
    "gemini_l7_dev_avoid_scattering": (
        "Growth area: avoid scattering across parallel tasks."
    ),
    "gemini_l7_dev_focus_one_subject": (
        "Growth area: focus on one subject."
    ),
    "gemini_l7_dev_prioritize_information": (
        "Growth area: prioritize information."
    ),
    "gemini_l7_dev_slow_down": "Growth area: slow down.",
    "gemini_l7_env_indiscriminate_acquaintances": (
        "May form acquaintances broadly and indiscriminately."
    ),
    "gemini_l7_group_listening": (
        "Can track individual people while working with a large group."
    ),
    "gemini_l7_high_working_memory_speed": (
        "Very high working-memory speed."
    ),
    # --- S4.9B Pisces family review (35) ---
    "pisces_bio_afflicted_crumpled_speech": (
        "Speech may become fragmented or poorly formed."
    ),
    "pisces_bio_afflicted_information_chaos": (
        "Thinking can become contradictory and informationally chaotic."
    ),
    "pisces_bio_afflicted_lack_of_central_idea": (
        "Thinking may lack a central idea."
    ),
    "pisces_bio_afflicted_lack_of_logic": (
        "Thinking may lack logic."
    ),
    "pisces_bio_afflicted_lack_of_structure": (
        "Thinking may lack structure."
    ),
    "pisces_bio_afflicted_lying_distortion": (
        "Communication may involve lying or distortion."
    ),
    "pisces_bio_afflicted_mystification": (
        "Communication may involve mystification."
    ),
    "pisces_bio_afflicted_suggestibility": (
        "May become highly suggestible."
    ),
    "pisces_bio_afflicted_unclear_speech": (
        "Speech may become unclear."
    ),
    "pisces_bio_afflicted_words_exceed_completed_actions": (
        "Words may greatly exceed completed actions or results."
    ),
    "pisces_bio_humanities_aptitude": (
        "May show aptitude for the humanities."
    ),
    "pisces_bio_languages_aptitude": (
        "May show aptitude for languages."
    ),
    "pisces_bio_learning_emotional_psychological_attunement": (
        "Learning through emotional or psychological attunement with real "
        "people."
    ),
    "pisces_bio_learning_youtube_content_video": (
        "Learning can happen through YouTube or other video content."
    ),
    "pisces_bio_lose_grip_on_factual_reality": (
        "Thinking or learning can lose touch with factual reality."
    ),
    "pisces_bio_loses_disputes_insufficient_assertiveness": (
        "May often lose disputes because of insufficient assertiveness or "
        "forcefulness."
    ),
    "pisces_bio_lyrical_talent": "May show lyrical talent.",
    "pisces_bio_memory_range_chart_context": (
        "Memory may range from exceptional to very poor depending on chart "
        "context."
    ),
    "pisces_bio_motivation_emotional_atmosphere": (
        "Learning may be motivated by emotional atmosphere."
    ),
    "pisces_bio_motivation_kindred_people": (
        "Learning may be motivated by a sense of being among intellectually "
        "or emotionally kindred people."
    ),
    "pisces_bio_motivation_mystery": (
        "Learning may be motivated by mystery."
    ),
    "pisces_bio_motivation_mystico_psychological_engagement": (
        "Learning may be motivated by emotionally engaging mystical or "
        "psychological material."
    ),
    "pisces_bio_poetic_talent": "May show poetic talent.",
    "pisces_l7_captivity_in_illusions": (
        "May become caught in illusions."
    ),
    "pisces_l7_compressed_crumpled_speech": (
        "Speech may become compressed or disjointed."
    ),
    "pisces_l7_dev_alternate_speech_with_silence": (
        "Growth area: alternate speech flow with conscious silence."
    ),
    "pisces_l7_dev_formulate_central_idea": (
        "Growth area: formulate the central idea."
    ),
    "pisces_l7_exceptionally_strong_imagination": (
        "May show exceptionally strong imagination."
    ),
    "pisces_l7_learning_absorbing_overall_impression": (
        "Learning by absorbing or forming an overall impression."
    ),
    "pisces_l7_manipulation_susceptibility": (
        "May be susceptible to manipulation."
    ),
    "pisces_l7_nonobvious_logic": (
        "Logic may be difficult to comprehend or non-obvious."
    ),
    "pisces_l7_sensitivity_to_hidden_intonation": (
        "Sensitivity to hidden or underlying intonation."
    ),
    "pisces_l7_soulful_communication": (
        "Soulful or emotionally attuned communication."
    ),
    "pisces_l7_suggestibility": "May be suggestible.",
    "pisces_l7_words_can_diverge_from_reality": (
        "Words can diverge from reality."
    ),
    # --- S4.9B Aries family review (24) ---
    "aries_bio_ability_to_argue": (
        "May show an ability or tendency to argue."
    ),
    "aries_bio_engineering_ability": (
        "May show engineering ability or potential."
    ),
    "aries_bio_learns_through_trial_and_error": (
        "Learns through trial and error."
    ),
    "aries_bio_legal_ability": (
        "May show legal ability or potential."
    ),
    "aries_bio_martian_speed_coloring": (
        "Thinking, communication, and learning may be colored by speed and "
        "urgency."
    ),
    "aries_bio_motivation_challenge": (
        "Learning may be motivated by challenge."
    ),
    "aries_bio_motivation_contest_challenge": (
        "Learning may be motivated by being challenged to a fight or contest."
    ),
    "aries_bio_motivation_obstacle": (
        "Learning may be motivated by an obstacle."
    ),
    "aries_bio_oratory_ability": (
        "May show oratory ability or potential."
    ),
    "aries_bio_sales_ability": (
        "May show sales ability or potential."
    ),
    "aries_bio_technical_practicality": (
        "Thinking and learning may be practical and technically oriented."
    ),
    "aries_bio_vocal_ability": (
        "May show vocal ability or potential."
    ),
    "aries_l7_dev_listen_without_interrupting": (
        "Growth area: listen without interrupting."
    ),
    "aries_l7_dev_pause_before_forms": (
        "Growth area: pause before filling documents or forms."
    ),
    "aries_l7_dev_slow_down_before_answering": (
        "Growth area: slow down before answering."
    ),
    "aries_l7_dev_verify_dates": "Growth area: verify dates.",
    "aries_l7_dev_verify_facts": "Growth area: verify facts.",
    "aries_l7_learn_via_arguing": "Arguing supports learning.",
    "aries_l7_learn_via_competition": "Competition supports learning.",
    "aries_l7_learn_via_immediate_application": (
        "Immediate real-life application of knowledge supports learning."
    ),
    "aries_l7_learn_via_practice": "Practice supports learning.",
    "aries_l7_learn_via_proving": (
        "Trying to prove a point can support learning."
    ),
    "aries_l7_may_disregard_facts_vs_theory": (
        "May disregard facts when they do not fit an existing theory."
    ),
    "aries_l7_risk_not_hearing_other_viewpoint": (
        "May have difficulty hearing another point of view while learning."
    ),
    # --- S4.10B Scorpio family review (39) ---
    "scorpio_bio_afflicted_causticity": (
        "Communication may become caustic."
    ),
    "scorpio_bio_afflicted_maximalism_in_evaluations": (
        "Evaluations can become maximalist."
    ),
    "scorpio_bio_afflicted_mockery_malicious_wit": (
        "Communication may involve mockery, malicious wit, or snide remarks."
    ),
    "scorpio_bio_afflicted_quarrelsome_verbal_conflict": (
        "Communication may become quarrelsome or verbally abusive."
    ),
    "scorpio_bio_analytical_aptitude": "May show analytical aptitude.",
    "scorpio_bio_authoritative_voice_effect": (
        "Voice may have an authoritative or commanding effect."
    ),
    "scorpio_bio_critic_aptitude": "May show critic aptitude.",
    "scorpio_bio_influence_people": "May tend to influence people.",
    "scorpio_bio_intuitive_deep_thinking": (
        "Deep thinking with an intuitive quality."
    ),
    "scorpio_bio_learning_criticizing_others_ideas": (
        "Learning through criticizing or dismantling other people's ideas."
    ),
    "scorpio_bio_motivation_challenge_prove": (
        "Learning may be motivated by a challenge to prove oneself."
    ),
    "scorpio_bio_motivation_curiosity": (
        "Learning may be motivated by curiosity."
    ),
    "scorpio_bio_motivation_influence_linked_info": (
        "Learning may be motivated by information linked to the possibility "
        "of influence."
    ),
    "scorpio_bio_motivation_money": (
        "Learning may be motivated by money."
    ),
    "scorpio_bio_occupation_associations": (
        "Occupational themes associated with this placement include "
        "management, entrepreneurship, and psychology; these are not career "
        "assignments."
    ),
    "scorpio_bio_pluto_colored_framing": (
        "Thinking, communication, and learning may be colored by intensity, "
        "depth, and transformation themes."
    ),
    "scorpio_bio_psychological_penetration": (
        "May probe psychological material deeply."
    ),
    "scorpio_bio_researcher_aptitude": "May show researcher aptitude.",
    "scorpio_bio_speak_through_secrets": (
        "May speak through secrets, leaving others to figure things out."
    ),
    "scorpio_bio_sticky_attention": (
        "Attention can be sticky or persistent."
    ),
    "scorpio_bio_technical_aptitude": "May show technical aptitude.",
    "scorpio_l7_argument_dispute_learning": (
        "Argument or dispute can support learning."
    ),
    "scorpio_l7_asking_questions_to_expose_essence": (
        "Asking questions to expose the essence supports learning."
    ),
    "scorpio_l7_deep_concepts": "Deep concepts support learning.",
    "scorpio_l7_depth": "Depth of thinking.",
    "scorpio_l7_destroy_to_understand": (
        "May deconstruct or take apart ideas in order to understand."
    ),
    "scorpio_l7_dev_awareness_of_causticity": (
        "Growth area: become more aware of caustic communication."
    ),
    "scorpio_l7_dev_awareness_of_criticality": (
        "Growth area: become more aware of a tendency toward criticism."
    ),
    "scorpio_l7_dev_finish_explain_thought": (
        "Growth area: finish and explain a thought instead of cutting it off "
        "with hints."
    ),
    "scorpio_l7_env_manipulation_source_claim": (
        "Close-environment communication may involve a tendency toward "
        "manipulation."
    ),
    "scorpio_l7_env_transformative_role": (
        "May play a transformative role in the close environment."
    ),
    "scorpio_l7_hints": "May communicate through hints.",
    "scorpio_l7_learn_dig_to_essence": (
        "Digging to the essence supports learning."
    ),
    "scorpio_l7_practice_learning": "Practice supports learning.",
    "scorpio_l7_quiet_environment": (
        "A quiet environment supports learning."
    ),
    "scorpio_l7_risk_maximalism_in_evaluations": (
        "May show maximalism in evaluations."
    ),
    "scorpio_l7_risk_sharp_judgments": "Judgments can become sharp.",
    "scorpio_l7_sensitivity_to_intuitive_impressions": (
        "May be sensitive to intuitive impressions."
    ),
    "scorpio_l7_vulnerability_error_detection": (
        "Detecting vulnerabilities or errors supports learning."
    ),
    # --- S4.10B Libra family review (35) ---
    "libra_bio_afflicted_absence_of_conclusions": (
        "Thinking may reach no clear conclusions."
    ),
    "libra_bio_afflicted_absence_of_position": (
        "May lack a clear position."
    ),
    "libra_bio_afflicted_excessively_sugary_communication": (
        "Communication may become overly sweet or artificially positive."
    ),
    "libra_bio_afflicted_intellectual_indecision": (
        "Thinking can become intellectually indecisive."
    ),
    "libra_bio_afflicted_lying_distortion": (
        "Communication may involve lying or distortion."
    ),
    "libra_bio_communicator_aptitude": (
        "May show aptitude for communication."
    ),
    "libra_bio_compliment_skill": "May show skill with compliments.",
    "libra_bio_compromise_skill": "May show skill with compromise.",
    "libra_bio_dialogue_skill": "May show skill in dialogue.",
    "libra_bio_humanities_aptitude": (
        "May show aptitude for the humanities."
    ),
    "libra_bio_interviewer_aptitude": (
        "May show aptitude for interviewing."
    ),
    "libra_bio_learning_two_sides": (
        "Learning through two sides or two aspects of a situation."
    ),
    "libra_bio_motivation_aesthetic_environment": (
        "Learning may be motivated by an aesthetically pleasing environment."
    ),
    "libra_bio_motivation_attractive_people": (
        "Learning may be motivated by attractive or aesthetic people."
    ),
    "libra_bio_motivation_attractive_subject": (
        "Learning may be motivated by an attractive subject or material."
    ),
    "libra_bio_motivation_establish_fairness": (
        "Learning may be motivated by the possibility of establishing "
        "fairness."
    ),
    "libra_bio_motivation_possibility_to_discuss": (
        "Learning may be motivated by opportunities for discussion."
    ),
    "libra_bio_occupation_associations": (
        "Occupational themes associated with this placement include "
        "presenting, consulting, law, and politics; these are not career "
        "assignments."
    ),
    "libra_bio_salesperson_aptitude": "May show sales aptitude.",
    "libra_bio_venusian_diplomacy_aesthetic_coloring": (
        "Thinking, communication, and learning may be colored by diplomacy "
        "and aesthetic quality."
    ),
    "libra_l7_conversational_adaptation": (
        "Conversational adaptation or chameleon-like adjustment."
    ),
    "libra_l7_endless_pros_cons_weighing": (
        "May weigh pros and cons endlessly."
    ),
    "libra_l7_env_consultant_smoothing_role": (
        "May take on a consulting or conflict-smoothing role in the close "
        "environment."
    ),
    "libra_l7_env_easy_quick_contact": (
        "Contact may form easily and quickly."
    ),
    "libra_l7_reluctance_to_take_one_side": (
        "May be reluctant or afraid to take one side."
    ),
    "libra_l7_risk_avoiding_dispute": "May avoid dispute.",
    "libra_l7_risk_serving_two_masters": (
        "May try to serve two opposing sides."
    ),
    "libra_l7_support_aesthetic_environment": (
        "An aesthetic learning environment supports learning."
    ),
    "libra_l7_support_books": "Books support learning.",
    "libra_l7_support_dialogue": "Dialogue supports learning.",
    "libra_l7_support_exchange_of_opinions": (
        "Exchange of opinions supports learning."
    ),
    "libra_l7_support_lectures": "Lectures support learning.",
    "libra_l7_support_live_peer": "A live peer supports learning.",
    "libra_l7_support_live_teacher": "A live teacher supports learning.",
    "libra_l7_support_peer_collaboration": (
        "Peer collaboration on difficult problems supports learning."
    ),
    # --- S4.11B Cancer family review (31 new; 9 afflicted frozen above) ---
    "cancer_bio_can_be_hurt_in_communication": (
        "May be hurt or offended in communication."
    ),
    "cancer_bio_can_be_knocked_off_balance_in_speech": (
        "May be knocked off balance or confused in speech."
    ),
    "cancer_bio_communication_colored_by_emotionality": (
        "Communication may be colored by emotionality."
    ),
    "cancer_bio_depth_substantive_nature": "May show depth and substance.",
    "cancer_bio_humanities_aptitude": (
        "May show aptitude for the humanities."
    ),
    "cancer_bio_learning_colored_by_emotionality": (
        "Learning may be colored by emotionality."
    ),
    "cancer_bio_learns_around_familiar_people": (
        "Learns well around familiar or close people."
    ),
    "cancer_bio_motivation_comfortable_environment": (
        "Learning may be motivated by a comfortable environment."
    ),
    "cancer_bio_motivation_familiar_group": (
        "Learning may be motivated by a familiar group."
    ),
    "cancer_bio_motivation_favorite_teacher": (
        "Learning may be motivated when facts are connected to a favorite "
        "or respected teacher."
    ),
    "cancer_bio_motivation_strong_emotion": (
        "Learning may be motivated by strong emotion."
    ),
    "cancer_bio_motivation_tradition": (
        "Learning may be motivated by tradition."
    ),
    "cancer_bio_notice_rhyme": "May notice rhyme.",
    "cancer_bio_notice_subtext": "May notice subtext.",
    "cancer_bio_psychologically_dissect_texts": (
        "May analyze texts from a psychological perspective."
    ),
    "cancer_bio_see_hidden_meaning": "May see hidden meaning.",
    "cancer_bio_storyteller_talent": (
        "May show storyteller talent or potential."
    ),
    "cancer_bio_thinking_colored_by_emotionality": (
        "Thinking may be colored by emotionality."
    ),
    "cancer_bio_writer_association": (
        "May show writing aptitude or potential."
    ),
    "cancer_l7_arguments_arise_intuitively": (
        "Arguments may arise intuitively."
    ),
    "cancer_l7_dev_avoid_stuck_in_details": (
        "Growth area: avoid getting stuck in details."
    ),
    "cancer_l7_dev_retain_central_idea": (
        "Growth area: retain the central idea."
    ),
    "cancer_l7_dev_separate_emotion_from_argument": (
        "Growth area: separate emotion from rational argument."
    ),
    "cancer_l7_dev_structured_speech_training": (
        "Growth area: practice structuring speech."
    ),
    "cancer_l7_dev_subjectivity_risk": "Subjectivity can become a risk.",
    "cancer_l7_env_narrow_pleasant_circle": (
        "May keep a narrow circle of people found pleasant."
    ),
    "cancer_l7_env_possible_social_withdrawal": (
        "May withdraw socially in connection with sensitivity or "
        "vulnerability."
    ),
    "cancer_l7_learn_comfortable_environment": (
        "A comfortable, gentle environment supports learning."
    ),
    "cancer_l7_learn_small_segments": (
        "Dividing information into small pieces or segments supports "
        "learning."
    ),
    "cancer_l7_searches_for_roots": (
        "May search for the roots or origin of an idea."
    ),
    "cancer_l7_viewpoint_depends_on_tastes": (
        "Viewpoint may depend on tastes, views, or habits."
    ),
    # --- S4.11B Virgo family review (41) ---
    "virgo_bio_afflicted_cannot_see_forest_for_trees": (
        "May lose sight of the forest for the trees."
    ),
    "virgo_bio_afflicted_collecting_facts_without_central_idea": (
        "May collect facts without a central idea."
    ),
    "virgo_bio_afflicted_collecting_facts_without_conclusion": (
        "May collect facts without reaching a conclusion."
    ),
    "virgo_bio_afflicted_pettiness": (
        "Thinking or communication may become petty."
    ),
    "virgo_bio_afflicted_tediousness": (
        "Thinking or communication may become tedious."
    ),
    "virgo_bio_high_mastery_of_words": (
        "May show potential for very high mastery of words."
    ),
    "virgo_bio_legal_aptitude": "May show legal aptitude.",
    "virgo_bio_less_accumulation_for_its_own_sake": (
        "Learning merely for the sake of accumulating knowledge is "
        "described as less characteristic."
    ),
    "virgo_bio_literary_aptitude": "May show literary aptitude.",
    "virgo_bio_motivation_curiosity": (
        "Learning may be motivated by curiosity."
    ),
    "virgo_bio_motivation_practical_usefulness": (
        "Learning may be motivated by practical usefulness."
    ),
    "virgo_bio_occupation_associations": (
        "Occupational themes associated with this placement include "
        "writers, scientists, officials, and backstage negotiators; "
        "these are not career assignments."
    ),
    "virgo_bio_skill_operating_facts": (
        "May be skilled at working with facts."
    ),
    "virgo_bio_somewhat_dry_thinking_learning": (
        "Thinking and learning may be somewhat dry."
    ),
    "virgo_bio_speech_lacks_expressive_zest": (
        "Speech may lack expressive flair."
    ),
    "virgo_bio_sticky_strong_memory": "Sticky or strong memory.",
    "virgo_bio_strongly_articulated_wording": (
        "Strongly articulated or stamped wording."
    ),
    "virgo_bio_technical_aptitude": "May show technical aptitude.",
    "virgo_bio_writing_aptitude": "May show writing aptitude.",
    "virgo_l7_dev_avoid_micromanagement": (
        "Growth area: avoid micromanagement."
    ),
    "virgo_l7_dev_build_schemes": "Growth area: build schemes.",
    "virgo_l7_dev_construct_methodology": (
        "Growth area: develop a methodology."
    ),
    "virgo_l7_dev_put_each_detail_in_place": (
        "Growth area: put each detail into its place."
    ),
    "virgo_l7_dev_remove_unnecessary": (
        "Growth area: remove unnecessary elements."
    ),
    "virgo_l7_diary_recording_tendency": (
        "May have a tendency to keep a diary or records."
    ),
    "virgo_l7_emotionally_cool": (
        "May be emotionally cool or not easily moved by emotion."
    ),
    "virgo_l7_env_connections_from_duty": (
        "May maintain connections from duty or propriety."
    ),
    "virgo_l7_env_practical_sibling_communication": (
        "Practical or useful communication with siblings."
    ),
    "virgo_l7_fixation_on_everyday_details": (
        "May fixate on everyday or routine details."
    ),
    "virgo_l7_learning_algorithms": "Algorithms support learning.",
    "virgo_l7_learning_compile_others_opinions": (
        "Compiling other people's opinions supports learning."
    ),
    "virgo_l7_learning_notes": "Notes support learning.",
    "virgo_l7_learning_schemes": "Schemes support learning.",
    "virgo_l7_learning_tables": "Tables support learning.",
    "virgo_l7_observation_keeping": "May keep observations.",
    "virgo_l7_proper_intonation": "Proper or correct intonation.",
    "virgo_l7_risk_losing_whole_picture": (
        "May lose the whole picture because of details."
    ),
    "virgo_l7_risk_routine_fixation": "May become fixated on routine.",
    "virgo_l7_selects_significant_arguments": (
        "May identify or select significant arguments."
    ),
    "virgo_l7_simple_direct_communication": (
        "Simple or direct communication style."
    ),
    "virgo_l7_statistics_tracking": "May track statistics.",
    # --- S4.12B cross-family presentation policy (18) ---
    # presentation_ready != primary-section eligible; routing unchanged.
    "sag_bio_major_exile": (
        "Within the source framework, this placement is described as a "
        "major exile."
    ),
    "sag_bio_impartiality_disrupted": (
        "Within the source framework, Mercury's impartiality is described "
        "as disrupted."
    ),
    "sag_bio_learnability_disrupted": (
        "Within the source framework, Mercury's learnability is described "
        "as disrupted."
    ),
    "gemini_bio_major_domicile_sync": (
        "Within the source framework, Mercury and Gemini are described as "
        "strongly synchronized (major domicile)."
    ),
    "pisces_bio_minor_exile": (
        "Within the source framework, this placement is described as a "
        "minor exile."
    ),
    "virgo_bio_minor_domicile_near_sync": (
        "Within the source framework, Mercury and Virgo are described as "
        "near-synchronized (minor domicile)."
    ),
    "aquarius_bio_afflicted_source_adhd_effect_wording": (
        'Under affliction, the source explicitly uses an "ADHD effect" '
        "comparison; this is source terminology, not a medical diagnosis."
    ),
    "aquarius_bio_source_genius_intellect_archetype": (
        'The source archetypically describes this placement using '
        'exceptionally "genius"-like intellect language; this is not an '
        "IQ score, rank, or hiring conclusion."
    ),
    "aquarius_l7_source_genius_intellect_wording": (
        'The source uses strongest-intellect or "genius" wording for this '
        "placement; this is not an IQ score, rank, or hiring conclusion."
    ),
    "pisces_bio_universal_cosmic_intellect_synthesis": (
        "The source describes a universal or cosmic intellect that "
        "synthesizes knowledge across fields; this is a source claim, not "
        "a validated ability or rank."
    ),
    "cancer_bio_emotional_intelligence_source_claim": (
        "The source describes emotional-intelligence potential; this is "
        "not a measured or certified professional ability."
    ),
    "aquarius_l7_claircognizance": (
        'The source uses the term "claircognizance" or sudden knowing; '
        "this is not a scientifically validated ability."
    ),
    "pisces_bio_unusually_strong_intuition": (
        "The source claims unusually strong intuition; this is not a "
        "scientifically established ability."
    ),
    "pisces_l7_high_intuition": (
        "The source describes high intuition; this is not a scientifically "
        "established ability."
    ),
    "pisces_l7_correct_decisions_nonrational_routes": (
        "The source says correct decisions may sometimes emerge through "
        "unclear or non-rational routes; this is a source claim, not a "
        "validated decision-making ability."
    ),
    "pisces_l7_mystical_thinking": (
        "The source describes mystical thinking and a search for hidden "
        "meaning."
    ),
    "aries_bio_source_sexual_motivation_wording": (
        "One learning-drive theme in the source framework is sexual or "
        "intimate motivation; this is not a professional or hiring "
        "recommendation."
    ),
    "scorpio_bio_source_sexual_motivation": (
        "One learning-drive theme in the source framework is sexual or "
        "intimate motivation; this is not a professional or hiring "
        "recommendation."
    ),
    # --- S4.14B motion:retrograde family review (2) ---
    "rx_communication_learning_unusual": (
        "Communication and learning may operate in unusual ways."
    ),
    "rx_works_more_inwardly": (
        "Thinking, communication, and learning may operate more inwardly."
    ),
}


def get_human_fact_text(fact: SourceFact) -> str:
    """Return curated human copy when present; otherwise raw SourceFact.text."""
    override = HUMAN_COPY_OVERRIDES.get(fact.id)
    if override is not None:
        return override
    return fact.text


def presentation_overrides_for_facts(facts: Iterable[SourceFact]) -> dict[str, str]:
    """Map fact IDs present in `facts` to curated overrides only."""
    return {
        fact.id: HUMAN_COPY_OVERRIDES[fact.id]
        for fact in facts
        if fact.id in HUMAN_COPY_OVERRIDES
    }
