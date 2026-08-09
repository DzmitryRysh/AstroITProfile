"""Mercury Work Profile interpretation rules (milestone 2).

Element + sign + retrograde modifier only.
House, aspect, and dispositor interpretation are intentionally absent.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MercuryElementRule:
    thinking_type: str
    thinking: str
    communication: str


@dataclass(frozen=True)
class MercurySignRule:
    thinking: str
    learning: str
    communication: str
    strengths: tuple[str, ...]
    risks: tuple[str, ...]
    team_value: str
    possible_roles: tuple[str, ...]


@dataclass(frozen=True)
class MercuryRetrogradeRule:
    thinking: str
    learning: str
    communication: str
    strengths: tuple[str, ...]
    risks: tuple[str, ...]


ELEMENT_RULES: dict[str, MercuryElementRule] = {
    "fire": MercuryElementRule(
        thinking_type="Impulsive / Creative",
        thinking=(
            "Processes information through flashes, ideas and images. "
            "Tends to see the idea first and details later."
        ),
        communication=(
            "Expressive, confident, energetic; may speak quickly or interrupt."
        ),
    ),
    "earth": MercuryElementRule(
        thinking_type="Practical / Applied",
        thinking=(
            "Processes information sequentially through facts, experience and "
            "practical evidence. Step by step."
        ),
        communication=(
            "Measured, concrete, practical and generally focused on useful results."
        ),
    ),
    "air": MercuryElementRule(
        thinking_type="Logical / Abstract",
        thinking=(
            "Processes information quickly through connections, concepts and "
            "systems. Can handle many pieces of information at once."
        ),
        communication=(
            "Verbal, explanatory, connected; tends to communicate information easily."
        ),
    ),
    "water": MercuryElementRule(
        thinking_type="Emotional / Image-Based",
        thinking=(
            "Processes through feelings, associations, images and intuition. "
            "Less linear; information may form as impressions rather than a strict sequence."
        ),
        communication=(
            "Emotionally colored and contextual; logical sequencing may sometimes "
            "be less explicit."
        ),
    ),
}


SIGN_RULES: dict[str, MercurySignRule] = {
    "Aries": MercurySignRule(
        thinking=(
            "Thinking is fast, immediate, and often impulsive: an answer appears quickly. "
            "This style is strong at detecting weak points in another person's logic. "
            "It may become hasty or inattentive, and may defend an existing theory even "
            "when new facts challenge it."
        ),
        learning=(
            "Learns best through debate, proving a position, competition, and hands-on "
            "practice that applies knowledge immediately."
        ),
        communication=(
            "Communication is direct and easily becomes argumentative. Discussion can "
            "turn into debate, and active listening may drop when a position is already "
            "being defended."
        ),
        strengths=(
            "Rapid Problem Response",
            "Argument Analysis",
            "Weak-Point Detection",
            "Action-Based Learning",
            "Direct Communication",
        ),
        risks=(
            "Hasty Conclusions",
            "Weak Fact Verification",
            "Poor Active Listening",
            "Conflict Escalation",
            "Acting Before Discussion Is Complete",
        ),
        team_value=(
            "Potential Challenger / Rapid Problem Solver. "
            "Can be useful where the team needs speed, challenge, direct feedback "
            "and someone willing to attack weak logic."
        ),
        possible_roles=(
            "Incident Response",
            "Technical Troubleshooting",
            "Fast Prototyping",
            "Technical Review / Challenge",
            "High-pressure execution environments",
        ),
    ),
    "Taurus": MercurySignRule(
        thinking=(
            "Thinking is deliberate, grounded, practical, and thorough. Prefers "
            "trustworthy facts, tends to verify information, and may process more "
            "slowly while retaining learned material well. Abstract material may "
            "require more effort."
        ),
        learning=(
            "Learns best with enough time to absorb material, independent preparation, "
            "practical application, a comfortable stable environment, and a clear "
            "practical benefit."
        ),
        communication=(
            "Communication is measured, structured, and calm. Tends to think before "
            "speaking and wants conversation to lead to a useful result."
        ),
        strengths=(
            "Practical Reasoning",
            "Information Verification",
            "Knowledge Retention",
            "Deliberate Decision Support",
            "Applied Learning",
        ),
        risks=(
            "Slow Context Switching",
            "Cognitive Inertia",
            "Difficulty Adapting Quickly to Rapidly Changing Information",
        ),
        team_value=(
            "Can bring grounding, verification, consistency and practical judgment."
        ),
        possible_roles=(
            "Quality / Validation",
            "Stable Backend or Systems Work",
            "Data Operations",
            "Implementation requiring consistency",
            "Documentation / process-heavy technical work",
        ),
    ),
    "Gemini": MercurySignRule(
        thinking=(
            "Thinking is logical and highly information-oriented, with very fast "
            "working-memory processing across many information streams. Moves from "
            "parts toward the whole and may sometimes miss the overall picture; "
            "quantity of information may exceed depth."
        ),
        learning=(
            "Learns well through dialogue, lectures, books, teachers, groups, and "
            "exchanging information with several people."
        ),
        communication=(
            "Communication is strongly contact-oriented. Can explain high abstractions "
            "in simple language, hear multiple people in a group, and handle negotiation "
            "or commercial discussion."
        ),
        strengths=(
            "Fast Information Processing",
            "Rapid Learning",
            "Technical Explanation",
            "Negotiation",
            "Multi-Context Communication",
            "Information Connecting",
        ),
        risks=(
            "Information Overload",
            "Scattered Attention",
            "Loss of Depth",
            "Boredom With One Long Topic",
            "Too Many Parallel Threads",
        ),
        team_value=(
            "Potential Connector / Communicator. "
            "Useful for connecting people, information and different technical contexts."
        ),
        possible_roles=(
            "Solutions Engineering",
            "Technical Consulting",
            "Integrations",
            "Developer Relations",
            "Technical Support / Escalation",
            "Product–Engineering Communication",
        ),
    ),
    "Cancer": MercurySignRule(
        thinking=(
            "Connects ideas with past experience and roots. Imagination and associative "
            "processing are strong; arguments may arise intuitively and be difficult to "
            "verbalize. Thought can be influenced by emotional context."
        ),
        learning=(
            "Learns best when material is divided into smaller segments, using associations, "
            "images, and emotional memory, in a calm comfortable environment. Authority or "
            "tradition may help."
        ),
        communication=(
            "Communication carries emotion and is sensitive to conversational atmosphere. "
            "Can improvise based on context, but may find it difficult to express an "
            "intuitive thought clearly."
        ),
        strengths=(
            "Contextual Thinking",
            "Associative Memory",
            "Emotional Context Recognition",
            "Pattern Recall",
            "Context-Sensitive Communication",
        ),
        risks=(
            "Subjectivity",
            "Reduced Focus Under Emotional Load",
            "Difficulty Structuring Complex Thoughts Verbally",
            "Getting Lost in Details or Associations",
        ),
        team_value=(
            "Can contribute memory, context, sensitivity to atmosphere and "
            "understanding of how information connects with prior experience."
        ),
        possible_roles=(
            "User / Problem Discovery",
            "Knowledge and Context Management",
            "Customer-facing technical support",
            "Domain Analysis",
            "Context-heavy product work",
        ),
    ),
    "Leo": MercurySignRule(
        thinking=(
            "Tends toward monologue and pays attention to audience effect. Presentation "
            "is creative and non-standard; information is naturally reshaped into a personal "
            "creative form. May remain attached to own views even after recognizing problems."
        ),
        learning=(
            "Learns through presenting, standing out, vivid or engaging delivery, and "
            "creatively reworking information."
        ),
        communication=(
            "Communication is expressive, presentation-oriented, and authoritative in tone. "
            "Impression may be prioritized over precision, and competing opinions may not "
            "be fully heard."
        ),
        strengths=(
            "Presentation",
            "Idea Advocacy",
            "Creative Reframing",
            "Public Explanation",
            "Persuasive Delivery",
        ),
        risks=(
            "Resistance to Admitting Error",
            "Weak Listening",
            "Presentation Over Substance",
            "Overattachment to Own Interpretation",
        ),
        team_value=(
            "Can help communicate, present and champion an idea and give information "
            "a memorable form."
        ),
        possible_roles=(
            "Developer Advocacy",
            "Technical Presentation",
            "Product Evangelism",
            "Technical Training / Demonstration",
            "Client-facing concept presentation",
        ),
    ),
    "Virgo": MercurySignRule(
        thinking=(
            "Thinking is selective, analytical, and detail-focused, with strong logic after "
            "preparation and emotionally cool analysis. Tactical thinking is strong; strategy "
            "may be lost inside details."
        ),
        learning=(
            "Learns through practice, notes, algorithms, diagrams, tables, methodologies, "
            "and compiling and comparing information."
        ),
        communication=(
            "Communication uses precise formulations, asks for clarification, stays practical "
            "and simple, and tends to document observations and statistics."
        ),
        strengths=(
            "Precision Analysis",
            "Detail Verification",
            "Data Observation",
            "Methodical Problem Solving",
            "Debugging",
            "Documentation",
            "Statistical Discipline",
        ),
        risks=(
            "Micromanagement",
            "Losing the Big Picture",
            "Overfocus on Routine",
            "Excessive Detail",
        ),
        team_value=(
            "Potential Precision Analyst / Validator. "
            "Useful where accuracy, errors, data quality and methodical examination matter."
        ),
        possible_roles=(
            "QA / Testing",
            "Data Analysis",
            "Model Evaluation",
            "Debugging",
            "Data Quality",
            "Validation / Compliance-oriented technical work",
        ),
    ),
    "Libra": MercurySignRule(
        thinking=(
            "Thinking is fast and receptive. Understands through comparison and discussion, "
            "naturally sees several sides, synthesizes contradictory viewpoints, and evaluates "
            "intellectual constructions for balance and completeness."
        ),
        learning=(
            "Learns through dialogue, exchange of opinions, books, lectures, teacher or peer "
            "interaction, and solving difficult tasks with another person."
        ),
        communication=(
            "Communication is diplomatic, peaceful, and adaptable to the conversational partner. "
            "Synthesizes information well and is oriented toward fairness and agreement."
        ),
        strengths=(
            "Negotiation",
            "Perspective Integration",
            "Diplomatic Communication",
            "Consensus Building",
            "Information Synthesis",
        ),
        risks=(
            "Indecision",
            "Endless Weighing of Alternatives",
            "Avoidance of Necessary Conflict",
            "Difficulty Taking a Firm Position",
        ),
        team_value=(
            "Potential Mediator / Integrator. "
            "Useful where several people, departments or viewpoints must be reconciled."
        ),
        possible_roles=(
            "Solutions Consulting",
            "Business / Systems Analysis",
            "Product–Engineering Bridge",
            "Stakeholder Coordination",
            "Cross-team Integration",
        ),
    ),
    "Scorpio": MercurySignRule(
        thinking=(
            "Thinking is categorical and maximalist, with deep persistent memory and highly "
            "analytical focus. Detects non-verbal or hidden information, searches for essence, "
            "and investigates by breaking a problem apart to understand it."
        ),
        learning=(
            "Learns through deep investigation, independent study in a quiet environment, "
            "practical exploration, finding vulnerabilities or errors, questioning or debate "
            "to reveal essence, and working with deep concepts."
        ),
        communication=(
            "Communication is intense and probing, with many questions. Answers can be sharp; "
            "meaning may come through hints. The drive is to get beneath the surface."
        ),
        strengths=(
            "Deep Investigation",
            "Root-Cause Analysis",
            "Vulnerability Detection",
            "Analytical Depth",
            "Research Persistence",
            "Hidden-Pattern Detection",
        ),
        risks=(
            "Excessive Criticality",
            "Harsh Judgments",
            "Over-investigation",
            "Suspicion",
            "Communication Intensity",
        ),
        team_value=(
            "Potential Investigator. "
            "Useful where the team needs someone to dig beneath the obvious answer, "
            "find vulnerabilities and understand root causes."
        ),
        possible_roles=(
            "Security Research",
            "Root-Cause Investigation",
            "Complex Debugging",
            "Fraud / Anomaly Analysis",
            "Forensics",
            "Deep Research",
        ),
    ),
    "Sagittarius": MercurySignRule(
        thinking=(
            "Thinking is categorical, global, and large-scale. Asks why, searches for meaning, "
            "and sees the general idea before simple concrete detail. The intellectual approach "
            "can be non-standard. Moving from theory to practice is difficult, and precision or "
            "calculations may be neglected."
        ),
        learning=(
            "Learns by teaching or passing knowledge to others, working with university-level "
            "or encyclopedic material, understanding why the knowledge matters, and having a "
            "clear goal."
        ),
        communication=(
            "Communication is philosophical, ideological, and teaching-oriented. Concepts are "
            "communicated from the top down and may sound like a lecture rather than a dialogue. "
            "Ideas or people may be labeled too quickly."
        ),
        strengths=(
            "Big-Picture Thinking",
            "Conceptual Thinking",
            "Strategic Synthesis",
            "Meaning / Purpose Orientation",
            "Knowledge Teaching",
            "Non-standard Concept Generation",
        ),
        risks=(
            "Detail Neglect",
            "Precision Errors",
            "Theory-to-Practice Gap",
            "Weak Listening",
            "Intolerance of Competing Ideas",
            "Overgeneralization",
        ),
        team_value=(
            "Potential Conceptualizer / Explorer. "
            "Useful for seeing direction, framing the larger problem, exploring ideas "
            "and explaining why a system or project matters."
        ),
        possible_roles=(
            "R&D",
            "Technical Strategy",
            "Architecture Exploration",
            "Technology Research",
            "Technical Education",
            "Problem Framing",
        ),
    ),
    "Capricorn": MercurySignRule(
        thinking=(
            "Thinking is clearly structured, concrete, businesslike, scientific, highly logical, "
            "and concise. Looks for the core principle and prefers one task or one thought at a "
            "time. Information intake may be slower."
        ),
        learning=(
            "Learns by understanding purpose and sequence through systems, tables, schedules, "
            "plans, structure, notes, algorithms, diagrams, and clear indicators."
        ),
        communication=(
            "Communication is formal, concise, calm, and critical, based on common sense and "
            "verified authoritative information, and is not rushed."
        ),
        strengths=(
            "Structured Reasoning",
            "Algorithmic Thinking",
            "Technical Planning",
            "Sequential Execution Thinking",
            "Critical Review",
            "Systems Organization",
        ),
        risks=(
            "Rigidity",
            "Slow Intake of New Information",
            "Difficulty Changing an Established View",
            "Limited Communication Flexibility",
        ),
        team_value=(
            "Can bring structure, sequence, planning and disciplined technical reasoning."
        ),
        possible_roles=(
            "Backend / Systems Engineering",
            "Platform / Infrastructure",
            "MLOps",
            "Technical Planning",
            "Production Engineering",
            "Architecture Implementation",
        ),
    ),
    "Aquarius": MercurySignRule(
        thinking=(
            "Thinking is idealistic, global, and independent. Draws knowledge from many domains, "
            "rapidly explores many alternatives, and uses a strong abstract, insight-oriented "
            "style with good memory. Cognitive rhythm can be unusual."
        ),
        learning=(
            "Learns through books, lectures, groups, discussion, and independent study, and can "
            "handle large amounts of information quickly."
        ),
        communication=(
            "Communication is democratic and informal. Can speak extemporaneously on many topics; "
            "expression may be unpredictable or mood-dependent."
        ),
        strengths=(
            "Abstract Reasoning",
            "Rapid Pattern Exploration",
            "Alternative Solution Generation",
            "Cross-Domain Thinking",
            "Innovation",
            "Fast Information Exploration",
        ),
        risks=(
            "Scattered Attention",
            "Low Patience",
            "Lack of Systematic Follow-through",
            "Rapid Loss of Interest",
            "Insufficient Concrete Detail",
        ),
        team_value=(
            "Potential Explorer / Innovator. "
            "Useful where the team needs alternatives, emerging technology, "
            "experimentation and unconventional approaches."
        ),
        possible_roles=(
            "AI / ML Research",
            "R&D",
            "Emerging Technology",
            "Experimental Engineering",
            "Architecture Exploration",
            "Innovation / Prototyping",
        ),
    ),
    "Pisces": MercurySignRule(
        thinking=(
            "Perceives impression and image rather than only fact. Highly imaginative, intuitive, "
            "and non-linear; searches for hidden meaning. Can be suggestible and may reach "
            "conclusions through associations that are difficult to explain."
        ),
        learning=(
            "Learns through video and images, listening and absorbing, intuitive impression, "
            "solitude, and creative reinterpretation."
        ),
        communication=(
            "Communication is calm, emotional, and contextual, using images, metaphors, and "
            "indirect expression. A clear central line may be missing. Sensitive to subtext and tone."
        ),
        strengths=(
            "Imaginative Thinking",
            "Intuitive Association",
            "Context Sensitivity",
            "Metaphorical Explanation",
            "Creative Reframing",
            "Subtext Recognition",
        ),
        risks=(
            "Fuzzy Central Idea",
            "Fact / Interpretation Confusion",
            "Suggestibility",
            "Low Communication Structure",
            "Difficulty Keeping Expression Concrete",
        ),
        team_value=(
            "Can contribute imaginative reframing, intuitive connections, context and "
            "sensitivity to subtle information."
        ),
        possible_roles=(
            "Creative Technology / Product Concept",
            "UX / Experience-oriented technical work",
            "Visual or conceptual problem framing",
            "Creative prototyping",
            "Human-centered product exploration",
        ),
    ),
}


RETROGRADE_RULE = MercuryRetrogradeRule(
    thinking=(
        "Processing turns more inward and may take longer. Problems may be solved "
        "through unconventional paths, with a tendency to revisit and rethink material."
    ),
    learning=(
        "Learning is supported by repetition, revisiting previous material, and rewriting "
        "or reprocessing in own words. The path may be more individual and non-standard."
    ),
    communication=(
        "Written expression may be easier or stronger than spontaneous speech. Complex "
        "thoughts benefit from internal processing before speaking."
    ),
    strengths=(
        "Reflective Thinking",
        "Reprocessing and Refinement",
        "Unconventional Problem Solving",
    ),
    risks=(
        "Slower Spontaneous Response",
        "Verbal Expression May Lag Behind Internal Thought",
    ),
)


SIGN_UNAVAILABLE_LIMITATION = (
    "Interpretation omitted because Mercury sign is unavailable; no guess was made."
)
