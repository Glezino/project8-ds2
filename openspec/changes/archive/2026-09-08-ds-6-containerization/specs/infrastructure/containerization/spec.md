## Purpose

Defines the containerized development stack: building the backend and frontend Docker images, starting the full db/backend/frontend stack through Docker Compose, wiring service communication and environment configuration, and providing health reporting for the running services.

## ADDED Requirements

### Requirement: Backend container builds and runs the FastAPI app
The system SHALL build a backend Docker image that installs all declared backend and ML dependencies and serves the FastAPI application over HTTP.

#### Scenario: Build backend image
- **GIVEN** a backend `Dockerfile` exists in the repository
- **WHEN** the developer builds the backend image
- **THEN** the build completes successfully and the image contains all declared dependencies and the FastAPI application

#### Scenario: Run backend container
- **GIVEN** a successfully built backend image
- **WHEN** a container is started from that image
- **THEN** the FastAPI application serves requests on the configured HTTP port

### Requirement: Frontend container builds and serves the static app
The system SHALL build a frontend Docker image that compiles the Vite/TypeScript application and serves the resulting static files over HTTP.

#### Scenario: Build frontend image
- **GIVEN** a frontend `Dockerfile` exists in the repository
- **WHEN** the developer builds the frontend image
- **THEN** the build completes successfully and the image contains the compiled static application

#### Scenario: Serve static frontend
- **GIVEN** a successfully built frontend image
- **WHEN** a container is started from that image
- **THEN** the static application is served over HTTP

### Requirement: Docker Compose starts the full development stack
The system SHALL provide a Docker Compose configuration that starts the database, backend, and frontend services together for local development.

#### Scenario: Start the full stack
- **GIVEN** a Docker Compose configuration at the repository root covering `db`, `backend`, and `frontend`
- **WHEN** the developer runs the Compose start command
- **THEN** all three services start and remain running

#### Scenario: Stop the full stack
- **GIVEN** the full stack is running
- **WHEN** the developer runs the Compose stop command
- **THEN** all three services stop cleanly

### Requirement: Services communicate over Docker networking
The system SHALL place the services on a shared Docker network so they can reach each other by service name, without exposing internal service ports to the host.

#### Scenario: Backend reaches the database by service name
- **GIVEN** the full stack is running on a shared Docker network
- **WHEN** the backend connects to the database using the database service name
- **THEN** the connection is established without using a host-visible database port

#### Scenario: Frontend build reaches the backend
- **GIVEN** the full stack is running
- **WHEN** the frontend build resolves the backend URL
- **THEN** the backend is reachable from the frontend context

### Requirement: Environment variables are configurable
The system SHALL make backend and frontend runtime configuration injectable through environment variables, sourced from the repository `.env` file.

#### Scenario: Configure services from .env
- **GIVEN** a `.env` file at the repository root with service configuration values
- **WHEN** the developer starts the stack with Docker Compose
- **THEN** the services read their configuration from the provided environment variables

#### Scenario: Defaults apply without .env
- **GIVEN** no `.env` file or with some values missing
- **WHEN** the developer starts the stack with Docker Compose
- **THEN** the services start using sensible default values and document the available overrides

### Requirement: Development volumes preserve hot-reload
The system SHALL mount backend and frontend source directories into their containers during development so that source changes are reflected without rebuilding the image.

#### Scenario: Backend source change without rebuild
- **GIVEN** the development stack is running with the backend source mounted
- **WHEN** the developer edits a backend source file
- **THEN** the development server reloads the change without requiring an image rebuild

#### Scenario: Frontend source change without rebuild
- **GIVEN** the development stack is running with the frontend source mounted
- **WHEN** the developer edits a frontend source file
- **THEN** the development server reflects the change without requiring an image rebuild

### Requirement: Services report health
The system SHALL provide health checks for the running services so that their readiness can be observed by Docker Compose.

#### Scenario: Backend reports healthy
- **GIVEN** the full stack is running
- **WHEN** Docker evaluates the backend health check
- **THEN** the backend reports healthy when the application responds successfully on its health endpoint

#### Scenario: Frontend reports healthy
- **GIVEN** the full stack is running
- **WHEN** Docker evaluates the frontend health check
- **THEN** the frontend reports healthy when the served application responds successfully

#### Scenario: Database reports healthy
- **GIVEN** the full stack is running
- **WHEN** Docker evaluates the database health check
- **THEN** the database reports healthy when it accepts connections
