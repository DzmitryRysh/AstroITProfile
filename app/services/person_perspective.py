"""Reusable person/perspective copy for recruiter and self views.

Presentation-only. Never infers sex or pronouns from a person's name.
"""

from __future__ import annotations

from dataclasses import dataclass

PERSPECTIVE_SELF = "self"
PERSPECTIVE_THIRD = "third_person"

SEX_MALE = "male"
SEX_FEMALE = "female"
SEX_NEUTRAL = "neutral"
SEX_UNKNOWN = "unknown"

_MALE_VALUES = frozenset({"male", "m", "he", "him", "he/him"})
_FEMALE_VALUES = frozenset({"female", "f", "she", "her", "she/her"})
_NEUTRAL_VALUES = frozenset({"neutral", "they", "them", "they/them", "nonbinary", "non-binary"})


@dataclass(frozen=True)
class PersonPerspective:
    name: str
    perspective: str
    sex: str
    subject: str
    object: str
    possessive: str
    possessive_independent: str
    reflexive: str

    @property
    def subject_cap(self) -> str:
        return self.subject[:1].upper() + self.subject[1:]

    @property
    def possessive_cap(self) -> str:
        return self.possessive[:1].upper() + self.possessive[1:]

    @property
    def uses_plural_verb(self) -> bool:
        return self.subject in {"they", "you"}


def normalize_sex(value: str | None) -> str:
    """Map a structured sex/pronoun field. Empty or unknown stays unknown."""
    token = str(value or "").strip().lower()
    if token in _MALE_VALUES:
        return SEX_MALE
    if token in _FEMALE_VALUES:
        return SEX_FEMALE
    if token in _NEUTRAL_VALUES:
        return SEX_NEUTRAL
    return SEX_UNKNOWN


def build_person_perspective(
    *,
    name: str = "",
    sex: str | None = None,
    perspective: str | None = None,
) -> PersonPerspective:
    """Build pronoun forms from name + optional structured sex.

    Named recruiter views default to third person. Empty name defaults to self.
    Sex is never derived from the name string.
    """
    trimmed = str(name or "").strip()
    resolved_perspective = perspective or (
        PERSPECTIVE_THIRD if trimmed else PERSPECTIVE_SELF
    )
    if resolved_perspective not in {PERSPECTIVE_SELF, PERSPECTIVE_THIRD}:
        resolved_perspective = PERSPECTIVE_THIRD if trimmed else PERSPECTIVE_SELF
    resolved_sex = normalize_sex(sex)

    if resolved_perspective == PERSPECTIVE_SELF:
        subject, obj, poss, independent, reflexive = (
            "you",
            "you",
            "your",
            "yours",
            "yourself",
        )
    elif resolved_sex == SEX_MALE:
        subject, obj, poss, independent, reflexive = (
            "he",
            "him",
            "his",
            "his",
            "himself",
        )
    elif resolved_sex == SEX_FEMALE:
        subject, obj, poss, independent, reflexive = (
            "she",
            "her",
            "her",
            "hers",
            "herself",
        )
    else:
        subject, obj, poss, independent, reflexive = (
            "they",
            "them",
            "their",
            "theirs",
            "themselves",
        )

    return PersonPerspective(
        name=trimmed,
        perspective=resolved_perspective,
        sex=resolved_sex,
        subject=subject,
        object=obj,
        possessive=poss,
        possessive_independent=independent,
        reflexive=reflexive,
    )


def possessive_name(person: PersonPerspective) -> str:
    """Possessive page/person label. Never inferred from the name string's gender."""
    if person.perspective == PERSPECTIVE_SELF or not person.name:
        return "Your"
    name = person.name.strip()
    if name.lower().endswith("s"):
        return f"{name}'"
    return f"{name}'s"


def fill_person_template(template: str, person: PersonPerspective) -> str:
    """Fill {name}/{NamePossessive}/{They}/{they}/{them}/{their}/{theirs}/{themself} slots."""
    name = person.name or person.subject_cap
    return (
        template.replace("{NamePossessive}", possessive_name(person))
        .replace("{name}", name)
        .replace("{They}", person.subject_cap)
        .replace("{they}", person.subject)
        .replace("{them}", person.object)
        .replace("{their}", person.possessive)
        .replace("{theirs}", person.possessive_independent)
        .replace("{themself}", person.reflexive)
    )


def contextualize_neutral_sentence(text: str, person: PersonPerspective) -> str:
    """Attach a pronoun to a leading 'May ...' observation without 'He May'."""
    stripped = str(text or "").strip()
    if stripped.lower().startswith("may "):
        rest = stripped[4:]
        if rest:
            rest = rest[0].lower() + rest[1:]
        return f"{person.subject_cap} may {rest}"
    return stripped


def present_verb(person: PersonPerspective, base: str, singular: str) -> str:
    return base if person.uses_plural_verb else singular


def how_thinks_heading(person: PersonPerspective) -> str:
    if person.perspective == PERSPECTIVE_SELF or not person.name:
        return "How you think"
    return f"How {person.name} thinks"


def how_works_heading(person: PersonPerspective) -> str:
    if person.perspective == PERSPECTIVE_SELF or not person.name:
        return "How you work"
    return f"How {person.name} works"


def mars_section_heading(key: str, person: PersonPerspective) -> str | None:
    """Person-aware Mars headings. None means keep the existing neutral title."""
    they = person.subject
    them = person.object
    their_cap = person.possessive_cap
    if key == "how_you_start":
        return f"How {they} {present_verb(person, 'start', 'starts')}"
    if key == "how_you_execute":
        return f"How {they} {present_verb(person, 'execute', 'executes')}"
    if key == "work_rhythm":
        return f"{their_cap} work rhythm"
    if key == "when_you_get_stuck":
        return f"When {they} {present_verb(person, 'get', 'gets')} stuck"
    if key == "how_you_handle_obstacles":
        return f"How {they} {present_verb(person, 'handle', 'handles')} obstacles"
    if key == "compensations":
        return f"What helps {them} work better"
    return None


def mars_glance_title(key: str, person: PersonPerspective, fallback: str = "") -> str:
    if key == "execution_style":
        return "Execution style"
    if key == "what_may_slow_you_down":
        return f"What may slow {person.object} down"
    if key == "under_pressure":
        return "Under pressure"
    return fallback
