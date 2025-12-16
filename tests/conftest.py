"""Pytest configuration and fixtures for tests."""

import sys
from pathlib import Path

import pytest
from flask import Flask, g

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.routes import bp as main_bp


@pytest.fixture
def fix_app() -> Flask:
    """Flask app with main blueprint registered."""
    _app = Flask(__name__)

    _app.secret_key = "test-secret"  # noqa: S105
    _app.register_blueprint(main_bp)
    return _app


@pytest.fixture
def fix_db_and_auth(fix_app: Flask) -> None:
    """Attach a fake DB session object to `g` for request handling.

    This fixture ensures route handlers that expect `g.db_session` can run
    without a real database in the test environment.
    """

    @fix_app.before_request
    def _attach_db_session() -> None:
        g.db_session = object()


@pytest.fixture
def fix_fetch_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default `fetch_where` used by tests that don't override it."""

    def _fake_fetch_where(
        session: object,  # noqa: ARG001
        table: object,  # noqa: ARG001
        filter_map: dict[str, object],  # noqa: ARG001
    ) -> list[object]:
        from app.utils.db.models import User

        return [User(name="foo", hashed_password="bar")]  # noqa: S106

    monkeypatch.setattr("app.routes.fetch_where", _fake_fetch_where)


@pytest.fixture
def fix_stub_render(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub `render_template` to avoid template loading during tests."""
    monkeypatch.setattr("app.routes.render_template", lambda *a, **k: "")  # noqa: ARG005
