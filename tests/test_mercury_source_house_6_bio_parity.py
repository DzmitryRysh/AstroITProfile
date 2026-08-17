"""Tests for Mercury House 6 Bioastrology source parity (S4.25B)."""

from __future__ import annotations

import unittest
from collections import Counter

from app.schemas.mercury_work_profile import MercurySourceFactors
from app.services.mercury_human_copy import HUMAN_COPY_OVERRIDES
from app.services.mercury_human_copy_catalog import (
    APPROVED_RAW_FACT_IDS,
    NEEDS_REVIEW_FACT_IDS,
    STATUS_UNREVIEWED,
    build_catalog_entry,
    build_human_copy_catalog,
)
from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS, REPEATED_SIGNAL_SPECS
from app.services.mercury_source_knowledge_b2_houses import (
    HOUSE_6,
    HOUSE_6_BIO,
    REF_H6_BIO,
    REF_H6_L7,
)
from app.services.mercury_source_profile import (
    _provenance_key,
    build_source_profile_from_factors,
    detect_repeated_signals,
)


EXPECTED_BIO_IDS: tuple[str, ...] = (
    "h6_bio_communication_demanded_at_work",
    "h6_bio_intellect_demanded_at_work",
    "h6_bio_increased_concerns_hassles",
    "h6_bio_others_assign_work",
    "h6_bio_two_parallel_jobs_or_projects",
    "h6_bio_ongoing_professional_education",
    "h6_bio_professional_retraining",
    "h6_bio_interest_in_medicine",
    "h6_bio_several_pets",
    "h6_bio_source_vascular_disease_association",
    "h6_bio_source_respiratory_disease_association",
    "h6_bio_source_limb_fracture_association",
    "h6_bio_intellectual_transport_profession",
    "h6_bio_consultant_qualities",
    "h6_bio_sales_qualities",
)

EXPECTED_BIO_CANONICAL: dict[str, str] = {
    "h6_bio_communication_demanded_at_work": (
        "Communication is especially demanded by work circumstances."
    ),
    "h6_bio_intellect_demanded_at_work": (
        "Intellectual function is especially demanded by work circumstances."
    ),
    "h6_bio_increased_concerns_hassles": (
        "There may be an increased amount of concerns and hassles."
    ),
    "h6_bio_others_assign_work": (
        "Other people may repeatedly try to assign work or tasks to the person."
    ),
    "h6_bio_two_parallel_jobs_or_projects": (
        "There may be two parallel jobs or different projects at work."
    ),
    "h6_bio_ongoing_professional_education": (
        "There may be ongoing professional education."
    ),
    "h6_bio_professional_retraining": "There may be professional retraining.",
    "h6_bio_interest_in_medicine": "May show strong interest in medicine.",
    "h6_bio_several_pets": "There may be several domestic animals or pets.",
    "h6_bio_source_vascular_disease_association": (
        "Source-described association with diseases involving blood vessels."
    ),
    "h6_bio_source_respiratory_disease_association": (
        "Source-described association with diseases involving respiratory organs."
    ),
    "h6_bio_source_limb_fracture_association": (
        "Source-described association with limb fractures."
    ),
    "h6_bio_intellectual_transport_profession": (
        "Favorable association with intellectual and transport-related professions."
    ),
    "h6_bio_consultant_qualities": (
        "May support qualities associated with consulting."
    ),
    "h6_bio_sales_qualities": "May support qualities associated with sales.",
}

EXPECTED_BIO_TAGS: dict[str, tuple[str, ...]] = {
    "h6_bio_intellectual_transport_profession": (
        "intellectual_work",
        "transport_profession",
    ),
    "h6_bio_consultant_qualities": ("consulting",),
    "h6_bio_sales_qualities": ("sales",),
}

UNTAGGED_BIO_IDS: tuple[str, ...] = tuple(
    fact_id for fact_id in EXPECTED_BIO_IDS if fact_id not in EXPECTED_BIO_TAGS
)

MEDICAL_BIO_IDS: tuple[str, ...] = (
    "h6_bio_source_vascular_disease_association",
    "h6_bio_source_respiratory_disease_association",
    "h6_bio_source_limb_fracture_association",
)

