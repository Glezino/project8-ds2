---
jira: DS-4
---

## Context

The repo is a bare skeleton (see proposal.md - Why). Backend has only `app/main.py` (GET /health) and `app/config.py`; `backend/ml/` is empty. Frontend has single route/component and an Axios client in `src/lib/api.ts`. No database layer, no Alembic, no Docker Compose exist despite the stack/documentation mentioning them. This change defines the modular architecture and scaffolds its structure without building features.

Key constraints from project context: DRY/KISS (reuse existing patterns, don't over-abstract), layering by folder (frontend/, backend/, backend/ml/), mandatory TDD, and future independent Docker deployment per service.

## Goals / Non-Goals

**Goals:**
- Define clean, unidirectional layer boundaries in the backend with a versioned API
- Keep ML decoupled from API logic (internal library behind a clear function contract)
- Scaffold a frontend structure that separates pages, api client, components, hooks
- Establish the API contract pattern between frontend types and backend schemas
- Set up Alembic migrations and a local PostgreSQL via Docker Compose
- Document dependency direction in an architecture doc

**Non-Goals:**
- Implementing any actual feature (no datasets, models, predictions, real pages)
- Building ML pipelines or models
- Containerizing the backend/frontend services (only PostgreSQL DB container now)
- Authentication, authorization, or multi-tenancy
- CI/CD configuration

## Decisions

### 1. Backend layering: API -> Services -> Data Access (+ ML) as internal library

Modern FastAPI convention (router-per-resource, dependency injection). Business logic (`services/`) never imports FastAPI; API layer (`api/`) is a thin HTTP adapter.

```
app/
  main.py          # app factory, router mounting, lifespan
  config.py        # Settings (existing)
  api/
    deps.py        # shared FastAPI dependencies (get_db, etc.)
    v1/
      router.py    # aggregates all v1 routers
      health.py    # GET /health (moved here)
  schemas/         # Pydantic request/response models (mirrors frontend types)
  services/        # business logic; imports db/ and ml/; no FastAPI
  db/
    session.py     # engine, SessionLocal, get_db
    models.py      # SQLAlchemy 2.0 Mapped models (empty base for now)
    migrations/    # Alembic files
```

- **Alternative considered**: single `app/` with everything flat. Rejected — couples concerns, no dependency direction enforcement.
- **Alternative considered**: repository pattern layer between services and db. Rejected for now (KISS) — SQLAlchemy models + session directly in services is enough for this stage; add repositories only when queries get complex.

**Dependency rule (enforced):**
```
api/ --> services/ --> db/
         services/ --> ml/
api/ --> schemas/
```
Leaves (`db/`, `ml/`, `schemas/`) import nothing internal. Services can be tested without a server.

### 2. ML as internal library with a clean function contract

Keep `backend/ml/` inside the backend package (matches existing structure), but expose ML through plain functions (`predict`, `train`, `evaluate`) consumed only by `services/`. No FastAPI/HTTP in `ml/`. If it ever needs to become a separate service, the function signatures become the API contract.

```
ml/
  __init__.py
  inference/     # predict() etc. consumed by services
  training/      # training pipeline logic
  features/      # feature engineering transforms
  artifacts/     # saved models (gitignored; later volume-mounted)
  utils/         # shared helpers
```

- **Alternative considered**: separate ML Python package / separate ML HTTP service. Rejected — premature for this stage; increases setup/deployment complexity. Revisit when ML is feature-relevant.

### 3. Database: SQLAlchemy 2.0 Mapped style + Alembic at backend root

Use modern SQLAlchemy 2.0 `Mapped`/`mapped_column` typing. Alembic initialized from `backend/` root so `alembic/` sits alongside `app/`. `DATABASE_URL` comes from existing `config.py` Settings. For now only `Base` is defined — no concrete models (features create them later).

```
backend/
  alembic.ini
  alembic/
    env.py
    versions/ (empty)
  app/db/
    session.py
    models.py     # defines Base
```

- **Alternative considered**: legacy `Column` style. Rejected — `Mapped` is the current, type-safe standard and what SQLAlchemy documents as forward.
- **Alternative considered**: async SQLAlchemy (`asyncpg`). Rejected for now — sync is simpler at this stage and FastAPI handles sync endpoints via threadpool fine; can migrate to async later if concurrency demands.

### 4. Frontend structure: feature-aligned folders

Restructure `src/` and keep existing `lib/api.ts` as the base of the api client layer (DRY — reuse it, don't duplicate).

```
src/
  main.tsx, App.tsx, index.css   # existing
  pages/                         # route-level views
  components/
    ui/          # existing shadcn primitives
    layout/      # app shell/nav (empty scaffold for now)
    features/    # feature-specific components (empty)
  api/
    client.ts    # the Axios instance (moved from lib/api.ts)
    types.ts     # TS interfaces mirroring backend schemas
    # per-resource modules added with features
  hooks/         # custom data hooks (empty)
  lib/
    utils.ts     # existing cn() helper
```

- **Alternative considered**: keep everything in `components/`. Rejected — `pages/` and `api/` are the React/Data-flow norm and keep the axis of change clear.
- **API contract**: `api/types.ts` interfaces mirror `schemas/` Pydantic models, manually kept in sync. **(auto-generation with openapi-typescript is an Open Question).**

### 5. Docker Compose: PostgreSQL only

One `docker-compose.yml` at repo root starting Postgres for local dev. This matches the documented stack (PostgreSQL in Docker for development). No app containers yet (non-goal, aligns with future per-service Docker).

```yaml
services:
  db:
    image: postgres:16
    ports: ["5432:5432"]
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-password}
      POSTGRES_DB: ${POSTGRES_DB:-dbname}
    volumes: [pgdata:/var/lib/postgresql/data]
volumes:
  pgdata:
```

`.env.example` gains `POSTGRES_USER/PASSWORD/DB` (DATABASE_URL already present).

- **Alternative considered**: no DB container yet. Rejected — Alembic migrations + db layer need a target server to be testable; Docker is the documented local approach.

### 6. Architecture documentation

Create an architecture doc (at repo root, e.g. `docs/architecture.md`) containing the layered diagram, the dependency rules table, and the recorded decisions (ADR-style). This satisfies the DS-4 evidence requirement (architecture documentation + diagram + dependency boundaries).

## Risks / Trade-offs

- **[File moves break imports]** -> Health endpoint moved into `api/v1/health.py`; update `main.py` and the two tests referencing it. Frontend `lib/api.ts` moved to `api/client.ts`; update imports + Playwright smoke test. Run full test suite to catch.
- **[ML code drifts toward API layer]** -> Enforce the rule in the architecture doc and code review; `ml/` exposes functions only, no FastAPI dependency.
- **[sync SQLAlchemy may hit concurrency ceiling]** -> Acceptable for current scope; documented as a candidate for async migration later without changing layer boundaries.
- **[Types drift between frontend/backend]** -> Covered by `api/types.ts` convention; if drift becomes a problem, adopt openapi-typescript generation (Open Question).
- **[Dead/empty scaffold directories]** -> Keep scaffolding minimal (only empty `__init__.py`/`.gitkeep` where needed); features populate them. Avoid over-structuring.

## Migration Plan

1. Create backend layer directories and move health endpoint + update `main.py`/tests
2. Initialize Alembic
3. Restructure frontend, moving `lib/api.ts` -> `api/client.ts`, add `types.ts`
4. Add `docker-compose.yml` + `.env.example` vars
5. Write `docs/architecture.md`
6. Run `make lint` + `make test` to confirm green

Rollback: changes are additive file moves with no schema/data changes; reverting the branch restores prior state.

## Open Questions

- **API contract automation**: adopt `openapi-typescript` to auto-generate `api/types.ts` from the backend OpenAPI schema, or keep manual mirroring? Defers safely — either works within this structure and can be added later without changing boundaries.
