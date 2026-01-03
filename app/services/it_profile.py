from dataclasses import dataclass


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


def build_it_profile(*, sun_sign: str, is_day: bool,
                     mercury_sign: str,
                     uranus_house: int,
                     house_6_sign: str,
                     house_10_sign: str) -> ITProfile:

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

    m_score, m_strengths, m_risks, m_notes = MERCURY_TO_THINKING.get(
        mercury_sign,
        (0, [], [],"")
    )

    score = min(100, score + m_score)
    strengths = strengths + m_strengths
    risks = risks + m_risks
    notes = f"{notes} | {m_notes}"

    allowed = {1, 6, 10, 11}
    if uranus_house not in allowed:
        uranus_house = 0

    if uranus_house:
        u_score, u_strengths, u_risks, u_note = URANUS_HOUSE_TO_IT[uranus_house]
        score = min(100, score + u_score)
        strengths = strengths + u_strengths
        risks = risks + u_risks
        notes = f"{notes} | {u_note}"


    # --- 6th house: daily work style ---
    h6_strengths, h6_risks, h6_note = HOUSE6_SIGN_TO_WORKSTYLE.get(
        house_6_sign, ([], [], f"6th house {house_6_sign}: daily style noted.")
    )
    strengths += h6_strengths
    risks += h6_risks
    notes = f"{notes} | {h6_note}"

    # --- 10th house: career direction / archetype ---
    arch, h10_strengths, h10_risks, h10_note = HOUSE10_SIGN_TO_CAREER.get(
        house_10_sign, ("Backend Astronaut", [], [], f"10th house {house_10_sign}: career style noted.")
    )

    archetype = f"{archetype} / {arch}"

    strengths += h10_strengths
    risks += h10_risks
    notes = f"{notes} | {h10_note}"


    return ITProfile(
        score=score,
        archetype=archetype,
        strengths=strengths,
        risks=risks,
        notes=notes,
    )

