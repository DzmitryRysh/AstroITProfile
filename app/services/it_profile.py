from dataclasses import dataclass

@dataclass(frozen=True)
class ITProfile:
    score: int
    archetype: str
    strengths: list[str]
    risks: list[str]
    notes: str


SUN_SIGN_TO_IT = {
    "Aries": (78, "Product-Driven Builder",
              ["initiative", "speed", "risk-taking"],
              ["impatience", "burnout risk"],
              "High drive: good for fast-paced product work."),
    "Taurus": (74, "Reliable Systems Engineer",
               ["stability", "consistency", "long-term focus"],
               ["resistance to change"],
               "Strong for systems that require reliability and patience."),
    "Gemini": (76, "Polyglot Problem Solver",
               ["learning fast", "communication", "context switching"],
               ["scattered focus"],
               "Great for roles with varied tasks and communication."),
    "Virgo": (82, "Quality & Process Specialist",
              ["attention to detail", "debugging", "documentation"],
              ["perfectionism"],
              "Excellent for QA-minded engineering and clean backend work."),
    "Capricorn": (84, "Strategic Architect",
                  ["discipline", "planning", "ownership"],
                  ["overwork", "rigidity"],
                  "Strong for backend, architecture, and long-term projects."),
    "Aquarius": (80, "Innovative Technologist",
                 ["systems thinking", "original ideas", "future-oriented"],
                 ["detachment", "over-idealizing"],
                 "Great for R&D, architecture, and experimental tech."),
    "Pisces": (70, "Creative Product Thinker",
               ["empathy", "creativity", "user focus"],
               ["lack of structure"],
               "Good for UX-heavy product areas with strong guidance."),

}

def build_it_profile(*, sun_sign: str) -> ITProfile:
    score, archetype, strengths, risks, notes = SUN_SIGN_TO_IT.get(
        sun_sign,
        (72, "Balanced Engineer",
         ["adaptability", "learning mindset"],
         ["needs clearer structure"],
         "General profile: suitable for IT with the right direction.")
    )
    return ITProfile(score=score, archetype=archetype, strengths=strengths, risks=risks, notes=notes)