FORBIDDEN_APPROXIMATE_TAGS: tuple[str, ...] = (
    "intellectual_work",
    "lifelong_learning",
    "multiple_educations",
    "multiple_jobs",
    "multiple_side_jobs",
    "high_information_workload",
    "professional_contact_use",
    "work_travel",
    "occupation_associations",
    "small_problem_preoccupation",
    "inventing_small_problems",
    "multiple_tasks_at_once_risk",
    "diligent_duty_execution",
    "medical_interest",
    "pets",
    "health_risk",
    "vascular_risk",
    "respiratory_risk",
    "fracture_risk",
    "source_vascular_problem_risk",
    "source_hand_injury_risk",
    "source_finger_injury_risk",
    "source_injury_fracture_association",
    "persuasion",
    "trade_income",
    "learnability",
)

FROZEN_L7_HOUSE_6: tuple[
    tuple[str, str, str, str, tuple[str, ...], str, bool], ...
] = (
    (
        "h6_duties_performed_diligently",
        "work_application",
        "Duties are performed diligently.",
        "strength",
        ("diligent_duty_execution",),
        REF_H6_L7,
        False,
    ),
    (
        "h6_duties_performed_methodically",
        "work_application",
        "Duties are performed methodically.",
        "strength",
        ("methodical_duty_execution",),
        REF_H6_L7,
        False,
    ),
    (
        "h6_duties_performed_intelligently",
        "work_application",
        "Duties are performed intelligently.",
        "strength",
        ("intelligent_duty_execution",),
        REF_H6_L7,
        False,
    ),
    (
        "h6_duties_performed_rationally",
        "work_application",
        "Duties are performed rationally.",
        "strength",
        ("rational_duty_execution",),
        REF_H6_L7,
        False,
    ),
    (
        "h6_active_use_of_professional_contacts",
        "work_application",
        "Active use of connections / contacts in professional activity.",
        "strength",
        ("professional_contact_use",),
        REF_H6_L7,
        False,
    ),
    (
        "h6_work_involves_travel_or_moving",
        "mobility",
        "Work may involve a lot of travel / moving around.",
        "neutral",
        ("work_travel",),
        REF_H6_L7,
        False,
    ),
    (
        "h6_work_involves_processing_lots_of_information",
        "work_application",
        "Work may involve processing a lot of information.",
        "neutral",
        ("high_information_workload",),
        REF_H6_L7,
        False,
    ),
    (
        "h6_several_side_jobs",
        "work_application",
        "Several side jobs / multiple additional jobs.",
        "neutral",
        ("multiple_side_jobs",),
        REF_H6_L7,
        False,
    ),
    (
        "h6_occupation_associations",
        "source_specific",
        "Source-described occupation associations include consultant, dietitian, healer, "
        "doctor, communications worker, seller, journalist, commentator, and laboratory "
        "research; not career assignments.",
        "neutral",
        ("occupation_associations",),
        REF_H6_L7,
        False,
    ),
    (
        "h6_tendency_to_grab_several_tasks_at_once",
        "risk",
        "Tendency to grab several tasks at once (source-described risk of scattering "
        "across tasks, not positive multitasking).",
        "risk",
        ("multiple_tasks_at_once_risk",),
        REF_H6_L7,
        False,
    ),
    (
        "h6_preoccupation_with_small_matters",
        "risk",
        "Preoccupation with small matters.",
        "risk",
        ("small_problem_preoccupation",),
        REF_H6_L7,
        False,
    ),
    (
        "h6_may_invent_small_problems",
        "risk",
        "If small problems do not exist, the native may invent / create them.",
        "risk",
        ("inventing_small_problems",),
        REF_H6_L7,
        False,
    ),
    (
        "h6_dev_resolve_problem_decisively",
        "work_application",
        "Development focus: solve the problem quickly and permanently.",
        "neutral",
        ("resolve_problem_decisively",),
        REF_H6_L7,
        False,
    ),
    (
        "h6_dev_ignore_minor_problems",
        "work_application",
        "Development focus: ignore small problems.",
        "neutral",
        ("ignore_minor_problems",),
        REF_H6_L7,
        False,
    ),
)


def _house_6_facts():
    return [
        item
        for item in ALL_SOURCE_FACTS
        if item.factor_type == "house" and item.factor_key == "6"
    ]


def _ids(facts) -> set[str]:
    return {item.id for item in facts}


