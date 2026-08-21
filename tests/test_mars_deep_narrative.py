"""M10.5 Phase 2B — Human Mars Narrative tests."""

from __future__ import annotations

import re
import unittest
from datetime import date, time
from pathlib import Path

from app.services.mars_deep_narrative import TAG_PHRASE, tag_phrase
from app.services.mars_deep_profile import (
    build_mars_deep_profile,
    derive_presentation_lane,
    is_narrative_eligible,
)
from app.services.mars_facts import aspect_factor_key, compute_mars_source_factors
from app.services.mars_profile_synthesis import serialize_mars_source_profile
from app.services.mars_source_profile import build_mars_source_profile
from app.services.thinking_to_execution import build_thinking_to_execution
from app.services.contribution_profile import build_contribution_profile
from app.services.mercury_source_profile import build_mercury_source_profile
from app.schemas.mercury_source_profile import MercurySourceProfileRequest


AVDEY = dict(
    birth_date=date(1986, 7, 14),
    birth_time=time(7, 10),
    birth_place="Simferopol, Ukraine",
)

RAW_TAG_RE = re.compile(
    r"\b(planned_execution|effort_overload|completion_difficulty|"
    r"mood_dependent_action|hands_on_execution)\b"
)
DEBUG_RE = re.compile(
    r"(supported across|sign:|house:|motion:|aspect:|carried by)",
    re.I,
)


def _api(**natal):
    return serialize_mars_source_profile(build_mars_source_profile(**natal))


def _deep(**natal):
    return build_mars_deep_profile(_api(**natal))


class AspectCoveragePreflightTests(unittest.TestCase):
    def test_avdey_calculated_aspects_preserved_end_to_end(self):
        factors = compute_mars_source_factors(**AVDEY)
        calc_keys = [aspect_factor_key(a) for a in factors.mars_aspects]
        self.assertEqual(calc_keys, ["opposition_Sun", "square_Moon"])

        api = _api(**AVDEY)
        deep = api.synthesis.deep_profile
        config_keys = [a.factor_key for a in deep.configuration.aspects]
        block_keys = [b.identity.factor_key for b in deep.aspects]
        self.assertEqual(config_keys, calc_keys)
        self.assertEqual(block_keys, calc_keys)

    def test_avdey_mars_jupiter_sextile_excluded_by_geometry_orb(self):
        factors = compute_mars_source_factors(**AVDEY)
        planets = {a.planet for a in factors.mars_aspects}
        self.assertNotIn("Jupiter", planets)
        # Separation ~66.3° exceeds major-aspect orb for sextile (60°).
        # Not dropped by Deep builder / source matching.

    def test_unsupported_aspect_identity_preserved_without_invention(self):
        """If geometry has an aspect with no work pack, identity remains."""
        deep = _deep(**AVDEY)
        for block in deep.aspects:
            if not block.work_fact_ids:
                self.assertFalse(block.source_interpretation_available)
                self.assertIn(
                    "not currently available",
                    block.interaction.statement or "",
                )
                self.assertFalse(block.interaction.adds)
                self.assertFalse(block.interaction.reinforcing)


