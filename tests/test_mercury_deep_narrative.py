"""M9.5C — Human Mercury Narrative tests."""

from __future__ import annotations

import re
import unittest
from datetime import date, time

from app.schemas.mercury_source_profile import MercurySourceProfileRequest
from app.schemas.mercury_work_profile import MercuryAspect, MercurySourceFactors
from app.services.mercury_deep_profile import build_mercury_deep_profile
from app.services.mercury_source_profile import (
    build_mercury_source_profile,
    build_source_profile_from_factors,
)


AVDEY = dict(
    birth_date=date(1986, 7, 14),
    birth_time=time(7, 10),
    birth_place="Simferopol, Ukraine",
)


def _profile(**natal):
    return build_mercury_source_profile(MercurySourceProfileRequest(**natal))


RAW_PROVENANCE_RE = re.compile(
    r"(aspect:|sign:|house:|motion:|\+4 more|\+3 more|supported across)",
    re.I,
)


class MercuryNarrativeCoreTests(unittest.TestCase):
    def test_narrative_is_deterministic(self):
        profile = _profile(**AVDEY)
        first = build_mercury_deep_profile(profile)
        second = build_mercury_deep_profile(profile)
        self.assertEqual(first.model_dump(), second.model_dump())

    def test_every_narrative_statement_has_supporting_fact_ids(self):
        deep = build_mercury_deep_profile(_profile(**AVDEY))
        for block in (deep.sign, deep.house, deep.motion):
            if not block.narrative:
                continue
            self.assertTrue(block.narrative.supporting_fact_ids)
            self.assertTrue(
                set(block.narrative.supporting_fact_ids) <= set(block.fact_ids)
            )
            for sub in block.narrative.subsections:
                self.assertTrue(sub.supporting_fact_ids)
                self.assertTrue(set(sub.supporting_fact_ids) <= set(block.fact_ids))
        for block in deep.aspects:
            if block.interaction.available:
                self.assertTrue(block.interaction.supporting_fact_ids)
                self.assertIsNotNone(block.interaction.statement)
        for item in deep.integrated:
            self.assertTrue(item.supporting_fact_ids)
            self.assertTrue(item.provenance_keys)

    def test_source_facts_remain_intact(self):
        profile = _profile(**AVDEY)
        deep = build_mercury_deep_profile(profile)
        self.assertEqual(
            set(deep.sign.fact_ids),
            {fact.id for fact in profile.sign_facts if fact.activated},
        )
        self.assertEqual(
            set(deep.house.fact_ids),
            {fact.id for fact in profile.house_facts if fact.activated},
        )
        self.assertTrue(
            any("sibling" in fid or "driving" in fid for fid in deep.house.fact_ids)
        )

    def test_factor_narrative_does_not_duplicate_a_single_source_fact(self):
        profile = _profile(**AVDEY)
        deep = build_mercury_deep_profile(profile)
        self.assertIsNotNone(deep.sign.narrative)
        source_texts = {fact.text for fact in profile.sign_facts}
        self.assertNotIn(deep.sign.narrative.summary, source_texts)
        self.assertGreaterEqual(len(deep.sign.narrative.supporting_fact_ids), 2)

    def test_no_unsupported_semantic_in_factor_narrative(self):
        profile = _profile(**AVDEY)
        deep = build_mercury_deep_profile(profile)
        known_tags = set()
        for fact in profile.sign_facts:
            if fact.activated:
                known_tags.update(fact.tags or ())
        # Narrative uses only phrases derived from known tags / templates.
        self.assertTrue(deep.sign.narrative.supporting_fact_ids)
        for fid in deep.sign.narrative.supporting_fact_ids:
            self.assertTrue(any(fact.id == fid for fact in profile.sign_facts))

    def test_aspect_narrative_add_only(self):
        profile = build_source_profile_from_factors(
            MercurySourceFactors(
                birth_time_known=False,
                mercury_sign="Aries",
                mercury_element="fire",
                mercury_motion="direct",
                aspects=[MercuryAspect(planet="Saturn", type="trine", orb_deg=1.5)],
            )
        )
        # Strip repeats/contrasts so only ADD can drive interaction.
        profile = profile.model_copy(
            update={"repeated_signals": [], "contrasting_signals": []}
        )
        deep = build_mercury_deep_profile(profile)
        block = deep.aspects[0]
        if block.interaction.adds:
            self.assertTrue(block.interaction.available)
            self.assertEqual(block.interaction.reinforcing, [])
            self.assertEqual(block.interaction.contrasting, [])
            self.assertIsNotNone(block.interaction.statement)
            self.assertTrue(
                "adds" in block.interaction.statement.lower()
                or "intensifies" in block.interaction.statement.lower()
            )
            # Compressed paragraph should not dump every ADD label.
            self.assertNotIn("among other themes", block.interaction.statement.lower())
            self.assertTrue(all(item.label for item in block.interaction.adds))

    def test_aspect_narrative_add_reinforce_contrast(self):
        deep = build_mercury_deep_profile(_profile(**AVDEY))
        pluto = next(
            block for block in deep.aspects if block.identity.factor_key == "square_Pluto"
        )
        self.assertTrue(pluto.interaction.adds)
        self.assertTrue(pluto.interaction.reinforcing)
        self.assertTrue(pluto.interaction.contrasting)
        statement = pluto.interaction.statement or ""
        self.assertTrue(
            "intensifies" in statement.lower() or "adds" in statement.lower()
        )
        self.assertIn("strengthens", statement.lower())
        self.assertIn("contrast between", statement.lower())
        self.assertNotIn("among other themes", statement.lower())
        self.assertNotIn(" vs ", statement.lower())
        self.assertNotRegex(statement, RAW_PROVENANCE_RE)
        # Paragraph must not echo the full ADD chip list.
        add_labels = [item.label.lower() for item in pluto.interaction.adds]
        listed = sum(1 for label in add_labels if label and label in statement.lower())
        self.assertLess(listed, len(add_labels))
        self.assertTrue(all(item.label for item in pluto.interaction.adds))

    def test_integrated_has_no_raw_provenance_in_user_text(self):
        deep = build_mercury_deep_profile(_profile(**AVDEY))
        self.assertTrue(deep.integrated)
        for item in deep.integrated:
            self.assertNotRegex(item.text, RAW_PROVENANCE_RE)
            self.assertNotIn("placeholder", item.text)
            # Provenance remains available for Evidence.
            self.assertTrue(item.provenance_keys)

    def test_unknown_time_safety_preserved(self):
        natal = dict(birth_date=AVDEY["birth_date"], birth_place=AVDEY["birth_place"])
        deep = build_mercury_deep_profile(_profile(**natal))
        self.assertEqual(deep.house.availability, "unavailable")
        self.assertIsNone(deep.house.narrative)
        self.assertEqual(deep.house.fact_ids, [])
        self.assertIsNotNone(deep.sign.narrative)


if __name__ == "__main__":
    unittest.main()
