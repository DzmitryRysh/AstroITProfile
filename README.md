# AstroIT

AstroIT explores **work-style and team-contribution patterns** through structured
astrological profiles. It is a descriptive discussion tool for individuals and teams —
not a hiring decision engine.

Product entry: `/recruiter`

---

## What AstroIT does

AstroIT helps explore descriptive patterns related to:

- thinking and information processing
- execution style
- how thinking and execution interact
- contribution patterns
- what a project needs (Project Demand)
- how a person’s contribution patterns relate to that demand
- team / workflow coverage

Outputs are meant to support conversation. They are hypotheses and source-linked
patterns, not verdicts.

---

## What AstroIT does not do

AstroIT is **not**:

- a Fit Score engine
- a candidate ranking system
- an automated hiring decision system
- a validated aptitude or skills test
- a compatibility-percentage product
- a technical-skills verifier
- a scientific employment predictor

Technical qualifications, interviews, and human judgment remain separate.

---

## Product layers

Current analytical layers (frozen v1 architecture):

| Layer | Role |
|---|---|
| **Mercury (THINK)** | Thinking, communication, and learning-style patterns |
| **Mars (DO)** | Execution and how work gets done |
| **THINK → DO** | How thinking and execution interact |
| **Contribution Profile** | Contribution-pattern summary for a person |
| **Project Demand** | What the project needs across contribution dimensions |
| **Contribution × Project Demand Coverage** | How one person’s patterns relate to stated project needs |
| **Team / Workflow Coverage** | Team and workflow coverage views for setup and discussion |

These layers are descriptive. The product does not expose a hidden overall fit score
or rank people against each other.

---

## Current beta experience

A working **recruiter UI** ships with the app.

- **Entry:** `GET /` redirects to `/recruiter`
- **With private beta gate enabled:** unauthenticated browsers are sent to
  `/beta-access`; after a valid shared access code, the recruiter UI is available
- **Explore Yourself:** build a personal thinking / working profile from birth data
- **Project / team workflow:** set up people and project context, then explore
  contribution, demand, and coverage views
- **Saved Workspaces:** persist team/project *input* for later sessions
- **Load Demo Scenario:** sample data for trying the product without entering a full team

There are **no full user accounts** in this beta.

---

## Privacy and decision safeguards

- Outputs are descriptive context for discussion, not automated hiring decisions
- The product does not rank candidates
- Technical qualifications must be verified separately (CV, interviews, assessment)
- Birth data is sensitive input; treat it accordingly
- This beta does not include third-party analytics or tracking

When the invite-only gate is enabled:

- access uses a **shared beta access code**
- a **signed HttpOnly session cookie** authenticates the browser
- recruiter UI, API, and docs are protected
- `/health` remains public
- saved workspaces are **browser-scoped** (an anonymous scope is stored in that browser),
  not account-synced

Clearing cookies can make a previous browser scope unavailable even if workspace
records remain on disk. Another browser or device gets a separate saved-workspace
scope.

---

## Known beta limitations

1. **Birth time** — optional. Without it, house-dependent interpretations may be
   unavailable; a profile can still be built.
2. **Birth place** — search uses a curated list of supported locations (not
   worldwide geocoding).
3. **Workspaces** — scoped to the browser during private beta; no account-level
   cross-device sync.
4. **Private beta** — the product is still evolving; APIs and UI may change.

---

## Tech stack

- Python
- FastAPI
- Swiss Ephemeris (`pyswisseph`)
- Static recruiter UI (`app/ui/recruiter`)
- Docker production image
- JSON file persistence for workspaces
- `unittest` test suite

---

## Local development

Create/activate a virtualenv, install dependencies, then:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Useful URLs (gate **disabled** by default):

| URL | Purpose |
|---|---|
| http://127.0.0.1:8000/recruiter | Recruiter UI |
| http://127.0.0.1:8000/docs | OpenAPI / Swagger |
| http://127.0.0.1:8000/health | Health check |

The private beta gate is off unless `ASTROIT_BETA_GATE_ENABLED` is explicitly set
to a truthy value. Do not put real secrets in the repo.

You can also use `python run.py` for local reload on `127.0.0.1` (not for production).

---

## Docker / production

See **[docs/production.md](docs/production.md)** for build/run details, health
behavior, and workspace privacy notes.

Minimal example (gate disabled):

```powershell
docker build -t astroit:beta .

docker run --rm -p 8000:8000 `
  -e PORT=8000 `
  -e ASTROIT_WORKSPACE_STORE_PATH=/data/workspaces.json `
  -v ${PWD}/runtime-data:/data `
  astroit:beta
```

Use a durable volume for `ASTROIT_WORKSPACE_STORE_PATH` so saves survive container
restarts.

---

## Environment variables

| Variable | Notes |
|---|---|
| `ASTROIT_WORKSPACE_STORE_PATH` | Path to workspace JSON store (recommended in Docker/prod) |
| `ASTROIT_BETA_GATE_ENABLED` | Explicitly enable invite-only beta gate (default off) |
| `ASTROIT_BETA_ACCESS_CODE` | Shared invite code (required when gate on) |
| `ASTROIT_SESSION_SECRET` | Session signing secret, ≥16 chars (required when gate on) |
| `ASTROIT_COOKIE_SECURE` | Set cookie Secure flag (`true` on HTTPS) |
| `PORT` | Listen port inside the container (default `8000`) |

Never commit real access codes or session secrets.

---

## Testing

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

At the current beta checkpoint, the full unittest suite passes.

---

## Project status

Private beta: recruiter UI, analytical layers above, Docker production shell, and
invite-only gate with browser-scoped workspaces are in place. Analytical
architecture for this checkpoint is frozen; product copy and packaging continue to
evolve.

---

## Documentation

- [docs/production.md](docs/production.md) — Docker, env, health, beta access, workspace scope
