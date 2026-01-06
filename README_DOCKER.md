# Docker Deployment

## Quick Start

```bash
# Build
docker build -t taskorbit .

# Run (SQLite - Development)
docker run -p 8080:8080 taskorbit

# Run (PostgreSQL - Production)
docker run -p 8080:8080 \
  -e DB_TYPE=postgresql \
  -e DB_HOST=your-db-host \
  -e DB_USER=taskorbit_dbuser \
  -e DB_PASS=secret \
  -e DB_NAME=taskorbit \
  -e DB_SCHEMA=taskorbit \
  -e FLASK_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))") \
  taskorbit
```

## With Docker Compose (Recommended)

Full setup with PostgreSQL, dedicated schema, and app user:

```bash
# 1. Copy example and configure
cp docker-compose.example.yml docker-compose.yml

# 2. Create .env file
cat > .env << EOF
POSTGRES_PASSWORD=$(python -c "import secrets; print(secrets.token_hex(32))")
DB_APP_PASSWORD=$(python -c "import secrets; print(secrets.token_hex(32))")
FLASK_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")
EOF

# 3. Start services
docker-compose up -d

# 4. Check logs
docker-compose logs -f app
```

## Database Isolation & Security

### PostgreSQL Setup
- **Schema**: `taskorbit` (isolated from other apps)
- **App User**: `taskorbit_dbuser` (least privilege)
- **Permissions**: CREATE, SELECT, INSERT, UPDATE, DELETE (no DROP, no superuser)
- **Init Script**: [db_init_example.sql](db_init_example.sql) creates schema + user automatically

### SQLite Setup (Development)
- **Table Prefix**: `taskorbit_` (e.g., `taskorbit_user`, `taskorbit_task`)
- No isolation needed (single-app database)

### Why This Matters
✅ Multiple apps can share one PostgreSQL instance safely  
✅ App user cannot access other schemas or drop tables  
✅ Clear separation of concerns (admin vs app user)  
✅ Easy to backup/restore individual schemas  

## Configuration

All configuration via environment variables (see [app/config.py](app/config.py)):

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_SECRET` | `dev-secret-key` | **Required** Session secret (generate secure value!) |
| `DB_TYPE` | `sqlite` | Database type: `sqlite`, `postgresql`, `mysql` |
| `DB_HOST` | `.` | SQLite: directory path, PostgreSQL: hostname |
| `DB_USER` | - | Database user (e.g., `taskorbit_dbuser`) |
| `DB_PASS` | - | Database password |
| `DB_NAME` | `taskorbit.db` | Database/file name |
| `DB_SCHEMA` | `taskorbit` | PostgreSQL: schema name, SQLite: table prefix |

## Architecture

- **Base**: `python:3.13-slim` (~180MB final image)
- **Server**: Gunicorn with 4 workers (adjust in Dockerfile)
- **Dependencies**: Poetry v2 (no virtualenv in container)
- **User**: Non-root (UID 1000)
- **Port**: 8080

## Init Script Details

The [db_init_example.sql](db_init_example.sql) script:
1. Creates schema `taskorbit`
2. Creates user `taskorbit_dbuser` with password from `DB_APP_PASSWORD` environment variable
3. Grants minimal required privileges
4. Runs automatically on first PostgreSQL container start

**Important**: Set `DB_APP_PASSWORD` environment variable before starting the container!

## Notes

- **Slim vs Alpine**: Using slim for better `psycopg2-binary` compatibility
- **No wsgi.py**: Gunicorn uses factory pattern: `app.app:create_app`
- **Workers**: 4 is good for 4-core CPU. Formula: `2 × cores + 1` max.
- **Tests**: Always use SQLite, see [development/smoke_test.sh](development/smoke_test.sh)
