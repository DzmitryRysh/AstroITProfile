"""Tests for Mars human presentation copy layer (M7)."""

from __future__ import annotations

import unittest

from app.services.mars_human_copy import (
    HUMAN_COPY_OVERRIDES,
    get_human_fact_text,
    presentation_overrides_for_facts,
)
from app.services.mars_source_knowledge import ALL_MARS_SOURCE_FACTS
from app.services.mars_source_profile import MarsSourceFact


def _fact(
    fact_id: str,
    text: str,
    *,
    factor_type: str = "sign",
    factor_key: str = "Capricorn",
    category: str = "execution",
    scope: str = "WORK_CORE",
    polarity: str = "neutral",
    tags: tuple[str, ...] = (),
) -> MarsSourceFact:
    return MarsSourceFact(
        id=fact_id,
        factor_type=factor_type,
        factor_key=factor_key,
        text=text,
        source_reference="test",
        category=category,
        scope=scope,
        polarity=polarity,
        tags=tags,
        activation_condition=None,
        activated=True,
        unresolved=False,
    )


class MarsHumanCopyModuleTests(unittest.TestCase):
    def test_curated_id_returns_human_text(self):
        fact = _fact(
            "mars_rx_doing_and_redoing",
            "Doing and redoing.",
            factor_type="motion",
            factor_key="retrograde",
            category="work_rhythm",
        )
        self.assertEqual(
            get_human_fact_text(fact),
            "May revisit or redo actions before moving forward.",
        )

    def test_unmapped_fact_returns_raw_text(self):
        fact = _fact(
            "mars_capricorn_plans_then_executes",
            "No chaotic action: first plans, then executes.",
        )
        self.assertEqual(
            get_human_fact_text(fact),
            "No chaotic action: first plans, then executes.",
        )

    def test_unknown_id_cannot_silently_invent_copy(self):
        self.assertNotIn("invented_mars_fact", HUMAN_COPY_OVERRIDES)
        fact = _fact("invented_mars_fact", "Canonical raw wording.")
        self.assertEqual(get_human_fact_text(fact), "Canonical raw wording.")

    def test_raw_source_fact_text_unchanged(self):
        raw = "Doing and redoing."
        fact = _fact("mars_rx_doing_and_redoing", raw)
        _ = get_human_fact_text(fact)
        self.assertEqual(fact.text, raw)

    def test_override_mapping_uses_stable_ids(self):
        for key in HUMAN_COPY_OVERRIDES:
            self.assertIsInstance(key, str)
            self.assertTrue(key.startswith("mars_"))
            self.assertNotIn(" ", key)

    def test_duplicate_override_ids_impossible(self):
        keys = list(HUMAN_COPY_OVERRIDES.keys())
        self.assertEqual(len(keys), len(set(keys)))

    def test_every_curated_override_id_exists_in_canonical_knowledge(self):
        catalog_ids = {fact.id for fact in ALL_MARS_SOURCE_FACTS}
        missing = sorted(set(HUMAN_COPY_OVERRIDES) - catalog_ids)
        self.assertEqual(missing, [])

    def test_no_blank_human_copy(self):
        for fact_id, text in HUMAN_COPY_OVERRIDES.items():
            self.assertTrue(text.strip(), fact_id)

    def test_presentation_overrides_only_for_present_facts(self):
        mapped = _fact("mars_rx_doing_and_redoing", "Doing and redoing.")
        unmapped = _fact(
            "mars_capricorn_plans_then_executes",
            "No chaotic action: first plans, then executes.",
        )
        result = presentation_overrides_for_facts([mapped, unmapped])
        self.assertEqual(
            result,
            {
                "mars_rx_doing_and_redoing": (
                    "May revisit or redo actions before moving forward."
                )
            },
        )
        self.assertNotIn("mars_capricorn_plans_then_executes", result)

    def test_human_copy_deterministic(self):
        fact = _fact("mars_rx_doing_and_redoing", "Doing and redoing.")
        first = get_human_fact_text(fact)
        second = get_human_fact_text(fact)
        self.assertEqual(first, second)
        self.assertEqual(HUMAN_COPY_OVERRIDES["mars_rx_doing_and_redoing"], first)

    def test_source_facts_tags_categories_scopes_unchanged_by_lookup(self):
        snapshots = [
            (
                fact.id,
                fact.text,
                fact.tags,
                fact.category,
                fact.scope,
                fact.polarity,
                fact.activation_condition,
                fact.unresolved,
            )
            for fact in ALL_MARS_SOURCE_FACTS
        ]
        for fact in ALL_MARS_SOURCE_FACTS:
            runtime = _fact(
                fact.id,
                fact.text,
                factor_type=fact.factor_type,
                factor_key=fact.factor_key,
                category=fact.category,
                scope=fact.scope,
                polarity=fact.polarity,
                tags=fact.tags,
            )
            _ = get_human_fact_text(runtime)
        after = [
            (
                fact.id,
                fact.text,
                fact.tags,
                fact.category,
                fact.scope,
                fact.polarity,
                fact.activation_condition,
                fact.unresolved,
            )
            for fact in ALL_MARS_SOURCE_FACTS
        ]
        self.assertEqual(snapshots, after)

    def test_bio_copy_is_source_bounded_aptitude_not_hiring(self):
        by_id = {fact.id: fact.text for fact in ALL_MARS_SOURCE_FACTS}
        fact_id = "mars_mercury_bio_technical_analytical_it_engineering_aptitude"
        human = get_human_fact_text(_fact(fact_id, by_id[fact_id]))
        self.assertIn("The source associates this pairing with", human)
        self.assertIn("aptitude", human.lower())
        self.assertNotIn("Strong technical skills", human)
        self.assertNotIn("effective manager", human.lower())
        self.assertNotIn("would be good at", human.lower())
        self.assertNotIn("should work as", human.lower())

    def test_sun_l9_start_is_not_rewritten_as_start_problem(self):
        by_id = {fact.id: fact.text for fact in ALL_MARS_SOURCE_FACTS}
        for fact_id in (
            "mars_square_sun_l9_start_not_main_problem",
            "mars_opposition_sun_l9_start_not_main_problem",
        ):
            human = get_human_fact_text(_fact(fact_id, by_id[fact_id])).lower()
            self.assertIn("starting itself may not be the main problem", human)
            self.assertNotIn("difficulty starting", human)

    def test_moon_clusters_remain_alternatives(self):
        by_id = {fact.id: fact.text for fact in ALL_MARS_SOURCE_FACTS}
        a = get_human_fact_text(
            _fact(
                "mars_square_moon_l9_cluster_a_internal_fears",
                by_id["mars_square_moon_l9_cluster_a_internal_fears"],
            )
        )
        b = get_human_fact_text(
            _fact(
                "mars_square_moon_l9_cluster_b_overstrain",
                by_id["mars_square_moon_l9_cluster_b_overstrain"],
            )
        )
        self.assertTrue(a.startswith("One possible expression"))
        self.assertTrue(b.startswith("Another possible expression"))

    def test_rx_indecision_is_modifier_not_inability(self):
        human = HUMAN_COPY_OVERRIDES["mars_rx_indecision"].lower()
        self.assertIn("indecision", human)
        self.assertIn("modifier", human)
        self.assertNotIn("cannot act", human)
        self.assertNotIn("weak mars", human)
        self.assertNotIn("low energy", human)

    def test_occupation_lists_are_associations_not_assignments(self):
        human = HUMAN_COPY_OVERRIDES["mars_h6_occupation_associations"].lower()
        self.assertIn("association with work involving", human)
        self.assertNotIn("would be good at", human)
        self.assertNotIn("should work as", human)
        self.assertNotIn("is qualified", human)

    def test_aquarius_political_fact_stays_source_only_and_not_product_claim(self):
        by_id = {fact.id: fact for fact in ALL_MARS_SOURCE_FACTS}
        fact = by_id["mars_aquarius_source_democracy_liberalism_irresponsibility"]
        self.assertEqual(fact.scope, "SOURCE_ONLY")
        human = get_human_fact_text(
            _fact(fact.id, fact.text, scope=fact.scope, category=fact.category)
        )
        self.assertIn("source-only", human.lower())
        self.assertIn("not a work, civic, or product claim", human.lower())

    def test_no_mercury_human_copy_registry_contamination(self):
        from app.services.mercury_human_copy import HUMAN_COPY_OVERRIDES as MERCURY

        overlap = sorted(set(HUMAN_COPY_OVERRIDES) & set(MERCURY))
        self.assertEqual(overlap, [])
        self.assertTrue(all(key.startswith("mars_") for key in HUMAN_COPY_OVERRIDES))


