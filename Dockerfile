# Minimal Production Dockerfile for TaskOrbit
FROM python:3.12-slim

# Poetry v2 + Python environment
ENV POETRY_VERSION=2.0.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install Poetry and runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH="${POETRY_HOME}/bin:${PATH}"

WORKDIR /app

# Install dependencies (layer caching)
COPY pyproject.toml poetry.lock* ./
RUN poetry install --only main --no-root

# Copy application code
COPY . .

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

# Gunicorn with app factory pattern
# app.app:create_app() calls the factory function directly
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8080", \
     "--workers", "4", \
     "--worker-class", "sync", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app.app:create_app()"]
