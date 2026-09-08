---
jira: DS-4
---

## 1. Backend Layering

- [x] 1.1 Create backend layer directories (`app/api/`, `app/api/v1/`, `app/schemas/`, `app/services/`, `app/db/`) with `__init__.py` files and verify the structure exists (pytest import smoke test imports each package)
- [x] 1.2 Move the health endpoint into `app/api/v1/health.py` (with `v1/router.py` aggregating it), mount it from `app/main.py`, and update `tests/test_smoke.py` so the existing health tests pass (pytest)
- [x] 1.3 Add `app/api/deps.py` defining a shared `get_db` FastAPI dependency placeholder and verify it imports cleanly without a running server (pytest)
- [x] 1.4 Add `app/schemas/health.py` (or equivalent) Pydantic models for the health response and verify a round-trip validation test passes (pytest)

## 2. Data Access Layer

- [x] 2.1 Create `app/db/session.py` with engine + `SessionLocal` wired to `config.Settings.database_url` and a `get_db` generator; verify a unit test that calls `get_db()` yields a session and closes it (pytest, uses SQLite in-memory override or a lightweight engine)
- [x] 2.2 Create `app/db/models.py` defining SQLAlchemy 2.0 `Base` (declarative); verify a test imports it and reflects the metadata (pytest)

## 3. Alembic Migrations

- [x] 3.1 Run Alembic initialization from `backend/` root so `alembic.ini` + `alembic/` are created and `env.py` points to `app.db.models.Base.metadata` + Settings DATABASE_URL; verify `alembic check` / a dry-run migration produces no error and an empty initial migration file exists (pytest/ruff + CLI command)
- [x] 3.2 Add a test that imports the Alembic `env.py` config module without error so CI can validate the migration setup (pytest)

## 4. ML Module Boundaries

- [x] 4.1 Create `backend/ml/` sub-directories (`inference/`, `training/`, `features/`, `artifacts/`, `utils/`) with `__init__.py` files and verify each imports in the existing smoke test (pytest)
- [x] 4.2 Ensure `ml/` has no imports from `app.api` or FastAPI by adding a test that scans `ml/` module imports and asserts none reference `fastapi` or `app.api` (pytest)
- [x] 4.3 Add `ML_ARTIFACTS_PATH` to Settings/config and a test asserting the default resolves under `backend/ml/artifacts` (pytest)

## 5. Frontend Structure

- [x] 5.1 Create `frontend/src/{pages,components/layout,components/features,api,hooks}` directories; verify the Vite build (`npm run build`) succeeds with the new structure and Playwright smoke test stays green
- [x] 5.2 Move `src/lib/api.ts` Axios instance to `src/api/client.ts`, update imports, and verify the Playwright smoke test (which checks the API URL) passes
- [x] 5.3 Add `src/api/types.ts` with initial TypeScript interfaces mirroring the backend health schema; verify a TypeScript typecheck (`npm run build` / `tsc`) passes

## 6. Infrastructure (Database)

- [x] 6.1 Create root `docker-compose.yml` with a PostgreSQL 16 service wired to `.env` `POSTGRES_*` vars; verify `docker compose config` validates successfully
- [x] 6.2 Add `POSTGRES_USER/PASSWORD/DB` to `.env.example` and verify `make setup` copies/completes (or the vars are documented)

## 7. Documentation

- [x] 7.1 Write `docs/architecture.md` with the layered architecture diagram, dependency-direction rules table, and recorded decisions; verify the file renders (markdown present, reviewed)

## 8. Pre-Commit Verification

- [x] 8.1 Run `make lint` and confirm no lint/format errors (ruff + eslint/prettier)
- [x] 8.2 Run `make test` and confirm the full backend pytest + frontend Playwright suites pass
