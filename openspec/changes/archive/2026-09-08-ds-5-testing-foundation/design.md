## Context

The backend already has pytest configured with 10 unit test files, but lacks shared fixtures (`conftest.py`), an integration test directory, and a test database strategy. The frontend has Playwright for e2e but no component testing framework. The Makefile has `make test` (runs everything) and `make lint`, but no granular targets for running test subsets.

Current backend tests use ad-hoc SQLite (`sqlite://`) in individual files. There is no `conftest.py`, no `__init__.py` in `tests/`, and no `tests/integration/` directory. The frontend has no Vitest or React Testing Library setup.

## Goals / Non-Goals

**Goals:**
- SQLite as the default test database for all backend tests (unit + integration)
- Vitest + React Testing Library for frontend component testing
- Clear directory separation: unit tests in `backend/tests/`, integration tests in `backend/tests/integration/`, e2e tests in `frontend/e2e/`
- Granular Makefile targets for running test subsets
- Shared test fixtures via `conftest.py` (database sessions, FastAPI test client)
- Example passing tests at each level (unit, integration, component, e2e)

**Non-Goals:**
- Changing the production or local dev database (PostgreSQL via Docker stays)
- Adding test coverage reporting (pytest-cov is already a dep, can be done later)
- CI/CD pipeline configuration
- Changing Alembic migration workflow
- Adding new linting tools (ruff + ESLint + Prettier are sufficient)

## Decisions

### 1. SQLite in-memory for all backend tests

**Choice:** In-memory SQLite (`sqlite://` with `StaticPool`) configured via `conftest.py` fixtures.

**Rationale:**
- Fast (no disk I/O, no Docker dependency)
- Already used ad-hoc in `test_session.py` and `test_models.py`
- Isolation: each test session gets a fresh database
- `make test` works without Docker running

**Alternatives considered:**
- File-based SQLite (`sqlite:///test.db`): slower, requires cleanup, harder to debug. Chosen against.
- Docker PostgreSQL for integration tests: adds friction to `make test`, requires Docker running. Chosen against for now; can be added as a separate `make test-integration-pg` target later if needed.
- Testcontainers: heavyweight dependency, overkill for this project size.

### 2. Vitest for frontend component testing

**Choice:** Vitest with jsdom environment, `@testing-library/react`, `@testing-library/jest-dom`.

**Rationale:**
- Native Vite integration (same config shape, fast HMR for tests)
- Jest-compatible API (familiar, well-documented)
- Already the standard choice for Vite projects
- Lightweight compared to Jest + ts-jest + babel overhead

**Alternatives considered:**
- Jest with ts-jest: works but requires separate transform config, slower in Vite projects. Chosen against.
- No frontend unit tests: violates TDD mandate. Not acceptable.

### 3. conftest.py with shared fixtures

**Choice:** Single `backend/tests/conftest.py` providing:
- `db_session` fixture: creates tables in SQLite, yields session, tears down
- `client` fixture: FastAPI TestClient with overridden `get_db` dependency
- `setup_test_db` session-scoped fixture for expensive setup

**Rationale:**
- Follows pytest conventions
- `httpx.AsyncClient` already available as dev dependency for async tests
- Dependency override pattern (`app.dependency_overrides[get_db]`) is the FastAPI-recommended approach

### 4. Test directory structure

```
backend/
  tests/
    __init__.py              (new)
    conftest.py              (new - shared fixtures)
    test_smoke.py            (existing)
    test_api.py              (existing)
    test_config.py           (existing)
    test_schemas.py          (existing)
    test_models.py           (existing)
    test_deps.py             (existing)
    test_session.py          (existing - refactor to use conftest fixtures)
    test_alembic.py          (existing)
    test_ml_boundary.py      (existing)
    test_ruff_compliance.py  (existing)
    integration/
      __init__.py            (new)
      test_health.py         (new - example integration test)

frontend/
  src/
    __tests__/
      App.test.tsx           (new - example component test)
  e2e/
    smoke.spec.ts            (existing)
```

### 5. Makefile granular targets

```
make test              # everything (existing)
make test-unit         # backend unit tests only (pytest --ignore=tests/integration)
make test-integration  # backend integration tests only (pytest tests/integration)
make test-e2e          # frontend e2e tests (playwright test)
make test-frontend     # frontend component tests (vitest run)
make lint              # existing
```

### 6. Vitest configuration

**Choice:** Separate `vitest.config.ts` extending the Vite config pattern.

**Rationale:**
- Keeps `vite.config.ts` clean for production builds
- Vitest config adds `test` block with jsdom environment and setup files
- Test files discovered by `**/*.test.{ts,tsx}` pattern in `src/`

## Risks / Trade-offs

- **[SQLite vs PostgreSQL behavioral differences]** → Some PostgreSQL-specific features (JSONB, arrays, certain constraints) won't be testable with SQLite. Mitigation: integration tests against SQLite cover 90% of cases; add a `make test-integration-pg` target later if PostgreSQL-specific behavior needs testing.

- **[Vitest test isolation with global state]** → React component tests may share state if not properly isolated. Mitigation: Vitest resets module state between tests by default; use `beforeEach` for cleanup.

- **[Existing tests may break with conftest.py]** → Adding `conftest.py` with session-scoped fixtures could interfere with existing tests that create their own engines. Mitigation: existing tests use local `sqlite://` and don't depend on conftest fixtures; they'll continue to work unchanged.

- **[No coverage threshold enforcement]** → pytest-cov is available but not enforced. Mitigation: can add `--cov` flags and minimum thresholds later without changing this design.
