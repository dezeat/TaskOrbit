-- PostgreSQL Initialization Script for TaskOrbit
-- This script creates a dedicated schema and user with minimal privileges
-- 
-- IMPORTANT: Password is read from environment variable DB_APP_PASSWORD
--
-- Usage:
--   1. Set environment variables before starting container:
--      DB_APP_PASSWORD=your-secure-password
--   2. Mount this script in docker-compose.yml:
--      volumes:
--        - ./db_init_example.sql:/docker-entrypoint-initdb.d/01_init.sql
--   3. The script runs automatically on first container start
--   4. App creates tables via SQLAlchemy after schema is ready

-- Create dedicated schema for TaskOrbit
CREATE SCHEMA IF NOT EXISTS taskorbit;

-- Create dedicated app user (NOT a superuser)
-- Password from environment variable
CREATE USER taskorbit_dbuser WITH PASSWORD :'DB_APP_PASSWORD';

-- Grant connection to database
GRANT CONNECT ON DATABASE taskorbit TO taskorbit_dbuser;

-- Grant schema usage and creation rights
GRANT USAGE ON SCHEMA taskorbit TO taskorbit_dbuser;
GRANT CREATE ON SCHEMA taskorbit TO taskorbit_dbuser;

-- Grant table-level privileges (CREATE for table creation, DML operations)
GRANT CREATE, SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA taskorbit TO taskorbit_dbuser;

-- Grant privileges on future tables (important!)
ALTER DEFAULT PRIVILEGES IN SCHEMA taskorbit 
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO taskorbit_dbuser;

-- Grant sequence privileges (needed for auto-increment/serial columns)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA taskorbit TO taskorbit_dbuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA taskorbit 
    GRANT USAGE, SELECT ON SEQUENCES TO taskorbit_dbuser;

-- Set default search_path for the user (optional, but convenient)
ALTER USER taskorbit_dbuser SET search_path TO taskorbit, public;

-- Log completion
\echo 'TaskOrbit schema and user created successfully!'
\echo 'Schema: taskorbit'
\echo 'User: taskorbit_dbuser'
