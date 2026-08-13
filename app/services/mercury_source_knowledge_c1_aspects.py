"""Mercury Source Profile v2 — Aspect Batch C1 (verified harmonious parity).

C1 closes source-verified Bioastrology harmonious gaps:

- Aliases for existing Moon / Jupiter / Saturn harmonious packs
  (pair-specific source labels \"трин/секстиль\")
- New Mercury–Uranus harmonious pack (trin/sextile), separate from conjunction

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


REF_URANUS_HARM = "bioastrology_mercury_uranus_harmonious"

# ---------------------------------------------------------------------------
# Mercury–Uranus trine/sextile — Bioastrology (pair-specific "трин/секстиль")
# Canonical public catalog key: trine_Uranus
# Alias: sextile_Uranus -> trine_Uranus
# Do NOT reuse conjunction_Uranus.
# ---------------------------------------------------------------------------
URANUS_HARMONIOUS: tuple[SourceFactDef, ...] = (
    _f(
        "uranus_harm_learning_progress_integration",
        "aspect",
        "trine_Uranus",
        "learning",
        "The communication and learning function smoothly combines with the "
        "progress / inventiveness principle.",
        "strength",
        "harmonious_learning_progress_integration",
        source_reference=REF_URANUS_HARM,
    ),
    _f(
        "uranus_harm_thinking_imagination_acceleration",
        "aspect",
        "trine_Uranus",
        "thinking",
        "Accelerates thinking and imagination.",
        "strength",
        "thinking_imagination_acceleration",
        source_reference=REF_URANUS_HARM,
    ),
    _f(
        "uranus_harm_source_genius_fresh_open_mind",
        "aspect",
        "trine_Uranus",
        "source_specific",
        "Source describes +1 to genius, freshness and openness of mind "
        "(source-described claim; not an objectively validated intelligence score).",
        "strength",
        "source_genius_fresh_open_mind",
        source_reference=REF_URANUS_HARM,
    ),
    _f(
        "uranus_harm_technical_talents",
        "aspect",
        "trine_Uranus",
        "work_application",
        "Source describes +1 to technical talents.",
        "strength",
        "technical_ability",
        source_reference=REF_URANUS_HARM,
    ),
    _f(
        "uranus_harm_rebellious_free_thinking",
        "aspect",
        "trine_Uranus",
        "thinking",
        "Source describes +1 to rebellious free thinking.",
        "strength",
        "rebellious_free_thinking",
        source_reference=REF_URANUS_HARM,
    ),
    _f(
        "uranus_harm_interest_ability_psychology",
        "aspect",
        "trine_Uranus",
        "source_specific",
        "Source describes +1 to interests and abilities in psychology "
        "(source-described claim; not a scientifically validated professional competency).",
        "neutral",
        "source_psychology_interest_ability",
        source_reference=REF_URANUS_HARM,
    ),
    _f(
        "uranus_harm_interest_ability_numerology",
        "aspect",
        "trine_Uranus",
        "source_specific",
        "Source describes +1 to interests and abilities in numerology "
        "(source-described claim; not a scientifically validated professional competency).",
        "neutral",
        "source_numerology_interest_ability",
        source_reference=REF_URANUS_HARM,
    ),
    _f(
        "uranus_harm_interest_ability_astrology",
        "aspect",
        "trine_Uranus",
        "source_specific",
        "Source describes +1 to interests and abilities in astrology "
        "(source-described claim; not a scientifically validated professional competency).",
        "neutral",
        "source_astrology_interest_ability",
        source_reference=REF_URANUS_HARM,
    ),
    _f(
        "uranus_harm_claircognizance",
        "aspect",
        "trine_Uranus",
        "source_specific",
        "Source describes +1 to claircognizance (\"яснознание\") "
        "(source-framework claim; not scientifically established perception, "
        "not a diagnostic/hiring fact).",
        "neutral",
        "source_claircognizance",
        source_reference=REF_URANUS_HARM,
    ),
    _f(
        "uranus_harm_sense_of_humor",
        "aspect",
        "trine_Uranus",
        "communication",
        "Source describes +1 to sense of humor.",
        "neutral",
        "sense_of_humor",
        source_reference=REF_URANUS_HARM,
    ),
)

C1_ASPECT_PACKS: tuple[SourceFactDef, ...] = URANUS_HARMONIOUS

# Source-justified aliases: pair-specific Bioastrology material labeled "трин/секстиль".
# Sharing is NOT merely because both aspects are "harmonious" in general.
C1_ASPECT_PACK_ALIASES: dict[str, str] = {
    "trine_Moon": "sextile_Moon",
    "trine_Jupiter": "sextile_Jupiter",
    "sextile_Saturn": "trine_Saturn",
    "sextile_Uranus": "trine_Uranus",
}

C1_SUPPORTED_ASPECT_KEYS = frozenset(
    {
        "trine_Moon",
        "trine_Jupiter",
        "sextile_Saturn",
        "trine_Uranus",
        "sextile_Uranus",
    }
)
