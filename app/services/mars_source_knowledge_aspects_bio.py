"""Bioastrology Chapter 6 Mars pair aptitude / professional associations.

Pair-level source claims. Not validated competence, job-fit, or hiring.
Activate on any supported major Mars aspect to that planet.
No invented Bio Moon/Mars parity in this pass.
"""

from __future__ import annotations

from app.services.mars_source_knowledge import MarsSourceFactDef, _f

BIO_PAIR_PLANETS: tuple[str, ...] = (
    "Sun",
    "Mercury",
    "Venus",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
)

REF_BIO_SUN = "bioastrology_mars_aspect_sun"
REF_BIO_MERCURY = "bioastrology_mars_aspect_mercury"
REF_BIO_VENUS = "bioastrology_mars_aspect_venus"
REF_BIO_JUPITER = "bioastrology_mars_aspect_jupiter"
REF_BIO_SATURN = "bioastrology_mars_aspect_saturn"
REF_BIO_URANUS = "bioastrology_mars_aspect_uranus"
REF_BIO_NEPTUNE = "bioastrology_mars_aspect_neptune"
REF_BIO_PLUTO = "bioastrology_mars_aspect_pluto"

EXPECTED_BIO_ASPECT_SOURCE_REFERENCES: dict[str, str] = {
    "Sun": REF_BIO_SUN,
    "Mercury": REF_BIO_MERCURY,
    "Venus": REF_BIO_VENUS,
    "Jupiter": REF_BIO_JUPITER,
    "Saturn": REF_BIO_SATURN,
    "Uranus": REF_BIO_URANUS,
    "Neptune": REF_BIO_NEPTUNE,
    "Pluto": REF_BIO_PLUTO,
}

BIO_MOON_NOT_EXTRACTED_LIMITATION = (
    "Bioastrology Mars-Moon pair source is not yet extracted."
)


def _bio(
    planet: str,
    slug: str,
    category: str,
    text: str,
    polarity: str,
    scope: str,
    *tags: str,
) -> MarsSourceFactDef:
    return _f(
        f"mars_{planet.lower()}_bio_{slug}",
        f"pair_{planet}",
        category,
        text,
        polarity,
        scope,
        *tags,
        source_reference=EXPECTED_BIO_ASPECT_SOURCE_REFERENCES[planet],
        factor_type="aspect",
    )


BIO_SUN_PACK: tuple[MarsSourceFactDef, ...] = (
    _bio("Sun", "manual_work_aptitude", "professional_association",
         "Source-described manual-work aptitude; not technical ability and not a "
         "validated competency or hiring claim.",
         "strength", "WORK_DETAIL"),
    _bio("Sun", "selling_persuasion_aptitude", "professional_association",
         "Source-described selling / persuasion aptitude; not a validated competency "
         "or hiring claim.",
         "strength", "WORK_DETAIL"),
    _bio("Sun", "anti_crisis_aptitude", "professional_association",
         "Source-described anti-crisis aptitude; not generic risk tolerance and not a "
         "validated competency or hiring claim.",
         "strength", "WORK_DETAIL"),
    _bio("Sun", "skilled_action_in_chaos_uncertainty", "professional_association",
         "Source-described skilled action in chaos / uncertainty; not a validated "
         "competency or hiring claim.",
         "strength", "WORK_DETAIL"),
)

BIO_MERCURY_PACK: tuple[MarsSourceFactDef, ...] = (
    _bio("Mercury", "selling_persuasion_aptitude", "professional_association",
         "Source-described selling / persuasion aptitude; not a validated competency "
         "or hiring claim.",
         "strength", "WORK_DETAIL"),
    _bio("Mercury", "mobile_quick_intellect_predisposition", "professional_association",
         "Source-described mobile / quick intellect predisposition; not a Mercury "
         "thinking claim and not a validated competency.",
         "neutral", "WORK_DETAIL"),
    _bio("Mercury", "technical_analytical_it_engineering_aptitude", "professional_association",
         "Source-described technical / analytical / IT-engineering aptitude as one "
         "source claim; not a validated competency or hiring claim.",
         "strength", "WORK_DETAIL"),
    _bio("Mercury", "vocal_musical_aptitude", "professional_association",
         "Source-described vocal and/or musical aptitude; not a validated competency "
         "or hiring claim.",
         "strength", "WORK_DETAIL"),
    _bio("Mercury", "sense_of_humor", "source_specific",
         "Source-described sense of humor; not a validated competency.",
         "neutral", "WORK_DETAIL"),
)

BIO_VENUS_PACK: tuple[MarsSourceFactDef, ...] = (
    _bio("Venus", "design_aptitude", "professional_association",
         "Source-described design aptitude (photography, clothing, websites, "
         "architecture, and similar); not a validated competency or hiring claim.",
         "strength", "WORK_DETAIL"),
)

BIO_JUPITER_PACK: tuple[MarsSourceFactDef, ...] = (
    _bio("Jupiter", "philosopher_aptitude", "professional_association",
         "Source-described philosopher aptitude; not a validated competency or hiring claim.",
         "strength", "WORK_DETAIL"),
    _bio("Jupiter", "teacher_mentor_aptitude", "professional_association",
         "Source-described teacher / mentor aptitude; not a validated competency or hiring claim.",
         "strength", "WORK_DETAIL"),
    _bio("Jupiter", "ideological_manager_aptitude", "professional_association",
         "Source-described ideological-manager aptitude; not a validated competency "
         "or hiring claim.",
         "strength", "WORK_DETAIL"),
    _bio("Jupiter", "sets_goals", "professional_association",
         "Source-described aptitude for setting goals; not a validated competency.",
         "strength", "WORK_DETAIL"),
    _bio("Jupiter", "invents_strategies", "professional_association",
         "Source-described aptitude for inventing strategies; not strategic execution "
         "style and not a validated competency.",
         "strength", "WORK_DETAIL"),
    _bio("Jupiter", "inspires", "professional_association",
         "Source-described aptitude to inspire; not a validated competency or hiring claim.",
         "strength", "WORK_DETAIL"),
    _bio("Jupiter", "moral_material_value_orientation", "source_specific",
         "Source associates a particular moral / material-value orientation; not a "
         "moral verdict or hiring claim.",
         "neutral", "WORK_DETAIL"),
)

