"""Mercury Deep Profile M9.5A — factor-first backend presentation tests."""

from __future__ import annotations

import unittest
from datetime import date, time
from unittest.mock import patch

from app.schemas.mercury_source_profile import MercurySourceProfileRequest, SourceFact
from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_deep_profile import (
    MAX_HIGHLIGHTS,
    MAX_INTEGRATED_TAKEAWAYS,
    build_mercury_deep_profile,
    select_highlight_fact_ids,
)
from app.services.mercury_human_copy_catalog import (
    STATUS_APPROVED_RAW,
    STATUS_UNREVIEWED,
    derive_review_status,
)
from app.services.mercury_profile_synthesis import (
    SECTION_SPECS,
    attach_mercury_profile_synthesis,
    build_mercury_profile_synthesis,
)
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
)


AVDEY = dict(
    birth_date=date(1986, 7, 14),
    birth_time=time(7, 10),
    birth_place="Simferopol, Ukraine",
)
VLAD = dict(
    birth_date=date(1986, 5, 16),
    birth_time=time(15, 0),
    birth_place="Dnipro, Ukraine",
)


def _profile(**natal):
    return build_mercury_source_profile(MercurySourceProfileRequest(**natal))


def _deep(**natal):
    return build_mercury_deep_profile(_profile(**natal))


class DeepProfileFactorOwnershipTests(unittest.TestCase):
    def test_sign_facts_are_all_under_sign_block(self):
        profile = _profile(**AVDEY)
        deep = build_mercury_deep_profile(profile)
        self.assertEqual(deep.sign.factor_type, "sign")
        self.assertEqual(deep.sign.factor_key, profile.calculated.mercury_sign)
        self.assertEqual(deep.sign.availability, "available")
        self.assertEqual(deep.sign.ownership, "canonical_source")
        self.assertEqual(deep.sign.content_kind, "source")
        self.assertEqual(
            set(deep.sign.fact_ids),
            {fact.id for fact in profile.sign_facts if fact.activated},
        )
        self.assertTrue(deep.sign.fact_ids)
        self.assertTrue(
            any("sibling" in fact.id or "debate" in fact.id or "sales" in fact.id
                for fact in profile.sign_facts)
            or any("sibling" in fid or "driving" in fid for fid in deep.house.fact_ids)
        )

    def test_house_facts_all_under_house_when_birth_time_known(self):
        profile = _profile(**AVDEY)
        deep = build_mercury_deep_profile(profile)
        self.assertTrue(deep.configuration.house_available)
        self.assertEqual(deep.house.availability, "available")
        self.assertEqual(deep.house.factor_key, str(profile.calculated.mercury_house))
        self.assertEqual(
            set(deep.house.fact_ids),
            {fact.id for fact in profile.house_facts if fact.activated},
        )
        self.assertTrue(
            any(
                fact.id in deep.house.fact_ids
                for fact in profile.house_facts
                if "sibling" in fact.id or "driving" in fact.id or "sales" in fact.id
            )
        )

    def test_unknown_birth_time_house_unavailable_explicitly(self):
        natal = dict(birth_date=AVDEY["birth_date"], birth_place=AVDEY["birth_place"])
        profile = _profile(**natal)
        deep = build_mercury_deep_profile(profile)
        self.assertFalse(profile.calculated.birth_time_known)
        self.assertFalse(deep.configuration.house_available)
        self.assertIsNone(deep.configuration.mercury_house)
        self.assertEqual(deep.house.availability, "unavailable")
        self.assertEqual(deep.house.fact_ids, [])
        self.assertEqual(deep.house.highlight_fact_ids, [])
        self.assertIsNotNone(deep.house.unavailable_reason)
        self.assertIn("birth time", deep.house.unavailable_reason.lower())
        self.assertIn("birth time", deep.configuration.house_unavailable_reason.lower())
        self.assertTrue(
            any("houses and angles omitted" in item for item in deep.limitations)
        )

    def test_motion_facts_remain_separated(self):
        profile = _profile(**AVDEY)
        deep = build_mercury_deep_profile(profile)
        self.assertEqual(profile.calculated.mercury_motion, "retrograde")
        self.assertEqual(deep.motion.availability, "available")
        self.assertEqual(deep.motion.factor_key, "retrograde")
        self.assertEqual(
            set(deep.motion.fact_ids),
            {fact.id for fact in profile.motion_facts if fact.activated},
        )
        self.assertTrue(
            set(deep.motion.fact_ids).isdisjoint(set(deep.sign.fact_ids))
        )
        self.assertTrue(
            set(deep.motion.fact_ids).isdisjoint(set(deep.house.fact_ids))
        )

    def test_direct_motion_without_facts_is_neutral_default(self):
        profile = _profile(**VLAD)
        deep = build_mercury_deep_profile(profile)
        self.assertEqual(profile.calculated.mercury_motion, "direct")
        self.assertEqual(deep.motion.availability, "neutral_default")
        self.assertEqual(deep.motion.fact_ids, [])
        self.assertEqual(deep.motion.factor_key, "direct")


