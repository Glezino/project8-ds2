## 1. Backend Environment and Dependencies

- [x] 1.1 Initialize the Python project with uv in `backend/` (`uv init --python 3.12`), and verify `backend/pyproject.toml` and `backend/uv.lock` exist and `uv sync` completes without errors.
- [x] 1.2 Declare the FastAPI runtime dependencies (fastapi, uvicorn[standard], pydantic, pydantic-settings, sqlalchemy, alembic) in `backend/pyproject.toml`, and verify `uv lock` resolves and `uv sync` installs them.
- [x] 1.3 Declare the ML dependencies (polars, scikit-learn, xgboost, optuna, seaborn, matplotlib), and verify `uv sync` installs them without errors.
- [x] 1.4 Write a pytest smoke test (pytest) that imports the declared backend packages and asserts their importable versions, and verify the test passes with `uv run pytest` (confirms pytest + env work).

## 2. Backend Linting and Formatting

- [x] 2.1 Configure `ruff` (lint + format) in `backend/pyproject.toml` (`[tool.ruff]`), and verify the configuration loads with `uv run ruff check backend/` and `uv run ruff format --check backend/` against the current source.
- [x] 2.2 Add a ruff compliance test that runs `ruff check` on `backend/` (pytest subprocess), confirm it fails on a deliberately non-compliant snippet, then run it again green once the snippet is fixed (TDD style, ensures lint is enforced).

## 3. Frontend Application

- [x] 3.1 Scaffold the React + TypeScript application with Vite in `frontend/` (`npm create vite@latest . -- --template react-ts`), and verify `npm install` completes and `npm run dev`/`npm run build` succeed.
- [x] 3.2 Confirm TypeScript strict mode is active (default Vite template `tsconfig.json`) and `tsc --noEmit` passes on the scaffolded source.
- [x] 3.3 Install and configure Tailwind CSS (current v4) with the `@tailwindcss/vite` plugin, and verify a `@tailwind`-styled element renders in the built bundle.
- [x] 3.4 Install `react-router-dom` and wire a minimal route (e.g. `/`), verified by a Playwright smoke test that the routed page renders.
- [x] 3.5 Install `axios` and add a minimal typed API client module (no endpoints yet), verified by `tsc --noEmit` passing.
- [x] 3.6 Configure shadcn/ui (`npx shadcn@latest init`) and add one baseline component (e.g. button), and verify the component imports render without errors.

## 4. Frontend Linting and Formatting

- [x] 4.1 Configure ESLint 9 flat config (`eslint.config.js`) with typescript-eslint, react-hooks, react-refresh plugins, and verify `npm run lint` passes.
- [x] 4.2 Configure Prettier (`.prettierrc`, `format:check` script) and verify `npm run format:check` passes on the current source.

## 5. Environment-Variable Handling

- [x] 5.1 Configure backend env reading: add a pydantic-settings `Settings` model that loads the repo-root `.env` (DATABASE_URL, API_HOST, API_PORT, DEBUG), and verify with a pytest that settings load from a temporary `.env`.
- [x] 5.2 Confirm the frontend reads `VITE_API_URL` from `.env` (Vite convention with `import.meta.env`), verified by a Playwright test that the app exposes the configured value.
- [x] 5.3 Update `.env.example` to reflect the variables actually consumed by both stacks, and verify each documented variable matches what `make setup` expects and that `.env` is gitignored.

## 6. Makefile Commands

- [x] 6.1 Implement `make setup` (uv sync, npm install, copy `.env.example` → `.env` if absent) and verify it runs end-to-end on a fresh clone state.
- [x] 6.2 Implement `make start`/`make stop` (run/stop backend uvicorn and frontend vite dev servers) and verify both servers respond to health checks after start and are stopped after stop.
- [x] 6.3 Implement `make test` (pytest backend + Playwright frontend) and verify it runs both suites and reports exit codes.
- [x] 6.4 Implement `make lint` (ruff check + format check + npm lint + format check) and verify a lint violation causes a non-zero exit.
- [x] 6.5 Implement `make clean` (remove `.venv`, `node_modules`, caches) and verify artifacts are removed.
- [x] 6.6 Verify `make help` lists all targets with descriptions.

## 7. Documentation

- [x] 7.1 Update the README setup section with prerequisites (Python 3.12, uv, Node.js, npm, Make), the `make setup` flow, the target table, and `.env` usage, and verify the documented commands succeed when followed step by step.

## 8. Final Verification

- [x] 8.1 Run the full gate `make lint && make test` from a clean state and verify both exit 0 (no skipped tests, no lint findings).