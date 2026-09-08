---
jira: DS-2
---

## Why

We need to set up the project repository and initial structure so that development can begin, ensuring a clean separation of frontend, backend, and ML components, and that the repository can be reproducibly built on any developer’s machine.

## What Changes

- Create a new GitHub repository and initialize Git.
- Add top‑level directories: `frontend/`, `backend/`, and `backend/ml/`.
- Add common project files: `README.md`, `.gitignore`, `.env.example`.
- Configure initial Git branches and commit using Conventional Commits.
- Document the repository layout and setup steps.

## Capabilities

### New Capabilities
<!-- No new functional capabilities; this change only introduces project scaffolding. -->

### Modified Capabilities
<!-- No existing capabilities are modified. -->

## Impact

- Introduces the repository structure used by all subsequent changes.
- Affects CI/CD pipelines (future) and developer onboarding.
- No runtime code changes; only tooling and documentation.
