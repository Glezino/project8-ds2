## Why

The project mandates TDD (every new feature starts with a failing test), but the testing and code-quality infrastructure is incomplete. Backend has pytest but no integration test structure or shared fixtures. Frontend has Playwright for e2e but no component testing framework. There is no unified way to run unit, integration, and e2e tests in isolation. This blocks the team from practicing TDD effectively and from validating changes continuously.

## What Changes

- **SQLite for testing**: Configure SQLite as the default test database (fast, zero-dependency). Keep PostgreSQL via Docker for local dev and production.
- **Frontend component testing**: Add Vitest + React Testing Library for unit and component tests in `frontend/`.
- **Integration test structure**: Create `backend/tests/integration/` with shared fixtures (database sessions, test client) for tests that exercise the API against a real database.
- **Test directory organization**: Define clear separation between unit tests (`backend/tests/`), integration tests (`backend/tests/integration/`), and e2e tests (`frontend/e2e/`).
- **Makefile test targets**: Add granular test commands (`make test-unit`, `make test-integration`, `make test-e2e`) alongside the existing `make test`.
- **Linting and formatting**: Confirm existing ruff + ESLint + Prettier configuration is complete; no new tools needed.
- **Example tests**: Add one passing unit test (backend), one passing component test (frontend), and one passing integration test (backend API against SQLite).

## Capabilities

### New Capabilities

_(none — this is a tooling/configuration change; no new observable behavior)_

### Modified Capabilities

_(none — existing `dev-environment` spec already covers standardized test and lint commands)_

## Impact

- **Backend**: SQLite in-memory test DB configured in new `backend/tests/conftest.py`; new `tests/integration/` directory; `httpx` already available for async test client.
- **Frontend**: `package.json` gains `vitest` + `@testing-library/react` + `@testing-library/jest-dom` as dev dependencies; new `vitest.config.ts`; new `src/__tests__/` directory.
- **Makefile**: New targets for granular test execution.
- **No database schema changes**: SQLite is test-only; Alembic migrations continue targeting PostgreSQL.
- **No environment variable changes**: Test DB URL is hardcoded in test config, not read from `.env`.
- **No Docker changes**: Integration tests use SQLite, not the Docker PostgreSQL container.