class MarsHumanCopySynthesisIntegrationTests(unittest.TestCase):
    def _display(self, synthesis, fact_id: str) -> str:
        return synthesis.presentation_text_by_fact_id.get(
            fact_id, synthesis.facts_by_id[fact_id].text
        )

    def test_avdey_human_copy_and_repeat_safety(self):
        from datetime import date, time

        from app.services.mars_profile_synthesis import build_mars_profile_synthesis
        from app.services.mars_source_profile import build_mars_source_profile

        profile = build_mars_source_profile(
            birth_date=date(1986, 7, 14),
            birth_time=time(7, 10),
            birth_place="Simferopol, Ukraine",
        )
        synthesis = build_mars_profile_synthesis(profile)
        by_key = {item.key: item for item in synthesis.sections}

        execute = self._display(synthesis, "mars_capricorn_plans_then_executes")
        self.assertIn("plans", execute.lower())
        self.assertIn("executes", execute.lower())
        hesitate = self._display(
            synthesis, "mars_rx_repeated_hesitation_measure_seven_times"
        )
        self.assertIn("hesitation", hesitate.lower())
        self.assertIn("effort_overload", by_key["under_pressure"].repeated_signals)
        self.assertEqual(
            [signal.signal for signal in synthesis.repeated_signals],
            ["effort_overload"],
        )

        start = self._display(synthesis, "mars_opposition_sun_l9_start_not_main_problem")
        self.assertIn("starting itself may not be the main problem", start.lower())
        self.assertNotIn("difficulty starting", start.lower())
        completion = self._display(
            synthesis, "mars_opposition_sun_l9_completion_difficulty"
        )
        self.assertIn("completion", completion.lower())

        mood_a = self._display(
            synthesis, "mars_square_moon_l9_cluster_a_action_depending_on_mood"
        )
        overwork_b = self._display(
            synthesis, "mars_square_moon_l9_cluster_b_heavy_work_overwork"
        )
        self.assertIn("one possible expression", mood_a.lower())
        self.assertIn("another possible expression", overwork_b.lower())

        conflict = self._display(synthesis, "mars_h6_workplace_conflict_pushes_line")
        self.assertIn("workplace conflict", conflict.lower())

        self.assertNotIn("mars_rx_auto_aggression", synthesis.facts_by_id)
        self.assertNotIn("mars_rx_sexual_temperament_suppression", synthesis.facts_by_id)
        self.assertNotIn("mars_rx_auto_aggression", synthesis.presentation_text_by_fact_id)
        self.assertNotIn(
            "mars_rx_sexual_temperament_suppression",
            synthesis.presentation_text_by_fact_id,
        )

        for fact_id, human in synthesis.presentation_text_by_fact_id.items():
            self.assertEqual(human, HUMAN_COPY_OVERRIDES[fact_id])
            self.assertEqual(
                synthesis.facts_by_id[fact_id].text,
                next(item.text for item in ALL_MARS_SOURCE_FACTS if item.id == fact_id),
            )

    def test_vlad_dzmitry_bio_source_bounded_no_tense_rx(self):
        from datetime import date, time

        from app.services.mars_profile_synthesis import build_mars_profile_synthesis
        from app.services.mars_source_profile import build_mars_source_profile

        vlad = build_mars_profile_synthesis(
            build_mars_source_profile(
                birth_date=date(1986, 5, 16),
                birth_time=time(15, 0),
                birth_place="Dnipro, Ukraine",
            )
        )
        dzmitry = build_mars_profile_synthesis(
            build_mars_source_profile(
                birth_date=date(1985, 11, 12),
                birth_time=time(14, 15),
                birth_place="Zhodino, Belarus",
            )
        )
        for synthesis in (vlad, dzmitry):
            ids = set(synthesis.facts_by_id)
            self.assertFalse(any("_l9_" in fact_id for fact_id in ids))
            self.assertFalse(any(fact_id.startswith("mars_rx_") for fact_id in ids))
            self.assertEqual(synthesis.repeated_signals, ())
            tech = self._display(
                synthesis,
                "mars_mercury_bio_technical_analytical_it_engineering_aptitude",
            )
            self.assertIn("The source associates this pairing with", tech)
            self.assertIn("aptitude", tech.lower())
            self.assertNotIn("Strong technical skills", tech)
            mentor = self._display(synthesis, "mars_jupiter_bio_teacher_mentor_aptitude")
            self.assertIn("teacher or mentor aptitude", mentor.lower())
            self.assertNotIn("effective manager", mentor.lower())
            for fact in synthesis.facts_by_id.values():
                self.assertNotEqual(fact.scope, "SOURCE_ONLY")
                self.assertNotEqual(fact.scope, "PERSONAL_MARS")
