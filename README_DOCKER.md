# Docker Deployment

## Quick Start

```bash
# Build
docker build -t taskorbit .

# Run (SQLite)
docker run -p 8080:8080 taskorbit

# Run (PostgreSQL)
docker run -p 8080:8080 \
  -e DB_TYPE=postgresql \
  -e DB_HOST=your-db-host \
  -e DB_USER=taskorbit \
  -e DB_PASS=secret \
  -e DB_NAME=taskorbit \
  -e FLASK_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))") \
  taskorbit
```

## With Docker Compose

See [docker-compose.example.yml](docker-compose.example.yml) for a complete setup with PostgreSQL.

```bash
cp docker-compose.example.yml docker-compose.yml
# Edit docker-compose.yml with your secrets
docker-compose up -d
```

## Configuration

All configuration via environment variables (see [app/config.py](app/config.py)):

| Variable | Default | Required |
|----------|---------|----------|
| `FLASK_SECRET` | `dev-secret-key` | Yes (production) |
| `DB_TYPE` | `sqlite` | No |
| `DB_HOST` | `.` | No |
| `DB_USER` | - | If DB_TYPE != sqlite |
| `DB_PASS` | - | If DB_TYPE != sqlite |
| `DB_NAME` | `taskorbit.db` | No |

## Architecture

- **Base**: `python:3.12-slim` (~150MB final image)
- **Server**: Gunicorn with 4 workers
- **Dependencies**: Poetry v2 (no virtualenv in container)
- **User**: Non-root (UID 1000)
- **Port**: 8080

## Notes

- **Why slim not alpine?** Better compatibility with `psycopg2-binary` wheels (no build deps needed)
- **No wsgi.py?** Gunicorn uses app factory pattern directly: `app.app:create_app()`
- **Workers?** `4` is good for 4-core N100. Adjust in Dockerfile CMD if needed.
