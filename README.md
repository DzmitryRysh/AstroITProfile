# Astro IT Profile

Astro IT Profile is a FastAPI-based backend project that generates an explainable IT profile using precise astronomical calculations.

The goal of the project is **not astrology as belief**, but an engineering-style experiment: translating astronomical configurations into structured thinking styles, work patterns, and IT career archetypes — with all calculations fully transparent and interview-ready.

---

## ✨ Key Features

* **FastAPI backend** with clean, modular architecture
* **Swiss Ephemeris (pyswisseph)** as the single source of astronomical truth
* Deterministic calculations (no randomization, no tables by date)
* Explainable business logic layered on top of raw astronomical data
* Portfolio-level codebase (~800–900 LOC)

---

## 🧠 What the API Calculates

Based on **date, time, and place of birth**, the service computes:

* ☉ **Sun sign** – base personality type
* ☿ **Mercury sign** – thinking and problem-solving style (Swiss Ephemeris)
* ☾ **Day / Night chart** – focus vs collaboration mode
* ♅ **Uranus house** (1 / 6 / 10 / 11 only) – main IT potential indicator
* 🏠 **6th house sign** – daily work style
* 🏔 **10th house sign** – career direction and IT archetype

All planets and houses are calculated via **Swiss Ephemeris**, not simplified date tables.

---

## 🧩 IT Profile Model

The IT profile is built layer by layer:

1. **Sun sign** → base IT personality
2. **Day / Night chart** → work mode modifier
3. **Mercury sign** → cognitive and thinking style
4. **Uranus house** → IT specialization potential
5. **6th house sign** → daily work habits
6. **10th house sign** → career trajectory

The result includes:

* IT fit score
* IT archetype (e.g. *Backend Astronaut*, *Systems Analyst*)
* Strengths
* Risks
* Human-readable explanation (`notes`)

---

## 🚀 Getting Started

### Requirements

* Python **3.12.x** (required)
* Windows OS

> Python 3.12 is recommended on Windows to ensure smooth installation of
> Swiss Ephemeris (pyswisseph) via prebuilt wheels.
> Newer Python versions may require manual C++ compilation.

> Python 3.13+ may require manual C++ compilation for Swiss Ephemeris.

### Installation

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Run the Server

```bash
uvicorn app.main:app --reload
```

Open:

```
http://127.0.0.1:8000/docs
```

---

## 📥 API Example

### Request

```json
{
  "birth_date": "1995-11-18",
  "birth_time": "14:30",
  "birth_place": "Berlin, Germany"
}
```

### Response (example)

```json
{
  "title": "Astro IT Profile (draft)",
  "sun_sign": "Scorpio",
  "it_fit_score": 100,
  "it_archetype": "Deep Systems Analyst / Backend Astronaut",
  "strengths": ["focus", "systems thinking", "analysis"],
  "risks": ["over-intensity"],
  "notes": "Strong fit for backend and deep technical domains.",
  "chart_type": "day",
  "mercury_sign": "Sagittarius",
  "uranus_house": 11,
  "house_6_sign": "Virgo",
  "house_10_sign": "Aquarius"
}
```

---

## 🏗 Architecture Overview

```
AstroITProfile/
├─ app/
│  ├─ api/            # FastAPI routes
│  ├─ services/       # Astro calculations & business logic
│  ├─ schemas/        # Pydantic models
│  └─ main.py
├─ data/              # Places and coordinates
├─ tests/
└─ requirements.txt
```

Key design decisions:

* Swiss Ephemeris is the **only** source for planetary data
* Business logic is fully separated from API layer
* No hidden heuristics or magic constants

---

## 🎯 Project Status

* Core calculations: ✅ complete
* Uranus house logic: ✅ complete
* House 6 / 10 sign logic: ✅ complete
* Aspects: ⏳ planned (future)
* Frontend: ❌ not planned (backend-only project)

---

## ⚠️ Disclaimer

This project is experimental and educational.
It does **not** claim scientific validity — the focus is on software architecture, deterministic computation, and explainable logic.

---

## 📌 Why This Project

This project demonstrates:

* backend API design
* working with external C-based libraries
* timezone and astronomical calculations
* layered business logic
* explainability over black-box results

---

## 📄 License

MIT (or specify if different)
