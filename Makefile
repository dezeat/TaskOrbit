

PYTHON := python3
DB_CONFIG ?= app/utils/db/default_db_config.yaml
HOST ?= 127.0.0.1
PORT ?= 5000
DB_PATH := $(shell grep "host:" $(DB_CONFIG) | awk '{print $$2}')/$(shell grep "name:" $(DB_CONFIG) | awk '{print $$2}')

.PHONY: help setup start dev seed reset rebuild launch format lint type test check clean checkfix

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Install dependencies
	poetry install

start: ## Start app (prod)
	FLASK_DEBUG=0 poetry run $(PYTHON) main.py $(DB_CONFIG)

dev: ## Start app (dev)
	FLASK_DEBUG=1 FLASK_HOST=$(HOST) FLASK_PORT=$(PORT) poetry run $(PYTHON) main.py $(DB_CONFIG)

seed: ## Seed database
	poetry run $(PYTHON) -m app.utils.db.seed $(DB_CONFIG)

reset: ## Delete SQLite DB file
	@if [ -f "$(DB_PATH)" ]; then rm "$(DB_PATH)"; fi

rebuild: reset seed ## Reset DB and seed

launch: rebuild dev ## Reset DB, seed, and start dev server

format: ## Format code
	poetry run ruff format .

lint: ## Lint code
	poetry run ruff check .

type: ## Type check
	poetry run mypy ./app

test: ## Run tests
	poetry run pytest

check: format lint type test ## Run all QA checks

clean: ## Clean cache/temp files
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

checkfix: ## Auto-fix lint issues
	poetry run ruff check --fix .