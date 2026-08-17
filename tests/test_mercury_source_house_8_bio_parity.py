"""Tests for Mercury House 8 Bioastrology source parity (S4.27B)."""

from __future__ import annotations

import unittest
from collections import Counter

from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_human_copy import HUMAN_COPY_OVERRIDES
from app.services.mercury_human_copy_catalog import (
    APPROVED_RAW_FACT_IDS,
    NEEDS_REVIEW_FACT_IDS,
    STATUS_UNREVIEWED,
    build_catalog_entry,
    build_human_copy_catalog,
)
from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS, REPEATED_SIGNAL_SPECS
from app.services.mercury_source_knowledge_b3_houses import (
    HOUSE_8,
    HOUSE_8_BIO,
    REF_H8_BIO,
    REF_H8_L7,
)
from app.services.mercury_source_profile import (
    _provenance_key,
    build_source_profile_from_factors,
    detect_repeated_signals,
)


EXPECTED_BIO_IDS: tuple[str, ...] = (
    "h8_bio_communication_learning_demanded_in_crises",
    "h8_bio_communication_learning_demanded_in_finance",
    "h8_bio_communication_learning_demanded_in_psychology",
    "h8_bio_communication_learning_demanded_in_magic",
    "h8_bio_commercial_resourcefulness",
    "h8_bio_investments_other_people_money",
    "h8_bio_tongue_enemy_crisis_effect",
    "h8_bio_power_of_word",
    "h8_bio_solitary_critical_learning_method",
    "h8_bio_analytical_ability",
    "h8_bio_detective_ability",
    "h8_bio_interest_in_energies",
    "h8_bio_interest_in_sex",
    "h8_bio_afflicted_gossip",
    "h8_bio_afflicted_hate",
    "h8_bio_afflicted_traffic_accident_association",
    "h8_bio_afflicted_vascular_disease_association",
    "h8_bio_afflicted_joint_disease_association",
    "h8_bio_afflicted_lung_disease_association",
    "h8_bio_afflicted_limb_disease_association",
)

EXPECTED_BIO_CANONICAL: dict[str, str] = {
    "h8_bio_communication_learning_demanded_in_crises": (
        "Communication and learning may be demanded in crisis situations."
    ),
    "h8_bio_communication_learning_demanded_in_finance": (
        "Communication and learning may be demanded in financial matters."
    ),
    "h8_bio_communication_learning_demanded_in_psychology": (
        "Communication and learning may be demanded in psychology-related contexts."
    ),
    "h8_bio_communication_learning_demanded_in_magic": (
        "Communication and learning may be demanded in magic-related contexts."
    ),
    "h8_bio_commercial_resourcefulness": "Commercial resourcefulness.",
    "h8_bio_investments_other_people_money": (
        "Circumstances may require calculating investments and other people's money."
    ),
    "h8_bio_tongue_enemy_crisis_effect": (
        "Source-described \"my tongue is my enemy\" crisis effect."
    ),
    "h8_bio_power_of_word": "The word may carry strong influence or power.",
    "h8_bio_solitary_critical_learning_method": (
        "Learning may occur alone and in a critical mode, through analyzing sources "
        "and errors, comparing, and evaluating."
    ),
    "h8_bio_analytical_ability": "May support analytical ability.",
    "h8_bio_detective_ability": "May support detective abilities.",
    "h8_bio_interest_in_energies": "May show strong interest in energies.",
    "h8_bio_interest_in_sex": "May show strong interest in sex.",
    "h8_bio_afflicted_gossip": (
        "When Mercury is afflicted, the source associates this placement with "
        "gossip (afflicted-Mercury dependency; no house-affliction resolver is "
        "applied; not hard_aspected)."
    ),
    "h8_bio_afflicted_hate": (
        "When Mercury is afflicted, the source associates this placement with "
        "hate (afflicted-Mercury dependency; no house-affliction resolver is "
        "applied; not hard_aspected)."
    ),
    "h8_bio_afflicted_traffic_accident_association": (
        "When Mercury is afflicted, the source associates this placement with "
        "traffic accidents (afflicted-Mercury dependency; no house-affliction "
        "resolver is applied; not hard_aspected)."
    ),
    "h8_bio_afflicted_vascular_disease_association": (
        "When Mercury is afflicted, the source associates this placement with "
        "diseases involving blood vessels (afflicted-Mercury dependency; "
        "no house-affliction resolver is applied; not hard_aspected)."
    ),
    "h8_bio_afflicted_joint_disease_association": (
        "When Mercury is afflicted, the source associates this placement with "
        "diseases involving joints (afflicted-Mercury dependency; no house-affliction "
        "resolver is applied; not hard_aspected)."
    ),
    "h8_bio_afflicted_lung_disease_association": (
        "When Mercury is afflicted, the source associates this placement with "
        "diseases involving lungs (afflicted-Mercury dependency; no house-affliction "
        "resolver is applied; not hard_aspected)."
    ),
    "h8_bio_afflicted_limb_disease_association": (
        "When Mercury is afflicted, the source associates this placement with "
        "diseases involving limbs (afflicted-Mercury dependency; no house-affliction "
        "resolver is applied; not hard_aspected)."
    ),
}

