# Dev Environment Specification

## Purpose

Defines the reproducible local development environment for the project: dependency installation, standardized command targets, environment-variable configuration, and documented setup so any developer can start working from a fresh clone.

## Requirements

### Requirement: Backend dependencies install reproducibly
The system SHALL install all backend and ML dependencies from a single dependency manifest using `uv` without requiring manual steps beyond a standard setup command.

#### Scenario: Fresh clone backend setup
- **GIVEN** a fresh checkout of the repository on a machine with Python 3.12, `uv`, and `make` available
- **WHEN** the developer runs `make setup`
- **THEN** a virtual environment is created and all declared backend dependencies are installed without errors

### Requirement: Frontend dependencies install reproducibly
The system SHALL install all frontend dependencies from a committed lockfile/manifest using the package manager defined for the project without requiring manual steps beyond a standard setup command.

#### Scenario: Fresh clone frontend setup
- **GIVEN** a fresh checkout of the repository on a machine with Node.js and the project package manager available
- **WHEN** the developer runs `make setup`
- **THEN** all declared frontend dependencies are installed without errors

### Requirement: Standardized development commands
The system SHALL provide Makefile targets for the common tasks: dependency setup, starting/stopping the services, running the test suite, and running the linter.

#### Scenario: Help lists standard targets
- **GIVEN** the repository is checked out
- **WHEN** the developer runs `make help`
- **THEN** the available targets for setup, start, stop, test, and lint are listed

#### Scenario: Running the test suite
- **GIVEN** the repository is checked out and dependencies are installed
- **WHEN** the developer runs `make test`
- **THEN** the backend test suite runs and any configured end-to-end tests are executed, reporting success or failure

#### Scenario: Running the linter
- **GIVEN** the repository is checked out and dependencies are installed
- **WHEN** the developer runs `make lint`
- **THEN** the backend and frontend linters run and report any violations, exiting non-zero if violations are found

### Requirement: Environment configuration through .env
The system SHALL read environment configuration from a local `.env` file at the repository root, and SHALL provide a committed `.env.example` that documents every required variable with placeholder values.

#### Scenario: Configure environment from example
- **GIVEN** a `.env.example` file exists at the repository root documenting all required variables
- **WHEN** the developer copies it to `.env` and fills in real values
- **THEN** the services read their configuration from the `.env` file

#### Scenario: Sensitive values not committed
- **GIVEN** the repository is configured with the standard ignore rules
- **WHEN** the developer creates a local `.env` file
- **THEN** the `.env` file is ignored by version control and never committed

### Requirement: Local development tools documented
The system SHALL document the required development tools (Python version, uv, Node.js, package manager, Make) and the local setup steps in the repository documentation.

#### Scenario: Prerequisites are documented
- **GIVEN** the repository documentation
- **WHEN** a new developer reads the setup section
- **THEN** the required tools and versions are listed along with the concrete steps to run the project locally

### Requirement: Docker Compose provides the application startup path
The system SHALL provide a Docker Compose startup path that brings up the database, backend, and frontend services for local development, in addition to the existing host-based `make start` path.

#### Scenario: Compose starts all application services
- **GIVEN** a Docker Compose configuration covering `db`, `backend`, and `frontend`
- **WHEN** the developer runs the Compose start command
- **THEN** the database, backend, and frontend services all start together

#### Scenario: Compose and make startup paths coexist
- **GIVEN** both the Docker Compose configuration and the Makefile targets exist
- **WHEN** the developer uses either the Compose start command or `make start`
- **THEN** both paths remain available and documented