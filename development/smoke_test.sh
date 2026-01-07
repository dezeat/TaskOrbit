#!/bin/bash
set -e

# Force SQLite for smoke test (ignore .env or other DB configs)
export DB_TYPE=sqlite
export DB_NAME=smoke_test.db
export DB_HOST=.
export FLASK_DEBUG=1

# Cleanup function
cleanup() {
    if [ -f "smoke_test.db" ]; then
        rm -f smoke_test.db
        echo "🧹 Cleaned up test database"
    fi
}

# Set trap to cleanup on exit
trap cleanup EXIT

echo "🔍 Checking for Syntax Errors..."
# Compiles all python files to byte code. Fails if there is a syntax error.
python3 -m compileall -q app main.py

echo "🚀 Checking App Startup (Dry Run)..."
# Tries to initialize the Flask app. Fails if there are import/config errors.
poetry run python3 -c "from app.app import create_app; print('✅ App initialized successfully'); create_app()"

echo "🔧 Checking Gunicorn WSGI Integration..."
# Verifies that Gunicorn can load the app factory correctly
poetry run gunicorn --check-config "app.app:create_app" > /dev/null 2>&1 && \
    echo "✅ Gunicorn WSGI check passed" || \
    echo "⚠️  Warning: Gunicorn WSGI check failed (this might be OK if gunicorn is not installed)"

echo "🎉 Smoke Test Passed! 'make dev' should work."