class House6BioCoverageTests(unittest.TestCase):
    def test_programmatic_bio_count_is_15(self):
        self.assertEqual(len(HOUSE_6_BIO), 15)
        self.assertEqual(len(EXPECTED_BIO_IDS), 15)
        self.assertEqual(len(EXPECTED_BIO_CANONICAL), 15)
        self.assertEqual(tuple(item.id for item in HOUSE_6_BIO), EXPECTED_BIO_IDS)

    def test_house_6_source_counts(self):
        house_6 = _house_6_facts()
        lesson7 = [item for item in house_6 if item.source_reference == REF_H6_L7]
        bio = [item for item in house_6 if item.source_reference == REF_H6_BIO]
        self.assertEqual(len(HOUSE_6), 14)
        self.assertEqual(len(lesson7), 14)
        self.assertEqual(len(bio), 15)
        self.assertEqual(len(house_6), 29)
        self.assertEqual(len(HOUSE_6) + len(HOUSE_6_BIO), 29)

    def test_all_bio_use_bioastrology_source_reference(self):
        self.assertTrue(all(item.source_reference == REF_H6_BIO for item in HOUSE_6_BIO))
        self.assertEqual(REF_H6_BIO, "bioastrology_mercury_house_6")

    def test_all_house_6_facts_share_factor_identity(self):
        house_6 = _house_6_facts()
        self.assertEqual(len(house_6), 29)
        self.assertTrue(all(item.factor_type == "house" for item in house_6))
        self.assertTrue(all(item.factor_key == "6" for item in house_6))
        self.assertTrue(all(item.activation_condition is None for item in house_6))
        self.assertTrue(all(item.unresolved is False for item in HOUSE_6_BIO))
        self.assertTrue(all(item.unresolved is False for item in HOUSE_6))

    def test_ids_globally_unique(self):
        ids = [item.id for item in ALL_SOURCE_FACTS]
        dupes = [item_id for item_id, count in Counter(ids).items() if count > 1]
        self.assertEqual(dupes, [])


class House6BioCanonicalTests(unittest.TestCase):
    def test_exact_canonical_strings_for_all_15(self):
        by_id = {item.id: item for item in HOUSE_6_BIO}
        self.assertEqual(set(by_id), set(EXPECTED_BIO_CANONICAL))
        for fact_id, canonical in EXPECTED_BIO_CANONICAL.items():
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].text, canonical)


class House6PartialFidelityTests(unittest.TestCase):
    def test_intellect_demanded_is_not_information_processing(self):
        by_id = {item.id: item for item in HOUSE_6 + HOUSE_6_BIO}
        bio = by_id["h6_bio_intellect_demanded_at_work"]
        l7 = by_id["h6_work_involves_processing_lots_of_information"]
        self.assertNotEqual(bio.id, l7.id)
        self.assertNotEqual(bio.text, l7.text)
        self.assertEqual(bio.source_reference, REF_H6_BIO)
        self.assertEqual(l7.source_reference, REF_H6_L7)
        self.assertEqual(bio.tags, ())
        self.assertNotIn("intellectual_work", bio.tags)
        self.assertNotIn("high_information_workload", bio.tags)
        self.assertIn("high_information_workload", l7.tags)

    def test_two_jobs_or_projects_is_not_several_side_jobs(self):
        by_id = {item.id: item for item in HOUSE_6 + HOUSE_6_BIO}
        bio = by_id["h6_bio_two_parallel_jobs_or_projects"]
        l7 = by_id["h6_several_side_jobs"]
        self.assertNotEqual(bio.id, l7.id)
        self.assertNotEqual(bio.text, l7.text)
        self.assertEqual(bio.source_reference, REF_H6_BIO)
        self.assertEqual(l7.source_reference, REF_H6_L7)
        self.assertEqual(bio.tags, ())
        self.assertNotIn("multiple_side_jobs", bio.tags)
        self.assertIn("multiple_side_jobs", l7.tags)
        self.assertIn("jobs", bio.text.lower())
        self.assertIn("projects", bio.text.lower())


