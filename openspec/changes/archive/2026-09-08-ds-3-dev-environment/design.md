## Context

The repository is a greenfield scaffold from DS-2: `frontend/`, `backend/`, and `backend/ml/` exist but contain only `.gitkeep` files, the root `Makefile` targets only print placeholder text, and `.env.example` documents the required variables as comments. No dependency manifest, lockfile, or transitive tooling configuration exists anywhere. This design converts that scaffolding into a reproducible developer environment without adding Docker services or application code (see proposal.md — Why).

## Goals / Non-Goals

**Goals:**
- Backend installable and testable via `uv` from a single `pyproject.toml` targeting Python 3.12.
- Frontend installable and testable via npm from a Vite + React + TypeScript project.
- Linting/formatting configured for both stacks around a single shared report command (`make lint`).
- Environment configuration centralized in `.env`, with `.env.example` as the documented source of truth.
- Real Makefile targets replacing the placeholders; setup steps documented in the README.

**Non-Goals:**
- No application code, API endpoints, or UI features.
- No Docker services or `docker-compose.yml` (deferred; `make start/stop` run dev servers directly until then).
- No CI/CD pipeline configuration.
- No Alembic migrations or database schema.

## Decisions

### D1. Backend with `uv` and a single flat `pyproject.toml`
Initialize the backend at `backend/` with `uv` (`uv init --python 3.12`), declare all runtime and dev dependencies in one `pyproject.toml`, and pin resolutions in a committed `uv.lock`. Dependencies:
- Runtime: `fastapi`, `uvicorn[standard]`, `pydantic`, `pydantic-settings`, `sqlalchemy`, `alembic`
- ML: `polars`, `scikit-learn`, `xgboost`, `optuna`, `seaborn`, `matplotlib`
- Dev: `pytest`, `pytest-cov`, `httpx` (for TestClient), `ruff`

Rationale: `uv` is specified by DS-3, is materially faster than `pip`/`poetry`, and `uv.lock` guarantees reproducible installs. ML dependencies stay flat (as decided) to keep a single dependency set for every developer, accepting a heavier install in exchange for simplicity.
*Alternative considered:* ML deps in a `[project.optional-dependencies] ml` group — rejected by decision; keeps the manifest single-source.

> **Note for the apply phase:** installing `xgboost` + `optuna` + `matplotlib` on a fresh machine can be slow; this is expected and must not be treated as a failure.

### D2. Ruff for backend linting/formatting
Configure `ruff` (lint + format) entirely inside `pyproject.toml` under `[tool.ruff]`. Targets: default `E`/`F` rule sets, line length 100, format enabled. Runs via `ruff check` and `ruff format --check`.
Rationale: replaces `black` + `flake8` + `isort` with one fast tool (decided); the codebase is greenfield so no legacy config migration exists.

### D3. Frontend with Vite + TypeScript
Scaffold the React application with the Vite `react-ts` template in `frontend/` (`npm create vite@latest . -- --template react-ts`). TypeScript in strict mode (template default, kept). Add `react-router-dom` (latest v7) for routing and `axios` for HTTP. `package-lock.json` is committed for reproducible installs.
Rationale: the stack is fixed by the project (React, Vite, TypeScript, React Router DOM, Axios).

### D4. Tailwind CSS v4 + shadcn/ui
Install Tailwind CSS v4 via the `@tailwindcss/vite` plugin (registered in `vite.config.ts`) and `tailwindcss` + `@tw-animate-css` (or the v4-compatible transition helper) as dependencies. Then run `npx shadcn@latest init` to set up components.json and the `src/components` alias, adding a couple of baseline components.
Rationale: Tailwind v4 is stable and natively supported by shadcn/ui; the Vite plugin removes the `postcss`/`autoprefixer` config boilerplate. If `shadcn init` requires interactive prompts during apply, use its CLI flags / a non-interactive path.
*Alternative considered:* Tailwind v3.4 + PostCSS + `tailwindcss-animate` — older but more battle-tested; rejected to avoid scaffolding with an already-superseded major version.

