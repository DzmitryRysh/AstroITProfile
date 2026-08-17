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
# S4.0 pilot + S4.2 golden-exposure batch. Presentation only.
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
        "Thinking and speech can become destructive and oriented toward "
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
