# AGENTS.md

Instructions for any AI agent (OpenCode or otherwise) working in this repository.

## 1. Agent's Role in the Workflow

This agent is responsible for: exploring the codebase and Jira history, generating the OpenSpec artifacts (proposal, specs, design, tasks), implementing the code following TDD, running lint and tests, making commits, and opening the Pull Request.

**The agent NEVER merges a PR.** It opens the PR and stops: review and merge are always manual.

**The agent never pushes directly to** **`main`** **or** **`develop`****.** All changes go through a feature branch and a PR.

**The agent prepares everything (branch, code, tests, commits, verified PR), but the merge and updating the status of the Jira issue are always done manually by the user.**

## 2. Project Stack and Structure

* Frontend: `frontend/` — React (Vite), TypeScript, Tailwind, Shadcn/ui, Axios, React Router DOM
* Backend: `backend/` — Python, FastAPI, Pydantic, SQLAlchemy, Alembic
* Machine Learning: `backend/ml/` — Polars, Scikit-learn, XGBoost, Optuna, Seaborn, Matplotlib
* Database: Supabase (Postgres) in production, PostgreSQL in a Docker container for development
* Infrastructure: each service has its own Docker container (so it can be started in isolation); `docker-compose.yml` starts all services for local development
* Automation: `Makefile` with setup, installation, service startup, and test commands (check the Makefile or run `make help` to see the available commands before using standalone docker/pip/npm commands directly)

Before creating a new abstraction, component, service, utility, dependency, or layer, **check whether an existing project pattern already solves the problem**. Prioritize DRY and KISS over adding new code.

## 3. Complete Workflow (per Jira Issue)

Each development task starts from a Jira issue (e.g. `DS-10`) and follows these phases in order.

### Phase 0 — Explore

The issue is defined in Jira first. Once it is ready, the user provides its contents to the agent (code, title, description, acceptance criteria) and runs `/openspec-explore` to start the exploration and begin defining the technical contract.

In this phase, investigate:

* The Jira issue content provided by the user.
* Existing specs in `openspec/specs/` related to that area.
* The relevant current code (folders, patterns, and similar components that have already been implemented).

Do not invent acceptance criteria that were not provided; if anything is unclear, ask before proceeding to the proposal phase.

### Phase 1 — Propose

```bash
openspec new change ds-10-<short-slug>
openspec instructions proposal --change ds-10-<short-slug>
```

Write `proposal.md`, including `jira: DS-10` in the frontmatter and the exact scope of the issue.

### Phase 2 — Specs, Design, and Tasks

```bash
openspec instructions specs  --change ds-10-<short-slug>
openspec instructions design --change ds-10-<short-slug>
openspec instructions tasks  --change ds-10-<short-slug>
```

Follow the rules in `openspec/config.yaml` for each artifact. Check progress with:

```bash
openspec status --change ds-10-<short-slug>
```

Before moving on to implementation, present the artifacts (proposal, specs, design, tasks) for the user to review, unless explicitly instructed to skip the review.

### Phase 3 — Implement (TDD)

For each task in `tasks.md`:

1. Write the corresponding test (pytest for backend/ML, Playwright for e2e) and confirm that it fails.
2. Implement the minimum code required to make the test pass.
3. Refactor if necessary, keeping the tests green.
4. Mark the task as completed in `tasks.md` only when its test is green.

### Phase 4 — Pre-Commit Verification

Before committing:

```bash
make lint
make test
```

(or the equivalent commands defined in the project's Makefile). Do not continue if anything fails.

### Phase 5 — Branch, Commits, and PR

See the exact conventions in Section 4. Once all tasks in the change are complete:

* Make sure lint and tests pass locally.
* Push the branch.
* Open the PR linking the Jira issue.
* **Stop here.** Do not merge or approve the PR yourself — wait for human review.

### Phase 6 — Archive (After Merge)

Once the PR has been merged (confirmed by the user), archive the change:

```bash
openspec archive ds-10-<short-slug>
```

## 4. Git Conventions and Jira Traceability

* **Branch**: `<type>/DS-XX-<short-slug>` — e.g. `feature/DS-10-login-form`
  Types: `feature`, `fix`, `chore`, `refactor`, `docs`, `test`
* **Commits**: Conventional Commits using the Jira issue code as the scope: `<type>(DS-XX): <description in imperative form>` — e.g. `feat(DS-10): add login form validation`
* **Pull Request**: title using the same format as the main commit, e.g. `feat(DS-10): add login form validation`. The PR description must link the Jira issue and summarize what changes and why (the how is already documented in `design.md`).
* The Jira issue code must always appear in the branch, commits, and PR — this is the minimum required traceability, even without automatic integration with the Jira API.

## 5. Testing

* Backend and ML: `pytest`. Every new module in `backend/` or `backend/ml/` must include its tests alongside the code, not as a final step added at the end.
* Frontend and end-to-end flows: `Playwright`.
* Do not commit code without its corresponding tests or while the test suite is failing.

## 6. What This Agent MUST NOT Do

* Do not merge or approve Pull Requests: the user always performs the merge after reviewing that lint and tests pass.
* Do not push directly to `main` or `develop`.
* Do not skip lint or tests to "move faster".
* Do not create a new dependency, service, or abstraction layer without first checking whether an existing pattern already covers it.
* Do not modify the status of Jira issues: the user is responsible for manually updating task statuses in Jira. Jira traceability is limited to the identifier in the branch, commits, and PR.
