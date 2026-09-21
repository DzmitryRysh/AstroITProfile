# Production container (M13A)

Minimal notes for building and running AstroIT as a single FastAPI container.
Analytical behavior is unchanged. Auth and tenancy are out of scope for this shell.

## Build

```powershell
docker build -t astroit:beta .
```

## Run

```powershell
docker run --rm -p 8000:8000 `
  -e PORT=8000 `
  -e ASTROIT_WORKSPACE_STORE_PATH=/data/workspaces.json `
  -v ${PWD}/runtime-data:/data `
  astroit:beta
```

Omit the `-v` mount for an ephemeral container filesystem (workspace saves will not survive container removal).

## Environment

| Variable | Required | Purpose |
|---|---|---|
| `PORT` | No (default `8000`) | HTTP listen port inside the container |
| `ASTROIT_WORKSPACE_STORE_PATH` | Recommended in prod | Absolute path to workspace JSON (e.g. `/data/workspaces.json`) |

Local development can continue to use `python run.py` (binds `127.0.0.1`, reload enabled). Do not use `run.py` in production.

## Health

- `GET /health` → `{"status":"ok"}`
- Docker `HEALTHCHECK` probes `/health` on the configured `PORT`

## UI

- Recruiter UI: `GET /recruiter`
- API docs (still open in this phase): `/docs`

Production start command used by the image:

```text
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```