EXPECTED_BIO_TAGS: dict[str, tuple[str, ...]] = {
    "h8_bio_analytical_ability": ("analytical_thinking",),
}

UNTAGGED_BIO_IDS: tuple[str, ...] = tuple(
    fact_id for fact_id in EXPECTED_BIO_IDS if fact_id not in EXPECTED_BIO_TAGS
)

UNRESOLVED_BIO_IDS: tuple[str, ...] = (
    "h8_bio_afflicted_gossip",
    "h8_bio_afflicted_hate",
    "h8_bio_afflicted_traffic_accident_association",
    "h8_bio_afflicted_vascular_disease_association",
    "h8_bio_afflicted_joint_disease_association",
    "h8_bio_afflicted_lung_disease_association",
    "h8_bio_afflicted_limb_disease_association",
)

L7_MEDICAL_IDS: tuple[str, ...] = (
    "h8_source_vascular_problem_risk",
    "h8_source_hand_injury_risk",
    "h8_source_finger_injury_risk",
)

AFFLICTED_MEDICAL_BIO_IDS: tuple[str, ...] = (
    "h8_bio_afflicted_vascular_disease_association",
    "h8_bio_afflicted_joint_disease_association",
    "h8_bio_afflicted_lung_disease_association",
    "h8_bio_afflicted_limb_disease_association",
)

FORBIDDEN_APPROXIMATE_TAGS: tuple[str, ...] = (
    "financial_resourcefulness",
    "commercial_ability",
    "word_caused_crisis_risk",
    "verbal_influence",
    "persuasion",
    "argumentation",
    "debate",
    "detective_thinking",
    "secrets_detective_occult_interest_associations",
    "source_sexual_motivation_wording",
    "source_vascular_problem_risk",
    "source_hand_injury_risk",
    "source_finger_injury_risk",
    "intrigue_tendency",
    "malicious_speech",
    "research_talent",
    "deep_thinking",
    "perceptiveness",
)