class MarsNarrativeEligibilityTests(unittest.TestCase):
    def test_only_narrative_eligible_facts_support_synthesis(self):
        deep = _deep(**AVDEY)
        for block in (deep.sign, deep.house, deep.motion):
            if not block.narrative:
                continue
            eligible = set(block.narrative_eligible_fact_ids)
            self.assertTrue(set(block.narrative.supporting_fact_ids) <= eligible)
            for sub in block.narrative.subsections:
                self.assertTrue(set(sub.supporting_fact_ids) <= eligible)

    def test_sensitive_source_specific_unresolved_cannot_drive_narrative(self):
        api = _api(**AVDEY)
        deep = api.synthesis.deep_profile
        by_id = {f.id: f for f in deep.secondary_facts}
        for fact in api.sign_facts + api.house_facts + api.motion_facts + api.aspect_facts:
            by_id[fact.id] = fact
        for block in (deep.sign, deep.house, deep.motion):
            for fid in block.narrative.supporting_fact_ids if block.narrative else []:
                fact = by_id.get(fid)
                self.assertIsNotNone(fact)
                self.assertTrue(is_narrative_eligible(fact))
                self.assertEqual(derive_presentation_lane(fact), "core")
        for item in deep.integrated:
            for fid in item.supporting_fact_ids:
                fact = by_id.get(fid)
                self.assertIsNotNone(fact)
                self.assertTrue(is_narrative_eligible(fact))
                self.assertNotEqual(derive_presentation_lane(fact), "sensitive_source")
                self.assertNotEqual(derive_presentation_lane(fact), "source_specific")
                self.assertFalse(fact.unresolved)

    def test_deterministic_output(self):
        first = _deep(**AVDEY)
        second = _deep(**AVDEY)
        self.assertEqual(first.model_dump(), second.model_dump())

    def test_no_raw_tags_or_provenance_in_human_text(self):
        deep = _deep(**AVDEY)
        texts = []
        for block in (deep.sign, deep.house, deep.motion):
            if block.narrative:
                texts.append(block.narrative.core_theme)
                texts.append(block.narrative.summary)
                texts.extend(sub.text for sub in block.narrative.subsections)
        for block in deep.aspects:
            if block.interaction.statement:
                texts.append(block.interaction.statement)
        texts.extend(item.text or "" for item in deep.integrated)
        blob = "\n".join(texts)
        self.assertIsNone(RAW_TAG_RE.search(blob))
        self.assertIsNone(DEBUG_RE.search(blob))

    def test_summary_does_not_repeat_subsection_wording(self):
        deep = _deep(**AVDEY)
        for block in (deep.sign, deep.house, deep.motion):
            if not block.narrative or not block.narrative.subsections:
                continue
            summary = block.narrative.summary.lower()
            for sub in block.narrative.subsections:
                # Full subsection sentence must not be embedded in summary.
                self.assertNotIn(sub.text.lower(), summary)


class MarsAspectNarrativeTests(unittest.TestCase):
    def test_avdey_sun_opposition_adds_completion_difficulty(self):
        deep = _deep(**AVDEY)
        sun = next(b for b in deep.aspects if b.identity.factor_key == "opposition_Sun")
        self.assertTrue(sun.source_interpretation_available)
        tags = {item.tag for item in sun.interaction.adds}
        self.assertIn("completion_difficulty", tags)
        statement = sun.interaction.statement or ""
        self.assertIn("Sun opposition", statement)
        self.assertIn("completion", statement.lower())
        self.assertNotIn("adds more", statement.lower())
        self.assertNotIn("to Mars", statement)

    def test_avdey_moon_square_reinforces_effort_overload(self):
        deep = _deep(**AVDEY)
        moon = next(b for b in deep.aspects if b.identity.factor_key == "square_Moon")
        reinf = {item.tag for item in moon.interaction.reinforcing}
        self.assertIn("effort_overload", reinf)
        self.assertFalse(moon.interaction.contrasting)
        statement = moon.interaction.statement or ""
        self.assertIn("Moon square", statement)
        self.assertIn("emotional state", statement.lower())
        self.assertIn("effort-overload", statement.lower())
        self.assertNotIn("adds more", statement.lower())

    def test_complicate_absent(self):
        deep = _deep(**AVDEY)
        for block in deep.aspects:
            self.assertEqual(block.interaction.contrasting, [])


class MarsIntegratedNarrativeTests(unittest.TestCase):
    def test_max_three_to_four_takeaways(self):
        deep = _deep(**AVDEY)
        self.assertLessEqual(len(deep.integrated), 4)
        self.assertGreaterEqual(len(deep.integrated), 1)

    def test_integrated_includes_base_when_strong_sign_themes(self):
        deep = _deep(**AVDEY)
        bases = [item for item in deep.integrated if item.basis == "base_character"]
        self.assertEqual(len(bases), 1)
        self.assertIn("task focus", bases[0].text.lower())
        self.assertTrue(bases[0].supporting_fact_ids)

    def test_integrated_not_aspect_only_when_base_exists(self):
        deep = _deep(**AVDEY)
        bases = {item.basis for item in deep.integrated}
        self.assertIn("base_character", bases)
        self.assertFalse(bases <= {"aspect_addition", "repeated_signal"})

    def test_integrated_includes_house_and_motion_modifiers(self):
        deep = _deep(**AVDEY)
        modifiers = [
            item for item in deep.integrated if item.basis == "factor_modifier"
        ]
        self.assertGreaterEqual(len(modifiers), 2)
        blob = " ".join(item.text.lower() for item in modifiers)
        self.assertIn("house 6", blob)
        self.assertIn("retrograde", blob)

    def test_integrated_traceable_and_human(self):
        deep = _deep(**AVDEY)
        for item in deep.integrated:
            self.assertTrue(item.text)
            self.assertTrue(item.supporting_fact_ids)
            self.assertIsNone(RAW_TAG_RE.search(item.text))
            self.assertIsNone(DEBUG_RE.search(item.text))

    def test_integrated_no_sensitive_source_support(self):
        api = _api(**AVDEY)
        deep = api.synthesis.deep_profile
        by_id = {f.id: f for f in deep.secondary_facts}
        for fact in api.sign_facts + api.house_facts + api.motion_facts + api.aspect_facts:
            by_id[fact.id] = fact
        for item in deep.integrated:
            for fid in item.supporting_fact_ids:
                fact = by_id[fid]
                self.assertTrue(is_narrative_eligible(fact))
                self.assertNotEqual(derive_presentation_lane(fact), "sensitive_source")
                self.assertNotEqual(derive_presentation_lane(fact), "source_specific")
                self.assertFalse(fact.unresolved)


