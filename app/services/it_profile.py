from dataclasses import dataclass
import swisseph as swe
from typing import Optional



@dataclass(frozen=True)
class ITProfile:
    score: int
    personality_style_archetype: str
    it_archetype: str
    strengths: list[str]
    risks: list[str]
    notes: str


SUN_SIGN_TO_IT = {
"Aries": (
        0,
        "Product-Driven Builder",
        ["initiative", "speed", "risk-taking"],
        ["impatience", "burnout risk"],
        "High energy and drive — strong fit for fast-moving product teams."
    ),
    "Taurus": (
        0,
        "Reliable Systems Engineer",
        ["stability", "consistency", "long-term focus"],
        ["resistance to change"],
        "Great for systems requiring reliability and persistence."
    ),
    "Gemini": (
        0,
        "Polyglot Problem Solver",
        ["fast learning", "communication", "context switching"],
        ["scattered focus"],
        "Well-suited for roles with diverse tasks and collaboration."
    ),
    "Cancer": (
        0,
        "Supportive Team Engineer",
        ["empathy", "team care", "responsibility"],
        ["overprotectiveness"],
        "Strong in team-oriented environments and long-term products."
    ),
    "Leo": (
        0,
        "Technical Leader",
        ["confidence", "ownership", "influence"],
        ["ego clashes"],
        "Naturally fits leadership or lead engineer paths."
    ),
    "Virgo": (
        0,
        "Quality & Process Specialist",
        ["attention to detail", "debugging", "documentation"],
        ["perfectionism"],
        "Excellent for clean backend systems and quality-focused work."
    ),
    "Libra": (
        0,
        "Architecture Mediator",
        ["balance", "design sense", "decision support"],
        ["indecisiveness"],
        "Good at designing balanced systems and APIs."
    ),
    "Scorpio": (
        0,
        "Deep Systems Analyst",
        ["focus", "investigation", "security mindset"],
        ["over-intensity"],
        "Strong fit for security, backend, and deep technical domains."
    ),
    "Sagittarius": (
        0,
        "Exploring Technologist",
        ["vision", "learning", "adaptability"],
        ["lack of routine"],
        "Thrives in innovation-heavy and exploratory roles."
    ),
    "Capricorn": (
        0,
        "Strategic Architect",
        ["discipline", "planning", "ownership"],
        ["overwork", "rigidity"],
        "Excellent for architecture and long-term responsibility."
    ),
    "Aquarius": (
        0,
        "Innovative Technologist",
        ["systems thinking", "original ideas", "future orientation"],
        ["detachment"],
        "Great for R&D and non-standard technical solutions."
    ),
    "Pisces": (
        0,
        "Creative Product Thinker",
        ["empathy", "creativity", "user focus"],
        ["lack of structure"],
        "Good fit for UX-driven and product-focused roles."
    ),
}

MERCURY_TO_THINKING = {
    "Aries": (3, ["decisive thinking", "fast decisions"], ["impatience"],
              "Mercury in Aries: fast, direct, action-oriented mind."),
    "Taurus": (2, ["stable logic", "practical mindset"], ["stubbornness"],
               "Mercury in Taurus: consistent, grounded, pragmatic thinking."),
    "Gemini": (5, ["quick learning", "multitasking"], ["scattered focus"],
               "Mercury in Gemini: fast switching, curiosity, strong communication."),
    "Cancer": (2, ["memory", "context sensitivity"], ["subjectivity"],
               "Mercury in Cancer: intuitive, context-based thinking, strong recall."),
    "Leo": (3, ["confident expression", "presentation skill"], ["ego bias"],
            "Mercury in Leo: expressive, persuasive, leadership communication."),
    "Virgo": (5, ["detail focus", "analysis", "debug mindset"], ["overthinking"],
              "Mercury in Virgo: analytical, precise, engineering-grade thinking."),
    "Libra": (3, ["balanced reasoning", "negotiation"], ["indecision"],
              "Mercury in Libra: structured comparison, UX/product-friendly reasoning."),
    "Scorpio": (4, ["deep analysis", "security mindset"], ["obsession"],
                "Mercury in Scorpio: investigative, depth-first, threat-model mindset."),
    "Sagittarius": (3, ["big-picture thinking", "learning drive"], ["lack of detail"],
                    "Mercury in Sagittarius: big-picture, theory-first, loves learning."),
    "Capricorn": (4, ["systems thinking", "planning"], ["rigidity"],
                  "Mercury in Capricorn: structured, architectural, long-term planning."),
    "Aquarius": (4, ["innovative thinking", "abstract systems"], ["detachment"],
                 "Mercury in Aquarius: unconventional, systems-level, future-oriented thinking."),
    "Pisces": (3, ["pattern intuition", "creative synthesis"], ["fuzziness"],
               "Mercury in Pisces: intuitive synthesis, creative connections, less linear logic."),
}

