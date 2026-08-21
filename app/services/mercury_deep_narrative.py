"""Mercury Deep Profile narrative (M9.5C/D) — deterministic human synthesis.

Presentation-only. Groups existing reviewed tags and presentation-ready facts
into coherent factor / aspect / integrated copy. Does not invent astrology,
rewrite source knowledge, or call an LLM.

M9.5D: compress duplication, humanize labels, outcome-first Integrated copy.
User-facing text must not expose raw provenance keys (sign:Leo, aspect:…).
Those remain on provenance_keys / fact_ids for Evidence.
"""

from __future__ import annotations

from collections import Counter

from app.schemas.mercury_source_profile import (
    DeepMercuryAdditiveTheme,
    DeepMercuryAspectBlock,
    DeepMercuryContrastingSignal,
    DeepMercuryFactorBlock,
    DeepMercuryFactorNarrative,
    DeepMercuryIntegratedTakeaway,
    DeepMercuryNarrativeSubsection,
    DeepMercuryReinforcingSignal,
    SourceFact,
)
from app.services.mercury_human_copy_catalog import (
    STATUS_APPROVED_OVERRIDE,
    STATUS_APPROVED_RAW,
    derive_review_status,
)

PRESENTATION_READY_STATUSES = frozenset(
    {STATUS_APPROVED_OVERRIDE, STATUS_APPROVED_RAW}
)

# Human noun-phrases for synthesis sentences (not source quotes).
TAG_PHRASE: dict[str, str] = {
    "monologue_thinking": "monologue-style thinking",
    "monologue_communication": "monologue-style communication",
    "analytical_thinking": "analytical depth",
    "debate": "debate potential",
    "argumentation": "strong argumentation",
    "persuasion": "persuasive pressure",
    "nonstandard_thinking": "nonstandard thinking",
    "sales": "sales-oriented expression",
    "superficiality": "surface-level thinking",
    "lying": "a lying risk in communication",
    "appearance_of_competence": "an appearance-of-competence risk",
    "performance_learning": "learning through performance",
    "standing_out_learning": "learning by standing out",
    "learning_motivation": "strong learning motivation",
    "talkative": "talkativeness",
    "openness": "openness",
    "sign_emphasis": "emphasis on the Mercury sign",
    "aspect_emphasis": "emphasis on Mercury aspects",
    "intellectual_work": "intellectual work",
    "transport_profession": "transport-related work themes",
    "consulting": "consulting themes",
    "written_expression": "easier written expression",
    "rewriting": "rewriting and revisiting material",
    "creative": "creative mental expression",
    "expressive": "expressive communication",
    "presentation": "presentation-oriented communication",
    "audience_effect_tracking": "sensitivity to audience response",
    "oratory": "oratory potential",
    "stubbornness": "stubborn mental positions",
    "distinguish_real_vs_appearance": "separating real knowledge from impressive appearance",
    "hear_others_opinions": "hearing others' opinions",
    "move_beyond_monologue": "moving beyond monologue",
    "misleading_presentation": "misleading presentation risk",
    "ego_interference": "ego interference with facts",
    "amplifier": "amplification of Mercury patterns",
    "youthful": "a youthful manner",
    "learnability": "easier learning",
    "siblings": "sibling relevance",
    "driving_relevance": "driving or transport themes",
    "mobility": "mobility themes",
    "inward_processing": "more inward processing",
    "nonstandard_learning": "unusual learning paths",
    "relearning": "a tendency to relearn",
    "unexpected_conclusions": "unexpected conclusions",
    "conflict": "sharper conflict",
    "pessimism": "a more pessimistic tone",
    "sharp_speech": "sharper speech",
    "hurtful_speech": "more cutting speech",
    "powerful_words": "powerful wording",
    "focus": "sustained mental focus",
    "discipline": "mental discipline",
    "planning": "planned mental organization",
    "strong_memory": "strong memory",
    "structured_speech": "structured speech",
    "technical_ability": "technical aptitude",
    "insight": "penetrating insight",
    "criticism_based_learning": "learning through criticism",
    "vulnerability_detection": "spotting weak points in systems or arguments",
    "idea_appropriation": "adopting others' ideas as one's own",
    "dust_in_eyes": "misleading impression risk",
    "admiration_seeking": "seeking admiration",
    "recognition_seeking": "seeking recognition",
    "lordly_sibling_position": "a dominant role among siblings",
}

