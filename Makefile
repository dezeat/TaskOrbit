PYTHON = python3
POETRY = poetry

DB_CONFIG ?= app/utils/db/default_db_config.yaml
SQLITE_PATH ?= app/default_sqlite.db

# Simple project tasks
.PHONY: setup start dev init-db reset-db seed-db launch format lint type test clean

setup:
	@echo "Poetry is available. Run 'poetry install' if dependencies are missing."

# Start without debug (uses env vars if set)
start:
	@echo "Starting app..."
	$(POETRY) run $(PYTHON) main.py $(DB_CONFIG)

# Dev server on localhost:5000
dev:
	@echo "Starting dev server on http://127.0.0.1:5000"
	FLASK_DEBUG=1 FLASK_HOST=127.0.0.1 FLASK_PORT=5000 $(POETRY) run $(PYTHON) main.py $(DB_CONFIG)

# Initialize / seed DB (idempotent)
init-db:
	@echo "Seeding database..."
	@$(POETRY) run $(PYTHON) main.py $(DB_CONFIG) --init-db

# Remove sqlite DB file so next run starts fresh
reset-db:
	@rm -f $(SQLITE_PATH)
	@echo "Removed $(SQLITE_PATH)"

# Reset, seed and start dev server
launch: reset-db init-db dev

# Formatting and checks
format:
	@$(POETRY) run ruff format .

lint:
	@$(POETRY) run ruff check .

type:
	@$(POETRY) run mypy ./app

test:
	@$(POETRY) run pytest

clean:
	@rm -f $(SQLITE_PATH)
	@echo "Cleaned project artifacts"