class House6AtomicFidelityTests(unittest.TestCase):
    def test_communication_demanded_is_not_intellect_demanded(self):
        by_id = {item.id: item for item in HOUSE_6_BIO}
        communication = by_id["h6_bio_communication_demanded_at_work"]
        intellect = by_id["h6_bio_intellect_demanded_at_work"]
        self.assertNotEqual(communication.text, intellect.text)
        self.assertEqual(communication.tags, ())
        self.assertEqual(intellect.tags, ())

    def test_communication_demanded_is_not_professional_contact_use(self):
        by_id = {item.id: item for item in HOUSE_6 + HOUSE_6_BIO}
        bio = by_id["h6_bio_communication_demanded_at_work"]
        contacts = by_id["h6_active_use_of_professional_contacts"]
        self.assertNotEqual(bio.text, contacts.text)
        self.assertNotIn("professional_contact_use", bio.tags)

    def test_hassles_are_not_small_matter_preoccupation(self):
        by_id = {item.id: item for item in HOUSE_6 + HOUSE_6_BIO}
        hassles = by_id["h6_bio_increased_concerns_hassles"]
        preoccupation = by_id["h6_preoccupation_with_small_matters"]
        invent = by_id["h6_may_invent_small_problems"]
        self.assertNotEqual(hassles.text, preoccupation.text)
        self.assertNotEqual(hassles.text, invent.text)
        self.assertEqual(hassles.category, "source_specific")
        self.assertEqual(hassles.polarity, "neutral")
        lowered = hassles.text.lower()
        self.assertNotIn("anxiety", lowered)
        self.assertNotIn("disorder", lowered)

    def test_others_assign_work_is_not_duty_execution_or_task_grabbing(self):
        by_id = {item.id: item for item in HOUSE_6 + HOUSE_6_BIO}
        assigned = by_id["h6_bio_others_assign_work"]
        diligent = by_id["h6_duties_performed_diligently"]
        grab = by_id["h6_tendency_to_grab_several_tasks_at_once"]
        self.assertNotEqual(assigned.text, diligent.text)
        self.assertNotEqual(assigned.text, grab.text)
        self.assertIn("other people", assigned.text.lower())
        self.assertEqual(assigned.tags, ())

    def test_professional_education_is_not_retraining(self):
        by_id = {item.id: item for item in HOUSE_6_BIO}
        education = by_id["h6_bio_ongoing_professional_education"]
        retraining = by_id["h6_bio_professional_retraining"]
        self.assertNotEqual(education.text, retraining.text)
        self.assertEqual(education.tags, ())
        self.assertEqual(retraining.tags, ())
        self.assertNotIn("lifelong_learning", education.tags)
        self.assertNotIn("lifelong_learning", retraining.tags)

    def test_medicine_interest_is_not_occupation_association(self):
        by_id = {item.id: item for item in HOUSE_6 + HOUSE_6_BIO}
        interest = by_id["h6_bio_interest_in_medicine"]
        occupation = by_id["h6_occupation_associations"]
        house4 = next(
            item for item in ALL_SOURCE_FACTS if item.id == "h4_bio_interest_in_medicine"
        )
        self.assertNotEqual(interest.text, occupation.text)
        self.assertEqual(interest.text, house4.text)
        self.assertEqual(interest.category, "thinking")
        self.assertEqual(interest.polarity, "strength")
        self.assertEqual(interest.tags, ())

    def test_consultant_and_sales_qualities_are_not_occupation_list(self):
        by_id = {item.id: item for item in HOUSE_6 + HOUSE_6_BIO}
        consultant = by_id["h6_bio_consultant_qualities"]
        sales = by_id["h6_bio_sales_qualities"]
        occupation = by_id["h6_occupation_associations"]
        self.assertNotEqual(consultant.text, occupation.text)
        self.assertNotEqual(sales.text, occupation.text)
        self.assertNotEqual(consultant.text, sales.text)
        self.assertEqual(consultant.tags, ("consulting",))
        self.assertEqual(sales.tags, ("sales",))
        self.assertNotIn("occupation_associations", consultant.tags)
        self.assertNotIn("occupation_associations", sales.tags)

    def test_intellectual_transport_profession_is_not_work_travel(self):
        by_id = {item.id: item for item in HOUSE_6 + HOUSE_6_BIO}
        profession = by_id["h6_bio_intellectual_transport_profession"]
        travel = by_id["h6_work_involves_travel_or_moving"]
        processing = by_id["h6_work_involves_processing_lots_of_information"]
        self.assertNotEqual(profession.text, travel.text)
        self.assertNotEqual(profession.text, processing.text)
        self.assertEqual(
            profession.tags, ("intellectual_work", "transport_profession")
        )
        self.assertNotIn("work_travel", profession.tags)


