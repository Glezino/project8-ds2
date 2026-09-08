## 1. Setup Repository

- [x] 1.1 Create a new GitHub repository named `project8-ds2` (or appropriate name) and clone it locally. Verify by running `git remote -v` and confirming the origin URL.
- [x] 1.2 Initialise Git in the repository (if not already) with `git init`. Verify that a `.git` folder exists.

## 2. Create Project Structure

- [x] 2.1 Add top‑level directory `frontend/`. Verify with `ls frontend` (should be empty).
- [x] 2.2 Add top‑level directory `backend/`. Verify with `ls backend`.
- [x] 2.3 Add `backend/ml/` directory. Verify with `ls backend/ml`.

## 3. Add Documentation and Configuration Files

- [x] 3.1 Create `README.md` with project overview and quick‑start instructions. Verify that the file exists and contains a heading (`# Project8 DS2`).
- [x] 3.2 Create `.gitignore` using a combined Python/Node template. Verify that common patterns (e.g., `__pycache__/`, `node_modules/`) are present.
- [x] 3.3 Create `.env.example` with placeholder environment variable comments. Verify that the file contains at least one comment line starting with `#`.

## 4. Git Branches and Initial Commit

- [x] 4.1 Create a new branch `chore/DS-2-initial-setup`. Verify with `git branch` that the branch exists.
- [x] 4.2 Stage all scaffold files (`git add .`). Verify that `git status` shows no untracked files.
- [x] 4.3 Make the initial Conventional Commit: `git commit -m "chore(DS-2): initial project scaffold"`. Verify that the commit appears in `git log -1`.
- [x] 4.4 Push the branch to GitHub (`git push -u origin chore/DS-2-initial-setup`). Verify that the remote branch appears on GitHub.

## 5. Verify Reproducibility

- [x] 5.1 Run the project's `make help` to ensure the Makefile is accessible. Verify that the command exits with status 0 and lists available targets.
- [x] 5.2 Clone the repository in a fresh directory, checkout `chore/DS-2-initial-setup`, and run `make setup` (or the appropriate setup target). Verify that the command completes without errors and that the expected directories and files are present.