URANUS_HOUSE_TO_IT = {
    1: (
        14,
        ["independent tech identity", "self-directed learning", "builder mindset"],
        ["rebelliousness", "difficulty with rigid rules"],
        "Uranus in 1st: strong individual tech drive and autonomy."
    ),
    6: (
        18,
        ["automation mindset", "process optimization", "engineering routine"],
        ["restlessness in repetitive work"],
        "Uranus in 6th: daily work thrives on optimization and tooling."
    ),
    10: (
        20,
        ["career tech leadership", "public technical role", "ambition through innovation"],
        ["pressure to prove competence"],
        "Uranus in 10th: technology becomes a career axis and status driver."
    ),
    11: (
        16,
        ["systems/network thinking", "platform/community orientation", "team innovation"],
        ["detachment from emotions"],
        "Uranus in 11th: strong fit for platforms, communities, and large systems."
    ),
}


HOUSE6_SIGN_TO_WORKSTYLE = {
    "Aries": (
        ["fast execution", "initiative", "ship-first mindset"],
        ["burnout from постоянных спринтов", "impatience with slow processes"],
        "6th house Aries: daily mode = 'push to prod and ask questions later' "
    ),
    "Taurus": (
        ["stability", "reliable routines", "strong ops discipline"],
        ["resistance to sudden changes", "slow to refactor"],
        "6th house Taurus: daily mode = 'stable uptime guardian' ️"
    ),
    "Gemini": (
        ["context switching", "quick troubleshooting", "communication"],
        ["scattered focus", "too many tabs open (literally)"],
        "6th house Gemini: daily mode = 'human load balancer' "
    ),
    "Cancer": (
        ["care for team", "attention to context", "strong memory"],
        ["takes feedback personally", "mood-driven productivity"],
        "6th house Cancer: daily mode = 'team’s emotional DevOps' "
    ),
    "Leo": (
        ["ownership", "presentation skill", "lead by example"],
        ["ego clashes", "overpromising"],
        "6th house Leo: daily mode = 'tech lead energy without the title' "
    ),
    "Virgo": (
        ["precision", "debug mindset", "process optimization"],
        ["overthinking", "perfectionism"],
        "6th house Virgo: daily mode = 'linting reality itself' "
    ),
    "Libra": (
        ["balanced decisions", "clean collaboration", "good UX sense"],
        ["indecision", "too much consensus"],
        "6th house Libra: daily mode = 'PR diplomat' "
    ),
    "Scorpio": (
        ["deep focus", "investigation", "security instincts"],
        ["over-intensity", "paranoia about edge cases"],
        "6th house Scorpio: daily mode = 'logs whisperer / incident detective' "
    ),
    "Sagittarius": (
        ["learning drive", "big-picture thinking", "exploration"],
        ["lack of detail", "skips boring steps"],
        "6th house Sagittarius: daily mode = 'research sprint enjoyer' "
    ),
    "Capricorn": (
        ["discipline", "architecture thinking", "long-term planning"],
        ["rigidity", "too serious about process"],
        "6th house Capricorn: daily mode = 'SRE with a calendar' "
    ),
    "Aquarius": (
        ["innovation", "systems thinking", "automation love"],
        ["detachment", "rebellion vs legacy"],
        "6th house Aquarius: daily mode = 'automation anarchist' "
    ),
    "Pisces": (
        ["creative solutions", "pattern intuition", "empathy"],
        ["fuzzy boundaries", "hard to estimate tasks"],
        "6th house Pisces: daily mode = 'fixes bugs by vibes (and it works)' "
    ),
}

