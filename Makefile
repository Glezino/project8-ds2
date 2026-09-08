.PHONY: help setup start stop test lint clean

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

setup: ## Install dependencies and configure the environment
	@echo "Installing backend dependencies (uv sync)..."
	cd backend && uv sync
	@echo "Installing frontend dependencies (npm install)..."
	cd frontend && npm install
	@if [ ! -f .env ]; then echo "Creating .env from .env.example..."; cp .env.example .env; else echo ".env already exists, skipping."; fi

start: ## Start the backend and frontend dev servers
	@echo "Starting backend (uvicorn) on http://localhost:8000..."
	@mkdir -p .run
	@cd backend && nohup uv run uvicorn app.main:app --host $${API_HOST:-0.0.0.0} --port $${API_PORT:-8000} > $(CURDIR)/.run/backend.log 2>&1 </dev/null &
	@echo "Starting frontend (vite) on http://localhost:5173..."
	@cd frontend && nohup npm run dev > $(CURDIR)/.run/frontend.log 2>&1 </dev/null &
	@echo "Services started. Logs in .run/. Use 'make stop' to stop them."

stop: ## Stop the backend and frontend dev servers
	@for pid in $$(netstat -ano 2>/dev/null | grep 'LISTENING' | grep -E ':8000|:5173' | awk '{print $$NF}' | sort -u); do taskkill //F //PID $$pid >/dev/null 2>&1; done
	@echo "Services stopped."

test: ## Run the backend and frontend test suites
	@echo "Running backend tests (pytest)..."
	cd backend && uv run pytest
	@echo "Running frontend end-to-end tests (Playwright)..."
	cd frontend && npm run test:e2e

lint: ## Run the backend and frontend linters and formatters
	@echo "Running backend ruff check..."
	cd backend && uv run ruff check .
	@echo "Running backend ruff format check..."
	cd backend && uv run ruff format --check .
	@echo "Running frontend eslint..."
	cd frontend && npm run lint
	@echo "Running frontend prettier check..."
	cd frontend && npm run format:check

clean: ## Remove install artifacts and caches
	@echo "Removing backend virtual environment..."
	rm -rf backend/.venv
	@echo "Removing frontend node_modules..."
	rm -rf frontend/node_modules
	@echo "Removing caches..."
	rm -rf backend/.pytest_cache backend/.ruff_cache frontend/dist frontend/test-results frontend/playwright-report .run
	@echo "Done."
