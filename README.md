# TaskOrbit

## Project Overview

TaskOrbit is a task management web-app. The app is built with Flask and SQLAlchemy, ensuring modularity and scalability. It supports schema-based database isolation for PostgreSQL and uses SQLite as the default database for local development. 

This project was developed as a hobby to learn and explore:
- SQLAlchemy for database management
- HTMX for dynamic front-end interactions
- Pydantic for data validation
- Python web development with Flask
- General web development practices


## Design Decisions

### Application-Managed Table Creation
TaskOrbit uses SQLAlchemy ORM for managing database tables. The application dynamically creates tables based on the configured database backend.

### Schema-Based Isolation for PostgreSQL
For PostgreSQL, TaskOrbit uses a dedicated schema (`taskorbit`) to isolate application tables. This ensures better organization and security.

### SQLite as Default for Local Development
SQLite is used as the default database for local development. It simplifies setup and eliminates the need for a database server.

### Least-Privilege Database Access
The application uses a dedicated database user (`taskorbit_dbuser`) with minimal privileges to enhance security.

---

## Repository Structure

- **app/**: Contains the core application logic.
  - `app.py`: Application factory for creating the Flask app.
  - `config.py`: Configuration management using Pydantic.
  - `models.py`: SQLAlchemy ORM models.
  - `routes.py`: API routes and endpoints.
  - `schemas.py`: Data validation schemas.
  - `static/`: Static assets (icons, images, JavaScript).
  - `templates/`: HTML templates for the frontend.
  - `utils/`: Utility modules (logging, security, database helpers).
- **development/**: Development utilities.
  - `query.py`: Database query helpers.
  - `seed.py`: Database seeding script.
  - `smoke_test.sh`: Smoke test script.
- **tests/**: Unit and integration tests.
  - `unit/`: Unit tests for isolated components.
  - `integration/`: Integration tests for end-to-end functionality.
- **Dockerfile**: Docker image definition for production.
- **docker-compose.example.yml**: Example Docker Compose configuration for containerized deployment.
- **db_init_example.sql**: SQL script for initializing PostgreSQL schema and user.
- **pyproject.toml**: Poetry configuration for dependency management.

---

## Local Development

### Requirements
- Python 3.13+
- Poetry for dependency management

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/taskorbit.git
   cd taskorbit
   ```
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Start the application:
   ```bash
   poetry run python main.py
   ```

### Default Behavior
- SQLite is used as the default database.
- The application runs on `127.0.0.1:5000` with debug mode enabled.

---

## Containerized Deployment

### Using Docker Compose
1. Set environment variables:
   ```bash
   export POSTGRES_PASSWORD=your-password
   export DB_APP_PASSWORD=your-app-password
   ```
2. Start the containers:
   ```bash
   docker-compose -f docker-compose.example.yml up
   ```

### PostgreSQL Schema and User Setup
- The `db_init_example.sql` script creates the `taskorbit` schema and a dedicated user with minimal privileges.

### Startup Flow
- PostgreSQL initializes the schema and user on the first start.
- The application connects to the database and creates tables dynamically.

---

## Configuration

### Required Environment Variables
- `FLASK_SECRET`: Secret key for Flask.
- `DB_TYPE`: Database type (`sqlite` or `postgresql`).
- `DB_HOST`: Database host.
- `DB_PORT`: Database port.
- `DB_NAME`: Database name.
- `DB_USER`: Database user.
- `DB_PASS`: Database password.
- `DB_SCHEMA`: Database schema (PostgreSQL only).

### Deployment-Specific Configuration
- The `.env` file is used for local development.
- Environment variables are used for production.

---

## Testing

### Unit Tests
- Located in `tests/unit/`.
- Test isolated components like database models and utility functions.

### Integration Tests
- Located in `tests/integration/`.
- Test end-to-end functionality, including API routes and database interactions.

### Running Tests
1. Install development dependencies:
   ```bash
   poetry install --with dev
   ```
2. Run tests:
   ```bash
   pytest
   ```