HOUSE10_SIGN_TO_CAREER = {
    "Aries": (
        "Backend Astronaut",
        ["leadership drive", "ownership", "build from scratch"],
        ["conflicts with hierarchy"],
        "10th house Aries: career = 'first into the unknown' "
    ),
    "Taurus": (
        "Infrastructure Guardian",
        ["reliability", "systems stability", "steady growth"],
        ["can get stuck in comfort zone"],
        "10th house Taurus: career = 'makes systems boring (in a good way)' "
    ),
    "Gemini": (
        "API Storyteller",
        ["communication", "product sense", "integration skills"],
        ["scattered career direction"],
        "10th house Gemini: career = 'connects everything to everything' "
    ),
    "Cancer": (
        "Team Anchor Engineer",
        ["mentoring", "support culture", "context keeping"],
        ["over-caring / burnout"],
        "10th house Cancer: career = 'builds teams as much as code' "
    ),
    "Leo": (
        "Tech Lead Performer",
        ["visibility", "presentation", "guiding others"],
        ["ego traps"],
        "10th house Leo: career = 'the one people listen to in incidents' "
    ),
    "Virgo": (
        "Quality Assassin",
        ["engineering excellence", "testing mindset", "clean code"],
        ["perfectionism slows shipping"],
        "10th house Virgo: career = 'turns chaos into checklists' "
    ),
    "Libra": (
        "Product-API Diplomat",
        ["cross-team alignment", "architecture tradeoffs", "design sense"],
        ["decision paralysis"],
        "10th house Libra: career = 'wins by making everyone agree' "
    ),
    "Scorpio": (
        "Security Systems Analyst",
        ["investigation", "threat modeling", "deep systems"],
        ["over-control"],
        "10th house Scorpio: career = 'goes deep where others fear to debug' "
    ),
    "Sagittarius": (
        "Research Engineer",
        ["learning", "exploration", "big vision"],
        ["skips details"],
        "10th house Sagittarius: career = 'maps the future stack' "
    ),
    "Capricorn": (
        "Architecture Manager (without the MBA)",
        ["structure", "planning", "scalable systems"],
        ["rigidity / bureaucracy"],
        "10th house Capricorn: career = 'builds ladders, not hacks' "
    ),
    "Aquarius": (
        "Platform Futurist",
        ["innovation", "distributed systems", "community tech"],
        ["detachment"],
        "10th house Aquarius: career = 'ships tomorrow’s infrastructure' "
    ),
    "Pisces": (
        "Creative Integrator",
        ["intuition", "creative synthesis", "human-centered tech"],
        ["unclear boundaries"],
        "10th house Pisces: career = 'glues worlds together' "
    ),
}


def build_it_profile(
    *,
    sun_sign: str,
    is_day: bool,
    mercury_sign: str,
    uranus_house: int,
    house_6_sign: str,
    house_10_sign: str,
    main_ruler_name: str,
    main_ruler_sign: str,
    main_ruler_house: int,
    co_ruler_name: Optional[str] = None,
    co_ruler_sign: Optional[str] = None,
    co_ruler_house: Optional[int] = None,
) -> ITProfile:

    # ---- 0) Sun is STYLE only (NO score impact) ----
    sun_base = SUN_SIGN_TO_IT.get(
        sun_sign,
        (
            0,
            "Balanced Engineer",
            ["adaptability", "learning mindset"],
            ["needs clearer structure"],
            "General profile: suitable for IT with the right direction.",
        ),
    )
    _unused, personality_style_archetype, strengths, risks, notes = sun_base

    # day/night -> narrative only
    if is_day:
        strengths = strengths + ["team-oriented work style"]
        notes = f"{notes} | Day chart: energy is more externally expressed."
    else:
        strengths = strengths + ["deep focus potential"]
        notes = f"{notes} | Night chart: energy is more internal and focused."

    # ---- 1) Mercury block (0..100) ----
    m_points, m_strengths, m_risks, m_notes = MERCURY_TO_THINKING.get(
        mercury_sign,
        (2, [], [], "Mercury: default practical thinking."),
    )
    mercury_score = mercury_points_to_score(int(m_points))
    strengths = strengths + m_strengths
    risks = risks + m_risks
    notes = f"{notes} | {m_notes}"

    # ---- 2) Uranus block (0..100) ----
    allowed = {1, 6, 10, 11}
    if uranus_house not in allowed:
        uranus_house = 0

    if uranus_house:
        u_points, u_strengths, u_risks, u_note = URANUS_HOUSE_TO_IT[uranus_house]
        strengths = strengths + u_strengths
        risks = risks + u_risks
        notes = f"{notes} | {u_note}"

    uranus_score = URANUS_HOUSE_TO_SCORE.get(uranus_house, DEFAULT_URANUS_SCORE)

    # ---- 3) House 6 block (soft) ----
    h6_strengths, h6_risks, h6_note = HOUSE6_SIGN_TO_WORKSTYLE.get(
        house_6_sign, ([], [], f"6th house {house_6_sign}: daily style noted.")
    )
    strengths += h6_strengths
    risks += h6_risks
    notes = f"{notes} | {h6_note}"
    workstyle_score = HOUSE6_SIGN_TO_SCORE.get(house_6_sign, DEFAULT_HOUSE_SCORE)

    # ---- 4) House 10 block (soft) ----
    arch, h10_strengths, h10_risks, h10_note = HOUSE10_SIGN_TO_CAREER.get(
        house_10_sign,
        ("Backend Astronaut", [], [], f"10th house {house_10_sign}: career style noted."),
    )

    it_archetype = arch
    strengths += h10_strengths
    risks += h10_risks
    notes = f"{notes} | {h10_note}"
    career_score = HOUSE10_SIGN_TO_SCORE.get(house_10_sign, DEFAULT_HOUSE_SCORE)


    # ---- 5) Final weighted score (0..100) ----
    tech_signature = (
        0.45 * uranus_score +
        0.35 * mercury_score +
        0.10 * career_score +
        0.10 * workstyle_score
    )

    score = clamp_0_100(tech_signature)

    # clean duplicates (optional but nice)
    strengths = list(dict.fromkeys(strengths))
    risks = list(dict.fromkeys(risks))

    # debug note to validate calibration
    notes = (
        f"{notes} | Scores: Uranus={uranus_score}, Mercury={mercury_score}, "
        f"Career(10H)={career_score}, Workstyle(6H)={workstyle_score} -> Total={score}"
    )

    ruler_info = f"10H rulers: main={main_ruler_name} in {main_ruler_sign} (H{main_ruler_house})"
    if co_ruler_name:
        ruler_info += f"; co={co_ruler_name} in {co_ruler_sign} (H{co_ruler_house})"
    notes = f"{notes} | {ruler_info}"

    def ruler_prefix(house_num: int) -> str:
        if house_num == 1:
            return "Public / Visible"
        if house_num == 10:
            return "Career Axis"
        if house_num == 11:
            return "Network / Platform"
        if house_num == 6:
            return "Craft / Skill Builder"
        return "Strategic"

    it_archetype = f"{ruler_prefix(main_ruler_house)} {it_archetype}"

    return ITProfile(
        score=score,
        personality_style_archetype=personality_style_archetype,
        it_archetype=it_archetype,
        strengths=strengths,
        risks=risks,
        notes=notes,
    )


