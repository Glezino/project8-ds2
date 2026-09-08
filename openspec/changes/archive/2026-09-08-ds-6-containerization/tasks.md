## 1. Backend Container

- [x] 1.1 Create `backend/.dockerignore` excluding `.venv`, `__pycache__`, caches, and ML artifacts so the build context stays small, and verify `docker build` uses only the intended context (e.g. `docker build` dry/output of context).
- [x] 1.2 Create `backend/Dockerfile` (uv-based, `python:3.12-slim`, `uv sync --frozen`, serve `app.main:app` via uvicorn) and verify `docker build --target backend backend` produces a backend image successfully.
- [x] 1.3 Run the built backend image and verify HTTP service works. Infra verification (manual): start the container and confirm uvicorn launches on the configured port; confirm no pytest/Playwright behavioral change (application code unchanged).

## 2. Frontend Container

- [x] 2.1 Create `frontend/.dockerignore` excluding `node_modules`, `dist`, `test-results`, and caches so the build context stays small, and verify the build context excludes those directories.
- [x] 2.2 Create `frontend/Dockerfile` (multi-stage: `node` build stage running `npm ci` + `npm run build`, then `nginx:alpine` serving `frontend/dist/`) plus `frontend/nginx.conf`, and verify `docker build frontend` produces a frontend image successfully.
- [x] 2.3 Run the built frontend image and verify the static app is served over HTTP (manual/`curl` check on the served port); confirm no Playwright behavioral change (application code unchanged).

## 3. Docker Compose Stack

- [x] 3.1 Extend root `docker-compose.yml` with `backend` and `frontend` services while keeping `db`, adding a shared `app-net` network, and remove the `db` host port in favor of internal-only access; verify `docker compose config` validates without errors.
- [x] 3.2 Configure service networking so frontend/backend/db resolve each other by service name over `app-net`; verify `docker compose config` shows the correct network wiring on each service.
- [x] 3.3 Wire environment variables: set `DATABASE_URL` in the `backend` service to the `db:5432` hostname using `${POSTGRES_*}` interpolation, and pass `VITE_API_URL` as a build arg to the frontend build stage; verify the resolved config in `docker compose config` shows the expected values.
- [x] 3.4 Add health checks (backend via `/api/v1/health`, frontend on its served port, db via `pg_isready`) and use `depends_on` for startup ordering; verify `docker compose config` lists healthchecks on each service.

## 4. Development Volumes and Override

- [x] 4.1 Create a git-ignored `docker-compose.override.yml` that bind-mounts `backend/` and `frontend/` and enables hot-reload (uvicorn `--reload`, vite HMR with `--host`); verify the override applies with `docker compose config` and that it is not tracked by git.

## 5. Validation

- [x] 5.1 Build all images: run `docker compose build` and verify backend and frontend images build successfully.
- [x] 5.2 Verify the complete stack: run `docker compose up -d` and confirm all three services reach a healthy state (`docker compose ps` shows healthy); then confirm the backend responds on `/api/v1/health` and the frontend serves the app over HTTP (manual/`curl` checks).
- [x] 5.3 Stop the stack cleanly: run `docker compose down` and verify all containers and the shared network are removed.
- [x] 5.4 Final gate: run `make lint` and `make test`, and confirm both pass before committing, with no application-code changes introduced by this change.

## 6. Finalization

- [x] 6.1 Update `docs/architecture.md` (ADR-5) to reflect that backend and frontend are now containerized and the full stack starts via Docker Compose, and verify the documentation matches the implemented layout.
- [x] 6.2 Verify the full change: mark this task complete only after 5.4 passes and all verification tasks (5.1–5.3) are green.
