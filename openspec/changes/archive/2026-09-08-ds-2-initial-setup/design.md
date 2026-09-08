## Context

The repository currently contains only the OpenSpec configuration and the .opencode tooling. There are no `frontend/`, `backend/`, or `backend/ml/` directories, no README, and no Git history beyond the initial commit used to bootstrap the tooling.

## Goals / Non-Goals

**Goals:**
- Create a new GitHub repository and initialise it with a `main` branch.
- Add top‑level directories `frontend/`, `backend/`, and `backend/ml/` to separate responsibilities as defined in the project stack.
- Add common project files: `README.md`, `.gitignore`, `.env.example`.
- Configure an initial Git branch for this change (`chore/DS-2-initial-setup`) and make an initial Conventional Commit (`chore(DS-2): initial project scaffold`).
- Document the repository layout and provide reproducible setup instructions in the README.

**Non‑Goals:**
- No application code or runtime functionality is added.
- No new third‑party dependencies are introduced.
- No CI/CD pipeline configuration is added at this stage.

## Decisions

- **Directory Structure:** Use the three top‑level directories `frontend/`, `backend/`, and `backend/ml/` as the canonical separation of concerns for the stack (React frontend, FastAPI backend, ML utilities).
- **Git Workflow:** Initialise the repository with `git init` and create a `main` branch. The change will be developed on a `chore/DS-2-initial-setup` branch and the first commit will follow the Conventional Commits format (`chore(DS-2): initial project scaffold`).
- **README Content:** Provide a brief project overview, a quick‑start guide that references the existing `Makefile` (`make setup`, `make start`), and a section linking to the proposal for motivation.
- **.gitignore:** Use a combined template covering Python, Node/TypeScript, and VSCode environment files. Include entries for `__pycache__/`, `.env`, `node_modules/`, `dist/`, and common IDE directories.
- **.env.example:** Add placeholder comment lines for environment variables that will be required by the services (e.g., `# DATABASE_URL=postgresql://...`). No actual secrets are included.
- **Branch Naming:** Follow the convention `<type>/DS-XX-<slug>`; for this change the slug is `initial-setup`.
- **Makefile Usage:** Leverage the existing `Makefile` (present in the repo) for local development; no changes are needed at this stage.

## Risks / Trade‑offs

- **Overly Generic .gitignore:** May omit project‑specific generated files. This risk is mitigated by allowing iterative refinement of the `.gitignore` as the project evolves.
- **Directory Choice Rigidity:** If future requirements demand additional top‑level domains (e.g., `infra/`), they can be added without breaking the current layout.
- **Initial Commit Convention:** The first commit sets a precedent; any deviation later could cause inconsistency. Enforcing Conventional Commits in CI will minimise drift.

No open questions remain; the design is complete and ready for task breakdown.
