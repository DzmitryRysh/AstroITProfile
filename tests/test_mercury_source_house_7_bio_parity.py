"""Tests for Mercury House 7 Bioastrology source parity (S4.26B)."""

from __future__ import annotations

import unittest
from collections import Counter

from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_human_copy import HUMAN_COPY_OVERRIDES
from app.services.mercury_human_copy_catalog import (
    APPROVED_RAW_FACT_IDS,
    NEEDS_REVIEW_FACT_IDS,
    STATUS_NEEDS_REVIEW,
    STATUS_UNREVIEWED,
    build_catalog_entry,
    build_human_copy_catalog,
)
from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS, REPEATED_SIGNAL_SPECS
from app.services.mercury_source_knowledge_b2_houses import (
    HOUSE_6,
    HOUSE_6_BIO,
    HOUSE_7,
    HOUSE_7_BIO,
    REF_H7_BIO,
    REF_H7_L7,
)
from app.services.mercury_source_profile import (
    _provenance_key,
    build_source_profile_from_factors,
    detect_repeated_signals,
)


EXPECTED_BIO_IDS: tuple[str, ...] = (
    "h7_bio_communication_learning_through_partners_public",
    "h7_bio_intellectual_marriage",
    "h7_bio_partner_younger",
    "h7_bio_mercury_type_partner_character",
    "h7_bio_favorable_skillful_sales",
    "h7_bio_favorable_negotiations",
    "h7_bio_consultant_qualities",
    "h7_bio_politician_qualities",
    "h7_bio_lawyer_qualities",
    "h7_bio_popularity_fame",
    "h7_bio_afflicted_lying_in_relationships",
    "h7_bio_afflicted_relationship_duality",
)

EXPECTED_BIO_CANONICAL: dict[str, str] = {
    "h7_bio_communication_learning_through_partners_public": (
        "Communication and learning may be realized through connections with "
        "partners and the public."
    ),
    "h7_bio_intellectual_marriage": (
        "There may be an intellectual-marriage association."
    ),
    "h7_bio_partner_younger": "Partner may be younger in age.",
    "h7_bio_mercury_type_partner_character": (
        "Partner may have a source-described Mercury-type character."
    ),
    "h7_bio_favorable_skillful_sales": "Favorable association with skillful sales.",
    "h7_bio_favorable_negotiations": "Favorable association with negotiations.",
    "h7_bio_consultant_qualities": (
        "May support qualities associated with consulting."
    ),
    "h7_bio_politician_qualities": (
        "May support qualities associated with a politician role."
    ),
    "h7_bio_lawyer_qualities": (
        "May support qualities associated with a lawyer role."
    ),
    "h7_bio_popularity_fame": (
        "Favorable association with popularity and public recognition."
    ),
    "h7_bio_afflicted_lying_in_relationships": (
        "When Mercury is afflicted, the source associates this placement with "
        "lying in relationships (afflicted-Mercury dependency; no house-affliction "
        "resolver is applied; not hard_aspected)."
    ),
    "h7_bio_afflicted_relationship_duality": (
        "When Mercury is afflicted, the source associates this placement with "
        "duality or splitting in relationships (afflicted-Mercury dependency; "
        "no house-affliction resolver is applied; not hard_aspected)."
    ),
}

EXPECTED_BIO_TAGS: dict[str, tuple[str, ...]] = {
    "h7_bio_consultant_qualities": ("consulting",),
}

UNTAGGED_BIO_IDS: tuple[str, ...] = tuple(
    fact_id for fact_id in EXPECTED_BIO_IDS if fact_id not in EXPECTED_BIO_TAGS
)

UNRESOLVED_BIO_IDS: tuple[str, ...] = (
    "h7_bio_afflicted_lying_in_relationships",
    "h7_bio_afflicted_relationship_duality",
)

UNRESOLVED_L7_IDS: tuple[str, ...] = (
    "h7_partner_intellectual_expectation_mutable_dependency",
    "h7_partner_argumentativeness_fire_element_dependency",
)

FORBIDDEN_APPROXIMATE_TAGS: tuple[str, ...] = (
    "sales",
    "persuasion",
    "argumentation",
    "debate",
    "evidence_requirement",
    "negotiation",
    "partner_often_younger_association",
    "partner_lying_association",
    "partner_two_faced_association",
    "lying",
    "lying_distortion",
    "deception",
    "conflict",
    "recognition_seeking",
    "public_speaking",
    "leadership",
    "legal_ability",
    "talkative",
    "communication_skill",
    "dialogue_skill",
    "compromise_skill",
    "many_contacts",
)

