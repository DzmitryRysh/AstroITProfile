"""Mercury Source Profile v2 — Aspect Batch C3 (verified Pluto harmonious).

C3 closes the source-verified Bioastrology Mercury–Pluto harmonious branch:

- Canonical pack: trine_Pluto
- Alias: sextile_Pluto -> trine_Pluto

Pair-specific source explicitly labels the branch \"трин/секстиль\".
Sharing is SOURCE_JUSTIFIED, not a general \"both harmonious\" shortcut.

DO NOT reuse square_Pluto.
DO NOT mark harmonious facts unresolved.

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


REF_PLUTO_HARM = "bioastrology_mercury_pluto_harmonious"

# ---------------------------------------------------------------------------
# Mercury–Pluto trine/sextile — Bioastrology (pair-specific "трин/секстиль")
# Canonical public catalog key: trine_Pluto
# Alias: sextile_Pluto -> trine_Pluto
# Do NOT reuse square_Pluto.
# ---------------------------------------------------------------------------
PLUTO_HARMONIOUS: tuple[SourceFactDef, ...] = (
    _f(
        "pluto_harm_thinking_intensity_integration",
        "aspect",
        "trine_Pluto",
        "thinking",
        "The thinking / communication / learning function smoothly and "
        "harmoniously connects with very powerful, intense Pluto-type energy.",
        "strength",
        "harmonious_thinking_pluto_integration",
        source_reference=REF_PLUTO_HARM,
    ),
    _f(
        "pluto_harm_persuasiveness",
        "aspect",
        "trine_Pluto",
        "communication",
        "Persuasiveness.",
        "strength",
        "persuasion",
        source_reference=REF_PLUTO_HARM,
    ),
    _f(
        "pluto_harm_perceptiveness",
        "aspect",
        "trine_Pluto",
        "thinking",
        "Perceptiveness.",
        "strength",
        "perceptiveness",
        source_reference=REF_PLUTO_HARM,
    ),
    _f(
        "pluto_harm_verbal_force",
        "aspect",
        "trine_Pluto",
        "communication",
        "Power of the word / verbal force.",
        "strength",
        "verbal_force",
        source_reference=REF_PLUTO_HARM,
    ),
    _f(
        "pluto_harm_blunt_truth_speech",
        "aspect",
        "trine_Pluto",
        "communication",
        "Ability to tell blunt truth / call things by their penetrating names.",
        "strength",
        "blunt_truth_speech",
        source_reference=REF_PLUTO_HARM,
    ),
    _f(
        "pluto_harm_source_nlp_aptitude",
        "aspect",
        "trine_Pluto",
        "source_specific",
        "Source describes NLP aptitude "
        "(source-described claim; not scientifically validated mind-reading, "
        "not a manipulation diagnosis, and not a hiring competency).",
        "neutral",
        "source_nlp_aptitude",
        source_reference=REF_PLUTO_HARM,
    ),
    _f(
        "pluto_harm_debate_ability",
        "aspect",
        "trine_Pluto",
        "communication",
        "Ability to conduct debates.",
        "strength",
        "debate",
        source_reference=REF_PLUTO_HARM,
    ),
    _f(
        "pluto_harm_weighty_arguments",
        "aspect",
        "trine_Pluto",
        "communication",
        "Ability to find strong / weighty arguments.",
        "strength",
        "argumentation",
        source_reference=REF_PLUTO_HARM,
    ),
    _f(
        "pluto_harm_technical_talents",
        "aspect",
        "trine_Pluto",
        "work_application",
        "Technical talents.",
        "strength",
        "technical_ability",
        source_reference=REF_PLUTO_HARM,
    ),
    _f(
        "pluto_harm_source_diagnostic_aptitude",
        "aspect",
        "trine_Pluto",
        "source_specific",
        "Source describes ability to make diagnoses "
        "(source-described pattern; not a medical qualification, clinical "
        "diagnostic competence, healthcare credential, or hiring evidence).",
        "neutral",
        "source_diagnostic_aptitude",
        source_reference=REF_PLUTO_HARM,
    ),
    _f(
        "pluto_harm_vulnerability_detection",
        "aspect",
        "trine_Pluto",
        "work_application",
        "Ability to see vulnerabilities.",
        "strength",
        "vulnerability_detection",
        source_reference=REF_PLUTO_HARM,
    ),
    _f(
        "pluto_harm_analytical_quality",
        "aspect",
        "trine_Pluto",
        "thinking",
        "Analytical quality / analyticality.",
        "strength",
        "analytical_thinking",
        source_reference=REF_PLUTO_HARM,
    ),
    _f(
        "pluto_harm_source_psychological_aptitude",
        "aspect",
        "trine_Pluto",
        "source_specific",
        "Source describes psychological abilities "
        "(source-described aptitude; not equated with insight, empathy, "
        "psychology profession, or diagnostic skill).",
        "neutral",
        "source_psychological_aptitude",
        source_reference=REF_PLUTO_HARM,
    ),
    _f(
        "pluto_harm_source_hypnotic_aptitude",
        "aspect",
        "trine_Pluto",
        "source_specific",
        "Source describes hypnotic abilities "
        "(astrology-source claim; not a scientifically established ability "
        "measurement; not equated with persuasion, manipulation, or leadership).",
        "neutral",
        "source_hypnotic_aptitude",
        source_reference=REF_PLUTO_HARM,
    ),
)

C3_ASPECT_PACKS: tuple[SourceFactDef, ...] = PLUTO_HARMONIOUS

# Source-justified alias: pair-specific Bioastrology material labeled "трин/секстиль".
C3_ASPECT_PACK_ALIASES: dict[str, str] = {
    "sextile_Pluto": "trine_Pluto",
}

C3_SUPPORTED_ASPECT_KEYS = frozenset({"trine_Pluto", "sextile_Pluto"})
