# TaskOrbit

TaskOrbit is a lightweight task management web application built with Flask and SQLAlchemy. It provides a simple UI for creating, editing, toggling, searching and deleting tasks, with a minimal database-backed backend suitable for local development and demos.

## Features

- Simple task CRUD (create, read, update, delete)
- Toggle task completion
- List filtering by status (active / done)
- Server-side templates with partials for fast UI updates
- Pluggable DB configuration via YAML (SQLite local or server databases)
- Seeder to populate an initial admin user and sample tasks

- HTMX-powered partial updates for a snappy UX (used in templates/partials)
- Uses `pydantic` dataclasses for lightweight domain models and `SQLAlchemy` for persistence

## Quick Links

- Project entry: [main.py](main.py)
- Flask app factory: [app/app.py](app/app.py)
- DB models: [app/utils/db/models.py](app/utils/db/models.py)
- DB config factory: [app/utils/db/config.py](app/utils/db/config.py)
- DB factory + engine: [app/utils/db/database.py](app/utils/db/database.py)
- Seeder: [app/utils/db/seed.py](app/utils/db/seed.py)
- Default DB config: [app/utils/db/default_db_config.yaml](app/utils/db/default_db_config.yaml)

## Getting Started (recommended)

These instructions assume you are developing on Linux and have Python 3.10+ installed.

1. Fork the repository on GitHub and clone your fork:

```bash
git clone <your-fork-url>
cd TaskOrbit
```

2. (Recommended) Install with Poetry (preferred for this project):

```bash
# Install poetry if you don't have it
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate a shell with the virtual env
poetry shell
```

Alternative: Create a virtualenv and use pip to install the minimal deps listed in `pyproject.toml`.

## Configure and Run (local development)

By default the application will use the YAML file at `app/utils/db/default_db_config.yaml`, which points to a local SQLite file. To run the app locally:

```bash
# (optional) seed the database
python -m app.utils.db.seed app/utils/db/default_db_config.yaml

# Run the app (uses the config at app/utils/db/default_db_config.yaml by default)
python main.py
```

Environment variables supported:

- `FLASK_HOST` — host to bind (default 127.0.0.1)
- `FLASK_PORT` — port (default 5000)
- `FLASK_DEBUG` — enable debug mode (1/true)
- `FLASK_SECRET` — secret key for Flask sessions

Example run binding to all interfaces:

```bash
FLASK_HOST=0.0.0.0 FLASK_PORT=5000 FLASK_DEBUG=1 FLASK_SECRET=dev_secret python main.py
```

## Database

The application uses SQLAlchemy with a small wrapper in `app/utils/db`. The factory supports local SQLite config (used by default) and server configs for Postgres/MySQL via the YAML configuration.

Default config file: [app/utils/db/default_db_config.yaml](app/utils/db/default_db_config.yaml)

Seeding the DB (creates an `admin` user and a couple sample tasks):

```bash
python -m app.utils.db.seed app/utils/db/default_db_config.yaml
```

If you want to point to another database, create a YAML file following the structure in `default_db_config.yaml` and pass its path to `main.py` or `app.utils.db.seed`.

## Learning Goals

- Learn HTMX by exploring and extending the server-rendered partials in `templates/partials` which the app updates via HTMX triggers.
- Practice Python dataclasses and `pydantic`-backed models (see `app/utils/db/models.py`).
- Learn SQLAlchemy ORM usage and session management through `app/utils/db/database.py` and the request session lifecycle in `app/app.py`.

This project is intentionally small so you can safely experiment with HTMX-driven UI patterns and the data layer without large infrastructure overhead.

## Project Structure

- `main.py` — application entrypoint that initializes DB and runs the Flask app
- `app/` — Flask application package
	- `app/app.py` — app factory and HTTP routes
	- `templates/` & `static/` — UI templates and static assets
	- `utils/db/` — DB models, config factory, engine and seeder
- `utils/` — helper utilities (logger, exceptions)

## Development

Recommended workflow:

1. Create a feature branch from `main`.
2. Run the app locally and iterate on templates or backend code.
3. Run the seeder if you need demo data.
4. Add tests in `tests/` and run `pytest`.

Useful commands:

```bash
# Run tests
poetry run pytest

# Lint with ruff
poetry run ruff check .
```

## Contributing

Contributions are welcome. Open an issue or a pull request describing the change. For larger changes, open an issue first to discuss the design.

Guidelines:

- Keep changes minimal and focused.
- Add tests for new behavior.
- Ensure linter passes (`ruff`).

## Troubleshooting

- If the server fails to start, check that the DB config file exists and points to a writable path.
- If you see SQLAlchemy errors, confirm the target DB driver is installed (e.g., `psycopg2` for Postgres).

## License

This project is licensed under the MIT License.

---

If you want, I can also:

- Add a `Makefile` target to run the app with the default config.
- Create a minimal `requirements.txt` for pip installs.
- Add a short developer guide with VS Code launch configurations.

Please tell me which of those you'd like next.
