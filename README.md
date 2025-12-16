# TaskOrbit

TaskOrbit is a web-based task manager and to-do list application designed for simplicity and efficiency. The application leverages **HTMX** for dynamic, lightweight frontend updates and a robust **Flask** backend with **SQLAlchemy** for data management.

### Features
* **Dynamic UI**: Powered by HTMX for a seamless, single-page-app feel without the complexity of a heavy JS framework.
* **Backend**: Flask-based architecture with structured logging and configuration.
* **Database Agnostic**: Built on SQLAlchemy; supports SQLite (default for dev), PostgreSQL, and MySQL.
* **Developer Friendly**: Fully typed (Mypy), linted (Ruff), and automated via Makefiles.

### Tech Stack
- **Frontend**: HTMX, Jinja2 Templates
- **Backend**: Python 3.12+, Flask, SQLAlchemy
- **Database**: SQLite (Development), PostgreSQL (Production target)
- **Dependency Management**: Poetry
- **CI/CD**: GitHub Actions (Planned)

---

### Getting Started

#### Prerequisites
* Python 3.12+
* [Poetry](https://python-poetry.org/docs/#installation)

#### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/taskorbit.git](https://github.com/yourusername/taskorbit.git)
    cd taskorbit
    ```

2.  **Install dependencies:**
    ```bash
    make setup
    # OR manually: poetry install
    ```

### Development Workflow

The project includes a `Makefile` to streamline development tasks.

| Command | Description |
| :--- | :--- |
| `make dev` | **Start the server** in debug mode (hot-reloading enabled). |
| `make launch` | **Fresh Start:** Resets the DB, seeds it with data, and starts the server. |
| `make seed` | **Populate DB:** Runs the seeding script to add Admin user and default tasks. |
| `make reset` | **Wipe DB:** Deletes the local SQLite database file. |
| `make check` | **Quality Assurance:** Runs formatting, linting, type-checking, and tests. |

