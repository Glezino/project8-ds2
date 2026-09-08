# Project8 DS2 - Architecture

This document records the modular architecture and the boundaries between frontend,
backend, ML, persistence, and infrastructure. It is the reference for dependency
direction and is enforced during code review.

Created for Jira issue DS-4.

## 1. System Overview

```
+==================================================================+
|                          FRONTEND                                 |
|                React (Vite) + TypeScript + Tailwind               |
|                                                                   |
|   pages/              Route-level views                           |
|   components/ui/      Shadcn primitives                           |
|   components/layout/  App shell / navigation                      |
|   components/features Feature-specific components                 |
|   api/                HTTP client + types (API contract)          |
|   hooks/              Custom data hooks                           |
+------------------------------+-----------------------------------+
                               |
                     HTTP (Axios) -> /api/v1
                               |
                               v
+==================================================================+
|                         BACKEND (FastAPI)                         |
|                                                                   |
|  +-------------------+     +-------------------+                 |
|  |  API Layer        |---->|  Services Layer   |                 |
|  |  app/api/         |     |  app/services/    |                 |
|  |  - routers        |     |  - business logic |                 |
|  |  - deps           |     |  - orchestration  |                 |
|  +-------------------+     +---------+---------+                 |
|  Schemas app/schemas/                |                           |
|  (Pydantic request/response)         |                           |
|                                      v                           |
|                       +---------------------+                    |
|                       |   Data Access       |                    |
|                       |   app/db/           |                    |
|                       |   - SQLAlchemy 2.0  |                    |
|                       |   - Alembic         |                    |
|                       +----------+----------+                    |
|                                  |                               |
+==================================================================+
                                   |
                                   v
                       +---------------------+
                       |    PostgreSQL       |
                       |  (Docker: dev /     |
                       |   Supabase: prod)   |
                       +---------------------+

+==================================================================+
|   ML MODULE (backend/ml/)                                        |
|                                                                   |
|   inference/   prediction functions (consumed by services)        |
|   training/    training pipeline logic                            |
|   features/    feature engineering transforms                     |
|   artifacts/   saved models (gitignored; volume-mounted later)    |
|   utils/       shared helpers                                     |
|                                                                   |
|   Exposes plain functions only. No HTTP, no FastAPI imports.      |
+==================================================================+
```

## 2. Dependency Direction

The dependency rule is unidirectional. It is the core architectural constraint
and is enforced during code review (and by `tests/test_ml_boundary.py` for ML):

```
  app/api       -->  app/services  -->  app/db
  app/api       -->  app/schemas
  app/services  -->  app/db
  app/services  -->  ml
```

| Layer            | May import                            | Must NOT import                |
|------------------|---------------------------------------|--------------------------------|
| `app/api`        | `app/services`, `app/schemas`, FastAPI | `app/db` directly              |
| `app/services`   | `app/db`, `ml`                        | `app/api`, FastAPI             |
| `app/schemas`    | - (leaf: pure Pydantic)               | internal layers                |
| `app/db`         | - (leaf: SQLAlchemy)                  | `app/api`, `app/services`, `ml` |
| `ml`             | ML data/artifacts only                | `app.*`, FastAPI               |

Leaves (`app/db`, `app/schemas`, `ml`) import nothing internal. Services can be
tested without a running server.

## 3. Recorded Decisions

### ADR-1: Backend layering (API -> Services -> Data Access + ML)

`app/api/` is a thin HTTP adapter: routers, FastAPI dependencies, request/response
handling. `app/services/` holds business logic and is framework-agnostic.
`app/db/` owns SQLAlchemy models/session and Alembic migrations. Versioned API
under `app/api/v1/`.

Alternatives considered: single flat `app/` (rejected - couples concerns);
repository pattern (deferred - add only when queries get complex, KISS).

### ADR-2: ML as an internal library with a clean function contract

ML lives inside `backend/ml/` and exposes plain functions (`predict`, `train`,
`evaluate`). Services consume ML through these functions; ML never touches HTTP.
If ML must become a separate service later, the function signatures become the
API contract.

Alternatives considered: separate ML Python package / separate ML service
(rejected as premature; revisit when ML is feature-relevant).

### ADR-3: SQLAlchemy 2.0 Mapped style + Alembic

Modern `Mapped`/`mapped_column` typing. Alembic initialized from `backend/`
root; `env.py` targets `app.db.models.Base.metadata` and reads the URL from
`Settings.database_url`. Sync engine for now; async is a candidate if
concurrency demands it (boundaries unchanged).

Alternatives considered: legacy `Column` style (rejected); async SQLAlchemy
(rejected for now).

### ADR-4: Frontend feature-aligned structure

`pages/` (route views), `components/` (ui primitives / layout / feature
components), `api/` (Axios client + `types.ts` API contract), `hooks/`, `lib/`
(utilities). The backend API contract is mirrored in `src/api/types.ts` and
manually kept in sync with `app/schemas/`.

### ADR-5: Docker for the full development stack

`docker-compose.yml` at the repo root provides PostgreSQL, the backend, and the
frontend as separate containers on a shared internal network (`app-net`) for
local development. Each service has its own Dockerfile (per-service Docker
layout). Only browser-facing ports (`backend: 8000`, `frontend: 5173`) are
exposed to the host; the database is reachable only by service name inside the
network. For day-to-day development, a git-ignored `docker-compose.override.yml`
bind-mounts `backend/` and `frontend/` and enables hot-reload (uvicorn `--reload`,
Vite HMR). The host-based `make start` path remains available as an alternative.

### ADR-6: Configuration

Backend reads `.env` via pydantic-settings (`backend/app/config.py`), including
`ML_ARTIFACTS_PATH`. Frontend reads `VITE_API_URL` via `import.meta.env`.
Database credentials come from `POSTGRES_*` vars used by `docker-compose.yml`.
Inside Docker, `docker-compose.yml` sets `DATABASE_URL` to the `db` service
name on the internal network and passes `VITE_API_URL` as a frontend build arg
(it is inlined at build time); the host `make start` path reads both from the
root `.env` as before.

## 4. API Contract

The frontend `src/api/types.ts` interfaces mirror the backend `app/schemas/`
Pydantic models. Both sides share the same shapes. Auto-generation
(openapi-typescript) is a candidate if manual drift becomes a problem.

## 5. Conventions

- New backend features follow the layering: router in `app/api/v1/`, validation
  models in `app/schemas/`, business logic in `app/services/`, persistence in
  `app/db/`.
- ML models/artifacts are stored under `backend/ml/artifacts/` and are not
  committed to version control.
- Every new backend/ML module ships its tests alongside the code (pytest).
- Frontend features add pages, hooks, and API modules under the corresponding
  folders; the API contract lives in `src/api/types.ts`.