class House6MedicalSourceTests(unittest.TestCase):
    def test_three_medical_atoms_remain_distinct_and_unconditional(self):
        by_id = {item.id: item for item in HOUSE_6_BIO}
        texts = set()
        for fact_id in MEDICAL_BIO_IDS:
            fact = by_id[fact_id]
            with self.subTest(fact_id=fact_id):
                self.assertEqual(fact.category, "source_specific")
                self.assertEqual(fact.polarity, "risk")
                self.assertEqual(fact.tags, ())
                self.assertIsNone(fact.activation_condition)
                self.assertFalse(fact.unresolved)
                self.assertNotEqual(fact.activation_condition, "hard_aspected")
                texts.add(fact.text)
        self.assertEqual(len(texts), 3)

    def test_medical_facts_do_not_reuse_house_8_tags_or_diagnosis_language(self):
        by_id = {item.id: item for item in HOUSE_6_BIO}
        forbidden = (
            "source_vascular_problem_risk",
            "source_hand_injury_risk",
            "source_finger_injury_risk",
            "source_injury_fracture_association",
            "health_risk",
            "vascular_risk",
            "respiratory_risk",
            "fracture_risk",
        )
        for fact_id in MEDICAL_BIO_IDS:
            fact = by_id[fact_id]
            lowered = fact.text.lower()
            with self.subTest(fact_id=fact_id):
                for tag in forbidden:
                    self.assertNotIn(tag, fact.tags)
                self.assertIn("source-described association", lowered)
                self.assertNotIn("diagnosis", lowered)
                self.assertNotIn("guaranteed", lowered)
                self.assertNotIn("medical advice", lowered)


class House6BioTagGuardTests(unittest.TestCase):
    def test_exact_tags_for_profession_consultant_and_sales(self):
        by_id = {item.id: item for item in HOUSE_6_BIO}
        for fact_id, tags in EXPECTED_BIO_TAGS.items():
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].tags, tags)

    def test_b6_01_through_b6_12_have_no_tags(self):
        by_id = {item.id: item for item in HOUSE_6_BIO}
        self.assertEqual(len(UNTAGGED_BIO_IDS), 12)
        for fact_id in UNTAGGED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertEqual(by_id[fact_id].tags, ())
                for tag in FORBIDDEN_APPROXIMATE_TAGS:
                    self.assertNotIn(tag, by_id[fact_id].tags)

    def test_intellect_demanded_does_not_receive_intellectual_work_tag(self):
        intellect = next(
            item
            for item in HOUSE_6_BIO
            if item.id == "h6_bio_intellect_demanded_at_work"
        )
        self.assertNotIn("intellectual_work", intellect.tags)
        self.assertEqual(intellect.tags, ())

    def test_education_facts_do_not_receive_lifelong_learning_tag(self):
        by_id = {item.id: item for item in HOUSE_6_BIO}
        education = by_id["h6_bio_ongoing_professional_education"]
        retraining = by_id["h6_bio_professional_retraining"]
        self.assertNotIn("lifelong_learning", education.tags)
        self.assertNotIn("lifelong_learning", retraining.tags)

    def test_sales_repeat_spec_unchanged(self):
        tags = {spec["tag"] for spec in REPEATED_SIGNAL_SPECS}
        self.assertIn("sales", tags)
        self.assertNotIn("consulting", tags)
        self.assertNotIn("intellectual_work", tags)
        sales_specs = [spec for spec in REPEATED_SIGNAL_SPECS if spec["tag"] == "sales"]
        self.assertEqual(len(sales_specs), 1)
        self.assertEqual(sales_specs[0]["min_factor_keys"], 2)


class House6Lesson7FrozenTests(unittest.TestCase):
    def test_existing_14_lesson7_facts_unchanged(self):
        self.assertEqual(len(HOUSE_6), 14)
        self.assertEqual(len(FROZEN_L7_HOUSE_6), 14)
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
            for item in HOUSE_6
        )
        self.assertEqual(actual, FROZEN_L7_HOUSE_6)
        self.assertTrue(all(item.activation_condition is None for item in HOUSE_6))
        self.assertTrue(all(item.factor_type == "house" for item in HOUSE_6))
        self.assertTrue(all(item.factor_key == "6" for item in HOUSE_6))