class DeepProfileHighlightTests(unittest.TestCase):
    def test_factors_expose_all_fact_ids_plus_highlight_subset(self):
        profile = _profile(**AVDEY)
        deep = build_mercury_deep_profile(profile)
        for block in (deep.sign, deep.house, deep.motion):
            if block.availability != "available":
                continue
            self.assertTrue(block.fact_ids)
            self.assertLessEqual(len(block.highlight_fact_ids), MAX_HIGHLIGHTS)
            self.assertTrue(set(block.highlight_fact_ids) <= set(block.fact_ids))
        for block in deep.aspects:
            self.assertTrue(block.fact_ids)
            self.assertLessEqual(len(block.highlight_fact_ids), MAX_HIGHLIGHTS)
            self.assertTrue(set(block.highlight_fact_ids) <= set(block.fact_ids))

    def test_highlight_selection_avoids_same_theme_when_diverse(self):
        facts = [
            SourceFact(
                id="a1",
                factor_type="sign",
                factor_key="Leo",
                category="thinking",
                text="t1",
                polarity="strength",
                tags=["monologue_thinking"],
                source_reference="test",
            ),
            SourceFact(
                id="a2",
                factor_type="sign",
                factor_key="Leo",
                category="thinking",
                text="t2",
                polarity="strength",
                tags=["monologue_thinking"],
                source_reference="test",
            ),
            SourceFact(
                id="b1",
                factor_type="sign",
                factor_key="Leo",
                category="communication",
                text="c1",
                polarity="strength",
                tags=["debate"],
                source_reference="test",
            ),
            SourceFact(
                id="c1",
                factor_type="sign",
                factor_key="Leo",
                category="learning",
                text="l1",
                polarity="neutral",
                tags=["learning_style"],
                source_reference="test",
            ),
            SourceFact(
                id="d1",
                factor_type="sign",
                factor_key="Leo",
                category="risk",
                text="r1",
                polarity="risk",
                tags=["superficiality"],
                source_reference="test",
            ),
        ]

        def fake_status(fact_id: str) -> str:
            return STATUS_APPROVED_RAW

        with patch(
            "app.services.mercury_deep_profile.derive_review_status",
            fake_status,
        ):
            highlights = select_highlight_fact_ids(facts)
        self.assertEqual(highlights, ["a1", "b1", "c1", "d1"])
        self.assertNotIn("a2", highlights)

    def test_highlight_ordering_is_deterministic(self):
        profile = _profile(**AVDEY)
        first = build_mercury_deep_profile(profile)
        second = build_mercury_deep_profile(profile)
        self.assertEqual(first.sign.highlight_fact_ids, second.sign.highlight_fact_ids)
        self.assertEqual(
            [block.highlight_fact_ids for block in first.aspects],
            [block.highlight_fact_ids for block in second.aspects],
        )


