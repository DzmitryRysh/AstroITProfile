"""Person/perspective helper — recruiter third-person vs self you/your."""

from __future__ import annotations

import unittest

from datetime import date, time

from app.services.mars_profile_synthesis import build_mars_profile_synthesis
from app.services.mars_source_profile import build_mars_source_profile
from app.services.mars_work_glance import (
    EXECUTION_TEMPLATES,
    PRESSURE_TEMPLATES,
    SLOWDOWN_TEMPLATES,
    build_mars_work_glance,
    render_mars_glance_text,
    render_mars_glance_title,
)
from app.services.person_perspective import (
    PERSPECTIVE_SELF,
    PERSPECTIVE_THIRD,
    build_person_perspective,
    fill_person_template,
    how_thinks_heading,
    how_works_heading,
    mars_section_heading,
    normalize_sex,
    possessive_name,
)

AVDEY = dict(
    birth_date=date(1986, 7, 14),
    birth_time=time(7, 10),
    birth_place="Simferopol, Ukraine",
)


def _synthesis():
    return build_mars_profile_synthesis(build_mars_source_profile(**AVDEY))


class PersonPerspectiveTests(unittest.TestCase):
    def test_male_structured_field_uses_he_him_his(self):
        person = build_person_perspective(name="Avdey", sex="male")
        self.assertEqual(person.perspective, PERSPECTIVE_THIRD)
        self.assertEqual((person.subject, person.object, person.possessive), ("he", "him", "his"))
        self.assertEqual(how_works_heading(person), "How Avdey works")
        self.assertEqual(how_thinks_heading(person), "How Avdey thinks")
        self.assertEqual(mars_section_heading("how_you_start", person), "How he starts")
        self.assertEqual(mars_section_heading("compensations", person), "What helps him work better")

    def test_female_structured_field_uses_she_her(self):
        person = build_person_perspective(name="Avdey", sex="female")
        self.assertEqual((person.subject, person.object, person.possessive), ("she", "her", "her"))
        self.assertEqual(how_works_heading(person), "How Avdey works")
        self.assertEqual(mars_section_heading("how_you_start", person), "How she starts")
        self.assertEqual(mars_section_heading("work_rhythm", person), "Her work rhythm")

    def test_explicit_neutral_uses_they(self):
        person = build_person_perspective(name="Sam", sex="they/them")
        self.assertEqual((person.subject, person.object, person.possessive), ("they", "them", "their"))
        self.assertEqual(mars_section_heading("how_you_start", person), "How they start")

    def test_unknown_does_not_guess_from_name(self):
        person = build_person_perspective(name="Avdey")
        self.assertEqual(person.sex, "unknown")
        self.assertEqual((person.subject, person.object, person.possessive), ("they", "them", "their"))
        self.assertNotEqual(person.subject, "he")
        self.assertEqual(normalize_sex(None), "unknown")
        self.assertEqual(normalize_sex(""), "unknown")
        self.assertEqual(normalize_sex("Avdey"), "unknown")

    def test_self_perspective_uses_you_your(self):
        person = build_person_perspective(name="", perspective=PERSPECTIVE_SELF)
        self.assertEqual((person.subject, person.object, person.possessive), ("you", "you", "your"))
        self.assertEqual(how_works_heading(person), "How you work")
        self.assertEqual(how_thinks_heading(person), "How you think")
        named_self = build_person_perspective(
            name="Avdey",
            sex="male",
            perspective=PERSPECTIVE_SELF,
        )
        self.assertEqual(named_self.subject, "you")
        self.assertEqual(how_works_heading(named_self), "How you work")

    def test_templates_have_no_hardcoded_avdey(self):
        blob = " ".join(
            item.display_template
            for item in (*EXECUTION_TEMPLATES, *SLOWDOWN_TEMPLATES, *PRESSURE_TEMPLATES)
        ).lower()
        self.assertNotIn("avdey", blob)
        self.assertNotIn("{he}", blob)

    def test_recruiter_glance_rendering_preserves_semantics(self):
        person = build_person_perspective(name="Avdey", sex="male")
        cards = {card.key: card for card in build_mars_work_glance(_synthesis())}
        execution = render_mars_glance_text(cards["execution_style"], person)
        slowdown = render_mars_glance_text(cards["what_may_slow_you_down"], person)
        pressure = render_mars_glance_text(cards["under_pressure"], person)
        self.assertEqual(
            execution,
            "Avdey tends to work in a deliberate and calculated way, with strong focus on the task.",
        )
        self.assertEqual(
            slowdown,
            "He may hesitate or feel an internal brake before fully committing to action.",
        )
        self.assertEqual(
            pressure,
            "Under pressure, he may take on too much or push himself into overwork.",
        )
        self.assertEqual(render_mars_glance_title(cards["what_may_slow_you_down"], person), "What may slow him down")
        self.assertNotIn("you", execution.lower())
        self.assertNotIn("your", slowdown.lower())
        unknown = build_person_perspective(name="Avdey")
        unknown_slow = render_mars_glance_text(cards["what_may_slow_you_down"], unknown)
        self.assertTrue(unknown_slow.startswith("They may"))
        self.assertNotIn("He may", unknown_slow)

    def test_fill_helper_self_slots(self):
        person = build_person_perspective(perspective=PERSPECTIVE_SELF)
        text = fill_person_template("{They} may hesitate before {their} next step.", person)
        self.assertEqual(text, "You may hesitate before your next step.")
        self.assertEqual(possessive_name(person), "Your")
        named = build_person_perspective(name="Alex", sex="female")
        self.assertEqual(possessive_name(named), "Alex's")
        self.assertEqual(
            fill_person_template("{NamePossessive} analytical thinking can pair with planned execution.", named),
            "Alex's analytical thinking can pair with planned execution.",
        )
        james = build_person_perspective(name="James")
        self.assertEqual(possessive_name(james), "James'")


if __name__ == "__main__":
    unittest.main()