FROZEN_L7_HOUSE_8: tuple[
    tuple[str, str, str, str, tuple[str, ...], str, bool], ...
] = (
    (
        "h8_ability_to_influence_people_through_words",
        "communication",
        "Ability to influence people through words.",
        "strength",
        ("verbal_influence",),
        REF_H8_L7,
        False,
    ),
    (
        "h8_ability_to_impose_ones_opinion",
        "communication",
        "Ability / tendency to impose one's opinion.",
        "neutral",
        ("opinion_imposition",),
        REF_H8_L7,
        False,
    ),
    (
        "h8_perceptiveness",
        "thinking",
        "Perceptiveness / penetrating perception.",
        "strength",
        ("perceptiveness",),
        REF_H8_L7,
        False,
    ),
    (
        "h8_research_talent",
        "learning",
        "Research talent.",
        "strength",
        ("research_talent",),
        REF_H8_L7,
        False,
    ),
    (
        "h8_deep_thinking",
        "thinking",
        "Deep thinking.",
        "strength",
        ("deep_thinking",),
        REF_H8_L7,
        False,
    ),
    (
        "h8_intense_intellectual_concentration",
        "focus",
        "Ability to concentrate intensely on intellectual work.",
        "strength",
        ("intense_intellectual_concentration",),
        REF_H8_L7,
        False,
    ),
    (
        "h8_decipher_information_from_hidden_sources",
        "thinking",
        "Ability to decipher information from hidden sources.",
        "strength",
        ("hidden_source_information_decoding",),
        REF_H8_L7,
        False,
    ),
    (
        "h8_financial_resourcefulness",
        "work_application",
        "Dexterity / resourcefulness in financial matters.",
        "strength",
        ("financial_resourcefulness",),
        REF_H8_L7,
        False,
    ),
    (
        "h8_maneuver_around_loans",
        "work_application",
        "Ability to maneuver around loans.",
        "neutral",
        ("loan_resourcefulness",),
        REF_H8_L7,
        False,
    ),
    (
        "h8_maneuver_around_discounts",
        "work_application",
        "Ability to maneuver around discounts.",
        "neutral",
        ("discount_resourcefulness",),
        REF_H8_L7,
        False,
    ),
    (
        "h8_interest_associations_secrets_detective_occult",
        "source_specific",
        "Source lists interest in secrets, detective stories, crime chronicles, mysticism, "
        "and occult topics; interest associations, not certified abilities.",
        "neutral",
        ("secrets_detective_occult_interest_associations",),
        REF_H8_L7,
        False,
    ),
    (
        "h8_thoughts_formulated_in_very_sharp_form",
        "communication",
        "Thoughts are formulated in a very sharp form.",
        "risk",
        ("sharp_thought_expression",),
        REF_H8_L7,
        False,
    ),
    (
        "h8_word_caused_crisis_risk",
        "risk",
        "Source wording \"my tongue is my enemy\": crisis can arise because of a letter / "
        "written word or a spoken word.",
        "risk",
        ("word_caused_crisis_risk",),
        REF_H8_L7,
        False,
    ),
    (
        "h8_intrigue_tendency",
        "risk",
        "Intrigue / scheming (source-described tendency, not a deterministic accusation).",
        "risk",
        ("intrigue_tendency",),
        REF_H8_L7,
        False,
    ),
    (
        "h8_malicious_speech",
        "risk",
        "Malicious talk / slanderous speech (source-described tendency, not a deterministic "
        "accusation).",
        "risk",
        ("malicious_speech",),
        REF_H8_L7,
        False,
    ),
    (
        "h8_source_vascular_problem_risk",
        "source_specific",
        "Source explicitly lists vascular problems as a source-described physical claim; "
        "not a medical diagnosis or validated health prediction.",
        "risk",
        ("source_vascular_problem_risk",),
        REF_H8_L7,
        False,
    ),
    (
        "h8_source_hand_injury_risk",
        "source_specific",
        "Source explicitly lists injuries to hands as a source-described physical claim; "
        "not a medical diagnosis or validated health prediction.",
        "risk",
        ("source_hand_injury_risk",),
        REF_H8_L7,
        False,
    ),
    (
        "h8_source_finger_injury_risk",
        "source_specific",
        "Source explicitly lists injuries to fingers as a source-described physical claim; "
        "not a medical diagnosis or validated health prediction.",
        "risk",
        ("source_finger_injury_risk",),
        REF_H8_L7,
        False,
    ),
)


def _house_8_facts():
    return [
        item
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "house" and item.factor_key == "8"
    ]


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


class House8BioCoverageTests(unittest.TestCase):
    def test_programmatic_bio_count_is_20(self):
        self.assertEqual(len(HOUSE_8_BIO), 20)
        self.assertEqual(len(EXPECTED_BIO_IDS), 20)
        self.assertEqual(len(EXPECTED_BIO_CANONICAL), 20)
        self.assertEqual(tuple(item.id for item in HOUSE_8_BIO), EXPECTED_BIO_IDS)

    def test_house_8_source_counts(self):
        house_8 = _house_8_facts()
        lesson7 = [item for item in house_8 if item.source_reference == REF_H8_L7]
        bio = [item for item in house_8 if item.source_reference == REF_H8_BIO]
        self.assertEqual(len(HOUSE_8), 18)
        self.assertEqual(len(lesson7), 18)
        self.assertEqual(len(bio), 20)
        self.assertEqual(len(house_8), 38)
        self.assertEqual(len(HOUSE_8) + len(HOUSE_8_BIO), 38)

    def test_all_bio_use_bioastrology_source_reference(self):
        self.assertTrue(all(item.source_reference == REF_H8_BIO for item in HOUSE_8_BIO))
        self.assertEqual(REF_H8_BIO, "bioastrology_mercury_house_8")

    def test_all_house_8_facts_share_factor_identity(self):
        house_8 = _house_8_facts()
        self.assertEqual(len(house_8), 38)
        self.assertTrue(all(item.factor_type == "house" for item in house_8))
        self.assertTrue(all(item.factor_key == "8" for item in house_8))
        self.assertTrue(all(item.activation_condition is None for item in house_8))

    def test_ids_globally_unique(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])