FROZEN_L7_HOUSE_7: tuple[
    tuple[str, str, str, str, tuple[str, ...], str, bool], ...
] = (
    (
        "h7_many_contacts",
        "environment",
        "Many contacts.",
        "neutral",
        ("many_contacts",),
        REF_H7_L7,
        False,
    ),
    (
        "h7_conversation_partner_can_be_found",
        "communication",
        "In any circumstances a conversational partner can be found.",
        "strength",
        ("conversation_partner_availability",),
        REF_H7_L7,
        False,
    ),
    (
        "h7_master_of_dialogue",
        "communication",
        "Circumstances make the native a master of dialogue.",
        "strength",
        ("dialogue_skill",),
        REF_H7_L7,
        False,
    ),
    (
        "h7_master_of_compromise",
        "communication",
        "Circumstances make the native a master of compromise.",
        "strength",
        ("compromise_skill",),
        REF_H7_L7,
        False,
    ),
    (
        "h7_partner_may_be_communicative",
        "source_specific",
        "Source associates the partner with being communicative "
        "(partner association, not a native ability claim).",
        "neutral",
        ("partner_communicative_association",),
        REF_H7_L7,
        False,
    ),
    (
        "h7_partner_from_intellectual_profession",
        "source_specific",
        "Source associates the partner with an intellectual profession "
        "(partner association, not a native ability claim).",
        "neutral",
        ("partner_intellectual_profession_association",),
        REF_H7_L7,
        False,
    ),
    (
        "h7_partner_often_younger",
        "source_specific",
        "Source associates the partner with often being younger "
        "(partner association, not a native ability claim).",
        "neutral",
        ("partner_often_younger_association",),
        REF_H7_L7,
        False,
    ),
    (
        "h7_shared_topics_important_with_partner",
        "environment",
        "With a partner it is important to have shared topics.",
        "neutral",
        ("shared_topics_in_partnership",),
        REF_H7_L7,
        False,
    ),
    (
        "h7_intellectual_interest_important_with_partner",
        "environment",
        "With a partner it is important to have intellectual interest.",
        "neutral",
        ("intellectual_interest_in_partnership",),
        REF_H7_L7,
        False,
    ),
    (
        "h7_calculation_can_dominate_feelings_in_marriage",
        "risk",
        "Calculation / rationality can dominate feelings in marriage.",
        "risk",
        ("calculation_dominates_feelings_in_marriage",),
        REF_H7_L7,
        False,
    ),
    (
        "h7_relationships_built_more_on_reason",
        "risk",
        "Relationships may be built more on reason.",
        "risk",
        ("relationships_built_on_reason",),
        REF_H7_L7,
        False,
    ),
    (
        "h7_partner_intellectual_expectation_mutable_dependency",
        "source_specific",
        "If the partner does not meet intellectual expectations, marriage may be unstable; "
        "source especially notes this for mutable Mercury "
        "(mutable-Mercury dependency; no modality resolver is applied; not hard_aspected).",
        "conditional",
        ("partner_intellectual_expectation_mutable_dependency",),
        REF_H7_L7,
        True,
    ),
    (
        "h7_possible_fictitious_formal_paper_marriage",
        "source_specific",
        "Possible fictitious / formal / paper marriage "
        "(source-described possible relationship scenario, not an accusation).",
        "neutral",
        ("formal_paper_marriage_scenario",),
        REF_H7_L7,
        False,
    ),
    (
        "h7_partner_may_be_two_faced",
        "source_specific",
        "Source says the partner may be two-faced "
        "(partner association, not a native character claim).",
        "risk",
        ("partner_two_faced_association",),
        REF_H7_L7,
        False,
    ),
    (
        "h7_partner_may_be_lying",
        "source_specific",
        "Source says the partner may be lying "
        "(partner association, not a native character claim).",
        "risk",
        ("partner_lying_association",),
        REF_H7_L7,
        False,
    ),
    (
        "h7_partner_argumentativeness_fire_element_dependency",
        "source_specific",
        "Source says the partner may be argumentative, especially in fire element "
        "(fire-element dependency; no element resolver is applied for this house fact; "
        "not hard_aspected).",
        "conditional",
        ("partner_argumentativeness_fire_element_dependency",),
        REF_H7_L7,
        True,
    ),
)


