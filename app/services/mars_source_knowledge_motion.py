"""Mars Lesson 9 retrograde motion source knowledge — HOW THE ACTION IMPULSE IS MODIFIED.

Direct Mars is a calculated state with no Lesson 9 interpretation pack.
Do not invent direct-Mars meanings. Retrograde is a modifier, not weakness.
"""

from __future__ import annotations

from app.services.mars_source_knowledge import MarsSourceFactDef, _f

REF_RX = "lesson9_mars_motion_retrograde"


def _m(
    fact_id: str,
    category: str,
    text: str,
    polarity: str,
    scope: str,
    *tags: str,
    source_reference: str,
    activation_condition: str | None = None,
    unresolved: bool = False,
) -> MarsSourceFactDef:
    return _f(
        fact_id,
        "retrograde",
        category,
        text,
        polarity,
        scope,
        *tags,
        source_reference=source_reference,
        factor_type="motion",
        activation_condition=activation_condition,
        unresolved=unresolved,
    )


RETROGRADE_PACK: tuple[MarsSourceFactDef, ...] = (
    _m("mars_rx_works_inwardly_yin_phase", "work_rhythm",
       "Action function works inwardly / has a more yin-like phase expression; "
       "not a global performance verdict.",
       "neutral", "WORK_CORE", source_reference=REF_RX),
    _m("mars_rx_braking_inhibition", "stuck_blocker",
       "Braking / inhibition of the action impulse.",
       "risk", "WORK_CORE", "action_inhibition", source_reference=REF_RX),
    _m("mars_rx_indecision", "stuck_blocker",
       "Indecision.",
       "risk", "WORK_CORE", source_reference=REF_RX),
    _m("mars_rx_doing_and_redoing", "work_rhythm",
       "Doing and redoing.",
       "neutral", "WORK_CORE", "redo_cycle", source_reference=REF_RX),
    _m("mars_rx_suppressed_will_internal_tension", "stuck_blocker",
       "Suppressed will / internal tension; not low energy and not aggression.",
       "risk", "WORK_CORE", "suppressed_will", source_reference=REF_RX),
    _m("mars_rx_push_pull_dynamics", "work_rhythm",
       "Push-pull action dynamics.",
       "conditional", "WORK_CORE", "push_pull_action", source_reference=REF_RX),
    _m("mars_rx_repeated_hesitation_measure_seven_times", "action_start",
       "Repeated hesitation: “measure seven times” / difficulty making the final cut or decision.",
       "risk", "WORK_CORE", "action_hesitation", source_reference=REF_RX),
    _m("mars_rx_unusual_muscular_activity", "source_specific",
       "Unusual muscular activity; not a medical or body claim.",
       "neutral", "SOURCE_ONLY", source_reference=REF_RX),
    _m("mars_rx_sexual_temperament_suppression", "source_specific",
       "Sexual-temperament suppression; not a diagnosis.",
       "risk", "PERSONAL_MARS", source_reference=REF_RX),
    _m("mars_rx_auto_aggression", "watchout",
       "Auto-aggression; not a prediction, diagnosis, or accusation.",
       "risk", "SOURCE_ONLY", source_reference=REF_RX),
)

MOTION_PACKS: dict[str, tuple[MarsSourceFactDef, ...]] = {
    "retrograde": RETROGRADE_PACK,
}

SUPPORTED_MOTION_KEYS: frozenset[str] = frozenset(MOTION_PACKS)
EXPECTED_MOTION_SOURCE_REFERENCES: dict[str, str] = {
    "retrograde": REF_RX,
}