# Short list labels for ADD / REINFORCE / COMPLICATE chips.
TAG_LABEL: dict[str, str] = {
    "analytical_thinking": "Analytical depth",
    "debate": "Debate potential",
    "argumentation": "Argumentation",
    "persuasion": "Persuasive pressure",
    "nonstandard_thinking": "Nonstandard thinking",
    "sales": "Sales-oriented expression",
    "superficiality": "Surface-level thinking",
    "conflict": "Sharper conflict",
    "pessimism": "Pessimistic tone",
    "sharp_speech": "Sharper speech",
    "hurtful_speech": "Cutting speech",
    "powerful_words": "Powerful wording",
    "monologue_thinking": "Monologue-style thinking",
    "monologue_communication": "Monologue-style communication",
    "focus": "Sustained focus",
    "discipline": "Mental discipline",
    "planning": "Planned organization",
    "inward_processing": "Inward processing",
    "relearning": "Relearning",
    "unexpected_conclusions": "Unexpected conclusions",
    "amplifier": "Amplification",
    "learnability": "Learnability",
    "youthful": "Youthful manner",
    "siblings": "Sibling relevance",
    "driving_relevance": "Driving / transport relevance",
    "technical_ability": "Technical aptitude",
    "insight": "Insight",
    "lying": "Lying risk",
    "appearance_of_competence": "Appearance-of-competence risk",
    "performance_learning": "Performance learning",
    "standing_out_learning": "Standing-out learning",
    "learning_motivation": "Learning motivation",
    "talkative": "Talkativeness",
    "presentation": "Presentation-oriented communication",
    "stubbornness": "Stubborn mental positions",
    "creative": "Creative expression",
    "audience_effect_tracking": "Audience sensitivity",
    "oratory": "Oratory potential",
    "distinguish_real_vs_appearance": "Real knowledge vs appearance",
    "hear_others_opinions": "Hearing others",
    "move_beyond_monologue": "Beyond monologue",
    "misleading_presentation": "Misleading-presentation risk",
    "ego_interference": "Ego interference",
    "idea_appropriation": "Adopting others' ideas",
    "dust_in_eyes": "Misleading impression risk",
    "admiration_seeking": "Seeking admiration",
    "recognition_seeking": "Seeking recognition",
    "lordly_sibling_position": "Dominant role among siblings",
}

SUBSECTION_META: tuple[tuple[str, str, frozenset[str]], ...] = (
    ("thinking", "Thinking", frozenset({"thinking"})),
    ("communication", "Communication", frozenset({"communication"})),
    ("learning", "Learning", frozenset({"learning", "memory", "focus"})),
    ("strengths", "Strengths", frozenset({"work_application"})),
    ("watchouts", "Watch-outs", frozenset({"risk"})),
    (
        "life_context",
        "Life-context themes",
        frozenset({"environment", "mobility"}),
    ),
)

ALWAYS_KEEP_SUBSECTIONS = frozenset(
    {"watchouts", "life_context", "conditional", "strengths"}
)

CONDITION_PHRASE: dict[str, str] = {
    "hard_aspected": "hard aspects to Mercury",
}

MAX_SUBSECTION_TAGS = 3
MAX_SUMMARY_TAGS = 3
PRIMARY_NARRATIVE_CATEGORIES = frozenset(
    {"thinking", "communication", "learning", "memory", "focus", "work_application"}
)

_ASPECT_ADD_GROUPS: tuple[tuple[str, frozenset[str]], ...] = (
    ("analytical depth", frozenset({"analytical_thinking"})),
    (
        "verbal force and persuasive pressure",
        frozenset({"persuasion", "powerful_words", "sharp_speech", "hurtful_speech"}),
    ),
    (
        "sharper conflict under tension",
        frozenset({"conflict", "pessimism"}),
    ),
)

_SIGNAL_TO_TAG: dict[str, str] = {
    "insight_seeing_not_obvious": "insight",
    "analytical_thinking": "analytical_thinking",
    "debate": "debate",
    "argumentation": "argumentation",
    "persuasion": "persuasion",
    "nonstandard_thinking": "nonstandard_thinking",
    "sales": "sales",
    "technical_ability": "technical_ability",
    "strong_memory": "strong_memory",
    "evidence_requirement": "evidence_requirement",
    "lifelong_learning": "lifelong_learning",
    "foreign_languages": "foreign_languages",
    "teaching": "teaching",
}