class House8BioCanonicalTests(unittest.TestCase):
    def test_exact_canonical_strings_for_all_20(self):
        by_id = {item.id: item for item in HOUSE_8_BIO}
        self.assertEqual(set(by_id), set(EXPECTED_BIO_CANONICAL))
        for fact_id, canonical in EXPECTED_BIO_CANONICAL.items():
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].text, canonical)


class House8ExactOverlapTests(unittest.TestCase):
    def test_tongue_enemy_exact_atom_keeps_separate_provenance(self):
        by_id = {item.id: item for item in HOUSE_8 + HOUSE_8_BIO}
        l7 = by_id["h8_word_caused_crisis_risk"]
        bio = by_id["h8_bio_tongue_enemy_crisis_effect"]
        self.assertNotEqual(l7.id, bio.id)
        self.assertEqual(l7.source_reference, REF_H8_L7)
        self.assertEqual(bio.source_reference, REF_H8_BIO)
        self.assertNotEqual(l7.text, bio.text)
        self.assertIn("my tongue is my enemy", l7.text.lower())
        self.assertIn("my tongue is my enemy", bio.text.lower())
        self.assertEqual(l7.tags, ("word_caused_crisis_risk",))
        self.assertEqual(bio.tags, ())
        self.assertNotIn("word_caused_crisis_risk", bio.tags)


class House8PartialFidelityTests(unittest.TestCase):
    def test_finance_demand_is_not_financial_skill_cluster(self):
        by_id = {item.id: item for item in HOUSE_8 + HOUSE_8_BIO}
        bio = by_id["h8_bio_communication_learning_demanded_in_finance"]
        neighbors = (
            by_id["h8_financial_resourcefulness"],
            by_id["h8_maneuver_around_loans"],
            by_id["h8_maneuver_around_discounts"],
        )
        for neighbor in neighbors:
            with self.subTest(neighbor=neighbor.id):
                self.assertNotEqual(bio.id, neighbor.id)
                self.assertNotEqual(bio.text, neighbor.text)
        self.assertEqual(bio.source_reference, REF_H8_BIO)
        self.assertIn("demanded", bio.text.lower())
        self.assertIn("communication", bio.text.lower())

    def test_magic_demand_is_not_occult_interest(self):
        by_id = {item.id: item for item in HOUSE_8 + HOUSE_8_BIO}
        bio = by_id["h8_bio_communication_learning_demanded_in_magic"]
        interest = by_id["h8_interest_associations_secrets_detective_occult"]
        self.assertNotEqual(bio.id, interest.id)
        self.assertNotEqual(bio.text, interest.text)
        self.assertIn("magic", bio.text.lower())
        self.assertIn("demanded", bio.text.lower())
        self.assertNotIn("secrets_detective_occult_interest_associations", bio.tags)

    def test_commercial_resourcefulness_is_partial_not_exact(self):
        by_id = {item.id: item for item in HOUSE_8 + HOUSE_8_BIO}
        bio = by_id["h8_bio_commercial_resourcefulness"]
        financial = by_id["h8_financial_resourcefulness"]
        self.assertNotEqual(bio.id, financial.id)
        self.assertNotEqual(bio.text, financial.text)
        self.assertEqual(bio.text, "Commercial resourcefulness.")
        self.assertNotIn("financial_resourcefulness", bio.tags)
        self.assertIn("financial_resourcefulness", financial.tags)

    def test_power_of_word_is_not_verbal_influence(self):
        by_id = {item.id: item for item in HOUSE_8 + HOUSE_8_BIO}
        bio = by_id["h8_bio_power_of_word"]
        influence = by_id["h8_ability_to_influence_people_through_words"]
        self.assertNotEqual(bio.id, influence.id)
        self.assertNotEqual(bio.text, influence.text)
        self.assertNotIn("verbal_influence", bio.tags)
        self.assertNotIn("persuasion", bio.tags)

    def test_solitary_learning_method_is_one_relational_atom(self):
        by_id = {item.id: item for item in HOUSE_8 + HOUSE_8_BIO}
        bio = by_id["h8_bio_solitary_critical_learning_method"]
        neighbors = (
            by_id["h8_research_talent"],
            by_id["h8_deep_thinking"],
            by_id["h8_decipher_information_from_hidden_sources"],
            by_id["h8_intense_intellectual_concentration"],
        )
        for neighbor in neighbors:
            with self.subTest(neighbor=neighbor.id):
                self.assertNotEqual(bio.id, neighbor.id)
                self.assertNotEqual(bio.text, neighbor.text)
        lowered = bio.text.lower()
        self.assertIn("alone", lowered)
        self.assertIn("critical", lowered)
        self.assertIn("analyzing sources", lowered)
        self.assertIn("errors", lowered)
        self.assertIn("comparing", lowered)
        self.assertIn("evaluating", lowered)

    def test_analytical_ability_is_not_l7_thinking_cluster(self):
        by_id = {item.id: item for item in HOUSE_8 + HOUSE_8_BIO}
        bio = by_id["h8_bio_analytical_ability"]
        neighbors = (
            by_id["h8_perceptiveness"],
            by_id["h8_research_talent"],
            by_id["h8_deep_thinking"],
        )
        for neighbor in neighbors:
            with self.subTest(neighbor=neighbor.id):
                self.assertNotEqual(bio.id, neighbor.id)
                self.assertNotEqual(bio.text, neighbor.text)
        self.assertEqual(bio.tags, ("analytical_thinking",))


