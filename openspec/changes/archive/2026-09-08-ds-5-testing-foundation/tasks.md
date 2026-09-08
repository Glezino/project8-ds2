## 1. Backend Testing Infrastructure (pytest + SQLite)

- [x] 1.1 Create test package structure: add `backend/tests/__init__.py`, `backend/tests/integration/` directory with `__init__.py`, and verify pytest discovers both unit and integration tests
- [x] 1.2 Create `backend/tests/conftest.py` with a session-scoped fixture that configures a SQLite in-memory database, creates all tables via `Base.metadata.create_all`, and an app-scoped `client` fixture that overrides the `get_db` dependency with a test session
- [x] 1.3 Write a failing integration test `backend/tests/integration/test_health.py` that calls `GET /api/v1/health` through the test client using the conftest fixtures, and confirm it fails because the fixtures do not exist yet
- [x] 1.4 Implement the conftest fixtures (session factory, `get_db` override, SQLAlchemy session per request) and confirm the integration test passes with `cd backend && uv run pytest tests/integration` (pytest)
- [x] 1.5 Verify all existing unit tests still pass with the new conftest.py present by running `cd backend && uv run pytest --ignore=tests/integration`
- [x] 1.6 Refactor `test_session.py` to use the shared `db_session` fixture from conftest instead of configuring its own engine, and confirm the refactored test passes

## 2. Frontend Component Testing (Vitest)

- [x] 2.1 Add `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, and `jsdom` as dev dependencies in `frontend/package.json` and verify `npm install` succeeds
- [x] 2.2 Create `frontend/vitest.config.ts` with the React plugin, `@` alias matching `vite.config.ts`, jsdom environment, and a setup file for `@testing-library/jest-dom`, and verify Vitest starts with `npm run test:unit`
- [x] 2.3 Add `test:unit` script (`vitest run`) and `test:unit:watch` (`vitest`) to `frontend/package.json` and verify `npm run test:unit` executes without config errors
- [x] 2.4 Write a failing component test `frontend/src/__tests__/App.test.tsx` that renders `App` and asserts the heading, button, and api-url test id are visible, and confirm it fails because Vitest setup files are not yet configured
- [x] 2.5 Create the Vitest setup file (imports `@testing-library/jest-dom`) and confirm the component test passes with `npm run test:unit`

## 3. End-to-End Testing (Playwright)

- [x] 3.1 Verify the existing Playwright configuration discovers tests by running `cd frontend && npx playwright test --list` and confirming `e2e/smoke.spec.ts` is listed
- [x] 3.2 Confirm the existing smoke tests pass by running `cd frontend && npx playwright test` (requires browsers installed via `npx playwright install chromium`)

## 4. Makefile Test Commands

- [x] 4.1 Add `test-unit` target to the Makefile that runs pytest excluding integration and component test discovery, and verify `make test-unit` succeeds
- [x] 4.2 Add `test-integration` target to the Makefile that runs pytest scoped to `tests/integration`, and verify `make test-integration` succeeds
- [x] 4.3 Add `test-frontend` target to the Makefile that runs `npm run test:unit` in `frontend/`, and verify `make test-frontend` succeeds
- [x] 4.4 Add `test-e2e` target to the Makefile that runs Playwright, update the umbrella `test` target to call the granular targets, and verify `make help` lists the new targets

## 5. Code Quality Checks

- [x] 5.1 Verify backend ruff configuration is complete by running `cd backend && uv run ruff check .` and `uv run ruff format --check .`, confirming both pass clean
- [x] 5.2 Verify frontend linting is reproducible by running `cd frontend && npm run lint` and confirming ESLint passes with no errors
- [x] 5.3 Verify frontend formatting is reproducible by running `cd frontend && npm run format:check` and confirming Prettier reports no files needing formatting
- [x] 5.4 Run the full `make lint` command and confirm all four checks (ruff check, ruff format, eslint, prettier) pass together

## 6. Documentation

- [x] 6.1 Update `README.md` (or a dedicated testing doc) to document the test directory structure (unit vs integration vs e2e), the granular `make test-*` commands, and the Vitest/SQLite/Playwright setup, and verify the documented commands match the Makefile targets
- [x] 6.2 Run the full verification suite `make lint && make test` and confirm everything passes end-to-end