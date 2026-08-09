"""Mercury Work Profile interpretation rules.

Milestone 2: element + sign + retrograde.
Milestone 3: house context + supported aspect modifiers.
Dispositor interpretation is intentionally absent.
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


@dataclass(frozen=True)
class MercuryHouseRule:
    themes: frozenset[str]
    thinking: str = ""
    learning: str = ""
    communication: str = ""
    team_value: str = ""
    thinking_reinforce: str = ""
    learning_reinforce: str = ""
    communication_reinforce: str = ""
    team_value_reinforce: str = ""
    strengths: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()


@dataclass(frozen=True)
class MercuryAspectRule:
    themes: frozenset[str]
    thinking: str = ""
    learning: str = ""
    communication: str = ""
    thinking_reinforce: str = ""
    learning_reinforce: str = ""
    communication_reinforce: str = ""
    communication_if_talkative: str = ""
    strengths: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()


SIGN_THEMES: dict[str, frozenset[str]] = {
    "Aries": frozenset({"fast_response", "haste", "listening", "conflict", "direct", "talkative"}),
    "Taurus": frozenset({"practical", "slow", "verify"}),
    "Gemini": frozenset({"fast_processing", "contact", "scattered", "negotiation", "talkative", "overload"}),
    "Cancer": frozenset({"context", "emotion", "private"}),
    "Leo": frozenset({"presentation", "talkative", "listening"}),
    "Virgo": frozenset({"detail", "method", "precision"}),
    "Libra": frozenset({"diplomacy", "negotiation", "talkative"}),
    "Scorpio": frozenset({"investigation", "depth", "sharp", "suspicion", "over_dig"}),
    "Sagittarius": frozenset({"conceptual", "theory", "teaching", "abstraction", "talkative", "precision_gap"}),
    "Capricorn": frozenset({"structure", "formal", "slow"}),
    "Aquarius": frozenset({"abstract", "scattered", "talkative", "innovation"}),
    "Pisces": frozenset({"imagination", "fog", "context", "fact_assumption"}),
}

TALKATIVE_THEMES = frozenset({"talkative", "contact"})

LABEL_THEME: dict[str, str] = {
    "Rapid Problem Response": "fast_response",
    "Fast Mental Response": "fast_response",
    "Rapid Learning": "rapid_learning",
    "Diplomatic Communication": "diplomacy",
    "Negotiation": "negotiation",
    "Presentation": "presentation",
    "Deep Investigation": "deep_investigation",
    "Hasty Conclusions": "haste",
    "Hasty Action": "haste",
    "Poor Active Listening": "listening",
    "Poor Listening Under Pressure": "listening",
    "Weak Listening": "listening",
    "Conflict Escalation": "conflict",
    "Conflict-Prone Communication": "conflict",
    "Information Overload": "overload",
    "Scattered Attention": "scattered",
    "Fragmented Attention": "scattered",
    "Fact / Interpretation Confusion": "fact_assumption",
    "Fact-Assumption Confusion": "fact_assumption",
    "Over-investigation": "over_dig",
    "Over-Fixation": "over_dig",
    "Suspicion": "suspicion",
    "Suspicion Bias": "suspicion",
}


HOUSE_RULES: dict[int, MercuryHouseRule] = {
    1: MercuryHouseRule(
        themes=frozenset({"fast_response", "talkative", "scattered"}),
        learning=(
            "Learning tends to happen through fast adaptation, active curiosity, "
            "and quick trial rather than long private preparation."
        ),
        communication=(
            "Communication is more visible and spontaneous, with quick reactions and quick wit."
        ),
        team_value=(
            "Useful where the team needs initiative and a fast, visible verbal response."
        ),
        learning_reinforce=(
            "The already quick style is further pulled toward fast adaptation and trying ideas out loud."
        ),
        communication_reinforce=(
            "Spontaneous, visible communication is even more likely; finishing one thread before starting the next needs attention."
        ),
        strengths=("Fast Adaptation", "Active Communication"),
        risks=(
            "Restlessness / Fussiness",
            "Starting Without Finishing",
            "Excessive Talking / Scattered Activity",
        ),
    ),
    2: MercuryHouseRule(
        themes=frozenset({"practical"}),
        learning=(
            "Information work tends to connect with practical value and usable outcomes."
        ),
        communication=(
            "Communication often sits in a commercial, persuasive, or written-information context "
            "where usefulness matters."
        ),
        team_value=(
            "Can help where analysis or explanation needs to become practically usable."
        ),
        strengths=("Commercial Communication", "Practical Information Use"),
        risks=(
            "Superficial Decisions",
            "Overconfidence in Practical Reasoning",
        ),
    ),
    3: MercuryHouseRule(
        themes=frozenset({"fast_processing", "contact", "scattered"}),
        learning=(
            "The working context strongly supports contact-based learning: switching information "
            "streams, writing or languages, useful questions, tactical thinking, dialogue, "
            "feedback, and group learning."
        ),
        communication=(
            "Dialogue, writing, and rapid information switching are close to daily work."
        ),
        team_value=(
            "Useful in high-contact learning and short-cycle information exchange."
        ),
        learning_reinforce=(
            "The already information-oriented style is further supported by dialogue, writing, "
            "and switching between streams; attention can disperse if contacts multiply."
        ),
        strengths=(
            "Rapid Learning",
            "Written Communication",
            "Tactical Problem Solving",
            "Information Switching",
        ),
        risks=(
            "Too Many Contacts / Information Streams",
            "Dispersion of Attention",
        ),
    ),
    4: MercuryHouseRule(
        themes=frozenset({"private", "context"}),
        learning=(
            "Thinking and learning tend to be strongest in familiar or private settings, "
            "including independent study and work with a smaller trusted circle. Interest "
            "often goes to background, history, or origins of information."
        ),
        communication=(
            "Communication is often more effective with a smaller trusted circle than in constant public exposure."
        ),
        team_value=(
            "Contributes more in private, focused, or context-heavy settings than in always-on visibility."
        ),
        strengths=("Independent Study", "Contextual Memory"),
        risks=("Communication May Remain Too Private",),
    ),
    5: MercuryHouseRule(
        themes=frozenset({"presentation", "teaching"}),
        learning=(
            "The context favors enjoyment of learning and intellectually creative reworking of material."
        ),
        communication=(
            "Ideas are often explained publicly or creatively through writing, speaking, or presentation."
        ),
        team_value=(
            "Useful where learning needs to be made engaging or publicly explainable."
        ),
        communication_reinforce=(
            "The already presentation-oriented style has more room for creative public explanation; "
            "substance still needs to stay ahead of performance."
        ),
        strengths=("Creative Communication", "Presentation", "Educational Creativity"),
        risks=("Over-Intellectualizing Creative or Emotional Situations",),
    ),
    6: MercuryHouseRule(
        themes=frozenset({"method", "detail", "precision"}),
        learning=(
            "The work context is operational and methodical: high information-processing load, "
            "routine or process thinking, and many small tasks."
        ),
        communication=(
            "Professional, process-oriented communication is part of daily execution."
        ),
        team_value=(
            "Useful where information must be handled methodically under workload."
        ),
        learning_reinforce=(
            "The already methodical style is further pulled into operational workload and small-task volume; "
            "priority can be lost inside minor problems."
        ),
        strengths=(
            "Process Thinking",
            "Operational Communication",
            "Methodical Information Handling",
        ),
        risks=(
            "Grabbing Too Many Small Tasks",
            "Losing Priority to Minor Problems",
            "Excessive Micro-Focus",
        ),
    ),
    7: MercuryHouseRule(
        themes=frozenset({"negotiation", "diplomacy", "conflict"}),
        learning=(
            "Thinking improves through dialogue, feedback, negotiation, and exchange with another person."
        ),
        communication=(
            "One-to-one exchange, compromise, and perspective-taking are central to how ideas develop."
        ),
        team_value=(
            "Useful where work depends on dialogue, feedback, and negotiated clarity."
        ),
        communication_reinforce=(
            "In one-to-one exchange, an already direct or conflict-prone style can become more argumentative; "
            "feedback still sharpens thinking."
        ),
        strengths=("Dialogue", "Negotiation", "Perspective Exchange"),
        risks=("Argumentativeness in Conflict-Prone Exchange",),
    ),
    8: MercuryHouseRule(
        themes=frozenset({"investigation", "depth", "sharp", "over_dig"}),
        thinking=(
            "This thinking style tends to become especially engaged in deep investigation, "
            "hidden dependencies, and complex information."
        ),
        learning=(
            "Learning favors intensive concentration, research, and uncovering what is not obvious."
        ),
        communication=(
            "Verbal influence can be strong; wording may become sharp when probing hidden problems."
        ),
        team_value=(
            "Useful where the team needs someone willing to stay with complex or non-obvious information."
        ),
        thinking_reinforce=(
            "The already investigative style is further engaged by hidden dependencies and complex information; "
            "this is a working context, not a job title."
        ),
        communication_reinforce=(
            "Probing communication can escalate tension if wording stays too sharp."
        ),
        strengths=("Deep Investigation", "Research Thinking", "Hidden-Pattern Analysis"),
        risks=(
            "Excessively Sharp Wording",
            "Communication Tension Escalation",
            "Over-Fixation on Hidden Problems",
        ),
    ),
    9: MercuryHouseRule(
        themes=frozenset({"conceptual", "theory", "abstraction", "teaching"}),
        thinking=(
            "Analysis tends to combine with abstraction: meaningful information is filtered, "
            "and arguments or conceptual justification matter."
        ),
        learning=(
            "The working context favors higher learning, theory, languages or broad knowledge, "
            "and conceptual justification."
        ),
        communication=(
            "Discussion often wants the larger argument, not only local detail."
        ),
        team_value=(
            "Useful where theory, knowledge synthesis, and conceptual framing are part of the work."
        ),
        thinking_reinforce=(
            "The already conceptual baseline has more room for theory, abstraction, and knowledge synthesis; "
            "precision weaknesses remain."
        ),
        learning_reinforce=(
            "Higher-learning and theoretical settings further support this style; detail verification is still required."
        ),
        strengths=("Conceptual Learning", "Theory Integration", "Knowledge Filtering"),
        risks=(
            "Excessive Abstraction / Formality",
            "Over-Processing Unnecessary Information",
        ),
    ),
    10: MercuryHouseRule(
        themes=frozenset({"formal", "presentation"}),
        learning=(
            "Large information volumes are often handled in a professional, publicly visible setting."
        ),
        communication=(
            "Intellect and communication tend to be visible in professional life; reputation can "
            "become linked with knowledge or information."
        ),
        team_value=(
            "Knowledge and communication may sit close to professional visibility."
        ),
        strengths=("Professional Communication", "Knowledge Leadership"),
        risks=(
            "Status Can Distort Curiosity",
            "Direction Changes Until Work Is Intellectually and Professionally Meaningful",
        ),
    ),
    11: MercuryHouseRule(
        themes=frozenset({"contact", "talkative"}),
        learning=(
            "Learning tends to happen through teams and networks: teaching and learning from others, "
            "exchanging ideas, and collaborative intellectual work."
        ),
        communication=(
            "Idea exchange in a group or network setting is a natural channel."
        ),
        team_value=(
            "Useful in collaborative, network, or idea-exchange settings."
        ),
        learning_reinforce=(
            "The already contact-oriented style is further supported by team and network learning; "
            "debate can become endless if ideas stay speculative."
        ),
        strengths=("Collaborative Learning", "Idea Exchange", "Team Knowledge Sharing"),
        risks=(
            "Endless Debate",
            "Too Many Speculative Ideas or Projects",
        ),
    ),
    12: MercuryHouseRule(
        themes=frozenset({"private", "internal", "fog"}),
        thinking=(
            "Strongest processing may happen internally or alone, especially with ambiguous "
            "information or hidden meanings."
        ),
        learning=(
            "Independent, self-paced learning and private research fit this context; ideas are "
            "often formulated better after internal processing."
        ),
        communication=(
            "Spontaneous public expression can be harder; useful ideas may stay private too long."
        ),
        team_value=(
            "Contributes more through internal processing and private deep work than through immediate public speech."
        ),
        thinking_reinforce=(
            "Internal or private processing is further emphasized; assumptions still need explicit verification."
        ),
        strengths=("Independent Deep Work", "Internal Processing"),
        risks=(
            "Difficult Spontaneous Public Expression",
            "Useful Ideas Kept Private Too Long",
            "Assumptions Replacing Explicit Verification",
        ),
    ),
}


_sun_conjunction = MercuryAspectRule(
    themes=frozenset({"listening", "talkative"}),
    communication=(
        "Speech can become more self-monitored, with concern about how words are received, "
        "and a swing between taking conversational space and holding back."
    ),
    risks=("Self-Critical Communication", "Public Expression Friction"),
)

_venus_conjunction = MercuryAspectRule(
    themes=frozenset({"diplomacy"}),
    communication=(
        "Attention to others' approval or reaction increases, which can make it harder to "
        "say no or risk offence."
    ),
    strengths=("Social Awareness",),
    risks=("Approval-Seeking Communication", "Difficulty Setting Verbal Boundaries"),
)

_venus_harmonious = MercuryAspectRule(
    themes=frozenset({"diplomacy"}),
    communication=(
        "Tact and socially smoother, more diplomatic expression come more easily."
    ),
    communication_reinforce=(
        "An already diplomatic style has more ease with tact; agreement-seeking can still delay a firm position."
    ),
    strengths=("Diplomatic Communication", "Tactful Expression"),
)

_moon_tense = MercuryAspectRule(
    themes=frozenset({"emotion"}),
    thinking=(
        "Emotion competes with reasoning; thinking becomes more subjective under emotional "
        "load, and decisions can depend heavily on mood."
    ),
    thinking_reinforce=(
        "Emotional context already shapes thinking; under load, mood can further compete with cooler reasoning."
    ),
    risks=("Mood-Dependent Reasoning", "Emotional Decision Noise"),
)

_mars_tense = MercuryAspectRule(
    themes=frozenset({"haste", "listening", "conflict", "fast_response"}),
    thinking=(
        "Thoughts convert rapidly into action. Impatience, haste, and sharper words increase; "
        "interrupting, arguing, or incomplete listening is more likely, and conflict or nervous "
        "fuss can appear under pressure."
    ),
    thinking_reinforce=(
        "The already fast, action-oriented processing style is further pushed toward immediate "
        "response under pressure, which can intensify haste, conflict, and incomplete listening."
    ),
    communication=(
        "Wording can become sharper; interrupting or arguing is more likely when pressure rises."
    ),
    communication_reinforce=(
        "Under pressure, wording can get sharper and listening can drop further."
    ),
    strengths=("Fast Mental Response",),
    risks=(
        "Hasty Action",
        "Poor Listening Under Pressure",
        "Conflict-Prone Communication",
    ),
)

_mars_harmonious = MercuryAspectRule(
    themes=frozenset({"fast_response", "direct"}),
    thinking=(
        "Thought and action connect efficiently: faster, sharper analytical response and an "
        "easier time talking, learning, and doing at once."
    ),
    communication=(
        "Expression can be persuasive and direct without as much friction between idea and execution."
    ),
    strengths=(
        "Fast Analytical Response",
        "Thought-to-Action Execution",
        "Persuasive Direct Communication",
    ),
)

_jupiter_tense = MercuryAspectRule(
    themes=frozenset({"overload", "abstraction"}),
    thinking=(
        "Too many ideas, plans, or information streams can inflate the scale of work, start "
        "too much, and lose the central point through long explanation or learning overload."
    ),
    thinking_reinforce=(
        "The already wide information intake can inflate scope further; the central message "
        "needs active protection."
    ),
    communication=(
        "Explanation may run long and lose the core message."
    ),
    risks=("Information Overload", "Scope Inflation", "Loss of Core Message"),
)

_jupiter_harmonious = MercuryAspectRule(
    themes=frozenset({"diplomacy", "talkative"}),
    communication=(
        "Socially engaging, diplomatically confident conversation comes more easily."
    ),
    strengths=("Engaging Communication",),
)

_saturn_tense = MercuryAspectRule(
    themes=frozenset({"guarded", "inhibit"}),
    communication=(
        "Fear of saying the wrong thing can inhibit speech, replay errors, feed negative "
        "thought loops, and produce silence when communication is needed."
    ),
    communication_if_talkative=(
        "Internal processing can stay quick and information-oriented, but external speech "
        "becomes more guarded, self-censored, or blocked when the cost of a wrong word feels high."
    ),
    learning=(
        "Learning may be slowed by fear of error and by replaying mistakes."
    ),
    risks=("Communication Inhibition", "Error Rumination", "Fear-Based Learning"),
)

_uranus_tense = MercuryAspectRule(
    themes=frozenset({"scattered", "innovation"}),
    thinking=(
        "Thoughts jump rapidly through unconventional associations and sudden insights, "
        "with high novelty orientation and difficulty staying on one topic."
    ),
    thinking_reinforce=(
        "The already novelty-oriented or multi-stream style jumps even faster; staying on one "
        "topic needs deliberate containment."
    ),
    strengths=("Non-Linear Problem Solving", "Unexpected Insight"),
    risks=("Fragmented Attention", "Mental Overstimulation"),
)

_neptune_tense = MercuryAspectRule(
    themes=frozenset({"imagination", "fog", "fact_assumption"}),
    thinking=(
        "Thoughts may become diffuse; imagination can mix with facts, making it harder to "
        "distinguish assumption from verified information. Explicit verification criteria "
        "and written facts help."
    ),
    thinking_reinforce=(
        "Imagination already shapes conclusions; verification criteria and written facts are "
        "needed so assumption does not pass as evidence."
    ),
    strengths=("Imaginative Association",),
    risks=("Mental Fog", "Fact-Assumption Confusion"),
)

_pluto_tense = MercuryAspectRule(
    themes=frozenset({"investigation", "over_dig", "suspicion", "sharp"}),
    thinking=(
        "Focus goes very deep, with a drive to keep digging for hidden causes; mental "
        "fixation, suspicion, and verbal pressure can increase."
    ),
    thinking_reinforce=(
        "The already investigative style digs further; fixation, suspicion, and verbal pressure "
        "can intensify without turning this into a job title."
    ),
    strengths=("Deep Investigation",),
    risks=("Over-Fixation", "Suspicion Bias", "Mental Pressure"),
)

ASPECT_RULES: dict[tuple[str, str], MercuryAspectRule] = {
    ("Sun", "conjunction"): _sun_conjunction,
    ("Venus", "conjunction"): _venus_conjunction,
    ("Venus", "trine"): _venus_harmonious,
    ("Venus", "sextile"): _venus_harmonious,
    ("Moon", "square"): _moon_tense,
    ("Moon", "opposition"): _moon_tense,
    ("Mars", "conjunction"): _mars_tense,
    ("Mars", "square"): _mars_tense,
    ("Mars", "opposition"): _mars_tense,
    ("Mars", "trine"): _mars_harmonious,
    ("Mars", "sextile"): _mars_harmonious,
    ("Jupiter", "square"): _jupiter_tense,
    ("Jupiter", "opposition"): _jupiter_tense,
    ("Jupiter", "trine"): _jupiter_harmonious,
    ("Jupiter", "sextile"): _jupiter_harmonious,
    ("Saturn", "conjunction"): _saturn_tense,
    ("Saturn", "square"): _saturn_tense,
    ("Saturn", "opposition"): _saturn_tense,
    ("Uranus", "conjunction"): _uranus_tense,
    ("Uranus", "square"): _uranus_tense,
    ("Uranus", "opposition"): _uranus_tense,
    ("Neptune", "conjunction"): _neptune_tense,
    ("Neptune", "square"): _neptune_tense,
    ("Neptune", "opposition"): _neptune_tense,
    ("Pluto", "conjunction"): _pluto_tense,
    ("Pluto", "square"): _pluto_tense,
    ("Pluto", "opposition"): _pluto_tense,
}

ASPECT_APPLY_ORDER = (
    "Sun",
    "Moon",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
)


def get_aspect_rule(planet: str, aspect_type: str) -> MercuryAspectRule | None:
    return ASPECT_RULES.get((planet, aspect_type))