# Uranus block: only house-based for MVP
URANUS_HOUSE_TO_SCORE = {
    1: 60,
    6: 68,
    10: 75,
    11: 72,
}
DEFAULT_URANUS_SCORE = 50

# Mercury thinking block: map your 0..5 points into a 0..100-ish score
def mercury_points_to_score(points: int) -> int:
    # points is 0..5
    # 0 -> 55, 5 -> 75
    return max(0, min(100, 55 + points * 4))

# House signs as "soft modifiers" (not too strong)
HOUSE6_SIGN_TO_SCORE = {
    "Virgo": 70,
    "Capricorn": 68,
    "Scorpio": 66,
    "Aquarius": 66,
    "Gemini": 64,
    "Aries": 62,
    "Taurus": 60,
    "Libra": 60,
    "Cancer": 58,
    "Leo": 58,
    "Sagittarius": 58,
    "Pisces": 56,
}
HOUSE10_SIGN_TO_SCORE = {
    "Capricorn": 70,
    "Aquarius": 68,
    "Virgo": 68,
    "Scorpio": 66,
    "Aries": 64,
    "Gemini": 64,
    "Taurus": 62,
    "Libra": 62,
    "Leo": 60,
    "Cancer": 60,
    "Sagittarius": 60,
    "Pisces": 58,
}
DEFAULT_HOUSE_SCORE = 60

SIGN_TO_RULER_TRADITIONAL = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

# Modern rulerships: useful for tech-oriented interpretation
SIGN_TO_RULER_MODERN = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Pluto",      # (often Mars co-ruler)
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Uranus",    # key for IT
    "Pisces": "Neptune",     # (often Jupiter co-ruler)
}

# Optional: co-rulers to keep both worlds (nice for explanation text)
SIGN_TO_CO_RULER = {
    "Scorpio": "Mars",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

PLANET_NAME_TO_SWE = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
}


def clamp_0_100(x: float) -> int:
    return int(max(0, min(100, round(x))))


def get_10h_rulers(mc_sign: str) -> tuple[str, str | None]:
    main = SIGN_TO_RULER_MODERN.get(mc_sign)
    if not main:
        main = SIGN_TO_RULER_TRADITIONAL.get(mc_sign, "Saturn")

    co = SIGN_TO_CO_RULER.get(mc_sign)
    return main, co