class DeepProfileAspectTests(unittest.TestCase):
    def test_aspect_facts_grouped_under_exact_calculated_aspect(self):
        profile = _profile(**AVDEY)
        deep = build_mercury_deep_profile(profile)
        calc_keys = [
            f"{aspect.type}_{aspect.planet}" for aspect in profile.calculated.aspects
        ]
        block_keys = [block.identity.factor_key for block in deep.aspects]
        self.assertEqual(block_keys, calc_keys)
        self.assertEqual(len(deep.aspects), 2)
        by_key = {block.identity.factor_key: block for block in deep.aspects}
        for key, block in by_key.items():
            expected = {
                fact.id
                for fact in profile.aspect_facts
                if fact.activated and fact.factor_key == key
            }
            self.assertEqual(set(block.fact_ids), expected)
            self.assertEqual(block.ownership, "canonical_source")
            self.assertEqual(block.content_kind, "source")

    def test_aspect_facts_do_not_leak_across_aspects(self):
        deep = _deep(**AVDEY)
        by_key = {block.identity.factor_key: set(block.fact_ids) for block in deep.aspects}
        self.assertIn("square_Pluto", by_key)
        self.assertIn("trine_Saturn", by_key)
        self.assertTrue(by_key["square_Pluto"].isdisjoint(by_key["trine_Saturn"]))
        self.assertTrue(by_key["square_Pluto"])
        self.assertTrue(by_key["trine_Saturn"])

    def test_aspect_can_expose_add_without_base_tag_overlap(self):
        profile = _profile(**AVDEY)
        deep = build_mercury_deep_profile(profile)
        saturn = next(
            block for block in deep.aspects if block.identity.factor_key == "trine_Saturn"
        )
        self.assertTrue(saturn.interaction.available)
        add_tags = {item.tag for item in saturn.interaction.adds}
        self.assertIn("analytical_thinking", add_tags)
        analytical = next(
            item for item in saturn.interaction.adds if item.tag == "analytical_thinking"
        )
        self.assertEqual(analytical.aspect_fact_ids, ["saturn_tr_analytical_ability"])
        self.assertTrue(set(analytical.aspect_fact_ids) <= set(saturn.fact_ids))
        for item in saturn.interaction.adds:
            self.assertTrue(set(item.aspect_fact_ids) <= set(saturn.fact_ids))
        self.assertIn("adds", saturn.interaction.statement.lower())
        self.assertIn("contrast between", saturn.interaction.statement.lower())
        self.assertNotIn(" vs ", saturn.interaction.statement.lower())

    def test_add_fact_ids_belong_to_exact_aspect(self):
        deep = _deep(**AVDEY)
        for block in deep.aspects:
            for theme in block.interaction.adds:
                self.assertTrue(set(theme.aspect_fact_ids) <= set(block.fact_ids))
                self.assertTrue(theme.aspect_fact_ids)

    def test_reinforcement_still_requires_base_overlap(self):
        profile = _profile(**AVDEY)
        deep = build_mercury_deep_profile(profile)
        pluto = next(
            block for block in deep.aspects if block.identity.factor_key == "square_Pluto"
        )
        reinforce_signals = {item.signal for item in pluto.interaction.reinforcing}
        self.assertIn("debate", reinforce_signals)
        debate = next(
            item for item in pluto.interaction.reinforcing if item.signal == "debate"
        )
        self.assertTrue(debate.base_fact_ids)
        self.assertTrue(any(key.startswith("sign:") for key in debate.base_provenance_keys))

        saturn = next(
            block for block in deep.aspects if block.identity.factor_key == "trine_Saturn"
        )
        reinforce_signals = {item.signal for item in saturn.interaction.reinforcing}
        self.assertNotIn("analytical_thinking", reinforce_signals)
        self.assertNotIn("technical_ability", reinforce_signals)
        self.assertNotIn("argumentation", reinforce_signals)

    def test_contrast_still_requires_existing_contrasting_evidence(self):
        profile = _profile(**AVDEY)
        deep = build_mercury_deep_profile(profile)
        saturn = next(
            block for block in deep.aspects if block.identity.factor_key == "trine_Saturn"
        )
        self.assertTrue(saturn.interaction.contrasting)
        pair = saturn.interaction.contrasting[0]
        self.assertEqual((pair.tag_a, pair.tag_b), ("superficiality", "analytical_thinking"))
        self.assertTrue(pair.base_fact_ids)
        self.assertTrue(any(fid.startswith("leo_") for fid in pair.base_fact_ids))

        stripped = profile.model_copy(update={"contrasting_signals": []})
        deep_stripped = build_mercury_deep_profile(stripped)
        saturn_stripped = next(
            block
            for block in deep_stripped.aspects
            if block.identity.factor_key == "trine_Saturn"
        )
        self.assertEqual(saturn_stripped.interaction.contrasting, [])

    def test_aspect_only_facts_do_not_falsely_appear_as_base_evidence(self):
        deep = _deep(**AVDEY)
        saturn = next(
            block for block in deep.aspects if block.identity.factor_key == "trine_Saturn"
        )
        for theme in saturn.interaction.adds:
            self.assertFalse(any(fid.startswith("leo_") for fid in theme.aspect_fact_ids))
            self.assertFalse(any(fid.startswith("h1_") for fid in theme.aspect_fact_ids))
            self.assertFalse(any(fid.startswith("rx_") for fid in theme.aspect_fact_ids))
        for item in saturn.interaction.reinforcing:
            self.assertTrue(all(fid.startswith("saturn_") for fid in item.aspect_fact_ids))

    def test_unreviewed_facts_cannot_become_add(self):
        profile = _profile(**AVDEY)
        deep = build_mercury_deep_profile(profile)
        saturn = next(
            block for block in deep.aspects if block.identity.factor_key == "trine_Saturn"
        )
        add_ids = {
            fid
            for theme in saturn.interaction.adds
            for fid in theme.aspect_fact_ids
        }
        for fact_id in add_ids:
            self.assertIn(
                derive_review_status(fact_id),
                {STATUS_APPROVED_RAW, "approved_override"},
            )
        self.assertNotIn("saturn_tr_patience", add_ids)
        self.assertNotIn("saturn_tr_planning", add_ids)
        self.assertNotIn("saturn_tr_driving_skill", add_ids)

        real = derive_review_status

        def fake_status(fact_id: str) -> str:
            if fact_id.startswith("saturn_"):
                return STATUS_UNREVIEWED
            return real(fact_id)

        with patch(
            "app.services.mercury_deep_profile.derive_review_status",
            fake_status,
        ):
            deep_blocked = build_mercury_deep_profile(profile)
        saturn_blocked = next(
            block
            for block in deep_blocked.aspects
            if block.identity.factor_key == "trine_Saturn"
        )
        self.assertEqual(saturn_blocked.interaction.adds, [])

    def test_empty_when_no_eligible_aspect_observations(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=False,
                mercury_sign="Aries",
                mercury_element="fire",
                mercury_motion="direct",
                aspects=[MercuryAspect(planet="Moon", type="square", orb_deg=1.0)],
            )
        )
        profile = profile.model_copy(
            update={
                "repeated_signals": [],
                "contrasting_signals": [],
                "aspect_facts": [
                    fact.model_copy(update={"unresolved": True})
                    for fact in profile.aspect_facts
                ],
            }
        )
        with patch(
            "app.services.mercury_deep_profile.derive_review_status",
            lambda _fid: STATUS_UNREVIEWED,
        ):
            deep = build_mercury_deep_profile(profile)
        block = deep.aspects[0]
        self.assertEqual(block.interaction.adds, [])
        self.assertEqual(block.interaction.reinforcing, [])
        self.assertEqual(block.interaction.contrasting, [])
        self.assertFalse(block.interaction.available)