class House8BioUniqueTests(unittest.TestCase):
    def test_detective_ability_is_not_detective_story_interest(self):
        by_id = {item.id: item for item in HOUSE_8 + HOUSE_8_BIO}
        ability = by_id["h8_bio_detective_ability"]
        interest = by_id["h8_interest_associations_secrets_detective_occult"]
        self.assertNotEqual(ability.text, interest.text)
        self.assertNotIn("detective_thinking", ability.tags)
        self.assertNotIn("secrets_detective_occult_interest_associations", ability.tags)

    def test_investments_other_people_money_is_distinct(self):
        fact = next(
            item for item in HOUSE_8_BIO if item.id == "h8_bio_investments_other_people_money"
        )
        self.assertIn("investments", fact.text.lower())
        self.assertIn("other people's money", fact.text.lower())
        self.assertEqual(fact.tags, ())
        self.assertEqual(fact.polarity, "neutral")


class House8InterestPolarityTests(unittest.TestCase):
    def test_energies_and_sex_interest_both_use_strength(self):
        by_id = {item.id: item for item in HOUSE_8_BIO}
        energies = by_id["h8_bio_interest_in_energies"]
        sex = by_id["h8_bio_interest_in_sex"]
        self.assertEqual(energies.category, "source_specific")
        self.assertEqual(sex.category, "source_specific")
        self.assertEqual(energies.polarity, "strength")
        self.assertEqual(sex.polarity, "strength")
        self.assertEqual(energies.tags, ())
        self.assertEqual(sex.tags, ())
        self.assertNotIn("source_sexual_motivation_wording", sex.tags)


