---
jira: DS-4
---

## Why

The project has a basic directory skeleton (frontend/, backend/, backend/ml/) but no defined architecture. Before building any feature, we need clear boundaries between layers: API, business logic, data access, ML, and infrastructure. Without this, each new feature risks coupling concerns (e.g., ML logic in API routes, business logic in database models) and creates tech debt that compounds.

## What Changes

- Define and document the layered backend architecture (API -> Services -> Data Access + ML)
- Define the frontend architecture (pages, components, api client, hooks)
- Create the backend directory structure: `app/api/`, `app/schemas/`, `app/services/`, `app/db/`, with versioned API (`api/v1/`)
- Restructure frontend `src/` into `pages/`, `components/`, `api/`, `hooks/`
- Initialize Alembic for database migrations
- Create `docker-compose.yml` for local PostgreSQL development
- Document dependency direction and architectural decisions
- Establish the API contract pattern (frontend `api/types.ts` mirrors backend `schemas/`)

## Capabilities

### New Capabilities

_(none — no user-facing behavior changes)_

### Modified Capabilities

_(none — no existing spec requirements change)_

> This change is pure architecture definition and structural scaffolding.
> No observable behavior changes; `skip_specs: true`.

## Impact

- **Backend**: New directory structure (`api/`, `schemas/`, `services/`, `db/`), `database.py` for session management, Alembic initialization, existing `health.py` moved into `api/v1/`
- **Frontend**: `src/` restructured into `pages/`, `components/`, `api/`, `hooks/`, `types.ts` for API contract
- **Infrastructure**: New `docker-compose.yml` at repo root for PostgreSQL
- **Dependencies**: No new runtime dependencies (SQLAlchemy, Alembic, FastAPI already in pyproject.toml)
- **Migration risk**: File moves only — no logic changes, no breaking changes to existing endpoints
