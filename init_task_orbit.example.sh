#!/bin/sh
set -euo pipefail

# Initialize TaskOrbit schema and user using environment variables
POSTGRES_DB=${POSTGRES_DB:-taskorbit}
POSTGRES_USER=${POSTGRES_USER:-postgres}
DB_APP_USER=${DB_APP_USER:-taskorbit_dbuser}
DB_APP_PASSWORD=${DB_APP_PASSWORD:-}
DB_SCHEMA=${DB_SCHEMA:-taskorbit}

if [ -z "${DB_APP_PASSWORD}" ]; then
  echo "ERROR: DB_APP_PASSWORD is not set. Aborting initialization." >&2
  exit 1
fi

# Escape single quotes in the password for safe embedding in SQL string literals
pw_escaped=$(printf '%s' "${DB_APP_PASSWORD}" | sed "s/'/''/g")

psql --username "${POSTGRES_USER}" --dbname "${POSTGRES_DB}" <<-EOSQL
-- Create schema if missing (idempotent)
CREATE SCHEMA IF NOT EXISTS ${DB_SCHEMA};

-- Create role/user if it does not exist; set/ensure password
DO \
\$\$ 
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_APP_USER}') THEN
    EXECUTE format('CREATE USER %I WITH PASSWORD %L', '${DB_APP_USER}', '${pw_escaped}');
  ELSE
    -- If user exists, ensure password is set/updated (safe to run)
    EXECUTE format('ALTER USER %I WITH PASSWORD %L', '${DB_APP_USER}', '${pw_escaped}');
  END IF;
END
\$\$;

-- Grant connection to database
GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO ${DB_APP_USER};

-- Grant schema usage and creation rights
GRANT USAGE ON SCHEMA ${DB_SCHEMA} TO ${DB_APP_USER};
GRANT CREATE ON SCHEMA ${DB_SCHEMA} TO ${DB_APP_USER};

-- Grant table-level privileges (DML operations)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA ${DB_SCHEMA} TO ${DB_APP_USER};

-- Grant privileges on future tables (important!)
ALTER DEFAULT PRIVILEGES IN SCHEMA ${DB_SCHEMA}
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ${DB_APP_USER};

-- Grant sequence privileges (needed for auto-increment/serial columns)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ${DB_SCHEMA} TO ${DB_APP_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA ${DB_SCHEMA}
    GRANT USAGE, SELECT ON SEQUENCES TO ${DB_APP_USER};

-- Set default search_path for the user (optional, but convenient)
ALTER USER ${DB_APP_USER} SET search_path TO ${DB_SCHEMA}, public;
EOSQL

echo "TaskOrbit schema and user created/validated: schema=${DB_SCHEMA}, user=${DB_APP_USER}"
