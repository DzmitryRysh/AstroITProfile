from dataclasses import dataclass
from app.services.astro_calc import calc_mercury_sign


@dataclass(frozen=True)
class ITProfile:
    score: int
    archetype: str
    strengths: list[str]
    risks: list[str]
    notes: str


SUN_SIGN_TO_IT = {
"Aries": (
        78,
        "Product-Driven Builder",
        ["initiative", "speed", "risk-taking"],
        ["impatience", "burnout risk"],
        "High energy and drive — strong fit for fast-moving product teams."
    ),
    "Taurus": (
        74,
        "Reliable Systems Engineer",
        ["stability", "consistency", "long-term focus"],
        ["resistance to change"],
        "Great for systems requiring reliability and persistence."
    ),
    "Gemini": (
        76,
        "Polyglot Problem Solver",
        ["fast learning", "communication", "context switching"],
        ["scattered focus"],
        "Well-suited for roles with diverse tasks and collaboration."
    ),
    "Cancer": (
        72,
        "Supportive Team Engineer",
        ["empathy", "team care", "responsibility"],
        ["overprotectiveness"],
        "Strong in team-oriented environments and long-term products."
    ),
    "Leo": (
        80,
        "Technical Leader",
        ["confidence", "ownership", "influence"],
        ["ego clashes"],
        "Naturally fits leadership or lead engineer paths."
    ),
    "Virgo": (
        82,
        "Quality & Process Specialist",
        ["attention to detail", "debugging", "documentation"],
        ["perfectionism"],
        "Excellent for clean backend systems and quality-focused work."
    ),
    "Libra": (
        75,
        "Architecture Mediator",
        ["balance", "design sense", "decision support"],
        ["indecisiveness"],
        "Good at designing balanced systems and APIs."
    ),
    "Scorpio": (
        81,
        "Deep Systems Analyst",
        ["focus", "investigation", "security mindset"],
        ["over-intensity"],
        "Strong fit for security, backend, and deep technical domains."
    ),
    "Sagittarius": (
        77,
        "Exploring Technologist",
        ["vision", "learning", "adaptability"],
        ["lack of routine"],
        "Thrives in innovation-heavy and exploratory roles."
    ),
    "Capricorn": (
        84,
        "Strategic Architect",
        ["discipline", "planning", "ownership"],
        ["overwork", "rigidity"],
        "Excellent for architecture and long-term responsibility."
    ),
    "Aquarius": (
        80,
        "Innovative Technologist",
        ["systems thinking", "original ideas", "future orientation"],
        ["detachment"],
        "Great for R&D and non-standard technical solutions."
    ),
    "Pisces": (
        70,
        "Creative Product Thinker",
        ["empathy", "creativity", "user focus"],
        ["lack of structure"],
        "Good fit for UX-driven and product-focused roles."
    ),
}

MERCURY_TO_THINKING = {
    "Aries": (
        3,
        ["fast decision making", "initiative"],
        ["impulsiveness"],
    ),
    "Taurus": (
        2,
        ["consistent thinking", "reliability"],
        ["slowness in switching context"],
    ),
    "Gemini": (
        5,
        ["quick learning", "multi-tasking"],
        ["context overload"],
    ),
    "Cancer": (
        2,
        ["intuitive understanding", "team empathy"],
        ["emotional bias"],
    ),
    "Leo": (
        3,
        ["confident communication", "presentation skills"],
        ["overconfidence"],
    ),
    "Virgo": (
        6,
        ["analytical thinking", "clean code"],
        ["overthinking"],
    ),
    "Libra": (
        3,
        ["system design balance", "architectural sense"],
        ["indecision"],
    ),
    "Scorpio": (
        5,
        ["deep focus", "problem investigation"],
        ["obsessiveness"],
    ),
    "Sagittarius": (
        4,
        ["big-picture thinking", "learning drive"],
        ["lack of detail"],
    ),
    "Capricorn": (
        4,
        ["structured thinking", "planning"],
        ["rigidity"],
    ),
    "Aquarius": (
        5,
        ["abstract thinking", "innovation"],
        ["detachment"],
    ),
    "Pisces": (
        2,
        ["creative thinking", "intuition"],
        ["lack of structure"],
    ),
}


def build_it_profile(*, sun_sign: str, is_day: bool, mercury_sign: str) -> ITProfile:
    score, archetype, strengths, risks, notes = SUN_SIGN_TO_IT.get(
        sun_sign,
        (72, "Balanced Engineer",
         ["adaptability", "learning mindset"],
         ["needs clearer structure"],
         "General profile: suitable for IT with the right direction.")
    )
    score_delta = 0
    extra_strengths: list[str] = []

    if is_day:
        score_delta += 3
        extra_strengths.append("team-oriented work style")
    else:
        score_delta += 5
        extra_strengths.append("deep focus and analytical thinking")

    score = min(100,score + score_delta)
    strengths = strengths + extra_strengths
    m_score, m_strengths, m_risks = MERCURY_TO_THINKING.get(
        mercury_sign,
        (0, [], [])
    )

    score = min(100, score + m_score)
    strengths = strengths + m_strengths
    risks = risks + m_risks

    return ITProfile(
        score=score,
        archetype=archetype,
        strengths=strengths,
        risks=risks,
        notes=notes,
    )