DEBUG_PHRASE_MARKERS = (
    "supported across",
    "carried by",
    "appears across",
    "cross-factor",
    "aspect-backed",
    "among other themes",
    "factor types",
    "sign:",
    "house:",
    "motion:",
    "aspect:",
)


def _is_presentation_ready(fact: SourceFact) -> bool:
    if not fact.activated or fact.unresolved:
        return False
    return derive_review_status(fact.id) in PRESENTATION_READY_STATUSES


def tag_phrase(tag: str) -> str:
    if tag in TAG_PHRASE:
        return TAG_PHRASE[tag]
    return tag.replace("_", " ")


def tag_label(tag: str) -> str:
    if tag in TAG_LABEL:
        return TAG_LABEL[tag]
    return " ".join(part.capitalize() for part in tag.split("_") if part)


def signal_label(signal: str) -> str:
    return tag_label(_SIGNAL_TO_TAG.get(signal, signal))


def _join_human(parts: list[str]) -> str:
    clean = [item for item in parts if item]
    if not clean:
        return ""
    if len(clean) == 1:
        return clean[0]
    if len(clean) == 2:
        return f"{clean[0]} and {clean[1]}"
    return f"{', '.join(clean[:-1])}, and {clean[-1]}"


def _ready_facts(facts: list[SourceFact]) -> list[SourceFact]:
    return [fact for fact in facts if _is_presentation_ready(fact)]


def _tag_counts(facts: list[SourceFact]) -> Counter:
    counts: Counter = Counter()
    for fact in facts:
        for tag in fact.tags or ():
            if tag:
                counts[tag] += 1
    return counts


def _top_tags(facts: list[SourceFact], limit: int) -> list[str]:
    return [tag for tag, _ in _tag_counts(facts).most_common(limit)]


def _facts_for_categories(
    facts: list[SourceFact], categories: frozenset[str]
) -> list[SourceFact]:
    return [fact for fact in facts if fact.category in categories]


def _subsection_text(title_key: str, tags: list[str]) -> str:
    phrases = [tag_phrase(tag) for tag in tags]
    joined = _join_human(phrases)
    if title_key == "thinking":
        return f"Thinking also includes {joined}."
    if title_key == "communication":
        return f"Communication also includes {joined}."
    if title_key == "learning":
        return f"Learning also includes {joined}."
    if title_key == "strengths":
        return f"Work-facing strengths include {joined}."
    if title_key == "watchouts":
        return f"Watch-outs include {joined}."
    if title_key == "life_context":
        return f"Life-context themes include {joined}."
    if title_key == "conditional":
        return f"Conditionally activated themes include {joined}."
    return f"This layer includes {joined}."


def _is_base_factor_fact(fact: SourceFact) -> bool:
    return not (fact.activation_condition or "").strip()


def _condition_phrase(condition: str) -> str:
    if condition in CONDITION_PHRASE:
        return CONDITION_PHRASE[condition]
    return condition.replace("_", " ")


def _build_conditional_subsection(
    conditional_facts: list[SourceFact],
) -> DeepMercuryNarrativeSubsection | None:
    if not conditional_facts:
        return None
    by_condition: dict[str, list[SourceFact]] = {}
    for fact in conditional_facts:
        key = (fact.activation_condition or "conditional").strip()
        by_condition.setdefault(key, []).append(fact)

    parts: list[str] = []
    support: list[str] = []
    for condition, bucket in sorted(by_condition.items()):
        tags = _top_tags(bucket, MAX_SUBSECTION_TAGS)
        if not tags:
            continue
        phrases = _join_human([tag_phrase(tag) for tag in tags])
        parts.append(
            f"In this chart, {_condition_phrase(condition)} also activate "
            f"{phrases}."
        )
        matched = [
            fact.id
            for fact in bucket
            if set(tags) & set(fact.tags or ())
        ]
        support.extend(matched or [fact.id for fact in bucket])

    if not parts:
        return None
    return DeepMercuryNarrativeSubsection(
        key="conditional",
        title="Conditionally activated in this chart",
        text=" ".join(parts),
        supporting_fact_ids=sorted(set(support)),
    )


