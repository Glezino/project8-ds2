.PHONY: help setup start stop test lint clean

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

setup: ## Install dependencies and configure the environment
	@echo "Setting up the project..."
	@echo "Frontend: npm install"
	@echo "Backend: create venv and install dependencies"

start: ## Start all services
	@echo "Starting services with Docker Compose..."

stop: ## Stop all services
	@echo "Stopping services..."

test: ## Run the test suite
	@echo "Running backend tests (pytest)..."
	@echo "Running end-to-end tests (Playwright)..."

lint: ## Run the linter
	@echo "Running linters..."

clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."