class DeepProfileIntegratedTests(unittest.TestCase):
    def test_integrated_references_ids_without_duplicating_source_sentences(self):
        profile = _profile(**AVDEY)
        deep = build_mercury_deep_profile(profile)
        self.assertLessEqual(len(deep.integrated), MAX_INTEGRATED_TAKEAWAYS)
        self.assertGreaterEqual(len(deep.integrated), 1)
        source_texts = {
            fact.text
            for fact in (
                list(profile.sign_facts)
                + list(profile.house_facts)
                + list(profile.motion_facts)
                + list(profile.aspect_facts)
            )
        }
        for item in deep.integrated:
            self.assertEqual(item.kind, "synthesis")
            self.assertTrue(item.supporting_fact_ids)
            self.assertTrue(item.provenance_keys)
            self.assertNotIn(item.text, source_texts)
            if item.basis == "aspect_addition":
                self.assertTrue(all(key.startswith("aspect:") for key in item.provenance_keys))
                self.assertTrue(
                    "intensifies" in item.text.lower()
                    or "beyond what the base" in item.text.lower()
                )
                self.assertNotRegex(item.text, r"(aspect:|sign:|house:|motion:)")
            else:
                self.assertGreaterEqual(
                    len(set(p.split(":")[0] for p in item.provenance_keys)),
                    2,
                )

    def test_integrated_can_represent_additive_aspect_modification(self):
        deep = _deep(**AVDEY)
        additive = [item for item in deep.integrated if item.basis == "aspect_addition"]
        self.assertTrue(
            any(item.key == "add:trine_Saturn" for item in additive)
            or any(
                "trine_Saturn" in key
                for item in deep.integrated
                for key in item.provenance_keys
            )
        )
        for item in additive:
            self.assertTrue(item.supporting_fact_ids)
            self.assertTrue(all(key.startswith("aspect:") for key in item.provenance_keys))
            self.assertTrue(
                "intensifies" in item.text.lower()
                or "beyond what the base" in item.text.lower()
            )

    def test_integrated_is_deterministic(self):
        profile = _profile(**AVDEY)
        first = build_mercury_deep_profile(profile)
        second = build_mercury_deep_profile(profile)
        self.assertEqual(first.model_dump(), second.model_dump())