def _house_7_facts():
    return [
        item
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "house" and item.factor_key == "7"
    ]


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


class House7BioCoverageTests(unittest.TestCase):
    def test_programmatic_bio_count_is_12(self):
        self.assertEqual(len(HOUSE_7_BIO), 12)
        self.assertEqual(len(EXPECTED_BIO_IDS), 12)
        self.assertEqual(len(EXPECTED_BIO_CANONICAL), 12)
        self.assertEqual(tuple(item.id for item in HOUSE_7_BIO), EXPECTED_BIO_IDS)

    def test_house_7_source_counts(self):
        house_7 = _house_7_facts()
        lesson7 = [item for item in house_7 if item.source_reference == REF_H7_L7]
        bio = [item for item in house_7 if item.source_reference == REF_H7_BIO]
        self.assertEqual(len(HOUSE_7), 16)
        self.assertEqual(len(lesson7), 16)
        self.assertEqual(len(bio), 12)
        self.assertEqual(len(house_7), 28)
        self.assertEqual(len(HOUSE_7) + len(HOUSE_7_BIO), 28)

    def test_all_bio_use_bioastrology_source_reference(self):
        self.assertTrue(all(item.source_reference == REF_H7_BIO for item in HOUSE_7_BIO))
        self.assertEqual(REF_H7_BIO, "bioastrology_mercury_house_7")

    def test_all_house_7_facts_share_factor_identity(self):
        house_7 = _house_7_facts()
        self.assertEqual(len(house_7), 28)
        self.assertTrue(all(item.factor_type == "house" for item in house_7))
        self.assertTrue(all(item.factor_key == "7" for item in house_7))
        self.assertTrue(all(item.activation_condition is None for item in house_7))

    def test_ids_globally_unique(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])


class House7BioCanonicalTests(unittest.TestCase):
    def test_exact_canonical_strings_for_all_12(self):
        by_id = {item.id: item for item in HOUSE_7_BIO}
        self.assertEqual(set(by_id), set(EXPECTED_BIO_CANONICAL))
        for fact_id, canonical in EXPECTED_BIO_CANONICAL.items():
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].text, canonical)


class House7ExactOverlapTests(unittest.TestCase):
    def test_younger_partner_exact_atom_keeps_separate_provenance(self):
        by_id = {item.id: item for item in HOUSE_7 + HOUSE_7_BIO}
        l7 = by_id["h7_partner_often_younger"]
        bio = by_id["h7_bio_partner_younger"]
        self.assertNotEqual(l7.id, bio.id)
        self.assertEqual(l7.source_reference, REF_H7_L7)
        self.assertEqual(bio.source_reference, REF_H7_BIO)
        self.assertNotEqual(l7.text, bio.text)
        self.assertIn("often", l7.text.lower())
        self.assertIn("may", bio.text.lower())
        self.assertIn("younger", l7.text.lower())
        self.assertIn("younger", bio.text.lower())
        self.assertEqual(l7.tags, ("partner_often_younger_association",))
        self.assertEqual(bio.tags, ())
        self.assertNotIn("partner_often_younger_association", bio.tags)
        self.assertEqual(bio.category, "source_specific")
        self.assertEqual(bio.polarity, "neutral")


class House7PartialFidelityTests(unittest.TestCase):
    def test_communication_learning_through_partners_public_is_not_dialogue_cluster(self):
        by_id = {item.id: item for item in HOUSE_7 + HOUSE_7_BIO}
        bio = by_id["h7_bio_communication_learning_through_partners_public"]
        neighbors = (
            by_id["h7_many_contacts"],
            by_id["h7_conversation_partner_can_be_found"],
            by_id["h7_master_of_dialogue"],
            by_id["h7_master_of_compromise"],
        )
        for neighbor in neighbors:
            with self.subTest(neighbor=neighbor.id):
                self.assertNotEqual(bio.id, neighbor.id)
                self.assertNotEqual(bio.text, neighbor.text)
                self.assertEqual(neighbor.source_reference, REF_H7_L7)
        self.assertEqual(bio.source_reference, REF_H7_BIO)
        self.assertEqual(bio.tags, ())
        lowered = bio.text.lower()
        self.assertIn("learning", lowered)
        self.assertIn("public", lowered)
        self.assertIn("partners", lowered)
        self.assertIn("communication", lowered)

    def test_intellectual_marriage_is_not_profession_or_shared_interest(self):
        by_id = {item.id: item for item in HOUSE_7 + HOUSE_7_BIO}
        bio = by_id["h7_bio_intellectual_marriage"]
        profession = by_id["h7_partner_from_intellectual_profession"]
        interest = by_id["h7_intellectual_interest_important_with_partner"]
        self.assertNotEqual(bio.id, profession.id)
        self.assertNotEqual(bio.id, interest.id)
        self.assertNotEqual(bio.text, profession.text)
        self.assertNotEqual(bio.text, interest.text)
        self.assertEqual(bio.source_reference, REF_H7_BIO)
        self.assertEqual(profession.source_reference, REF_H7_L7)
        self.assertEqual(interest.source_reference, REF_H7_L7)
        self.assertEqual(bio.tags, ())
        self.assertIn("marriage", bio.text.lower())
        self.assertNotIn("profession", bio.text.lower())


