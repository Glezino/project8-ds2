## Context

The stack is a FastAPI backend (Python 3.12, dependency-managed by `uv` using `uv.lock`) and a Vite/React frontend (Node/npm, build output in `frontend/dist/`). Today only PostgreSQL runs in Docker (root `docker-compose.yml`); backend and frontend run on the host via `make start`. ADR-5 (`docs/architecture.md`) already documents the per-service Docker layout as the future direction. Motivation is in `proposal.md`.

Key constraints shaping the design:

- Backend entrypoint is `app.main:app`, run under uvicorn. `Settings` (pydantic-settings) defaults `DATABASE_URL` to `postgresql://user:password@localhost:5432/dbname` — inside Docker this host must become the `db` service name.
- The browser is **outside** the containers, so `VITE_API_URL` must be a host-visible URL (`http://localhost:8000`) even though the backend runs in a container. The backend port is therefore exposed to the host.
- Requirements are in `specs/infrastructure/containerization/spec.md` and the delta in `specs/dev-environment/spec.md`.

## Goals / Non-Goals

**Goals:**
- Production-deployable Dockerfiles for backend and frontend.
- Docker Compose starts the full `db` + `backend` + `frontend` stack for local development.
- A single set of Dockerfiles serves both production builds and development hot-reload (via bind mounts).
- Backend and db communicate over an internal Docker network; only browser-facing ports are exposed.
- All service configuration flows through the existing `.env` mechanism.

**Non-Goals:**
- Changing application code: no API, schema, or frontend behavior changes.
- Orchestrated multi-host deployment (Kubernetes, cloud), TLS, or a shared frontend->backend proxy for production.
- Slimming or splitting the ML-heavy backend image.
- Altering the existing `make start` host path.

## Decisions

### D1: Backend image — `uv`-based, single production Dockerfile
Use `ghcr.io/astral-sh/uv` with the `python:3.12-slim` base (matches `.python-version` = 3.12). The image runs `uv sync --frozen` from `uv.lock` for a reproducible install, then serves `app.main:app` via uvicorn.

- **Why**: the project already standardizes on `uv` + `uv.lock`; using uv's official image avoids a second dependency resolver and matches ADR conventions.
- **Alternatives**: plain `pip install -r` (adds a second manifest — rejected); `python:3.12` full image (larger — slim is sufficient).

**Dev vs prod**: the same `Dockerfile` is used with a build arg / compose override. In dev, compose bind-mounts `backend/` into the image and runs uvicorn with `--reload`; in prod the image runs uvicorn as-is. No separate dev image is maintained.

### D2: Frontend image — multi-stage, nginx for production
Two stages: a `node` build stage that runs `npm ci` + `npm run build`, and an `nginx:alpine` runtime stage that serves `frontend/dist/`. A small `nginx.conf` (default port 80, serving the static files) is bundled.

- **Why**: matches the "deploy without restructuring" requirement — `npm run build` already produces the static bundle, and nginx is the conventional static host.
- **Alternatives**: running `vite` (dev server) in the runtime image (not deployable — rejected for the image itself).
- **Note (D4)**: because `VITE_API_URL` is inlined at build time, the frontend image is built once and reused; dev hot-reload is handled by the compose dev override described in D5.

### D3: Networking — shared internal network, host ports only where the browser needs them
Add an explicit network (e.g. `app-net`) to Compose. `db` and `backend` are reachable by service name internally and are **not** exposed to the host. `backend` exposes `8000:8000` and `frontend` exposes `5173:80` (or `80:80`) to the host so the browser can reach them.

- The `db` service keeps its existing `5432:5432` host mapping? No — with `backend` connecting over the internal network, the host port is no longer required. Keep it optional/removed to avoid exposing the DB. (Compose currently maps `5432:5432`; this is removed in favor of internal-only access.)
- **Why**: the browser must reach backend and frontend directly; nothing else needs host access.