BIO_SATURN_PACK: tuple[MarsSourceFactDef, ...] = (
    _bio("Saturn", "design_aptitude", "professional_association",
         "Source-described design aptitude; not a validated competency or hiring claim.",
         "strength", "WORK_DETAIL"),
    _bio("Saturn", "manual_work_aptitude", "professional_association",
         "Source-described manual-work aptitude; not a validated competency or hiring claim.",
         "strength", "WORK_DETAIL"),
    _bio("Saturn", "management_organizational_aptitude", "professional_association",
         "Source-described management / organizational aptitude; not a validated "
         "competency or hiring claim.",
         "strength", "WORK_DETAIL"),
)

BIO_URANUS_PACK: tuple[MarsSourceFactDef, ...] = (
    _bio("Uranus", "technical_analytical_it_engineering_aptitude", "professional_association",
         "Source-described technical / analytical / IT-engineering aptitude as one "
         "source claim; not a validated competency or hiring claim.",
         "strength", "WORK_DETAIL"),
    _bio("Uranus", "psychology_aptitude", "professional_association",
         "Source-described psychology aptitude; not diagnostic ability and not a "
         "validated competency or hiring claim.",
         "strength", "WORK_DETAIL"),
    _bio("Uranus", "planning_forecasting_aptitude", "professional_association",
         "Source-described planning / forecasting aptitude; not strategic execution "
         "and not a validated competency.",
         "strength", "WORK_DETAIL"),
    _bio("Uranus", "astrology_forecasting", "professional_association",
         "Source includes astrology forecasting; not a validated competency or hiring claim.",
         "neutral", "WORK_DETAIL"),
    _bio("Uranus", "hypnosis_extrasensory", "source_specific",
         "Hypnosis / extrasensory source claim; not a validated competency, diagnosis, "
         "or hiring claim.",
         "neutral", "SOURCE_ONLY"),
)

BIO_NEPTUNE_PACK: tuple[MarsSourceFactDef, ...] = (
    _bio("Neptune", "design_aptitude", "professional_association",
         "Source-described design aptitude; not a validated competency or hiring claim.",
         "strength", "WORK_DETAIL"),
    _bio("Neptune", "psychology_aptitude", "professional_association",
         "Source-described psychology aptitude; not diagnostic ability and not a "
         "validated competency or hiring claim.",
         "strength", "WORK_DETAIL"),
    _bio("Neptune", "hypnosis_extrasensory", "source_specific",
         "Hypnosis / extrasensory source claim; not a validated competency, diagnosis, "
         "or hiring claim.",
         "neutral", "SOURCE_ONLY"),
    _bio("Neptune", "medical_healing", "source_specific",
         "Medical / healing source claim; not a medical qualification, diagnosis, "
         "or hiring claim.",
         "neutral", "SOURCE_ONLY"),
)

BIO_PLUTO_PACK: tuple[MarsSourceFactDef, ...] = (
    _bio("Pluto", "selling_persuasion_aptitude", "professional_association",
         "Source-described selling / persuasion aptitude; not a validated competency "
         "or hiring claim.",
         "strength", "WORK_DETAIL"),
    _bio("Pluto", "anti_crisis_aptitude", "professional_association",
         "Source-described anti-crisis aptitude; not generic risk tolerance and not a "
         "validated competency or hiring claim.",
         "strength", "WORK_DETAIL"),
    _bio("Pluto", "skilled_action_in_chaos_uncertainty", "professional_association",
         "Source-described skilled action in chaos / uncertainty; not a validated "
         "competency or hiring claim.",
         "strength", "WORK_DETAIL"),
    _bio("Pluto", "management_organizational_aptitude", "professional_association",
         "Source-described management / organizational aptitude; not a validated "
         "competency or hiring claim.",
         "strength", "WORK_DETAIL"),
    _bio("Pluto", "psychology_aptitude", "professional_association",
         "Source-described psychology aptitude; not diagnostic ability and not a "
         "validated competency or hiring claim.",
         "strength", "WORK_DETAIL"),
    _bio("Pluto", "hypnosis_extrasensory", "source_specific",
         "Hypnosis / extrasensory source claim; not a validated competency, diagnosis, "
         "or hiring claim.",
         "neutral", "SOURCE_ONLY"),
    _bio("Pluto", "medical_healing", "source_specific",
         "Medical / healing source claim; not a medical qualification, diagnosis, "
         "or hiring claim.",
         "neutral", "SOURCE_ONLY"),
)

BIO_PAIR_PACKS: dict[str, tuple[MarsSourceFactDef, ...]] = {
    "Sun": BIO_SUN_PACK,
    "Mercury": BIO_MERCURY_PACK,
    "Venus": BIO_VENUS_PACK,
    "Jupiter": BIO_JUPITER_PACK,
    "Saturn": BIO_SATURN_PACK,
    "Uranus": BIO_URANUS_PACK,
    "Neptune": BIO_NEPTUNE_PACK,
    "Pluto": BIO_PLUTO_PACK,
}