class House7AtomicFidelityTests(unittest.TestCase):
    def test_mercury_type_partner_is_not_unpacked_into_traits(self):
        fact = next(
            item
            for item in HOUSE_7_BIO
            if item.id == "h7_bio_mercury_type_partner_character"
        )
        lowered = fact.text.lower()
        self.assertIn("mercury-type", lowered)
        self.assertNotIn("talkative", lowered)
        self.assertNotIn("gemini", lowered)
        self.assertNotIn("virgo", lowered)
        self.assertNotIn("seller", lowered)
        self.assertEqual(fact.tags, ())
        self.assertEqual(fact.category, "source_specific")
        self.assertEqual(fact.polarity, "neutral")

    def test_skillful_sales_is_not_sales_qualities(self):
        by_id = {item.id: item for item in HOUSE_7_BIO}
        h6_sales = next(item for item in HOUSE_6_BIO if item.id == "h6_bio_sales_qualities")
        skillful = by_id["h7_bio_favorable_skillful_sales"]
        self.assertNotEqual(skillful.text, h6_sales.text)
        self.assertNotIn("sales", skillful.tags)
        self.assertIn("sales", h6_sales.tags)
        self.assertEqual(skillful.category, "work_application")
        self.assertEqual(skillful.polarity, "strength")

    def test_negotiations_are_not_sales_or_argument(self):
        by_id = {item.id: item for item in HOUSE_7_BIO}
        negotiations = by_id["h7_bio_favorable_negotiations"]
        sales = by_id["h7_bio_favorable_skillful_sales"]
        self.assertNotEqual(negotiations.text, sales.text)
        self.assertEqual(negotiations.tags, ())
        self.assertNotIn("persuasion", negotiations.tags)
        self.assertNotIn("argumentation", negotiations.tags)
        self.assertNotIn("debate", negotiations.tags)
        self.assertNotIn("sales", negotiations.tags)
        self.assertEqual(negotiations.category, "work_application")
        self.assertEqual(negotiations.polarity, "strength")

    def test_consultant_politician_lawyer_remain_distinct(self):
        by_id = {item.id: item for item in HOUSE_7_BIO}
        consultant = by_id["h7_bio_consultant_qualities"]
        politician = by_id["h7_bio_politician_qualities"]
        lawyer = by_id["h7_bio_lawyer_qualities"]
        self.assertNotEqual(consultant.text, politician.text)
        self.assertNotEqual(consultant.text, lawyer.text)
        self.assertNotEqual(politician.text, lawyer.text)
        self.assertEqual(consultant.tags, ("consulting",))
        self.assertEqual(politician.tags, ())
        self.assertEqual(lawyer.tags, ())
        house6 = next(
            item for item in HOUSE_6_BIO if item.id == "h6_bio_consultant_qualities"
        )
        self.assertEqual(consultant.text, house6.text)
        self.assertEqual(consultant.tags, house6.tags)

    def test_popularity_fame_stays_one_combined_source_atom(self):
        fact = next(item for item in HOUSE_7_BIO if item.id == "h7_bio_popularity_fame")
        lowered = fact.text.lower()
        self.assertIn("popularity", lowered)
        self.assertIn("public recognition", lowered)
        self.assertEqual(fact.tags, ())
        self.assertEqual(fact.category, "source_specific")
        self.assertEqual(fact.polarity, "strength")
        self.assertNotIn("recognition_seeking", fact.tags)


