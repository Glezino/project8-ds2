---
jira: DS-6
---

## Why

The application is not yet containerized: only PostgreSQL runs in Docker (per ADR-5 in `docs/architecture.md`), while the backend and frontend run directly on the host via `make start`. This blocks any path toward reproducible deployment — the project cannot be deployed without first restructuring how services are built and run. Containerizing all services now establishes the strategy that later deployment will build on.

## What Changes

- Add a production-ready, multi-stage **backend Dockerfile** (`backend/Dockerfile`) that installs the full dependency set via `uv` from `uv.lock` and runs the FastAPI app with uvicorn.
- Add a production-ready, multi-stage **frontend Dockerfile** (`frontend/Dockerfile`) that builds the Vite/TypeScript app and serves the static output with nginx.
- Extend the root **`docker-compose.yml`** to add `backend` and `frontend` services, keeping the existing `db` service.
- Configure **service networking** so backend and db communicate over a shared Docker network; only the browser-facing ports (frontend and backend) are exposed to the host.
- Make **environment variables configurable** per service, sourced from `.env`, reusing the existing `.env`/`.env.example` pattern.
- Add **development volumes** so backend and frontend source changes hot-reload inside their containers.
- Add **health checks** (backend via the existing `/api/v1/health` endpoint; frontend/db via TCP/HTTP probes).
- Provide **development-mode variant of Docker Compose** (bind mounts + running dev servers) while the Dockerfiles themselves remain production-deployable.

## Capabilities

### New Capabilities

- `infrastructure/containerization`: Defines the behavior of the containerized development stack — building the backend and frontend images with Docker, starting the full stack (`db`, `backend`, `frontend`) through Docker Compose, allowing services to communicate over Docker networking, configuring environment variables per service, preserving hot-reload through development volumes, and reporting service health.

### Modified Capabilities

- `dev-environment`: The Docker Compose scope expands from "PostgreSQL only" to also start the backend and frontend containers; the docker-based startup path for the application services changes.

## Impact

- **Backend**: new `backend/Dockerfile`; no application-code, API, or schema changes. Runtime image includes the full ML stack (polars, scikit-learn, xgboost, optuna, seaborn, matplotlib).
- **Frontend**: new `frontend/Dockerfile` (+ nginx config); `VITE_API_URL` remains baked at build time, pointing at the host-visible backend URL (`http://localhost:8000`), matching the existing default. No application-code changes.
- **Infrastructure**: `docker-compose.yml` gains `backend` and `frontend` services; adds named volume(s), environment wiring, health checks, and a shared network. Adds `.dockerignore` files. No Makefile changes required (existing `make start` host path remains available).
- **Traceability**: branch `feature/DS-6-containerization`; commits and PR follow the `DS-6` issue code.
