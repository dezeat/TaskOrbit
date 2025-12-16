# --- Variables ---
PYTHON := python3
POETRY := poetry

# Defaults (can be overridden via environment variables)
DB_CONFIG ?= app/utils/db/default_db_config.yaml
HOST ?= 127.0.0.1
PORT ?= 5000

# Extract the database path from the yaml config for safe deletion
# This reads the 'host' and 'name' keys from the yaml and combines them.
DB_PATH := $(shell grep "host:" $(DB_CONFIG) | awk '{print $$2}')/$(shell grep "name:" $(DB_CONFIG) | awk '{print $$2}')

# --- Phony Targets ---
.PHONY: help setup start dev seed reset launch format lint type test clean check

# --- Default Target ---
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Setup & Run ---
setup: ## Install dependencies using Poetry
	@echo "Installing dependencies..."
	$(POETRY) install

start: ## Start the app in production mode
	@echo "Starting app (Production Mode)..."
	FLASK_DEBUG=0 $(POETRY) run $(PYTHON) main.py $(DB_CONFIG)

dev: ## Start the app in development mode with auto-reload
	@echo "Starting dev server on http://$(HOST):$(PORT)"
	FLASK_DEBUG=1 FLASK_HOST=$(HOST) FLASK_PORT=$(PORT) $(POETRY) run $(PYTHON) main.py $(DB_CONFIG)

# --- Database Management ---
seed: ## Seed the database with initial data
	@echo "Seeding database from $(DB_CONFIG)..."
	$(POETRY) run $(PYTHON) -m app.utils.db.seed $(DB_CONFIG)

reset: ## Delete the SQLite database file
	@if [ -f "$(DB_PATH)" ]; then \
		rm "$(DB_PATH)"; \
		echo "Deleted database at $(DB_PATH)"; \
	else \
		echo "No database found at $(DB_PATH) to delete."; \
	fi

rebuild: reset seed ## Delete DB, re-seed, and get ready
	@echo "Database rebuild complete."

launch: rebuild dev ## Reset DB, seed, and start dev server

# --- Quality Assurance ---
format: ## Run Ruff to format code
	@echo "Formatting code..."
	$(POETRY) run ruff format .

lint: ## Run Ruff to check for linting errors
	@echo "Linting code..."
	$(POETRY) run ruff check .

type: ## Run Mypy for static type checking
	@echo "Checking types..."
	$(POETRY) run mypy ./app

test: ## Run tests with Pytest
	@echo "Running tests..."
	$(POETRY) run pytest

check: format lint type test ## Run all QA checks (format, lint, type, test)

clean: ## Clean up cache and temporary files
	@echo "Cleaning artifacts..."
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf .ruff_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "Done."