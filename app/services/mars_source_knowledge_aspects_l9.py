"""Mars Lesson 9 tense aspect knowledge — HOW an aspect modifies ACTION.

Square and opposition share the same operational blocker pack per target.
Do not apply these packs to sextile, trine, or conjunction.
Do not invent generic energetic/initiative facts for every Mars aspect.
"""

from __future__ import annotations

from app.services.mars_source_knowledge import MarsSourceFactDef, _f

MARS_MAJOR_ASPECT_TYPES = frozenset(
    {"conjunction", "sextile", "square", "trine", "opposition"}
)
MARS_TENSE_ASPECT_TYPES = frozenset({"square", "opposition"})
L9_TENSE_PLANETS: tuple[str, ...] = (
    "Sun",
    "Moon",
    "Mercury",
    "Venus",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
)

REF_L9_SUN = "lesson9_mars_aspect_tense_sun"
REF_L9_MOON = "lesson9_mars_aspect_tense_moon"
REF_L9_MERCURY = "lesson9_mars_aspect_tense_mercury"
REF_L9_VENUS = "lesson9_mars_aspect_tense_venus"
REF_L9_JUPITER = "lesson9_mars_aspect_tense_jupiter"
REF_L9_SATURN = "lesson9_mars_aspect_tense_saturn"
REF_L9_URANUS = "lesson9_mars_aspect_tense_uranus"
REF_L9_NEPTUNE = "lesson9_mars_aspect_tense_neptune"
REF_L9_PLUTO = "lesson9_mars_aspect_tense_pluto"

EXPECTED_L9_ASPECT_SOURCE_REFERENCES: dict[str, str] = {
    "Sun": REF_L9_SUN,
    "Moon": REF_L9_MOON,
    "Mercury": REF_L9_MERCURY,
    "Venus": REF_L9_VENUS,
    "Jupiter": REF_L9_JUPITER,
    "Saturn": REF_L9_SATURN,
    "Uranus": REF_L9_URANUS,
    "Neptune": REF_L9_NEPTUNE,
    "Pluto": REF_L9_PLUTO,
}

# (slug, category, text, polarity, scope, *tags)
_Atom = tuple


def _tense_pack(planet: str, aspect_type: str, atoms: tuple[_Atom, ...]) -> tuple[MarsSourceFactDef, ...]:
    key = f"{aspect_type}_{planet}"
    ref = EXPECTED_L9_ASPECT_SOURCE_REFERENCES[planet]
    prefix = f"mars_{aspect_type}_{planet.lower()}_l9_"
    return tuple(
        _f(
            prefix + atom[0],
            key,
            atom[1],
            atom[2],
            atom[3],
            atom[4],
            *atom[5:],
            source_reference=ref,
            factor_type="aspect",
        )
        for atom in atoms
    )


def _expand_tense(planet: str, atoms: tuple[_Atom, ...]) -> dict[str, tuple[MarsSourceFactDef, ...]]:
    return {
        f"{aspect_type}_{planet}": _tense_pack(planet, aspect_type, atoms)
        for aspect_type in ("square", "opposition")
    }


SUN_ATOMS: tuple[_Atom, ...] = (
    ("start_not_main_problem", "action_start",
     "Starting itself may not be the main problem.",
     "neutral", "WORK_CORE"),
    ("completion_difficulty", "continuation",
     "Difficulty may appear in bringing work to completion.",
     "risk", "WORK_CORE", "completion_difficulty"),
    ("high_tension_in_work", "watchout",
     "High tension in work.",
     "risk", "WORK_CORE"),
    ("perfectionism", "execution",
     "Perfectionism in work.",
     "risk", "WORK_CORE"),
    ("anger_irritation", "watchout",
     "Anger / irritation.",
     "risk", "WORK_CORE"),
    ("eventual_burnout", "effort",
     "Eventual burnout.",
     "risk", "WORK_CORE"),
    ("eventual_unwillingness_to_act", "stuck_blocker",
     "Eventual unwillingness to act.",
     "risk", "WORK_CORE"),
)

MOON_ATOMS: tuple[_Atom, ...] = (
    ("cluster_a_internal_fears", "stuck_blocker",
     "Possible expression cluster A: internal fears.",
     "conditional", "WORK_CORE"),
    ("cluster_a_constraint_stiffness", "stuck_blocker",
     "Possible expression cluster A: constraint / stiffness.",
     "conditional", "WORK_CORE"),
    ("cluster_a_action_depending_on_mood", "action_start",
     "Possible expression cluster A: action depending on mood.",
     "conditional", "WORK_CORE", "mood_dependent_action"),
    ("cluster_b_overstrain", "effort",
     "Possible expression cluster B: overstrain.",
     "conditional", "WORK_CORE"),
    ("cluster_b_heavy_work_overwork", "effort",
     "Possible expression cluster B: heavy work / overwork.",
     "conditional", "WORK_CORE", "effort_overload"),
    ("cluster_b_hyperactivity", "work_rhythm",
     "Possible expression cluster B: hyperactivity.",
     "conditional", "WORK_CORE"),
    ("cluster_b_constant_tension", "watchout",
     "Possible expression cluster B: constant tension.",
     "conditional", "WORK_CORE"),
    ("cluster_b_burnout", "effort",
     "Possible expression cluster B: burnout.",
     "conditional", "WORK_CORE"),
)

