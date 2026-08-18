"""Mercury Source Profile v2 — House Batch B3.

House 8 has Lesson 7 + Bioastrology (dual-source parity).
House 11 has Lesson 7 + Bioastrology (dual-source parity).
House 12 remains Lesson 7 only until its Bioastrology pass.

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


REF_H8_L7 = "lesson7_mercury_house_8"
REF_H8_BIO = "bioastrology_mercury_house_8"
REF_H11_L7 = "lesson7_mercury_house_11"
REF_H11_BIO = "bioastrology_mercury_house_11"
REF_H12_L7 = "lesson7_mercury_house_12"

# ---------------------------------------------------------------------------
# Mercury in House 8 — Lesson 7
# ---------------------------------------------------------------------------
HOUSE_8: tuple[SourceFactDef, ...] = (
    _f("h8_ability_to_influence_people_through_words", "house", "8", "communication",
       "Ability to influence people through words.",
       "strength", "verbal_influence",
       source_reference=REF_H8_L7),
    _f("h8_ability_to_impose_ones_opinion", "house", "8", "communication",
       "Ability / tendency to impose one's opinion.",
       "neutral", "opinion_imposition",
       source_reference=REF_H8_L7),
    _f("h8_perceptiveness", "house", "8", "thinking",
       "Perceptiveness / penetrating perception.",
       "strength", "perceptiveness",
       source_reference=REF_H8_L7),
    _f("h8_research_talent", "house", "8", "learning",
       "Research talent.",
       "strength", "research_talent",
       source_reference=REF_H8_L7),
    _f("h8_deep_thinking", "house", "8", "thinking",
       "Deep thinking.",
       "strength", "deep_thinking",
       source_reference=REF_H8_L7),
    _f("h8_intense_intellectual_concentration", "house", "8", "focus",
       "Ability to concentrate intensely on intellectual work.",
       "strength", "intense_intellectual_concentration",
       source_reference=REF_H8_L7),
    _f("h8_decipher_information_from_hidden_sources", "house", "8", "thinking",
       "Ability to decipher information from hidden sources.",
       "strength", "hidden_source_information_decoding",
       source_reference=REF_H8_L7),
    _f("h8_financial_resourcefulness", "house", "8", "work_application",
       "Dexterity / resourcefulness in financial matters.",
       "strength", "financial_resourcefulness",
       source_reference=REF_H8_L7),
    _f("h8_maneuver_around_loans", "house", "8", "work_application",
       "Ability to maneuver around loans.",
       "neutral", "loan_resourcefulness",
       source_reference=REF_H8_L7),
    _f("h8_maneuver_around_discounts", "house", "8", "work_application",
       "Ability to maneuver around discounts.",
       "neutral", "discount_resourcefulness",
       source_reference=REF_H8_L7),
    _f("h8_interest_associations_secrets_detective_occult", "house", "8", "source_specific",
       "Source lists interest in secrets, detective stories, crime chronicles, mysticism, "
       "and occult topics; interest associations, not certified abilities.",
       "neutral", "secrets_detective_occult_interest_associations",
       source_reference=REF_H8_L7),
    _f("h8_thoughts_formulated_in_very_sharp_form", "house", "8", "communication",
       "Thoughts are formulated in a very sharp form.",
       "risk", "sharp_thought_expression",
       source_reference=REF_H8_L7),
    _f("h8_word_caused_crisis_risk", "house", "8", "risk",
       "Source wording \"my tongue is my enemy\": crisis can arise because of a letter / "
       "written word or a spoken word.",
       "risk", "word_caused_crisis_risk",
       source_reference=REF_H8_L7),
    _f("h8_intrigue_tendency", "house", "8", "risk",
       "Intrigue / scheming (source-described tendency, not a deterministic accusation).",
       "risk", "intrigue_tendency",
       source_reference=REF_H8_L7),
    _f("h8_malicious_speech", "house", "8", "risk",
       "Malicious talk / slanderous speech (source-described tendency, not a deterministic "
       "accusation).",
       "risk", "malicious_speech",
       source_reference=REF_H8_L7),
    _f("h8_source_vascular_problem_risk", "house", "8", "source_specific",
       "Source explicitly lists vascular problems as a source-described physical claim; "
       "not a medical diagnosis or validated health prediction.",
       "risk", "source_vascular_problem_risk",
       source_reference=REF_H8_L7),
    _f("h8_source_hand_injury_risk", "house", "8", "source_specific",
       "Source explicitly lists injuries to hands as a source-described physical claim; "
       "not a medical diagnosis or validated health prediction.",
       "risk", "source_hand_injury_risk",
       source_reference=REF_H8_L7),
    _f("h8_source_finger_injury_risk", "house", "8", "source_specific",
       "Source explicitly lists injuries to fingers as a source-described physical claim; "
       "not a medical diagnosis or validated health prediction.",
       "risk", "source_finger_injury_risk",
       source_reference=REF_H8_L7),
)

# ---------------------------------------------------------------------------
# Mercury in House 8 — Bioastrology (dual-source parity; HOUSE_8 L7 is frozen)
# ---------------------------------------------------------------------------
HOUSE_8_BIO: tuple[SourceFactDef, ...] = (
    _f("h8_bio_communication_learning_demanded_in_crises", "house", "8",
       "source_specific",
       "Communication and learning may be demanded in crisis situations.",
       "neutral",
       source_reference=REF_H8_BIO),
    _f("h8_bio_communication_learning_demanded_in_finance", "house", "8",
       "source_specific",
       "Communication and learning may be demanded in financial matters.",
       "neutral",
       source_reference=REF_H8_BIO),
    _f("h8_bio_communication_learning_demanded_in_psychology", "house", "8",
       "source_specific",
       "Communication and learning may be demanded in psychology-related contexts.",
       "neutral",
       source_reference=REF_H8_BIO),
    _f("h8_bio_communication_learning_demanded_in_magic", "house", "8",
       "source_specific",
       "Communication and learning may be demanded in magic-related contexts.",
       "neutral",
       source_reference=REF_H8_BIO),
    _f("h8_bio_commercial_resourcefulness", "house", "8", "work_application",
       "Commercial resourcefulness.",
       "strength",
       source_reference=REF_H8_BIO),
    _f("h8_bio_investments_other_people_money", "house", "8", "work_application",
       "Circumstances may require calculating investments and other people's money.",
       "neutral",
       source_reference=REF_H8_BIO),
    _f("h8_bio_tongue_enemy_crisis_effect", "house", "8", "risk",
       "Source-described \"my tongue is my enemy\" crisis effect.",
       "risk",
       source_reference=REF_H8_BIO),
    _f("h8_bio_power_of_word", "house", "8", "communication",
       "The word may carry strong influence or power.",
       "strength",
       source_reference=REF_H8_BIO),
    _f("h8_bio_solitary_critical_learning_method", "house", "8", "learning",
       "Learning may occur alone and in a critical mode, through analyzing sources "
       "and errors, comparing, and evaluating.",
       "strength",
       source_reference=REF_H8_BIO),
    _f("h8_bio_analytical_ability", "house", "8", "thinking",
       "May support analytical ability.",
       "strength", "analytical_thinking",
       source_reference=REF_H8_BIO),
    _f("h8_bio_detective_ability", "house", "8", "thinking",
       "May support detective abilities.",
       "strength",
       source_reference=REF_H8_BIO),
    _f("h8_bio_interest_in_energies", "house", "8", "source_specific",
       "May show strong interest in energies.",
       "strength",
       source_reference=REF_H8_BIO),
    _f("h8_bio_interest_in_sex", "house", "8", "source_specific",
       "May show strong interest in sex.",
       "strength",
       source_reference=REF_H8_BIO),
    _f("h8_bio_afflicted_gossip", "house", "8", "source_specific",
       "When Mercury is afflicted, the source associates this placement with "
       "gossip (afflicted-Mercury dependency; no house-affliction resolver is "
       "applied; not hard_aspected).",
       "conditional",
       source_reference=REF_H8_BIO, unresolved=True),
    _f("h8_bio_afflicted_hate", "house", "8", "source_specific",
       "When Mercury is afflicted, the source associates this placement with "
       "hate (afflicted-Mercury dependency; no house-affliction resolver is "
       "applied; not hard_aspected).",
       "conditional",
       source_reference=REF_H8_BIO, unresolved=True),
    _f("h8_bio_afflicted_traffic_accident_association", "house", "8",
       "source_specific",
       "When Mercury is afflicted, the source associates this placement with "
       "traffic accidents (afflicted-Mercury dependency; no house-affliction "
       "resolver is applied; not hard_aspected).",
       "conditional",
       source_reference=REF_H8_BIO, unresolved=True),
    _f("h8_bio_afflicted_vascular_disease_association", "house", "8",
       "source_specific",
       "When Mercury is afflicted, the source associates this placement with "
       "diseases involving blood vessels (afflicted-Mercury dependency; "
       "no house-affliction resolver is applied; not hard_aspected).",
       "conditional",
       source_reference=REF_H8_BIO, unresolved=True),
    _f("h8_bio_afflicted_joint_disease_association", "house", "8", "source_specific",
       "When Mercury is afflicted, the source associates this placement with "
       "diseases involving joints (afflicted-Mercury dependency; no house-affliction "
       "resolver is applied; not hard_aspected).",
       "conditional",
       source_reference=REF_H8_BIO, unresolved=True),
    _f("h8_bio_afflicted_lung_disease_association", "house", "8", "source_specific",
       "When Mercury is afflicted, the source associates this placement with "
       "diseases involving lungs (afflicted-Mercury dependency; no house-affliction "
       "resolver is applied; not hard_aspected).",
       "conditional",
       source_reference=REF_H8_BIO, unresolved=True),
    _f("h8_bio_afflicted_limb_disease_association", "house", "8", "source_specific",
       "When Mercury is afflicted, the source associates this placement with "
       "diseases involving limbs (afflicted-Mercury dependency; no house-affliction "
       "resolver is applied; not hard_aspected).",
       "conditional",
       source_reference=REF_H8_BIO, unresolved=True),
)

# ---------------------------------------------------------------------------
# Mercury in House 11 — Lesson 7
# ---------------------------------------------------------------------------
HOUSE_11: tuple[SourceFactDef, ...] = (
    _f("h11_constant_social_interaction", "house", "11", "environment",
       "Constant social interaction.",
       "neutral", "constant_social_interaction",
       source_reference=REF_H11_L7),
    _f("h11_learn_yourself", "house", "11", "learning",
       "Learn yourself.",
       "strength", "self_learning",
       source_reference=REF_H11_L7),
    _f("h11_teach_others", "house", "11", "learning",
       "Teach others (House 11 social-learning context; not equated with global teaching "
       "ability).",
       "neutral", "teaching_others",
       source_reference=REF_H11_L7),
    _f("h11_friends_are_sources_of_knowledge", "house", "11", "learning",
       "Friends are sources of knowledge.",
       "strength", "friends_as_knowledge_source",
       source_reference=REF_H11_L7),
    _f("h11_groups_are_sources_of_knowledge", "house", "11", "learning",
       "Collectives / groups are sources of knowledge.",
       "strength", "groups_as_knowledge_source",
       source_reference=REF_H11_L7),
    _f("h11_social_impulse_to_study", "house", "11", "learning",
       "Friends / groups create an impulse to study.",
       "neutral", "social_impulse_to_learning",
       source_reference=REF_H11_L7),
    _f("h11_scientific_type_of_thinking_context", "house", "11", "thinking",
       "Circumstances create a scientific type / style of thinking.",
       "strength", "scientific_thinking_context",
       source_reference=REF_H11_L7),
    _f("h11_democratic_contact_regardless_of_status", "house", "11", "communication",
       "Democratic contact regardless of social status.",
       "strength", "status_independent_democratic_contact",
       source_reference=REF_H11_L7),
    _f("h11_universal_mind", "house", "11", "thinking",
       "Universal mind (source-described cognition statement).",
       "strength", "universal_mind",
       source_reference=REF_H11_L7),
    _f("h11_pioneer_inventor_reformer_associations", "house", "11", "source_specific",
       "Source associations include pioneers, inventors, and reformers; archetypal / "
       "occupation associations, not automatic professional abilities.",
       "neutral", "pioneer_inventor_reformer_associations",
       source_reference=REF_H11_L7),
    _f("h11_many_quick_acquaintances", "house", "11", "environment",
       "Many quick acquaintances.",
       "neutral", "rapid_acquaintance_formation",
       source_reference=REF_H11_L7),
    _f("h11_acquaintances_for_exchanging_advice_and_ideas", "house", "11", "communication",
       "Purpose of acquaintances: exchanging advice and ideas.",
       "neutral", "advice_idea_exchange_contacts",
       source_reference=REF_H11_L7),
    _f("h11_empty_pointless_acquaintances", "house", "11", "risk",
       "Empty / pointless acquaintances.",
       "risk", "empty_contact_risk",
       source_reference=REF_H11_L7),
    _f("h11_unpromising_acquaintances", "house", "11", "risk",
       "Unpromising acquaintances.",
       "risk", "unpromising_contact_risk",
       source_reference=REF_H11_L7),
    _f("h11_fierce_bitter_arguments", "house", "11", "risk",
       "Fierce / bitter arguments.",
       "risk", "fierce_arguments",
       source_reference=REF_H11_L7),
    _f("h11_fierce_bitter_discussions", "house", "11", "risk",
       "Fierce / bitter discussions.",
       "risk", "fierce_discussions",
       source_reference=REF_H11_L7),
    _f("h11_gossip_from_friends", "house", "11", "source_specific",
       "Gossip from friends (friend / social-environment association, not a native trait).",
       "risk", "friend_gossip_risk",
       source_reference=REF_H11_L7),
    _f("h11_lying_from_friends", "house", "11", "source_specific",
       "Lying from friends (friend / social-environment association, not a native trait).",
       "risk", "friend_lying_risk",
       source_reference=REF_H11_L7),
    _f("h11_deception_from_friends", "house", "11", "source_specific",
       "Deception from friends (friend / social-environment association, not a native trait).",
       "risk", "friend_deception_risk",
       source_reference=REF_H11_L7),
    _f("h11_meaningless_plans", "house", "11", "risk",
       "Meaningless plans.",
       "risk", "meaningless_plan_risk",
       source_reference=REF_H11_L7),
    _f("h11_meaningless_projects", "house", "11", "risk",
       "Meaningless projects.",
       "risk", "meaningless_project_risk",
       source_reference=REF_H11_L7),
    _f("h11_plans_projects_detached_from_reality", "house", "11", "risk",
       "Plans / projects detached from reality.",
       "risk", "reality_detached_project_risk",
       source_reference=REF_H11_L7),
)

# ---------------------------------------------------------------------------
# Mercury in House 11 — Bioastrology (dual-source parity; HOUSE_11 L7 is frozen)
# ---------------------------------------------------------------------------
HOUSE_11_BIO: tuple[SourceFactDef, ...] = (
    _f("h11_bio_communication_learning_realized_through_internet", "house", "11",
       "source_specific",
       "Communication and learning may be realized through the Internet.",
       "neutral",
       source_reference=REF_H11_BIO),
    _f("h11_bio_communication_learning_realized_through_collectives", "house", "11",
       "source_specific",
       "Communication and learning may be realized through collectives or groups.",
       "neutral",
       source_reference=REF_H11_BIO),
    _f("h11_bio_communication_learning_realized_through_clubs", "house", "11",
       "source_specific",
       "Communication and learning may be realized through clubs.",
       "neutral",
       source_reference=REF_H11_BIO),
    _f("h11_bio_communication_learning_realized_through_gatherings", "house", "11",
       "source_specific",
       "Communication and learning may be realized through gatherings or meetings.",
       "neutral",
       source_reference=REF_H11_BIO),
    _f("h11_bio_communication_learning_realized_through_forums", "house", "11",
       "source_specific",
       "Communication and learning may be realized through forums.",
       "neutral",
       source_reference=REF_H11_BIO),
    _f("h11_bio_intellect_becomes_scientific", "house", "11", "thinking",
       "Over time, the intellect may become more scientific in orientation.",
       "neutral",
       source_reference=REF_H11_BIO),
    _f("h11_bio_intellect_becomes_technological", "house", "11", "thinking",
       "Over time, the intellect may become more technological in orientation.",
       "neutral",
       source_reference=REF_H11_BIO),
    _f("h11_bio_universal_intellect", "house", "11", "thinking",
       "Source describes a broadly universal intellect with an ability to learn "
       "across many subjects.",
       "strength",
       source_reference=REF_H11_BIO),
    _f("h11_bio_learning_oriented_toward_high_technologies", "house", "11", "learning",
       "Learning may be especially oriented toward high technologies.",
       "strength",
       source_reference=REF_H11_BIO),
    _f("h11_bio_learning_with_equals_or_peers", "house", "11", "learning",
       "Learning may occur with or through equals or peers.",
       "strength",
       source_reference=REF_H11_BIO),
    _f("h11_bio_learning_with_friends", "house", "11", "learning",
       "Learning may occur with or through friends.",
       "strength",
       source_reference=REF_H11_BIO),
    _f("h11_bio_learning_in_group_or_collective", "house", "11", "learning",
       "Learning may occur in a group or collective setting.",
       "strength",
       source_reference=REF_H11_BIO),
    _f("h11_bio_broad_social_popularity", "house", "11", "source_specific",
       "Favorable association with broad social popularity.",
       "strength",
       source_reference=REF_H11_BIO),
    _f("h11_bio_many_discussed_plans", "house", "11", "source_specific",
       "There may be a large number of discussed plans.",
       "neutral",
       source_reference=REF_H11_BIO),
    _f("h11_bio_many_discussed_projects", "house", "11", "source_specific",
       "There may be a large number of discussed projects.",
       "neutral",
       source_reference=REF_H11_BIO),
)

# ---------------------------------------------------------------------------
# Mercury in House 12 — Lesson 7
# ---------------------------------------------------------------------------
HOUSE_12: tuple[SourceFactDef, ...] = (
    _f("h12_mind_brightest_in_occult", "house", "12", "source_specific",
       "Mind shows itself most brightly in the occult "
       "(source-framework claim; not a scientifically validated skill).",
       "neutral", "occult_intellectual_expression",
       source_reference=REF_H12_L7),
    _f("h12_mind_brightest_in_unknown_unexplored", "house", "12", "source_specific",
       "Mind shows itself most brightly in the unknown / unexplored "
       "(source-framework claim; not a scientifically validated skill).",
       "neutral", "unknown_domain_intellectual_expression",
       source_reference=REF_H12_L7),
    _f("h12_ability_to_decipher_hidden_meanings", "house", "12", "thinking",
       "Ability to decipher hidden meanings.",
       "strength", "hidden_meaning_decoding",
       source_reference=REF_H12_L7),
    _f("h12_talent_for_putting_inexplicable_into_words", "house", "12", "communication",
       "Talent for putting the inexplicable into words "
       "(source-described expression claim; not treated as paranormal proof).",
       "strength", "verbalizing_inexplicable",
       source_reference=REF_H12_L7),
    _f("h12_many_secrets", "house", "12", "environment",
       "Many secrets.",
       "neutral", "secret_heavy_context",
       source_reference=REF_H12_L7),
    _f("h12_circumstances_require_keeping_secrets", "house", "12", "environment",
       "Circumstances require keeping secrets.",
       "neutral", "secret_keeping_requirement",
       source_reference=REF_H12_L7),
    _f("h12_ability_to_think_alone", "house", "12", "thinking",
       "Ability to think alone.",
       "strength", "solitary_thinking",
       source_reference=REF_H12_L7),
    _f("h12_ability_to_learn_alone", "house", "12", "learning",
       "Ability to learn alone.",
       "strength", "solitary_learning",
       source_reference=REF_H12_L7),
    _f("h12_learning_more_interesting_remotely", "house", "12", "learning",
       "Learning is more interesting remotely.",
       "neutral", "distance_learning_preference",
       source_reference=REF_H12_L7),
    _f("h12_learning_more_interesting_as_external_student", "house", "12", "learning",
       "Learning is more interesting as an external student / externship.",
       "neutral", "external_study_preference",
       source_reference=REF_H12_L7),
    _f("h12_talks_internally_more_than_externally", "house", "12", "communication",
       "Talks internally more often than externally.",
       "neutral", "internal_dialogue_dominance",
       source_reference=REF_H12_L7),
    _f("h12_difficult_to_express_oneself_in_front_of_people", "house", "12", "communication",
       "Difficult to express oneself in front of people.",
       "risk", "public_expression_difficulty",
       source_reference=REF_H12_L7),
    _f("h12_uncomfortable_to_express_oneself_in_front_of_people", "house", "12", "communication",
       "Uncomfortable to express oneself in front of people.",
       "risk", "public_expression_discomfort",
       source_reference=REF_H12_L7),
    _f("h12_writes_for_the_drawer", "house", "12", "communication",
       "Writes \"for the drawer\".",
       "neutral", "private_undisplayed_writing",
       source_reference=REF_H12_L7),
    _f("h12_does_not_show_fruits_of_intellectual_creativity", "house", "12", "communication",
       "Does not show fruits of intellectual creativity.",
       "neutral", "hidden_intellectual_output",
       source_reference=REF_H12_L7),
    _f("h12_subconscious_strongly_influences_thinking", "house", "12", "thinking",
       "Subconscious strongly influences thinking.",
       "neutral", "subconscious_influence_on_thinking",
       source_reference=REF_H12_L7),
    _f("h12_decisions_more_often_not_logical", "house", "12", "thinking",
       "Decisions are more often not logical.",
       "neutral", "nonlogical_decision_tendency",
       source_reference=REF_H12_L7),
    _f("h12_operates_with_guesses", "house", "12", "thinking",
       "Operates with guesses.",
       "neutral", "guess_based_reasoning",
       source_reference=REF_H12_L7),
    _f("h12_operates_with_gossip", "house", "12", "communication",
       "Operates with gossip.",
       "neutral", "gossip_based_information",
       source_reference=REF_H12_L7),
    _f("h12_solitude_through_internet_psychology_medicine", "house", "12", "source_specific",
       "May go into the internet, psychology, or medicine as a way of isolating / being alone "
       "(source-described solitude pathways; not a clinical diagnosis).",
       "neutral", "solitude_through_internet_psychology_medicine",
       source_reference=REF_H12_L7),
)

B3_HOUSE_PACKS: tuple[SourceFactDef, ...] = (
    HOUSE_8 + HOUSE_8_BIO + HOUSE_11 + HOUSE_11_BIO + HOUSE_12
)
B3_SUPPORTED_HOUSE_KEYS = frozenset({"8", "11", "12"})
