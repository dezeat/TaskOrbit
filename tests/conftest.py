"""Pytest fixtures for TaskOrbit tests."""

from collections.abc import Callable, Generator
from pathlib import Path

import pytest
from flask import Flask, g
from flask.testing import FlaskClient
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.models import BaseTable, UserTable
from app.routes import bp as main_bp
from app.utils.security import hash_password


@pytest.fixture
def fix_clean_config_cache() -> Generator[None, None, None]:
    """Ensures configuration cache is cleared before and after tests."""
    # Delayed import to avoid top-level side effects
    from app.config import get_config

    get_config.cache_clear()
    yield
    get_config.cache_clear()


@pytest.fixture
def mock_env_config(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[[dict[str, str]], None]:
    """Helper to set env vars and reload config within a test.

    Uses `monkeypatch` so env vars are automatically restored by pytest
    after the test finishes.
    """

    def _apply_env(env_vars: dict[str, str]) -> None:
        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        # We must clear cache again so the next call to get_config()
        # reads the new monkeypatched env vars.
        from app.config import get_config

        get_config.cache_clear()

    return _apply_env


@pytest.fixture
def fix_config() -> Callable[[], object]:
    """Returns the current app configuration."""

    def _get_config() -> object:
        from app.config import get_config

        return get_config()

    return _get_config


@pytest.fixture
def fix_app() -> Generator[Flask, None, None]:
    """Create a Flask application instance configured for testing."""
    test_engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    test_db_session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    )

    templates_path = Path.cwd() / "app" / "templates"
    app = Flask(__name__, template_folder=str(templates_path))

    app.config.update(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret",
        }
    )

    app.register_blueprint(main_bp)
    app.test_db_session = test_db_session  # type: ignore[attr-defined]

    with app.app_context():
        BaseTable.metadata.create_all(bind=test_engine)
        yield app
        test_db_session.remove()
        BaseTable.metadata.drop_all(bind=test_engine)


@pytest.fixture
def fix_client(fix_app: Flask) -> FlaskClient:
    """Return a Flask test client with database session injection."""

    @fix_app.before_request
    def _attach_session() -> None:
        g.db_session = fix_app.test_db_session  # type: ignore[attr-defined]

    @fix_app.teardown_appcontext
    def _remove_session(error: BaseException | None) -> None:  # noqa: ARG001
        if hasattr(g, "db_session"):
            g.db_session.remove()

    return fix_app.test_client()


@pytest.fixture
def fix_auth_client(fix_client: FlaskClient, fix_app: Flask) -> FlaskClient:
    """Return a Flask test client authenticated with a standard user."""
    user = UserTable(name="testuser", hashed_password=hash_password("password123"))
    fix_app.test_db_session.add(user)  # type: ignore[attr-defined]
    fix_app.test_db_session.commit()  # type: ignore[attr-defined]
    fix_client.post("/login", data={"username": "testuser", "password": "password123"})
    return fix_client
