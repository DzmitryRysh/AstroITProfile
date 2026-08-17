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
# S4.0–S4.4B + S4.5B Taurus family review. Presentation only.
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