class House6SameHouseSourceDedupTests(unittest.TestCase):
    def test_lesson7_and_bio_share_one_provenance_key(self):
        house_6 = _house_6_facts()
        keys = {_provenance_key(item) for item in house_6}
        self.assertEqual(keys, {"house:6"})
        for item in HOUSE_6 + HOUSE_6_BIO:
            with self.subTest(fact_id=item.id):
                self.assertEqual(_provenance_key(item), "house:6")

    def test_house_6_dual_source_cannot_create_repeat_alone(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=True,
                mercury_sign=None,
                mercury_element=None,
                mercury_motion="direct",
                mercury_house=6,
                aspects=[],
            )
        )
        self.assertEqual(len(profile.house_facts), 29)
        self.assertTrue(all(item.factor_key == "6" for item in profile.house_facts))
        self.assertIn("h6_bio_sales_qualities", _ids(profile.house_facts))
        self.assertIn(
            "h6_work_involves_processing_lots_of_information",
            _ids(profile.house_facts),
        )
        self.assertIn("h6_bio_intellect_demanded_at_work", _ids(profile.house_facts))
        sales_facts = [item for item in profile.house_facts if "sales" in item.tags]
        self.assertEqual(len(sales_facts), 1)
        repeats = detect_repeated_signals(profile.house_facts)
        self.assertEqual(repeats, [])
        for signal in repeats:
            house_sources = [src for src in signal.sources if src.startswith("house:")]
            self.assertLessEqual(len(house_sources), 1, signal)


class House6HumanCopyInventoryConsequenceTests(unittest.TestCase):
    def test_new_bio_facts_are_unreviewed_and_not_in_registries(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        for fact_id in EXPECTED_BIO_IDS:
            with self.subTest(fact_id=fact_id):
                self.assertNotIn(fact_id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(fact_id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(fact_id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[fact_id])
                self.assertEqual(entry.review_status, STATUS_UNREVIEWED)

    def test_existing_lesson7_facts_remain_unreviewed(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        for item in HOUSE_6:
            with self.subTest(l7_id=item.id):
                self.assertNotIn(item.id, HUMAN_COPY_OVERRIDES)
                self.assertNotIn(item.id, APPROVED_RAW_FACT_IDS)
                self.assertNotIn(item.id, NEEDS_REVIEW_FACT_IDS)
                entry = build_catalog_entry(by_id[item.id])
                self.assertEqual(entry.review_status, STATUS_UNREVIEWED)

    def test_house_6_family_counts_after_source_parity(self):
        report = build_human_copy_catalog()
        family = next(f for f in report.families if f.family_key == "house:6")
        self.assertEqual(family.total_facts, 29)
        self.assertEqual(family.approved_override, 0)
        self.assertEqual(family.approved_raw, 0)
        self.assertEqual(family.needs_review, 0)
        self.assertEqual(family.unreviewed, 29)
        self.assertEqual(family.reviewed_count, 0)
        self.assertEqual(family.presentation_ready_count, 0)


class House6SemanticLedgerTests(unittest.TestCase):
    def test_semantic_accounting_from_implemented_facts(self):
        l7_count = len(HOUSE_6)
        bio_count = len(HOUSE_6_BIO)
        exact_overlap = 0
        partial_overlap = 2
        conditional_unresolved = 0
        unique_bio = (
            bio_count - exact_overlap - partial_overlap - conditional_unresolved
        )
        unique_meanings = (
            l7_count + unique_bio + partial_overlap + conditional_unresolved
        )
        self.assertEqual(l7_count, 14)
        self.assertEqual(bio_count, 15)
        self.assertEqual(exact_overlap, 0)
        self.assertEqual(partial_overlap, 2)
        self.assertEqual(unique_bio, 13)
        self.assertEqual(conditional_unresolved, 0)
        self.assertEqual(unique_meanings, 29)
        self.assertEqual(l7_count + bio_count, 29)
        self.assertEqual(
            exact_overlap + partial_overlap + unique_bio + conditional_unresolved,
            15,
        )


if __name__ == "__main__":
    unittest.main()
