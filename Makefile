

PYTHON := python3
DB_CONFIG ?= app/utils/db/default_db_config.yaml
HOST ?= 127.0.0.1
PORT ?= 5000
DB_PATH := $(shell grep "host:" $(DB_CONFIG) | awk '{print $$2}')/$(shell grep "name:" $(DB_CONFIG) | awk '{print $$2}')

.PHONY: help setup start dev seed reset rebuild launch format ruff-check lint type test check clean checkfix

## Show this help message
help:
	@awk 'BEGIN {FS = ":"} /^## /{desc=substr($$0,4); getline; if ($$0 ~ /^[a-zA-Z0-9_-]+:/) {split($$0,a,":"); printf "\033[36m%-20s\033[0m %s\n", a[1], desc}}' $(MAKEFILE_LIST)

## Install dependencies
setup:
	poetry install

## Start app (prod)
start:
	FLASK_DEBUG=0 poetry run $(PYTHON) main.py $(DB_CONFIG)

## Start app (dev)
dev:
	FLASK_DEBUG=1 FLASK_HOST=$(HOST) FLASK_PORT=$(PORT) poetry run $(PYTHON) main.py $(DB_CONFIG)

## Seed database
seed:
	poetry run $(PYTHON) -m app.utils.db.seed $(DB_CONFIG)

## Delete SQLite DB file
reset:
	@if [ -f "$(DB_PATH)" ]; then rm "$(DB_PATH)"; fi

## Reset DB and seed
rebuild: reset seed

## Reset DB, seed, and start dev server
launch: rebuild dev

## Format code
format:
	poetry run ruff format .

## Check formatting (exit non-zero if formatting needed)
format-check:
	poetry run ruff format --check .

## Lint only `app`, `tests`, and `main.py`
ruff-check:
	poetry run ruff check app tests main.py

## Lint code
lint:
	poetry run ruff check .

## Type check
type:
	poetry run mypy ./app

## Run tests
test:
	poetry run pytest

## Run all QA checks (formatting is checked, not applied)
check: format-check lint type test

## Clean cache/temp files
clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

## Auto-fix lint issues
checkfix:
	poetry run ruff check --fix .