class MarsUnknownTimeNarrativeTests(unittest.TestCase):
    def test_house_unavailable_no_house_narrative(self):
        deep = _deep(
            birth_date=date(1986, 7, 14),
            birth_place="Simferopol, Ukraine",
            birth_time=None,
        )
        self.assertEqual(deep.house.availability, "unavailable")
        self.assertIsNone(deep.house.narrative)
        self.assertFalse(deep.house.fact_ids)
        self.assertTrue(deep.house.unavailable_reason)


class MarsRegressionBridgeTests(unittest.TestCase):
    def test_tte_and_contribution_unchanged_shape(self):
        from app.services.person_perspective import build_person_perspective

        mars = build_mars_source_profile(**AVDEY)
        mercury = build_mercury_source_profile(
            MercurySourceProfileRequest(**AVDEY)
        )
        person = build_person_perspective(name="Avdey", sex="male")
        tte = build_thinking_to_execution(mercury, mars, person)
        contrib = build_contribution_profile(mercury, mars, person, tte)
        self.assertIsNotNone(tte)
        self.assertIsNotNone(contrib)
        api = serialize_mars_source_profile(mars)
        self.assertIsNotNone(api.synthesis.deep_profile.sign.narrative)


class MarsTagCatalogTests(unittest.TestCase):
    def test_mars_owned_phrases_not_empty(self):
        self.assertIn("planned_execution", TAG_PHRASE)
        self.assertIn("fast_start", TAG_PHRASE)
        self.assertEqual(tag_phrase("hands_on_execution"), "direct, hands-on execution")


class MarsRecruiterUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        cls.js = (root / "app" / "ui" / "recruiter" / "app.js").read_text(
            encoding="utf-8"
        )
        cls.css = (root / "app" / "ui" / "recruiter" / "styles.css").read_text(
            encoding="utf-8"
        )

    def test_deep_mars_progressive_disclosure_helpers_present(self):
        self.assertIn("function renderDeepMars(", self.js)
        self.assertIn("data-deep-mars", self.js)
        self.assertIn("Explore deeper themes", self.js)
        self.assertIn("Integrated Mars", self.js)
        self.assertIn("Execution / Work Lens", self.js)
        self.assertIn("Sensitive source observations", self.js)
        self.assertIn("deep-aspect-unsupported", self.js)
        self.assertIn('["working", "Mars"]', self.js)
        self.assertNotIn('["working", "Working"]', self.js)
        self.assertIn("howTakesActionHeading", self.js)
        self.assertIn("takes action", self.js)
        self.assertIn("howWorksHeading", self.js)

    def test_integrated_before_work_lens_in_working_tab(self):
        # renderProfileWorking composes deep then work lens.
        idx_deep = self.js.index("renderDeepMars(synthesis)")
        idx_work = self.js.index("renderMarsWorkLens(synthesis, person)")
        self.assertLess(idx_deep, idx_work)
        lens = self.js.split("function renderMarsWorkLens", 1)[1].split(
            "function renderProfileWorking", 1
        )[0]
        self.assertIn("howWorksHeading(person)", lens)
        self.assertIn("How you work", self.js)

    def test_secondary_lane_styles_present(self):
        self.assertIn(".deep-sensitive-lane", self.css)


if __name__ == "__main__":
    unittest.main()