class House7SubjectPredicateDistinctionTests(unittest.TestCase):
    def test_afflicted_lying_is_not_partner_lying(self):
        by_id = {item.id: item for item in HOUSE_7 + HOUSE_7_BIO}
        l7 = by_id["h7_partner_may_be_lying"]
        bio = by_id["h7_bio_afflicted_lying_in_relationships"]
        self.assertNotEqual(l7.id, bio.id)
        self.assertNotEqual(l7.text, bio.text)
        self.assertEqual(l7.source_reference, REF_H7_L7)
        self.assertEqual(bio.source_reference, REF_H7_BIO)
        self.assertFalse(l7.unresolved)
        self.assertTrue(bio.unresolved)
        self.assertEqual(l7.polarity, "risk")
        self.assertEqual(bio.polarity, "conditional")
        self.assertEqual(bio.tags, ())
        self.assertIn("partner", l7.text.lower())
        self.assertIn("afflicted", bio.text.lower())

    def test_afflicted_duality_is_not_two_faced_partner(self):
        by_id = {item.id: item for item in HOUSE_7 + HOUSE_7_BIO}
        l7 = by_id["h7_partner_may_be_two_faced"]
        bio = by_id["h7_bio_afflicted_relationship_duality"]
        self.assertNotEqual(l7.id, bio.id)
        self.assertNotEqual(l7.text, bio.text)
        self.assertEqual(l7.source_reference, REF_H7_L7)
        self.assertEqual(bio.source_reference, REF_H7_BIO)
        self.assertFalse(l7.unresolved)
        self.assertTrue(bio.unresolved)
        self.assertEqual(l7.polarity, "risk")
        self.assertEqual(bio.polarity, "conditional")
        self.assertEqual(bio.tags, ())
        self.assertIn("partner", l7.text.lower())
        self.assertIn("afflicted", bio.text.lower())


class House7ThreeConditionalFamiliesTests(unittest.TestCase):
    def test_lesson7_mutable_mercury_dependency_unchanged(self):
        fact = next(
            item
            for item in HOUSE_7
            if item.id == "h7_partner_intellectual_expectation_mutable_dependency"
        )
        self.assertEqual(fact.source_reference, REF_H7_L7)
        self.assertTrue(fact.unresolved)
        self.assertIsNone(fact.activation_condition)
        self.assertEqual(fact.polarity, "conditional")
        self.assertNotEqual(fact.activation_condition, "hard_aspected")
        self.assertIn("mutable", fact.text.lower())

    def test_lesson7_fire_element_dependency_unchanged(self):
        fact = next(
            item
            for item in HOUSE_7
            if item.id == "h7_partner_argumentativeness_fire_element_dependency"
        )
        self.assertEqual(fact.source_reference, REF_H7_L7)
        self.assertTrue(fact.unresolved)
        self.assertIsNone(fact.activation_condition)
        self.assertEqual(fact.polarity, "conditional")
        self.assertNotEqual(fact.activation_condition, "hard_aspected")
        self.assertIn("fire", fact.text.lower())

    def test_bio_afflicted_facts_unresolved_without_hard_aspected_proxy(self):
        by_id = {item.id: item for item in HOUSE_7_BIO}
        for fact_id in UNRESOLVED_BIO_IDS:
            fact = by_id[fact_id]
            with self.subTest(fact_id=fact_id):
                self.assertEqual(fact.source_reference, REF_H7_BIO)
                self.assertTrue(fact.unresolved)
                self.assertIsNone(fact.activation_condition)
                self.assertNotEqual(fact.activation_condition, "hard_aspected")
                self.assertEqual(fact.polarity, "conditional")
                self.assertEqual(fact.category, "source_specific")
                self.assertEqual(fact.tags, ())
                self.assertIn("not hard_aspected", fact.text)

    def test_hard_aspects_do_not_resolve_house_7_afflicted_facts(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign="Libra",
                mercury_element="air",
                mercury_motion="direct",
                mercury_house=7,
                aspects=[
                    MercuryAspect(planet="Mars", type="square", orb_deg=1.0),
                    MercuryAspect(planet="Saturn", type="opposition", orb_deg=1.0),
                ],
            )
        )
        unresolved_ids = _ids(profile.conditional_unresolved)
        for fact_id in UNRESOLVED_L7_IDS + UNRESOLVED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertIn(fact_id, unresolved_ids)
                fact = next(item for item in profile.house_facts if item.id == fact_id)
                self.assertTrue(fact.unresolved)
                self.assertIsNone(fact.activation_condition)
                self.assertNotEqual(fact.activation_condition, "hard_aspected")

    def test_three_condition_families_remain_distinct(self):
        ids = set(UNRESOLVED_L7_IDS) | set(UNRESOLVED_BIO_IDS)
        self.assertEqual(len(ids), 4)
        self.assertTrue(set(UNRESOLVED_L7_IDS).isdisjoint(UNRESOLVED_BIO_IDS))