MERCURY_ATOMS: tuple[_Atom, ...] = (
    ("chaotic_activity", "work_rhythm",
     "Chaotic activity.",
     "risk", "WORK_CORE"),
    ("several_tasks_at_once", "work_rhythm",
     "Several tasks at once.",
     "risk", "WORK_CORE", "task_scatter"),
    ("difficulty_concentrating", "execution",
     "Difficulty concentrating.",
     "risk", "WORK_CORE"),
    ("unfinished_tasks", "continuation",
     "Unfinished tasks.",
     "risk", "WORK_CORE"),
    ("boredom_abandoning_work", "continuation",
     "Boredom can lead to abandoning work.",
     "risk", "WORK_CORE"),
)

VENUS_ATOMS: tuple[_Atom, ...] = (
    ("inertia_when_starting", "action_start",
     "Inertia when starting.",
     "risk", "WORK_CORE"),
    ("hesitate_retreat_at_start", "action_start",
     "May hesitate / retreat at start.",
     "risk", "WORK_CORE", "action_hesitation"),
    ("waits_for_ideal_conditions", "action_start",
     "Waits for ideal conditions.",
     "risk", "WORK_CORE"),
    ("fear_losing_money_resources", "stuck_blocker",
     "Fear of losing money / resources may interfere with action.",
     "risk", "WORK_CORE"),
)

JUPITER_ATOMS: tuple[_Atom, ...] = (
    ("loss_of_motivation_intermediate_too_small", "effort",
     "Loss of motivation because intermediate work feels too small.",
     "risk", "WORK_CORE"),
    ("large_result_takes_too_long", "continuation",
     "A large result takes too long.",
     "risk", "WORK_CORE"),
    ("intermediate_progress_not_meaningful", "effort",
     "Intermediate progress may not feel meaningful.",
     "risk", "WORK_CORE"),
    ("ideal_or_not_try_pattern", "stuck_blocker",
     "Source mentions an “if I cannot do it ideally, I may not try” pattern; not a diagnosis.",
     "risk", "WORK_CORE"),
)

SATURN_ATOMS: tuple[_Atom, ...] = (
    ("burnout_from_overwork", "effort",
     "Burnout from overwork.",
     "risk", "WORK_CORE", "effort_overload"),
    ("constraint_stiffness", "stuck_blocker",
     "Constraint / stiffness.",
     "risk", "WORK_CORE"),
    ("no_right_to_make_a_mistake", "watchout",
     "Feeling there is no right to make a mistake.",
     "risk", "WORK_CORE"),
    ("may_therefore_avoid_acting", "action_start",
     "May therefore avoid acting.",
     "risk", "WORK_CORE"),
)

URANUS_ATOMS: tuple[_Atom, ...] = (
    ("burnout_through_loss_of_focus", "effort",
     "Burnout through loss of focus.",
     "risk", "WORK_CORE"),
    ("difficulty_staying_with_one_thing", "work_rhythm",
     "Difficulty staying with one thing.",
     "risk", "WORK_CORE"),
    ("interest_in_everything_at_once", "work_rhythm",
     "Interest in everything at once.",
     "risk", "WORK_CORE"),
    ("inner_rebellion_against_doing_like_everyone", "execution",
     "Inner rebellion against doing things “like everyone”.",
     "risk", "WORK_CORE"),
    ("routine_irritates_need_for_freedom", "work_conditions",
     "Routine can irritate because of a need for freedom.",
     "risk", "WORK_CORE"),
    ("simple_everyday_work_uninteresting", "work_conditions",
     "Simple / everyday work may feel uninteresting.",
     "risk", "WORK_CORE"),
)

NEPTUNE_ATOMS: tuple[_Atom, ...] = (
    ("dependence_on_emotional_context_inspiration", "effort",
     "Strong dependence on emotional context / inspiration.",
     "conditional", "WORK_CORE"),
    ("without_inspiration_passivity_laziness_hide", "stuck_blocker",
     "Without inspiration: passivity / laziness / desire to hide; not a diagnosis.",
     "risk", "WORK_CORE"),
    ("feeling_powerless", "stuck_blocker",
     "Feeling powerless; not a diagnosis.",
     "risk", "WORK_CORE"),
    ("perfectionistic_idealization_prevents_starting", "action_start",
     "Perfectionistic idealization may prevent starting.",
     "risk", "WORK_CORE"),
    ("dreaming_without_doing", "execution",
     "Dreaming without doing.",
     "risk", "WORK_CORE"),
)

PLUTO_ATOMS: tuple[_Atom, ...] = (
    ("extreme_overwork_burnout", "effort",
     "Extreme overwork may lead to burnout.",
     "risk", "WORK_CORE", "effort_overload"),
    ("activation_rises_in_high_tension", "effort",
     "Activation rises in high-tension situations.",
     "conditional", "WORK_CORE", "crisis_activation"),
    ("postpone_until_pressure_intense", "continuation",
     "May postpone tasks until pressure becomes intense.",
     "risk", "WORK_CORE"),
)

L9_ASPECT_PACKS: dict[str, tuple[MarsSourceFactDef, ...]] = {}
L9_ASPECT_PACKS.update(_expand_tense("Sun", SUN_ATOMS))
L9_ASPECT_PACKS.update(_expand_tense("Moon", MOON_ATOMS))
L9_ASPECT_PACKS.update(_expand_tense("Mercury", MERCURY_ATOMS))
L9_ASPECT_PACKS.update(_expand_tense("Venus", VENUS_ATOMS))
L9_ASPECT_PACKS.update(_expand_tense("Jupiter", JUPITER_ATOMS))
L9_ASPECT_PACKS.update(_expand_tense("Saturn", SATURN_ATOMS))
L9_ASPECT_PACKS.update(_expand_tense("Uranus", URANUS_ATOMS))
L9_ASPECT_PACKS.update(_expand_tense("Neptune", NEPTUNE_ATOMS))
L9_ASPECT_PACKS.update(_expand_tense("Pluto", PLUTO_ATOMS))