def _fresh_tags(tags: list[str], consumed: set[str]) -> list[str]:
    return [tag for tag in tags if tag not in consumed]


def _should_keep_subsection(key: str, tags: list[str], consumed: set[str]) -> bool:
    if key in ALWAYS_KEEP_SUBSECTIONS:
        return bool(tags)
    return bool(_fresh_tags(tags, consumed))


def build_factor_narrative(
    *,
    factor_type: str,
    factor_key: str,
    title: str,
    facts: list[SourceFact],
) -> DeepMercuryFactorNarrative | None:
    ready = _ready_facts(facts)
    if not ready:
        return None

    core_facts = [fact for fact in ready if _is_base_factor_fact(fact)]
    conditional_facts = [
        fact for fact in ready if not _is_base_factor_fact(fact)
    ]
    narrative_pool = core_facts if core_facts else ready

    primary_facts = (
        _facts_for_categories(narrative_pool, PRIMARY_NARRATIVE_CATEGORIES)
        or narrative_pool
    )
    dominant = _top_tags(primary_facts, MAX_SUMMARY_TAGS)
    if not dominant:
        return None

    theme_labels = [tag_label(tag) for tag in dominant[:2]]
    core_theme = _join_human(theme_labels) if theme_labels else title
    phrases = [tag_phrase(tag) for tag in dominant]
    consumed = set(dominant)

    if factor_type == "sign":
        summary = (
            f"Mercury in {factor_key} tends toward {_join_human(phrases)}."
        )
    elif factor_type == "house":
        summary = (
            f"House {factor_key} shapes how this Mercury shows up, including "
            f"{_join_human(phrases)}."
        )
    elif factor_type == "motion":
        if factor_key.lower() == "retrograde":
            summary = (
                f"Retrograde motion turns Mercury toward "
                f"{_join_human(phrases)}."
            )
        else:
            summary = (
                f"{factor_key.capitalize()} motion relates to "
                f"{_join_human(phrases)}."
            )
    else:
        summary = f"This factor centers on {_join_human(phrases)}."

    subsections: list[DeepMercuryNarrativeSubsection] = []
    all_support: list[str] = [
        fact.id
        for fact in primary_facts
        if set(dominant) & set(fact.tags or ())
    ]

    for key, heading, categories in SUBSECTION_META:
        bucket = _facts_for_categories(narrative_pool, categories)
        if not bucket:
            continue
        tags = _top_tags(bucket, MAX_SUBSECTION_TAGS)
        if not tags:
            continue
        if not _should_keep_subsection(key, tags, consumed):
            continue
        display_tags = (
            tags
            if key in ALWAYS_KEEP_SUBSECTIONS
            else _fresh_tags(tags, consumed)
        )
        if not display_tags:
            continue
        support = [
            fact.id for fact in bucket if set(display_tags) & set(fact.tags or ())
        ] or [fact.id for fact in bucket]
        subsections.append(
            DeepMercuryNarrativeSubsection(
                key=key,
                title=heading,
                text=_subsection_text(key, display_tags),
                supporting_fact_ids=sorted(set(support)),
            )
        )
        all_support.extend(support)
        if key not in ALWAYS_KEEP_SUBSECTIONS:
            consumed.update(display_tags)

    conditional_sub = _build_conditional_subsection(conditional_facts)
    if conditional_sub is not None:
        subsections.append(conditional_sub)

    return DeepMercuryFactorNarrative(
        core_theme=core_theme,
        summary=summary,
        subsections=subsections,
        supporting_fact_ids=sorted(
            set(all_support) or [fact.id for fact in narrative_pool]
        ),
        conditional_fact_ids=sorted({fact.id for fact in conditional_facts}),
    )


def enrich_additive_themes(
    themes: list[DeepMercuryAdditiveTheme],
) -> list[DeepMercuryAdditiveTheme]:
    return [
        item.model_copy(update={"label": item.label or tag_label(item.tag)})
        for item in themes
    ]


def enrich_reinforcing(
    items: list[DeepMercuryReinforcingSignal],
) -> list[DeepMercuryReinforcingSignal]:
    return [
        item.model_copy(
            update={"label": item.label or signal_label(item.signal)}
        )
        for item in items
    ]