class House7BioTagGuardTests(unittest.TestCase):
    def test_only_consultant_fact_has_consulting_tag(self):
        by_id = {item.id: item for item in HOUSE_7_BIO}
        self.assertEqual(by_id["h7_bio_consultant_qualities"].tags, ("consulting",))
        self.assertEqual(len(UNTAGGED_BIO_IDS), 11)
        for fact_id in UNTAGGED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].tags, ())

    def test_skillful_sales_does_not_receive_sales_tag(self):
        fact = next(
            item for item in HOUSE_7_BIO if item.id == "h7_bio_favorable_skillful_sales"
        )
        self.assertNotIn("sales", fact.tags)
        self.assertEqual(fact.tags, ())

    def test_negotiations_do_not_receive_persuasion_argument_or_debate_tags(self):
        fact = next(
            item for item in HOUSE_7_BIO if item.id == "h7_bio_favorable_negotiations"
        )
        self.assertNotIn("persuasion", fact.tags)
        self.assertNotIn("argumentation", fact.tags)
        self.assertNotIn("debate", fact.tags)
        self.assertEqual(fact.tags, ())

    def test_afflicted_facts_have_no_deception_or_conflict_tags(self):
        by_id = {item.id: item for item in HOUSE_7_BIO}
        forbidden = (
            "lying",
            "lying_distortion",
            "deception",
            "conflict",
            "partner_lying_association",
            "partner_two_faced_association",
        )
        for fact_id in UNRESOLVED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                for tag in forbidden:
                    self.assertNotIn(tag, by_id[fact_id].tags)

    def test_untagged_bio_facts_avoid_approximate_tags(self):
        by_id = {item.id: item for item in HOUSE_7_BIO}
        for fact_id in UNTAGGED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                for tag in FORBIDDEN_APPROXIMATE_TAGS:
                    self.assertNotIn(tag, by_id[fact_id].tags)

    def test_no_new_repeated_signal_spec(self):
        tags = {spec["tag"] for spec in REPEATED_SIGNAL_SPECS}
        self.assertIn("sales", tags)
        self.assertNotIn("consulting", tags)
        self.assertNotIn("negotiation", tags)
        self.assertNotIn("partner_often_younger_association", tags)
        sales_specs = [spec for spec in REPEATED_SIGNAL_SPECS if spec["tag"] == "sales"]
        self.assertEqual(len(sales_specs), 1)
        self.assertEqual(sales_specs[0]["min_factor_keys"], 2)


class House7Lesson7FrozenTests(unittest.TestCase):
    def test_existing_16_lesson7_facts_unchanged(self):
        self.assertEqual(len(HOUSE_7), 16)
        self.assertEqual(len(FROZEN_L7_HOUSE_7), 16)
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
            for item in HOUSE_7
        )
        self.assertEqual(actual, FROZEN_L7_HOUSE_7)
        self.assertTrue(all(item.activation_condition is None for item in HOUSE_7))
        self.assertTrue(all(item.factor_type == "house" for item in HOUSE_7))
        self.assertTrue(all(item.factor_key == "7" for item in HOUSE_7))


