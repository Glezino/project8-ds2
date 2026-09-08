## ADDED Requirements

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