class House8AfflictedConditionalTests(unittest.TestCase):
    def test_all_seven_afflicted_bio_atoms_unresolved_without_hard_aspected(self):
        by_id = {item.id: item for item in HOUSE_8_BIO}
        for fact_id in UNRESOLVED_BIO_IDS:
            fact = by_id[fact_id]
            with self.subTest(fact_id=fact_id):
                self.assertTrue(fact.unresolved)
                self.assertIsNone(fact.activation_condition)
                self.assertNotEqual(fact.activation_condition, "hard_aspected")
                self.assertEqual(fact.polarity, "conditional")
                self.assertEqual(fact.category, "source_specific")
                self.assertEqual(fact.tags, ())
                self.assertIn("not hard_aspected", fact.text)

    def test_hard_aspects_do_not_resolve_afflicted_bio_facts(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Scorpio",
                mercury_element="water",
                mercury_motion="direct",
                mercury_house=8,
                aspects=[
                    MercuryAspect(planet="Mars", type="square", orb_deg=1.0),
                    MercuryAspect(planet="Saturn", type="opposition", orb_deg=1.0),
                ],
            )
        )
        unresolved_ids = _ids(profile.conditional_unresolved)
        for fact_id in UNRESOLVED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertIn(fact_id, unresolved_ids)
                fact = next(item for item in profile.house_facts if item.id == fact_id)
                self.assertTrue(fact.unresolved)
                self.assertIsNone(fact.activation_condition)

    def test_afflicted_gossip_is_not_intrigue_or_malicious_speech(self):
        by_id = {item.id: item for item in HOUSE_8 + HOUSE_8_BIO}
        bio = by_id["h8_bio_afflicted_gossip"]
        intrigue = by_id["h8_intrigue_tendency"]
        speech = by_id["h8_malicious_speech"]
        self.assertNotEqual(bio.id, intrigue.id)
        self.assertNotEqual(bio.id, speech.id)
        self.assertTrue(bio.unresolved)
        self.assertFalse(intrigue.unresolved)
        self.assertFalse(speech.unresolved)


class House8MedicalSeparationTests(unittest.TestCase):
    def test_l7_medical_facts_remain_unconditional(self):
        by_id = {item.id: item for item in HOUSE_8}
        for fact_id in L7_MEDICAL_IDS:
            fact = by_id[fact_id]
            with self.subTest(fact_id=fact_id):
                self.assertFalse(fact.unresolved)
                self.assertIsNone(fact.activation_condition)
                self.assertEqual(fact.source_reference, REF_H8_L7)

    def test_bio_afflicted_medical_is_not_l7_medical(self):
        by_id = {item.id: item for item in HOUSE_8 + HOUSE_8_BIO}
        l7_vascular = by_id["h8_source_vascular_problem_risk"]
        bio_vascular = by_id["h8_bio_afflicted_vascular_disease_association"]
        self.assertNotEqual(l7_vascular.id, bio_vascular.id)
        self.assertNotEqual(l7_vascular.text, bio_vascular.text)
        self.assertFalse(l7_vascular.unresolved)
        self.assertTrue(bio_vascular.unresolved)
        self.assertNotIn("source_vascular_problem_risk", bio_vascular.tags)

    def test_l7_hand_finger_injury_is_not_bio_limb_disease(self):
        by_id = {item.id: item for item in HOUSE_8 + HOUSE_8_BIO}
        hand = by_id["h8_source_hand_injury_risk"]
        finger = by_id["h8_source_finger_injury_risk"]
        limb = by_id["h8_bio_afflicted_limb_disease_association"]
        self.assertNotEqual(hand.text, limb.text)
        self.assertNotEqual(finger.text, limb.text)
        self.assertIn("hand", hand.text.lower())
        self.assertIn("finger", finger.text.lower())
        self.assertIn("limbs", limb.text.lower())
        self.assertFalse(hand.unresolved)
        self.assertFalse(finger.unresolved)
        self.assertTrue(limb.unresolved)

    def test_four_afflicted_medical_atoms_remain_distinct(self):
        by_id = {item.id: item for item in HOUSE_8_BIO}
        texts = set()
        for fact_id in AFFLICTED_MEDICAL_BIO_IDS:
            fact = by_id[fact_id]
            with self.subTest(fact_id=fact_id):
                self.assertTrue(fact.unresolved)
                self.assertEqual(fact.polarity, "conditional")
                self.assertEqual(fact.tags, ())
                texts.add(fact.text)
        self.assertEqual(len(texts), 4)


class House8BioTagGuardTests(unittest.TestCase):
    def test_only_analytical_ability_has_analytical_thinking_tag(self):
        by_id = {item.id: item for item in HOUSE_8_BIO}
        self.assertEqual(by_id["h8_bio_analytical_ability"].tags, ("analytical_thinking",))
        self.assertEqual(len(UNTAGGED_BIO_IDS), 19)
        for fact_id in UNTAGGED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].tags, ())

    def test_commercial_resourcefulness_has_no_financial_or_commercial_tags(self):
        fact = next(
            item for item in HOUSE_8_BIO if item.id == "h8_bio_commercial_resourcefulness"
        )
        self.assertNotIn("financial_resourcefulness", fact.tags)
        self.assertNotIn("commercial_ability", fact.tags)

    def test_untagged_bio_facts_avoid_approximate_tags(self):
        by_id = {item.id: item for item in HOUSE_8_BIO}
        for fact_id in UNTAGGED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                for tag in FORBIDDEN_APPROXIMATE_TAGS:
                    self.assertNotIn(tag, by_id[fact_id].tags)

    def test_no_new_repeated_signal_spec(self):
        tags = {spec["tag"] for spec in REPEATED_SIGNAL_SPECS}
        self.assertIn("analytical_thinking", tags)
        self.assertNotIn("detective_thinking", tags)
        analytical_specs = [
            spec for spec in REPEATED_SIGNAL_SPECS if spec["tag"] == "analytical_thinking"
        ]
        self.assertEqual(len(analytical_specs), 1)


