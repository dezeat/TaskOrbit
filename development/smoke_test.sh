#!/bin/bash
set -e

echo "🔍 Checking for Syntax Errors..."
# Compiles all python files to byte code. Fails if there is a syntax error.
python3 -m compileall -q app main.py

echo "🚀 Checking App Startup (Dry Run)..."
# Tries to initialize the Flask app. Fails if there are import/config errors.
# We set FLASK_DEBUG=1 to match 'make dev' behavior
export FLASK_DEBUG=1
poetry run python3 -c "from app.app import create_app; print('✅ App initialized successfully'); create_app()"

echo "🎉 Smoke Test Passed! 'make dev' should work."