def enrich_contrasting(
    items: list[DeepMercuryContrastingSignal],
) -> list[DeepMercuryContrastingSignal]:
    enriched: list[DeepMercuryContrastingSignal] = []
    for item in items:
        label = item.label or (
            f"{tag_label(item.tag_a)} and {tag_label(item.tag_b)}"
        )
        enriched.append(item.model_copy(update={"label": label}))
    return enriched


def _aspect_actor(aspect_title: str) -> str:
    parts = aspect_title.split()
    return parts[-1] if parts else aspect_title


def _grouped_add_phrases(adds: list[DeepMercuryAdditiveTheme]) -> list[str]:
    add_tags = {item.tag for item in adds}
    phrases: list[str] = []
    covered: set[str] = set()
    for phrase, group in _ASPECT_ADD_GROUPS:
        hit = add_tags & group
        if hit:
            phrases.append(phrase)
            covered.update(hit)
    leftover = sorted(add_tags - covered)
    if leftover and len(phrases) < 3:
        phrases.append(tag_phrase(leftover[0]))
    return phrases[:3]


def build_aspect_narrative_statement(
    *,
    aspect_title: str,
    adds: list[DeepMercuryAdditiveTheme],
    reinforcing: list[DeepMercuryReinforcingSignal],
    contrasting: list[DeepMercuryContrastingSignal],
) -> str | None:
    actor = _aspect_actor(aspect_title)
    parts: list[str] = []

    if adds:
        grouped = _grouped_add_phrases(adds)
        if len(grouped) == 1:
            parts.append(f"{actor} adds {grouped[0]} to Mercury.")
        else:
            parts.append(
                f"{actor} intensifies Mercury, adding {_join_human(grouped)}."
            )

    if reinforcing:
        labels = [
            tag_phrase(_SIGNAL_TO_TAG.get(item.signal, item.signal))
            for item in reinforcing
        ]
        parts.append(
            f"It strengthens {_join_human(labels)} already present in the "
            f"base Mercury."
        )

    if contrasting:
        for item in contrasting:
            parts.append(
                f"It creates a contrast between {tag_phrase(item.tag_a)} and "
                f"{tag_phrase(item.tag_b)}."
            )

    if not parts:
        return None
    return " ".join(parts)


def _human_layer(provenance_key: str) -> str:
    factor_type, _, factor_key = provenance_key.partition(":")
    if factor_type == "sign":
        return f"Mercury in {factor_key}"
    if factor_type == "house":
        return f"House {factor_key}"
    if factor_type == "motion":
        if factor_key.lower() == "retrograde":
            return "retrograde motion"
        if factor_key.lower() == "direct":
            return "direct motion"
        return f"{factor_key} motion"
    if factor_type == "aspect":
        aspect_type, _, planet = factor_key.partition("_")
        return f"Mercury {aspect_type} {planet}"
    return factor_key or provenance_key


def _ordered_layers(provenance_keys: list[str]) -> list[str]:
    rank = {"sign": 0, "house": 1, "motion": 2, "aspect": 3}

    def key_fn(item: str) -> tuple:
        factor_type, _, _ = item.partition(":")
        return (rank.get(factor_type, 99), item)

    return sorted(provenance_keys, key=key_fn)


def _aspect_planet_from_keys(provenance_keys: list[str]) -> str | None:
    for key in _ordered_layers(provenance_keys):
        if key.startswith("aspect:"):
            _, _, factor_key = key.partition(":")
            _, _, planet = factor_key.partition("_")
            return planet or None
    return None