class House8Lesson7FrozenTests(unittest.TestCase):
    def test_existing_18_lesson7_facts_unchanged(self):
        self.assertEqual(len(HOUSE_8), 18)
        self.assertEqual(len(FROZEN_L7_HOUSE_8), 18)
        actual = tuple(
            (
                item.id,
                item.category,
                item.text,
                item.polarity,
                item.tags,
                item.source_reference,
                item.unresolved,
            )
            for item in HOUSE_8
        )
        self.assertEqual(actual, FROZEN_L7_HOUSE_8)
        self.assertTrue(all(item.activation_condition is None for item in HOUSE_8))
        self.assertTrue(all(item.unresolved is False for item in HOUSE_8))


class House8SameHouseSourceDedupTests(unittest.TestCase):
    def test_lesson7_and_bio_share_one_provenance_key(self):
        house_8 = _house_8_facts()
        keys = {_provenance_key(item) for item in house_8}
        self.assertEqual(keys, {"house:8"})
        for item in HOUSE_8 + HOUSE_8_BIO:
            with self.subTest(fact_id=item.id):
                self.assertEqual(_provenance_key(item), "house:8")

    def test_house_8_dual_source_cannot_create_repeat_alone(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign=None,
                mercury_element=None,
                mercury_motion="direct",
                mercury_house=8,
                aspects=[],
            )
        )
        self.assertEqual(len(profile.house_facts), 38)
        self.assertTrue(all(item.factor_key == "8" for item in profile.house_facts))
        repeats = detect_repeated_signals(profile.house_facts)
        self.assertEqual(repeats, [])


class House8HumanCopyInventoryConsequenceTests(unittest.TestCase):
    def test_new_bio_facts_are_unreviewed_and_not_in_registries(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        for fact_id in EXPECTED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertNotIn(fact_id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_UNREVIEWED)

    def test_unresolved_bio_facts_remain_human_copy_unreviewed(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        for fact_id in UNRESOLVED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertTrue(by_id[fact_id].unresolved)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_UNREVIEWED)

    def test_house_8_family_counts_after_source_parity(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "house:8")
        self.assertEqual(family.total_facts, 38)
        self.assertEqual(family.approved_override, 0)
        self.assertEqual(family.approved_raw, 0)
        self.assertEqual(family.needs_review, 0)
        self.assertEqual(family.unreviewed, 38)
        self.assertEqual(family.reviewed_count, 0)
        self.assertEqual(family.presentation_ready_count, 0)


class House8SemanticLedgerTests(unittest.TestCase):
    def test_semantic_accounting_from_implemented_facts(self):
        l7_count = len(HOUSE_8)
        bio_count = len(HOUSE_8_BIO)
        exact_overlap = 1
        partial_overlap = 6
        conditional_unresolved = 7
        unique_bio = (
            bio_count - exact_overlap - partial_overlap - conditional_unresolved
        )
        unique_meanings = (
            l7_count + unique_bio + partial_overlap + conditional_unresolved
        )
        self.assertEqual(l7_count, 18)
        self.assertEqual(bio_count, 20)
        self.assertEqual(exact_overlap, 1)
        self.assertEqual(partial_overlap, 6)
        self.assertEqual(unique_bio, 6)
        self.assertEqual(conditional_unresolved, 7)
        self.assertEqual(unique_meanings, 37)
        self.assertEqual(l7_count + bio_count, 38)
        self.assertEqual(
            exact_overlap + partial_overlap + unique_bio + conditional_unresolved,
            20,
        )


if __name__ == "__main__":
    unittest.main()
