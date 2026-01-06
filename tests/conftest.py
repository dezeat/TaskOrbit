"""Pytest fixtures for TaskOrbit tests.

This module provides reusable fixtures used across unit and integration
tests.

The fixtures purposely avoid importing the application factory module at
import time to prevent side-effects (such as database connections or
configuration evaluation) leaking into the test runner.
"""

import os
from collections.abc import Callable, Generator
from pathlib import Path
from typing import Any as TypingAny
from typing import ContextManager, Protocol, cast

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.models import BaseTable, UserTable
from app.routes import bp as main_bp
from app.utils.security import hash_password


class TestApp(Protocol):
    """Minimal Protocol describing the test Flask app used in fixtures.

    Allows attaching test-only attributes like ``test_db_session`` while
    keeping static type-checkers satisfied.
    """

    # Core attributes/methods used by the tests
    config: dict
    test_db_session: scoped_session
    register_blueprint: Callable[[TypingAny], None]
    app_context: Callable[[], ContextManager[TypingAny]]
    before_request: Callable[[Callable[..., TypingAny]], None]
    teardown_appcontext: Callable[[Callable[..., TypingAny]], None]
    test_client: Callable[..., TypingAny]


@pytest.fixture
def fix_app() -> Generator[TestApp, None, None]:
    """Create a Flask application instance configured for testing.

    Uses an in-memory SQLite engine and a scoped session bound to that engine.
    """
    test_config = {
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    }

    # Create a dedicated in-memory engine for tests
    test_engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    test_db_session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    )

    # Build a lightweight Flask app instance without importing app.app
    # Use the application's templates folder so Jinja can find templates like
    # 'login.html' used by the routes.
    templates_path = Path.cwd() / "app" / "templates"
    # Create a Flask app and cast it to TestApp so type-checkers accept
    # attaching the `test_db_session` attribute below.
    app = cast("TestApp", Flask(__name__, template_folder=str(templates_path)))
    app.config.update(test_config)
    app.config["SECRET_KEY"] = "test-secret"  # noqa: S105

    # Register the application's blueprint so routes are available
    app.register_blueprint(main_bp)

    # Attach the test session to the app for access in other fixtures/tests
    app.test_db_session = test_db_session

    # Create tables on the test engine
    with app.app_context():
        BaseTable.metadata.create_all(bind=test_engine)
        yield app
        test_db_session.remove()
        BaseTable.metadata.drop_all(bind=test_engine)


@pytest.fixture
def fix_client(fix_app: TestApp) -> FlaskClient:
    """Return a standard Flask test client."""

    # Ensure each request has access to the test session via g.db_session
    @fix_app.before_request
    def _attach_session() -> None:
        from flask import g

        g.db_session = fix_app.test_db_session

    @fix_app.teardown_appcontext
    def _remove_session(exception: Exception | None) -> None:  # noqa: ARG001
        fix_app.test_db_session.remove()

    return fix_app.test_client()


@pytest.fixture
def fix_config_env() -> Generator[Callable[[dict[str, str]], None], None, None]:
    """Fixture to temporarily set environment variables and clear config cache.

    Yields a function that accepts a dict of env vars to set.
    Automatically restores original environment and clears cache after test.
    """
    original_env = os.environ.copy()

    def _set_env(env_vars: dict[str, str]) -> None:
        """Set environment variables and clear config cache."""
        os.environ.update(env_vars)
        from app.config import get_config

        get_config.cache_clear()

    yield _set_env

    # Cleanup: restore original environment and clear cache
    os.environ.clear()
    os.environ.update(original_env)
    from app.config import get_config

    get_config.cache_clear()


@pytest.fixture
def fix_config() -> Callable[[], "AppConfig"]:  # noqa: F821
    """Fixture that returns the get_config function for testing.

    Use with fix_config_env to test configuration with different env vars.
    """

    def _get_config() -> "AppConfig":  # noqa: F821
        from app.config import get_config

        return get_config()

    return _get_config

    return fix_app.test_client()


@pytest.fixture
def fix_auth_client(fix_client: FlaskClient, fix_app: TestApp) -> FlaskClient:
    """Return a Flask test client authenticated with a standard user.

    Seeds the in-memory DB with a test user and logs in so the client has a
    valid session.
    """
    with fix_app.app_context():
        user = UserTable(name="testuser", hashed_password=hash_password("password123"))
        fix_app.test_db_session.add(user)
        fix_app.test_db_session.commit()

    fix_client.post("/login", data={"username": "testuser", "password": "password123"})

    return fix_client