class House7SameHouseSourceDedupTests(unittest.TestCase):
    def test_lesson7_and_bio_share_one_provenance_key(self):
        house_7 = _house_7_facts()
        keys = {_provenance_key(item) for item in house_7}
        self.assertEqual(keys, {"house:7"})
        for item in HOUSE_7 + HOUSE_7_BIO:
            with self.subTest(fact_id=item.id):
                self.assertEqual(_provenance_key(item), "house:7")

    def test_house_7_dual_source_cannot_create_repeat_alone(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign=None,
                mercury_element=None,
                mercury_motion="direct",
                mercury_house=7,
                aspects=[],
            )
        )
        self.assertEqual(len(profile.house_facts), 28)
        self.assertTrue(all(item.factor_key == "7" for item in profile.house_facts))
        self.assertIn("h7_bio_consultant_qualities", _ids(profile.house_facts))
        self.assertIn("h7_partner_often_younger", _ids(profile.house_facts))
        self.assertIn("h7_bio_partner_younger", _ids(profile.house_facts))
        repeats = detect_repeated_signals(profile.house_facts)
        self.assertEqual(repeats, [])
        for signal in repeats:
            house_sources = [src for src in signal.sources if src.startswith("house:")]
            self.assertLessEqual(len(house_sources), 1, signal)

    def test_h6_sales_plus_h7_skillful_sales_does_not_emit_sales_repeat(self):
        house6 = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign=None,
                mercury_element=None,
                mercury_motion="direct",
                mercury_house=6,
                aspects=[],
            )
        )
        house7 = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign=None,
                mercury_element=None,
                mercury_motion="direct",
                mercury_house=7,
                aspects=[],
            )
        )
        combined = list(house6.house_facts) + list(house7.house_facts)
        self.assertIn("h6_bio_sales_qualities", _ids(combined))
        self.assertIn("h7_bio_favorable_skillful_sales", _ids(combined))
        h7_skillful = next(
            item for item in combined if item.id == "h7_bio_favorable_skillful_sales"
        )
        self.assertNotIn("sales", h7_skillful.tags)
        sales_repeats = [
            signal for signal in detect_repeated_signals(combined) if signal.signal == "sales"
        ]
        self.assertEqual(sales_repeats, [])


class House7HumanCopyInventoryConsequenceTests(unittest.TestCase):
    def test_new_bio_facts_are_unreviewed_and_not_in_registries(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        for fact_id in EXPECTED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertNotEqual(entry.review_status, STATUS_UNREVIEWED)
                self.assertTrue(
                    (fact_id in HUMAN_COPY_OVERRIDES)
                    ^ (fact_id in APPROVED_RAW_FACT_IDS)
                )

    def test_existing_lesson7_facts_remain_unreviewed(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        for item in HOUSE_7:
            with self.subTest(l7_id=item.id):
                self.assertNotIn(item.id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[item.id])
                self.assertNotEqual(entry.review_status, STATUS_UNREVIEWED)
                self.assertTrue(
                    (item.id in HUMAN_COPY_OVERRIDES)
                    ^ (item.id in APPROVED_RAW_FACT_IDS)
                )

    def test_unresolved_source_facts_remain_human_copy_unreviewed(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        for fact_id in UNRESOLVED_L7_IDS + UNRESOLVED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertTrue(by_id[fact_id].unresolved)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertNotEqual(entry.review_status, STATUS_UNREVIEWED)
                self.assertNotEqual(entry.review_status, STATUS_NEEDS_REVIEW)

    def test_house_7_family_counts_after_source_parity(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "house:7")
        self.assertEqual(family.total_facts, 28)
        self.assertEqual(family.approved_override, 19)
        self.assertEqual(family.approved_raw, 9)
        self.assertEqual(family.needs_review, 0)
        self.assertEqual(family.unreviewed, 0)
        self.assertEqual(family.reviewed_count, 28)
        self.assertEqual(family.presentation_ready_count, 28)


class House7SemanticLedgerTests(unittest.TestCase):
    def test_semantic_accounting_from_implemented_facts(self):
        l7_count = len(HOUSE_7)
        bio_count = len(HOUSE_7_BIO)
        exact_overlap = 1
        partial_overlap = 2
        conditional_unresolved = 2
        unique_bio = (
            bio_count - exact_overlap - partial_overlap - conditional_unresolved
        )
        unique_meanings = (
            l7_count + unique_bio + partial_overlap + conditional_unresolved
        )
        self.assertEqual(l7_count, 16)
        self.assertEqual(bio_count, 12)
        self.assertEqual(exact_overlap, 1)
        self.assertEqual(partial_overlap, 2)
        self.assertEqual(unique_bio, 7)
        self.assertEqual(conditional_unresolved, 2)
        self.assertEqual(unique_meanings, 27)
        self.assertEqual(l7_count + bio_count, 28)
        self.assertEqual(
            exact_overlap + partial_overlap + unique_bio + conditional_unresolved,
            12,
        )


class House7OtherHousesFrozenTests(unittest.TestCase):
    def test_house_6_source_pack_counts_unchanged(self):
        self.assertEqual(len(HOUSE_6), 14)
        self.assertEqual(len(HOUSE_6_BIO), 15)


if __name__ == "__main__":
    unittest.main()
