# Production container (M13A shell + M13B beta gate)

Minimal notes for building and running AstroIT as a single FastAPI container.
Analytical behavior is unchanged.

## Build

```powershell
docker build -t astroit:beta .
```

## Run (local Docker, gate disabled — developer default)

```powershell
docker run --rm -p 8000:8000 `
  -e PORT=8000 `
  -e ASTROIT_WORKSPACE_STORE_PATH=/data/workspaces.json `
  -v ${PWD}/runtime-data:/data `
  astroit:beta
```

Local development can continue to use `python run.py` (binds `127.0.0.1`, reload enabled). Do not use `run.py` in production.

## Run (invite-only beta gate enabled)

```powershell
docker run --rm -p 8000:8000 `
  -e PORT=8000 `
  -e ASTROIT_WORKSPACE_STORE_PATH=/data/workspaces.json `
  -e ASTROIT_BETA_GATE_ENABLED=true `
  -e ASTROIT_BETA_ACCESS_CODE=<shared-invite-code> `
  -e ASTROIT_SESSION_SECRET=<strong-random-secret-16plus-chars> `
  -e ASTROIT_COOKIE_SECURE=false `
  -v ${PWD}/runtime-data:/data `
  astroit:beta
```

For HTTPS deployments set `ASTROIT_COOKIE_SECURE=true`.

**Important:** the gate turns on only when `ASTROIT_BETA_GATE_ENABLED` is explicitly true (`1` / `true` / `yes` / `on`). Merely setting an access code does **not** enable authentication.

## Environment

| Variable | Required | Purpose |
|---|---|---|
| `PORT` | No (default `8000`) | HTTP listen port inside the container |
| `ASTROIT_WORKSPACE_STORE_PATH` | Recommended in prod | Absolute path to workspace JSON (e.g. `/data/workspaces.json`) |
| `ASTROIT_BETA_GATE_ENABLED` | No (default off) | Explicitly enable invite-only beta gate |
| `ASTROIT_BETA_ACCESS_CODE` | Required when gate on | Shared invite access code (never commit) |
| `ASTROIT_SESSION_SECRET` | Required when gate on | Signing secret for auth/scope cookies (≥16 chars) |
| `ASTROIT_COOKIE_SECURE` | No (default false) | Set cookie Secure flag (`true` on HTTPS) |

Startup fails clearly if the gate is enabled but access code or session secret is missing.

## Health

- `GET /health` → `{"status":"ok"}` — **always public**, even with the gate enabled
- Docker `HEALTHCHECK` probes `/health` on the configured `PORT`

## Access when gate is enabled

| Path | Behavior |
|---|---|
| `/health` | Public |
| `/beta-access` | Public login page / POST |
| `/beta-logout` | Clears auth cookie |
| `/recruiter`, `/`, `/api/v1/*` | Require auth cookie |
| `/docs`, `/redoc`, `/openapi.json` | Require auth |

Unauthorized browser requests redirect to `/beta-access`. Unauthorized API requests return `401` JSON.

## Workspace privacy (beta gate on)

- Each authenticated browser gets an opaque HttpOnly `workspace_scope` cookie (not derived from name, IP, birth data, or access code).
- Saved workspaces are tagged with that scope id server-side.
- List / get / update / delete only succeed for workspaces owned by the current scope.
- **Legacy unscoped** records (saved before scoping) are **hidden** while the gate is enabled so they are never shown to every beta visitor. They remain visible only when the gate is disabled (local mode).
- Clearing cookies or using another browser creates a different scope; that browser will not see the first browser’s saved workspaces.
- Persistent disk (`ASTROIT_WORKSPACE_STORE_PATH` on a volume) is still required for saves to survive container restart.
- There are **no full user accounts** in this beta.

## UI

- Recruiter UI: `GET /recruiter` (after login when gated)
- Sign out is available in the recruiter header

Production start command used by the image:

```text
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```