class DeepProfileCompatibilityTests(unittest.TestCase):
    def test_existing_work_synthesis_structures_unchanged(self):
        profile = _profile(**AVDEY)
        attached = attach_mercury_profile_synthesis(profile)
        synthesis = attached.synthesis
        self.assertIsNotNone(synthesis)
        self.assertIsNotNone(synthesis.deep_profile)
        section_keys = [section.key for section in synthesis.sections]
        self.assertEqual(section_keys, [spec[0] for spec in SECTION_SPECS])
        self.assertTrue(hasattr(synthesis, "thinking_at_a_glance"))
        self.assertTrue(hasattr(synthesis, "strongest_patterns"))
        self.assertTrue(hasattr(synthesis, "resolved_tensions"))
        self.assertTrue(hasattr(synthesis, "conditional_tensions"))
        self.assertTrue(hasattr(synthesis, "presentation_text_by_fact_id"))
        self.assertTrue(hasattr(synthesis, "facts_by_id"))
        internal = build_mercury_profile_synthesis(profile)
        self.assertEqual(len(internal.sections), len(SECTION_SPECS))

    def test_attached_deep_profile_matches_builder(self):
        profile = _profile(**VLAD)
        attached = attach_mercury_profile_synthesis(profile)
        direct = build_mercury_deep_profile(profile)
        self.assertEqual(
            attached.synthesis.deep_profile.model_dump(),
            direct.model_dump(),
        )

    def test_configuration_header_matches_calculated_snapshot(self):
        profile = _profile(**AVDEY)
        deep = build_mercury_deep_profile(profile)
        calc = profile.calculated
        self.assertEqual(deep.configuration.mercury_sign, calc.mercury_sign)
        self.assertEqual(deep.configuration.mercury_house, calc.mercury_house)
        self.assertEqual(deep.configuration.mercury_motion, calc.mercury_motion)
        self.assertEqual(deep.configuration.birth_time_known, calc.birth_time_known)
        self.assertEqual(
            [item.factor_key for item in deep.configuration.aspects],
            [f"{a.type}_{a.planet}" for a in calc.aspects],
        )


if __name__ == "__main__":
    unittest.main()