### D4: Frontend->backend URL — direct host URL, keep existing default
`VITE_API_URL` stays `http://localhost:8000` (the current `.env.example` default). The backend's port `8000` is exposed to the host, so the browser reaches the backend directly.

- **Why**: zero added config, matches the existing default, and avoids a vite dev proxy.
- **Alternatives**: a vite dev proxy `/api` -> backend (`Option B` from exploration). Rejected — more config, and the direct URL matches what's already documented.

### D5: Development hot-reload via compose override + bind mounts
A `docker-compose.override.yml` (already git-ignored) is used locally to bind-mount `backend/` and `frontend/` and enable live reload (uvicorn `--reload` for backend; `vite --host` with HMR for frontend). This keeps the checked-in `docker-compose.yml` production-lean while giving developers hot reload.

- **Why**: the checked-in compose stays clean; the override is a standard Compose mechanism Docker already ignores in git (`.gitignore` lists `docker-compose.override.yml`).
- **Trade-off**: dev and prod differ slightly (dev runs dev servers via the override). Mitigated because the images themselves are identical and deployable.

### D6: Environment wiring — reuse `.env`, override service-specific values in Compose
`docker-compose.yml` reads interpolation (`${VAR:-default}`) from the root `.env`, following the existing pattern. Because `DATABASE_URL` must point at the `db` hostname inside the network, set it explicitly in the `backend` service to `postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}` rather than relying on the `localhost` default in `Settings`. `VITE_API_URL` is passed as a build arg to the frontend build stage.

### D7: Health checks
- **Backend**: HTTP check against the existing `/api/v1/health` endpoint (`GET`, expecting success).
- **Frontend**: TCP/HTTP check against the served port (nginx responds on port 80).
- **db**: rely on postgres's built-in `pg_isready` (standard image practice).
Use Compose `healthcheck` blocks with sensible interval/timeout/retries so `depends_on` can gate startup order.

### D8: `.dockerignore` files
Add `.dockerignore` for `backend/` (exclude `.venv`, caches, artifacts) and `frontend/` (exclude `node_modules`, `dist`, `test-results`) so build contexts stay small and reproducible. Root `.gitignore` already covers `docker-compose.override.yml`.

## Risks / Trade-offs

- **Large ML dependencies slow backend builds** → the runtime image installs the full ML stack (polars, xgboost, sklearn, optuna, seaborn, matplotlib). Mitigated by uv's cached layer strategy; image size reduction is explicitly a non-goal (proposal).
- **Dev/prod divergence via override** → the same Dockerfiles are used in both; only the runtime command and mounts differ. Kept minimal and guarded by Compose's built-in override behavior.
- **`DATABASE_URL` localhost default vs container host** → if someone forgets the compose override to `db`, backend cannot reach the DB. Mitigated by setting `DATABASE_URL` explicitly in the compose `backend` service (D6), which is the single source used when running via Docker.
- **`VITE_API_URL` baked at build time** → changing the URL requires a rebuild. Accepted; matches Vite's model and the unchanged default.
- **No host port for Postgres** → host tools fallback to the `make start` path or must use the internal network. Accepted trade-off to reduce surface; local host Postgres via container was previously the only path, so removing the host DB port is a deliberate tightening.

## Migration Plan

1. Implement backend and frontend Dockerfiles + `.dockerignore` files.
2. Extend root `docker-compose.yml` with `backend`/`frontend` services, shared network, health checks, and env wiring; remove `db`'s host port.
3. Add the local `docker-compose.override.yml` for dev bind-mounts (git-ignored).
4. Verify: `docker compose build`, then `docker compose up`, then confirm backend `/api/v1/health` responds and the frontend page loads.
5. Rollback: revert to the existing host `make start` path — no application code changed, so nothing is lost.

## Open Questions

None — the spec, approach, and task breakdown are settled. (Automated validation of Compose configs/container builds is a manual verification step captured in tasks, since these are infra artifacts rather than pytest/Playwright unit behavior.)