def humanize_integrated_takeaway(
    item: DeepMercuryIntegratedTakeaway,
) -> DeepMercuryIntegratedTakeaway:
    """Outcome-first copy. Evidence relationships stay on provenance_keys."""
    ordered_keys = _ordered_layers(list(item.provenance_keys))
    has_sign = any(key.startswith("sign:") for key in ordered_keys)
    has_house = any(key.startswith("house:") for key in ordered_keys)
    has_motion = any(key.startswith("motion:") for key in ordered_keys)
    has_aspect = any(key.startswith("aspect:") for key in ordered_keys)
    planet = _aspect_planet_from_keys(ordered_keys)

    if item.basis == "repeated_signal":
        theme_phrase = tag_phrase(
            _SIGNAL_TO_TAG.get(item.signal or "", item.signal or "")
        )
        if has_sign and has_aspect and planet:
            text = (
                f"This Mercury already carries {theme_phrase}; {planet} can "
                f"intensify that edge."
            )
        elif has_sign and has_motion:
            if item.signal == "nonstandard_thinking":
                text = (
                    "Retrograde motion adds more inward, nonstandard processing "
                    "to the base Mercury."
                )
            else:
                text = (
                    f"Motion and sign together support {theme_phrase} in how "
                    f"this Mercury operates."
                )
        elif has_sign and has_house:
            if item.signal == "sales":
                text = (
                    "House expression can amplify outward, sales-facing "
                    "communication in this Mercury."
                )
            else:
                text = (
                    f"House expression can amplify {theme_phrase} in this "
                    f"Mercury."
                )
        else:
            text = f"This Mercury shows {theme_phrase} as a recurring theme."
    elif item.basis == "contrasting_signal":
        raw = item.signal or ""
        if "_vs_" in raw:
            tag_a, _, tag_b = raw.partition("_vs_")
            text = (
                f"A lasting tension can sit between {tag_phrase(tag_a)} and "
                f"{tag_phrase(tag_b)}."
            )
        else:
            text = (
                "A lasting contrast can shape how this Mercury works under "
                "pressure."
            )
    else:  # aspect_addition
        actor = planet or "This aspect"
        text = (
            f"{actor} intensifies verbal force, conflict, and persuasive "
            f"pressure beyond what the base Mercury factors alone suggest."
        )

    for key in item.provenance_keys:
        if key in text:
            text = text.replace(key, _human_layer(key))

    return item.model_copy(update={"text": text})


def select_integrated_for_presentation(
    takeaways: list[DeepMercuryIntegratedTakeaway],
    *,
    max_items: int = 4,
) -> list[DeepMercuryIntegratedTakeaway]:
    """Prefer outcome mix: character, modifiers, tension, aspect intensity."""
    repeats = [item for item in takeaways if item.basis == "repeated_signal"]
    contrasts = [item for item in takeaways if item.basis == "contrasting_signal"]
    additions = [item for item in takeaways if item.basis == "aspect_addition"]

    preferred_repeat_order = ("debate", "nonstandard_thinking", "sales")
    repeats_sorted = sorted(
        repeats,
        key=lambda item: (
            preferred_repeat_order.index(item.signal)
            if item.signal in preferred_repeat_order
            else 99,
            item.signal or "",
        ),
    )
    selected: list[DeepMercuryIntegratedTakeaway] = []
    selected.extend(repeats_sorted[:2])
    if contrasts:
        selected.append(contrasts[0])
    if additions:
        selected.append(additions[0])
    for item in repeats_sorted:
        if len(selected) >= max_items:
            break
        if item not in selected:
            selected.append(item)
    return selected[:max_items]


def attach_factor_narrative(
    block: DeepMercuryFactorBlock,
    facts: list[SourceFact],
) -> DeepMercuryFactorBlock:
    if block.availability != "available":
        return block
    narrative = build_factor_narrative(
        factor_type=block.factor_type,
        factor_key=block.factor_key,
        title=block.title,
        facts=facts,
    )
    if narrative is None:
        return block
    return block.model_copy(update={"narrative": narrative})


def attach_aspect_human_copy(
    block: DeepMercuryAspectBlock,
) -> DeepMercuryAspectBlock:
    interaction = block.interaction
    if not interaction.available:
        return block
    adds = enrich_additive_themes(list(interaction.adds))
    reinforcing = enrich_reinforcing(list(interaction.reinforcing))
    contrasting = enrich_contrasting(list(interaction.contrasting))
    statement = build_aspect_narrative_statement(
        aspect_title=block.identity.title,
        adds=adds,
        reinforcing=reinforcing,
        contrasting=contrasting,
    )
    return block.model_copy(
        update={
            "interaction": interaction.model_copy(
                update={
                    "adds": adds,
                    "reinforcing": reinforcing,
                    "contrasting": contrasting,
                    "statement": statement,
                }
            )
        }
    )
