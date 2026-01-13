# AstroIT Profile 🪐💻
**Astrology-driven career & technical aptitude profiling for IT professionals**

AstroIT Profile is an experimental analytics engine that maps **astrological career indicators** to **IT roles, technical strengths, risks, and growth paths**.

The project does **not** aim to replace traditional assessments (CVs, interviews, coding tests).  
Instead, it adds a **symbolic + structural layer** that helps explain:

- How a person naturally thinks in technical systems  
- Where their career energy is best expressed  
- Why certain IT roles feel natural or exhausting  
- What long-term technical growth path fits them best  

---

## Core Idea

AstroIT Profile translates **classical and modern astrology** into **clear, readable IT-oriented insights**.

Instead of vague horoscopes, the system works with:
- Houses (career, work style, visibility)
- Planetary rulers
- Technical planets (Mercury, Uranus, Saturn)
- Weighted scoring
- Explicit logic and explainable output

This makes astrology usable as a **decision-support tool**, not mysticism.

---

## What the Profile Includes

### 1. IT Fit Score (0–100)

A weighted score representing **technical alignment with IT work**, based on:

- Uranus (technology, innovation)
- Mercury (thinking style)
- 10th house (career axis)
- 6th house (daily work style)
- Career ruler bonuses
- Key aspects (advanced layer)

The score is **capped, calibrated, and explainable**.

---

### 2. Personality Style Archetype (Sun)

A **recognition layer** — how the person tends to express themselves.

Examples:
- Deep Systems Analyst  
- Strategic Architect  
- Innovative Technologist  

This layer supports **self-identification**, not career prediction.

---

### 3. IT Archetype (Career-Driven)

The **main professional archetype**, derived from:
- 10th house sign (MC)
- Ruler of the 10th house
- Ruler’s house placement

Examples:
- Public / Visible Research Engineer  
- Platform Futurist  
- Architecture-Focused Engineer  

This answers:
**“What role fits me long-term in IT?”**

---

### 4. Career Axis Block (Key Feature)

A dedicated structured block describing **career realization**.

Includes:
- Career theme (visibility, research, platforms, leadership, etc.)
- Plain-English summary
- Role hints
- Core factors:
  - MC sign
  - Main ruler
  - Ruler sign & house
- Career-related aspects
- Aspect score bonuses

This block is designed for **frontend visualization**.

---

### 5. Technical Mind (Mercury ↔ Uranus)

A special block detecting **aspects between Mercury and Uranus**.

Describes:
- Non-linear thinking
- Innovation style
- How technical insights arise
- Where the mind thrives (R&D, automation, architecture, security)

Each aspect includes:
- Aspect type
- Orb
- Impact (support / tension)
- Score bonus
- Title, explanation, and advice

---

### 6. Strengths & Risks

Human-readable lists generated from all active factors.

**Strengths** examples:
- systems thinking
- security mindset
- learning drive

**Risks** examples:
- over-intensity
- skipping details
- burnout tendency

---

### 7. Transparent Notes

Each profile includes a **debug-style explanation**:
- What contributed to the score
- Which bonuses were applied
- Which planets and houses mattered most

This keeps the system **auditable and honest**.

---

## Architecture Overview

**Backend**
- Python
- FastAPI
- Swiss Ephemeris (`swisseph`)

**Structure**
- `astro_calc` — planetary positions & houses
- `it_profile` — scoring logic
- `career_axis` — career interpretation
- `aspects` — aspect detection & scoring
- `technical_mind` — Mercury–Uranus logic
- `astro_service` — orchestration layer

All blocks are **modular and replaceable**.

---

## Current Status

- Core MVP implemented
- Career Axis logic complete
- Ruler bonuses implemented
- Aspect system (Level 2) live
- Technical Mind block live
- Stable API output

Frontend is planned next.

---

## Target Audience

- IT professionals & engineers  
- Career switchers into tech  
- Founders & indie hackers  
- Career coaches / HR innovators  
- Astrology-aware users who want structure  

---

## Roadmap

- Saturn & architecture depth
- Team compatibility profiles
- Money-focused project (MoneyCompass)
- Frontend dashboard
- Paid API / B2B integrations

---

## Disclaimer

AstroIT Profile is an **exploratory decision-support system**.  
It does not claim absolute truth and should not be used as the sole basis for life or career decisions.
