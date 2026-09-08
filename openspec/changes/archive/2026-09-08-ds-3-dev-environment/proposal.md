---
jira: DS-3
---

## Why

The repository currently contains only the DS-2 scaffolding (empty `frontend/`, `backend/`, and `backend/ml/` directories, a placeholder Makefile whose targets only print text, and a `.env.example` with commented placeholders). There is no reproducible way to install dependencies, no standard commands to build, test, or lint, and no configured environment-variable handling, so development cannot start.

## What Changes

- Initialize the backend as a Python 3.12 project managed with `uv`, declaring all dependencies (FastAPI stack + ML stack + test tooling) in a single `pyproject.toml`.
- Configure backend linting/formatting with `ruff`.
- Initialize the frontend as a React application with Vite, TypeScript, Tailwind CSS, shadcn/ui, React Router DOM, and Axios.
- Configure frontend linting/formatting with ESLint and Prettier.
- Configure environment-variable handling through `.env` and a maintained `.env.example`.
- Replace the placeholder Makefile targets with real commands for setup, service start/stop, testing, and linting.
- Document the local development setup in the README.

## Capabilities

### New Capabilities

- `dev-environment`: Reproducible local development environment — dependency installation, standardized command targets, environment-variable configuration, and documented setup for both the frontend and backend.

### Modified Capabilities

<!-- No existing capability specifications are affected; openspec/specs/ is currently empty. -->

## Impact

- **Backend** (`backend/`): introduces `pyproject.toml`, a `uv`-managed virtual environment, and ruff configuration; no runtime application code yet.
- **Frontend** (`frontend/`): introduces a Vite/React/TypeScript project with Tailwind, shadcn/ui, React Router, Axios, ESLint, and Prettier configuration; minimal entry point only.
- **Infrastructure**: rewrites the root `Makefile` with functional targets; no Docker or database services are added in this change.
- **Configuration**: `.env.example` (minor updates if needed) is the source of truth for required environment variables.
- **Documentation**: README updated with the concrete local setup steps.