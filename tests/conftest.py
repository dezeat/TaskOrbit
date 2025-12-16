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

    class FakeSession:
        def __init__(self) -> None:
            # default scalars result and get map can be overridden by tests
            self._scalars_result = []
            self._get_map = {}
            self.added: list[object] = []

        def scalars(self, _stmt: object):
            class _ScalarResult:
                def __init__(self, data: object) -> None:
                    self._data = data

                def all(self) -> object:
                    return self._data

            return _ScalarResult(self._scalars_result)

        def execute(self, _stmt: object):
            # emulate execute(...).scalars().all()
            return self.scalars(_stmt)

        def get(self, table: object, key: object) -> object | None:
            # Prefer explicit mapping when provided by tests. When not
            # present, fall back to returning the first scalar result (if
            # any) to emulate a user lookup by id for session validation.
            val = self._get_map.get((getattr(table, "__name__", None), key))
            if val is not None:
                return val
            return self._scalars_result[0] if self._scalars_result else None

        def add(self, obj: object) -> None:
            """Record objects added to the fake session for assertions."""
            self.added.append(obj)

    # create one fake session instance and attach it to the app so tests
    # can mutate it via `fix_app._fake_db`
    _fake = FakeSession()
    fix_app._fake_db = _fake

    @fix_app.before_request
    def _attach_db_session() -> None:
        g.db_session = fix_app._fake_db


@pytest.fixture
def fix_fetch_default(
    monkeypatch: pytest.MonkeyPatch, fix_db_and_auth, fix_app: Flask
) -> None:
    """Default `fetch_where` used by tests that don't override it.

    Sets a default user-like scalar result on the fake DB session so that
    route decorators can validate sessions without a real database.
    """
    from types import SimpleNamespace

    fix_app._fake_db._scalars_result = [
        SimpleNamespace(name="foo", hashed_password="hashed-bar", id="user-id")
    ]


@pytest.fixture
def fix_stub_render(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub `render_template` to avoid template loading during tests."""
    monkeypatch.setattr("app.routes.render_template", lambda *a, **k: "")  # noqa: ARG005
