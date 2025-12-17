

PYTHON := python3
DB_FILE := taskorbit.db

.PHONY: help setup start dev seed reset rebuild launch format lint type test check clean

## Show help
help:
	@awk 'BEGIN {FS = ":"} /^## /{desc=substr($$0,4); getline; if ($$0 ~ /^[a-zA-Z0-9_-]+:/) {split($$0,a,":"); printf "\033[36m%-20s\033[0m %s\n", a[1], desc}}' $(MAKEFILE_LIST)

## Install dependencies
setup:
	poetry install

## Start app (prod)
start:
	FLASK_DEBUG=0 poetry run $(PYTHON) main.py

## Start app (dev) - Relies on AppSettings defaults or .env file
dev:
	# We force DEBUG=1, but Host/Port come from AppSettings/Env
	FLASK_DEBUG=1 poetry run $(PYTHON) main.py

## Seed database
seed:
	poetry run $(PYTHON) -m development.seed

# query the dev db
query:
	poetry run $(PYTHON) -m development.query

## Reset DB file
reset:
	rm -f $(DB_FILE)

## Full Rebuild
rebuild: reset seed

## Launch Dev
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