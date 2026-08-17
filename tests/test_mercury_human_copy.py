"""Tests for Mercury human presentation copy layer (S4.0)."""

from __future__ import annotations

import unittest

from app.schemas.mercury_source_profile import SourceFact
from app.services.mercury_human_copy import (
    HUMAN_COPY_OVERRIDES,
    get_human_fact_text,
    presentation_overrides_for_facts,
)
from app.services.mercury_source_knowledge import ALL_SOURCE_FACTS


def _fact(
    fact_id: str,
    text: str,
    *,
    polarity: str = "neutral",
    tags: list[str] | None = None,
) -> SourceFact:
    return SourceFact(
        id=fact_id,
        factor_type="aspect",
        factor_key="Pluto_square",
        category="communication",
        text=text,
        polarity=polarity,
        tags=tags or [],
        source_reference="test",
        activated=True,
        unresolved=False,
    )


class HumanCopyModuleTests(unittest.TestCase):
    def test_curated_id_returns_human_text(self):
        fact = _fact(
            "pluto_sq_conflictual_communication",
            "Toxic conflictual atmosphere around communication.",
            polarity="risk",
        )
        self.assertEqual(
            get_human_fact_text(fact),
            "Communication can become highly conflictual and toxic.",
        )

    def test_unmapped_fact_returns_raw_text(self):
        fact = _fact("some_unmapped_fact", "Strong persuasiveness.")
        self.assertEqual(get_human_fact_text(fact), "Strong persuasiveness.")

    def test_unknown_id_cannot_silently_invent_copy(self):
        self.assertNotIn("invented_fact_id", HUMAN_COPY_OVERRIDES)
        fact = _fact("invented_fact_id", "Canonical raw wording.")
        self.assertEqual(get_human_fact_text(fact), "Canonical raw wording.")

    def test_raw_source_fact_text_unchanged(self):
        raw = "Toxic conflictual atmosphere around communication."
        fact = _fact("pluto_sq_conflictual_communication", raw, polarity="risk")
        _ = get_human_fact_text(fact)
        self.assertEqual(fact.text, raw)

    def test_override_mapping_uses_stable_ids(self):
        for key in HUMAN_COPY_OVERRIDES:
            self.assertIsInstance(key, str)
            self.assertTrue(key)
            self.assertNotIn(" ", key)

    def test_duplicate_override_ids_impossible(self):
        # Dict construction already dedupes; assert uniqueness of keys explicitly.
        keys = list(HUMAN_COPY_OVERRIDES.keys())
        self.assertEqual(len(keys), len(set(keys)))

    def test_every_curated_override_id_exists_in_canonical_knowledge(self):
        catalog_ids = {fact.id for fact in ALL_SOURCE_FACTS}
        missing = sorted(set(HUMAN_COPY_OVERRIDES) - catalog_ids)
        self.assertEqual(missing, [])

    def test_no_blank_human_copy(self):
        for fact_id, text in HUMAN_COPY_OVERRIDES.items():
            self.assertTrue(text.strip(), fact_id)

    def test_presentation_overrides_only_for_present_facts(self):
        mapped = _fact(
            "pluto_sq_words_can_hurt",
            "Words can strongly hurt / have high resonance.",
            polarity="risk",
        )
        unmapped = _fact("unmapped_x", "Strong persuasiveness.")
        result = presentation_overrides_for_facts([mapped, unmapped])
        self.assertEqual(
            result,
            {
                "pluto_sq_words_can_hurt": (
                    "Words can have strong impact and can hurt deeply."
                )
            },
        )
        self.assertNotIn("unmapped_x", result)

    def test_pilot_override_count(self):
        # S4.0–S4.15B (433) + S4.16B house:2 (19).
        self.assertEqual(len(HUMAN_COPY_OVERRIDES), 452)

    def test_s42_override_ids_exist_and_raw_text_unchanged(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        s42_ids = [
            "pluto_sq_core_conflict",
            "leo_afflicted_lying_distortion",
            "leo_afflicted_appearance_of_competence",
            "leo_afflicted_ego_interferes_with_facts",
            "leo_afflicted_extreme_stubbornness",
            "leo_afflicted_putting_on_a_show",
            "taurus_bio_afflicted_cognitive_sluggishness",
            "taurus_bio_afflicted_reduced_muted_intuition",
            "taurus_bio_afflicted_weak_abstract_thinking",
            "cancer_bio_afflicted_disregard_for_facts",
            "cancer_bio_afflicted_everyday_momentary_thinking",
            "cancer_bio_afflicted_habit_bound_momentary_reasoning",
            "cancer_bio_afflicted_losing_central_meaning",
            "cancer_bio_afflicted_losing_the_thread",
            "cancer_bio_afflicted_scatter_distractibility",
            "cancer_bio_afflicted_thinking_trapped_by_habits",
            "cancer_bio_afflicted_thinking_trapped_by_outdated_beliefs",
            "cancer_bio_afflicted_loss_of_focus",
            "leo_l7_throwing_dust_in_eyes",
            "leo_l7_lying_source_claim",
            "leo_l7_dev_creative_vision",
            "leo_l7_dev_creativity",
            "leo_l7_dev_hear_others_opinions",
            "uranus_cj_adhd_like_attention_scatter",
            "pisces_l7_dev_distinguish_own_vs_suggested",
        ]
        self.assertEqual(len(s42_ids), 25)
        for fact_id in s42_ids:
            with self.subTest(fact_id=fact_id):
                self.assertIn(fact_id, by_id)
                self.assertIn(fact_id, HUMAN_COPY_OVERRIDES)
                human = HUMAN_COPY_OVERRIDES[fact_id]
                self.assertTrue(human.strip())
                raw = by_id[fact_id].text
                self.assertNotEqual(raw, human)
                fact = _fact(fact_id, raw)
                self.assertEqual(get_human_fact_text(fact), human)
                self.assertEqual(fact.text, raw)

    def test_technical_proxy_and_cyrillic_absent_from_human_display(self):
        scaffolding_ids = [
            "leo_afflicted_lying_distortion",
            "leo_afflicted_putting_on_a_show",
            "taurus_bio_afflicted_cognitive_sluggishness",
            "cancer_bio_afflicted_loss_of_focus",
        ]
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        for fact_id in scaffolding_ids:
            raw = by_id[fact_id].text
            human = get_human_fact_text(_fact(fact_id, raw))
            self.assertIn("hard_aspected proxy", raw)
            self.assertIn("при поражении", raw)
            self.assertNotIn("hard_aspected", human)
            self.assertNotIn("при поражении", human)
            self.assertNotIn("Source affliction tendency", human)
            self.assertNotIn("activated via project", human)

    def test_sensitive_lying_claims_are_tendencies_not_accusations(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        for fact_id in ("leo_l7_lying_source_claim", "leo_afflicted_lying_distortion"):
            human = get_human_fact_text(_fact(fact_id, by_id[fact_id].text)).lower()
            self.assertNotIn("this person lies", human)
            self.assertNotIn("they deceive", human)
            self.assertNotIn("they are dishonest", human)
            self.assertTrue(
                "may" in human or "can" in human or "tendency" in human,
                human,
            )

    def test_development_focus_growth_area_copy(self):
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["leo_l7_dev_hear_others_opinions"],
            "Growth area: listen more carefully to other people's perspectives.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["leo_l7_dev_creative_vision"],
            "Growth area: develop a broader creative vision.",
        )
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["leo_l7_dev_creativity"],
            "Growth area: strengthen creative expression.",
        )

    def test_s421_vlad_live_ui_polish_overrides(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        expected = {
            "moon_sq_felt_and_thought_may_diverge": (
                "What is felt and what is thought / said may diverge.",
                "What is felt may differ from what is thought or said.",
            ),
            "taurus_practical_concrete_orientation": (
                "Practical / concrete orientation.",
                "Practical, concrete thinking.",
            ),
            "taurus_conversation_needs_practical_purpose": (
                "Conversation should have a practical / result-oriented purpose.",
                "Prefers conversations with a practical or result-oriented purpose.",
            ),
            "taurus_calm_authoritative_communication": (
                "Calm / authoritative communication style.",
                "Communication tends to be calm and authoritative.",
            ),
            "taurus_bio_slowness_dispute_disadvantage": (
                "May lose disputes because of slowness.",
                "A slower response pace can be a disadvantage in fast-moving "
                "arguments.",
            ),
        }
        self.assertEqual(len(expected), 5)
        for fact_id, (raw, human) in expected.items():
            with self.subTest(fact_id=fact_id):
                self.assertIn(fact_id, by_id)
                self.assertEqual(by_id[fact_id].text, raw)
                self.assertEqual(HUMAN_COPY_OVERRIDES[fact_id], human)
                fact = _fact(fact_id, raw)
                self.assertEqual(get_human_fact_text(fact), human)
                self.assertEqual(fact.text, raw)

    def test_s421_avdey_destroy_override_wording_polish(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        fact_id = "pluto_sq_destroy_dig_defeat_through_speech"
        raw = by_id[fact_id].text
        self.assertEqual(
            raw,
            "Tendency to destroy / dig / defeat through thinking and speech.",
        )
        human = (
            "Thinking and speech can become destructive and focused on "
            "defeating the other side."
        )
        self.assertEqual(HUMAN_COPY_OVERRIDES[fact_id], human)
        fact = _fact(fact_id, raw, polarity="risk")
        self.assertEqual(get_human_fact_text(fact), human)
        self.assertEqual(fact.text, raw)
        self.assertNotIn("oriented toward", human)

    def test_s421_vlad_avdey_structure_unchanged(self):
        from datetime import date, time

        from app.schemas.mercury_source_profile import MercurySourceProfileRequest
        from app.services.mercury_source_profile import build_mercury_source_profile

        vlad = build_mercury_source_profile(
            MercurySourceProfileRequest(
                birth_date=date(1986, 5, 16),
                birth_time=time(15, 0),
                birth_place="Dnipro, Ukraine",
            )
        )
        avdey = build_mercury_source_profile(
            MercurySourceProfileRequest(
                birth_date=date(1986, 7, 14),
                birth_time=time(7, 10),
                birth_place="Simferopol, Ukraine",
            )
        )
        self.assertEqual(
            [s.signal for s in vlad.repeated_signals],
            [
                "analytical_thinking",
                "persuasion",
                "lifelong_learning",
                "foreign_languages",
            ],
        )
        self.assertEqual(
            [(c.tag_a, c.tag_b) for c in vlad.contrasting_signals],
            [
                ("deliberate_processing", "fast_thinking"),
                ("deliberate_processing", "mental_switching_pressure"),
            ],
        )
        self.assertEqual(
            [s.signal for s in avdey.repeated_signals],
            [
                "analytical_thinking",
                "technical_ability",
                "debate",
                "argumentation",
                "nonstandard_thinking",
                "sales",
            ],
        )
        self.assertEqual(
            [(c.tag_a, c.tag_b) for c in avdey.contrasting_signals],
            [("superficiality", "analytical_thinking")],
        )
        for fact_id in (
            "moon_sq_felt_and_thought_may_diverge",
            "taurus_practical_concrete_orientation",
            "pluto_sq_destroy_dig_defeat_through_speech",
        ):
            profile = vlad if fact_id.startswith(("moon_", "taurus_")) else avdey
            # facts_by_id lives on synthesis; raw arrays preserve canonical text.
            all_facts = (
                list(profile.sign_facts)
                + list(profile.house_facts)
                + list(profile.aspect_facts)
                + list(profile.motion_facts)
            )
            match = next(f for f in all_facts if f.id == fact_id)
            self.assertEqual(match.text, next(f for f in ALL_SOURCE_FACTS if f.id == fact_id).text)

    def test_s422_dzmitry_live_ui_polish_overrides(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        expected = {
            "sag_thinks_in_categories_globally": (
                "Thinks in categories, globally, on a large scale.",
                "Thinks in broad categories and on a large scale.",
            ),
            "sag_asks_why_what_for": (
                'Asks "why?" / "what for?".',
                "Naturally asks why things matter and what they are for.",
            ),
            "sag_sees_elevated_misses_simple": (
                "Sees elevated / large meaning while missing the simple.",
                "May focus on larger meaning while overlooking simpler details.",
            ),
            "sag_nonstandard_in_intellectual_matters": (
                "Nonstandard in intellectual matters.",
                "Approaches intellectual questions in unconventional ways.",
            ),
            "sag_bio_imagination": (
                "Imagination (source-described tendency).",
                "Shows a tendency toward imaginative thinking.",
            ),
            "sag_bio_large_scale_thinking": (
                "Thoughts are large-scale.",
                "Thinking tends to operate on a large scale.",
            ),
            "sag_bio_global_thinking": (
                "Thoughts are global.",
                "Thinking tends to take a global perspective.",
            ),
            "sag_bio_categorical_thinking": (
                "Thoughts are categorical.",
                "Thinking can become categorical.",
            ),
            "sag_bio_thinking_connected_with_opinions_more_than_facts": (
                "Thinking is connected more with opinions than facts.",
                "Thinking may lean more on opinions than on facts.",
            ),
            "sag_bio_thinking_connected_with_image_of_facts": (
                "Thinking is connected with the image/representation of facts "
                "rather than raw factual material.",
                "Thinking may focus more on how facts are framed or represented "
                "than on raw factual material.",
            ),
            "uranus_cj_function_overridden_by_rebellious_superconsciousness": (
                'Communication and learning function is strongly overridden / '
                'transformed by rebellious technical "super-consciousness".',
                "Communication and learning can be strongly reshaped by "
                "unconventional, technically oriented thinking.",
            ),
            "uranus_cj_rebellious_free_thinking": (
                "Rebellious / free thinking.",
                "Thinking can be rebellious and free-spirited.",
            ),
            "sag_speaks_like_preacher_agitator_philosopher": (
                "Speaks like a preacher / agitator / philosopher.",
                "Communication can take on the tone of a preacher, agitator, or "
                "philosopher.",
            ),
            "sag_speech_maintains_authority": (
                "Speech is used to maintain authority.",
                "Speech may be used to maintain authority.",
            ),
            "sag_tends_to_teach_lecture": (
                "Tends to teach / lecture others.",
                "May slip into teaching or lecturing others.",
            ),
            "sag_broadcasts_from_above": (
                "Broadcasts ideas from above rather than entering equal dialogue.",
                "May communicate from a position of authority rather than as an "
                "equal dialogue partner.",
            ),
            "sag_love_of_pompous_wording": (
                "Love of pompous / high-flown wording.",
                "May favor pompous or high-flown language.",
            ),
            "sag_intolerance_of_others_opinions": (
                "Intolerance of other people's opinions and ideas.",
                "May become intolerant of other people's opinions and ideas.",
            ),
            "sag_tells_others_about_achievements": (
                "Likes telling others about own achievements / exploits.",
                "May enjoy talking about personal achievements and exploits.",
            ),
            "sag_bio_prolific_writing_tendency": (
                "Prolific writing tendency (source-described tendency).",
                "May have a strong tendency toward prolific writing.",
            ),
            "mars_tr_easier_to_argue_debate": (
                "Easier to argue / debate.",
                "Finds it easier to argue or debate.",
            ),
            "mars_tr_speech_clearer_more_forceful": (
                "Speech becomes louder / clearer and more forceful.",
                "Speech can become louder, clearer, and more forceful.",
            ),
            "jupiter_sx_native_and_foreign_languages": (
                "Native language / communication connects with foreign languages.",
                "Communication may have a strong connection with foreign languages.",
            ),
        }
        self.assertEqual(len(expected), 23)
        for fact_id, (raw, human) in expected.items():
            with self.subTest(fact_id=fact_id):
                self.assertIn(fact_id, by_id)
                self.assertEqual(by_id[fact_id].text, raw)
                self.assertEqual(HUMAN_COPY_OVERRIDES[fact_id], human)
                fact = _fact(fact_id, raw)
                self.assertEqual(get_human_fact_text(fact), human)
                self.assertEqual(fact.text, raw)

    def test_s422_dzmitry_representative_presentation_rules(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}

        slash_thinking = get_human_fact_text(
            _fact(
                "sag_thinks_in_categories_globally",
                by_id["sag_thinks_in_categories_globally"].text,
            )
        )
        self.assertNotIn(" / ", slash_thinking)

        imagination = get_human_fact_text(
            _fact("sag_bio_imagination", by_id["sag_bio_imagination"].text)
        )
        prolific = get_human_fact_text(
            _fact(
                "sag_bio_prolific_writing_tendency",
                by_id["sag_bio_prolific_writing_tendency"].text,
            )
        )
        self.assertNotIn("source-described", imagination.lower())
        self.assertNotIn("source-described", prolific.lower())

        uranus = get_human_fact_text(
            _fact(
                "uranus_cj_function_overridden_by_rebellious_superconsciousness",
                by_id[
                    "uranus_cj_function_overridden_by_rebellious_superconsciousness"
                ].text,
            )
        )
        self.assertNotIn("super-consciousness", uranus)
        self.assertNotIn("overridden", uranus.lower())

        preacher = get_human_fact_text(
            _fact(
                "sag_speaks_like_preacher_agitator_philosopher",
                by_id["sag_speaks_like_preacher_agitator_philosopher"].text,
            )
        )
        self.assertEqual(
            preacher,
            "Communication can take on the tone of a preacher, agitator, or "
            "philosopher.",
        )
        self.assertNotIn(" / ", preacher)

        for fact_id in (
            "sag_intolerance_of_others_opinions",
            "sag_speech_maintains_authority",
            "sag_broadcasts_from_above",
        ):
            human = get_human_fact_text(_fact(fact_id, by_id[fact_id].text)).lower()
            self.assertTrue("may" in human or "can" in human, human)
            self.assertNotIn("this person", human)

        for fact_id in (
            "mars_tr_easier_to_argue_debate",
            "mars_tr_speech_clearer_more_forceful",
        ):
            human = get_human_fact_text(_fact(fact_id, by_id[fact_id].text))
            self.assertNotIn(" / ", human)

    def test_s422_dzmitry_structure_unchanged(self):
        from datetime import date, time

        from app.schemas.mercury_source_profile import MercurySourceProfileRequest
        from app.services.mercury_profile_synthesis import build_mercury_profile_synthesis
        from app.services.mercury_source_profile import build_mercury_source_profile

        profile = build_mercury_source_profile(
            MercurySourceProfileRequest(
                birth_date=date(1985, 11, 12),
                birth_time=time(14, 15),
                birth_place="Zhodino, Belarus",
            )
        )
        synthesis = build_mercury_profile_synthesis(profile)
        self.assertEqual(
            [s.signal for s in profile.repeated_signals],
            ["persuasion", "foreign_languages", "teaching"],
        )
        self.assertEqual(
            [(c.tag_a, c.tag_b) for c in profile.contrasting_signals],
            [("global_thinking", "precision_risk")],
        )
        self.assertEqual(synthesis.traceability.total_fact_count, len(synthesis.facts_by_id))
        self.assertEqual(len(synthesis.sections), 6)

        sample_ids = (
            "sag_thinks_in_categories_globally",
            "uranus_cj_function_overridden_by_rebellious_superconsciousness",
            "sag_speaks_like_preacher_agitator_philosopher",
            "mars_tr_easier_to_argue_debate",
        )
        for fact_id in sample_ids:
            raw = next(f for f in ALL_SOURCE_FACTS if f.id == fact_id).text
            self.assertEqual(synthesis.facts_by_id[fact_id].text, raw)
            self.assertEqual(
                synthesis.presentation_text_by_fact_id[fact_id],
                HUMAN_COPY_OVERRIDES[fact_id],
            )
            self.assertNotEqual(synthesis.facts_by_id[fact_id].text, HUMAN_COPY_OVERRIDES[fact_id])

    def test_s44b_sagittarius_overrides_and_raw_invariant(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["sag_bio_afflicted_coarse_rude_communication"],
            "Communication can become coarse or rude.",
        )
        afflicted_raw = by_id["sag_bio_afflicted_coarse_rude_communication"].text
        human = get_human_fact_text(_fact(
            "sag_bio_afflicted_coarse_rude_communication", afflicted_raw
        ))
        self.assertIn("hard_aspected proxy", afflicted_raw)
        self.assertIn("при поражении", afflicted_raw)
        self.assertNotIn("hard_aspected", human)
        self.assertNotIn("при поражении", human)
        self.assertEqual(afflicted_raw, by_id["sag_bio_afflicted_coarse_rude_communication"].text)

        occupation = HUMAN_COPY_OVERRIDES["sag_bio_occupation_associations"]
        self.assertIn("not career assignments", occupation)
        self.assertEqual(
            get_human_fact_text(
                _fact(
                    "sag_tendency_to_attach_labels",
                    by_id["sag_tendency_to_attach_labels"].text,
                )
            ),
            "Tendency to attach labels.",
        )
        self.assertNotIn("sag_tendency_to_attach_labels", HUMAN_COPY_OVERRIDES)
        # S4.12B: framework status resolved via explicit override.
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["sag_bio_major_exile"],
            "Within the source framework, this placement is described as a "
            "major exile.",
        )
        self.assertIn("major exile", by_id["sag_bio_major_exile"].text.lower())

    def test_s45b_taurus_overrides_and_raw_invariant(self):
        by_id = {fact.id: fact for fact in ALL_SOURCE_FACTS}
        self.assertEqual(
            HUMAN_COPY_OVERRIDES["taurus_slower_switching_topics"],
            "May switch more slowly between topics or tasks.",
        )
        raw = by_id["taurus_slower_switching_topics"].text
        human = get_human_fact_text(_fact("taurus_slower_switching_topics", raw))
        self.assertIn(" / ", raw)
        self.assertNotIn(" / ", human)
        self.assertEqual(raw, by_id["taurus_slower_switching_topics"].text)

        aptitude_raw = by_id["taurus_bio_vocal_artistic_aptitude"].text
        aptitude_human = get_human_fact_text(
            _fact("taurus_bio_vocal_artistic_aptitude", aptitude_raw)
        )
        self.assertIn("source-described", aptitude_raw)
        self.assertNotIn("source-described", aptitude_human.lower())

        self.assertNotIn("taurus_harmonious_thinking", HUMAN_COPY_OVERRIDES)
        self.assertEqual(
            get_human_fact_text(
                _fact(
                    "taurus_harmonious_thinking",
                    by_id["taurus_harmonious_thinking"].text,
                )
            ),
            "Harmonious thinking.",
        )


if __name__ == "__main__":
    unittest.main()
