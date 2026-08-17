"""Mercury human presentation copy — curated overrides only.

SOURCE FACTS ARE IMMUTABLE EVIDENCE.

This layer supplies optional human-facing display text keyed by stable
SourceFact.id. It does not rewrite knowledge packs, change tags, or feed
repeat/contrast detection.
"""

from __future__ import annotations

from collections.abc import Iterable

from app.schemas.mercury_source_profile import SourceFact

# Curated S4.0 pilot overrides. Keys are stable SourceFact.id values.
HUMAN_COPY_OVERRIDES: dict[str, str] = {
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
