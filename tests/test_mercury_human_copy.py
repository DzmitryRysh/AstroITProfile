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
        self.assertEqual(len(HUMAN_COPY_OVERRIDES), 11)


if __name__ == "__main__":
    unittest.main()