### D5. ESLint 9 (flat config) + Prettier for the frontend
Use ESLint 9 with flat config (`eslint.config.js`), `typescript-eslint`, `eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`, `eslint-config-prettier`, and Prettier for formatting. Scripts: `lint`, `format:check`. The Vite template's ESLint setup is upgraded to flat config if the scaffolded version differs.
Rationale: industry standard for React/TS (decided); Prettier handles formatting while ESLint handles rules, keeping the toolset auditable.

### D6. Component architecture placeholders
No component architecture is designed yet; shadcn/ui's default `@/` alias and `src/components/ui` convention are adopted so future changes follow it (DRY check: this reuses shadcn's standard layout instead of inventing one).

### D7. Environment variables via `.env`
- Backend: `pydantic-settings` loads `backend/.env` (or the repo-root `.env` — one source, decided below); replace `os.environ` reads.
- Frontend: Vite loads `.env` automatically; only `VITE_*` prefixed variables are exposed to the client.
- One repo-root `.env` file is the single source used by both stacks; `cp .env.example .env` is the documented flow. `.env.example` (created in DS-2) is updated to reflect the variables actually consumed by the configured services (e.g. `DATABASE_URL`, `API_HOST`, `API_PORT`, `DEBUG`. `VITE_API_URL`).
Rationale: a single root `.env` avoids two files drifting apart and matches the existing `.gitignore` (`/.env`). `pydantic-settings` can be pointed at any path, so root-level works for the backend too.
*Alternative considered:* separate `backend/.env` + `frontend/.env` — rejected; adds duplication for no current benefit.

### D8. Real Makefile targets
Replace placeholder bodies with functional targets, keeping the existing `help` self-documentation pattern:
- `setup` — `uv sync` in `backend/`, `npm install` in `frontend/`, copy `.env.example` → `.env` if missing.
- `start` / `stop` — run/stop the two dev servers (backend `uvicorn` via `uv run`, frontend `vite`), noting that Docker orchestration arrives with a later Docker change.
- `test` — `pytest` in `backend/`, Playwright e2e in `frontend/`.
- `lint` — `uv run ruff check backend/` + `uv run ruff format --check` + frontend `npm run lint` + `npm run format:check`.
- `clean` — remove install artifacts (`backend/.venv`, `frontend/node_modules`, caches).
The Makefile lives at the repo root so all targets are documented in one place (matching DS-2 precedent).

### D9. Documentation
Update the README: prerequisites (Python 3.12, `uv`, Node.js 18+/20+, npm, Make), the exact setup flow, the `make` targets table, and where env variables live. Keep DS-2's structure overview.

## Risks / Trade-offs

- [Tailwind v4 + shadcn/ui incompatibilities or interactive `shadcn init` prompts] → Mitigation: install exact current shadcn v4-compatible versions; if CLI prompts block automation, pass explicit flags or use the documented manual init steps for the apply phase.
- [Heavy ML installs (`xgboost`, `optuna`, `matplotlib`, `scikit-learn`) slow down every `uv sync`] → Mitigation: accepted trade-off of the flat-manifest decision; `uv.lock` ensures repeatability and caching keeps rebuilds fast.
- [`make start` launching two background dev servers can outlive/linger] → Mitigation: `stop` target kills both; consider `uvicorn --reload` and `vite` used as foreground targets with `start`/`stop` documented as dev conveniences until Docker orchestration exists.
- [`.env` secret leakage] → Mitigation: `.gitignore` already ignores `.env`; the spec scenario covers the no-commit guarantee.

## Migration Plan

Greenfield change; nothing to migrate. Rollback is trivial: files added are removed by discarding the feature branch.

## Open Questions

None — remaining unknowns (exact package versions resolved at install time, Playwright browser download) do not change the design or task breakdown.