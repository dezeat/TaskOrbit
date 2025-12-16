
"""Pytest configuration and fixtures for tests."""

import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from flask import Flask

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.routes import bp as main_bp


@pytest.fixture
def fix_app() -> Flask:
    """Flask app with main blueprint registered."""
    _app = Flask(__name__)
    _app.register_blueprint(main_bp)
    return _app


@pytest.fixture
def fix_local_cfg() -> dict[str, str]:
    """Minimal local DB config dict."""
    return {"type": "sqlite", "host": "/tmp", "name": "db.sqlite"}  # noqa: S108


@pytest.fixture
def fix_server_cfg() -> dict[str, object]:
    """Example server DB config dict (port as string for validators)."""
    return {
        "type": "postgresql",
        "url": "db.example.local",
        "host": "db.example.local",
        "name": "mydb",
        "user": "bob",
        "pw": "s3cr3t",
        "port": "5432",
        "driver": "psycopg",
        "dialect": "postgresql",
        "echo": False,
    }


@pytest.fixture
def fix_user_data() -> dict[str, str]:
    """Sample `User` dataclass input mapping."""
    return {"name": "alice", "hashed_password": "pw"}


@pytest.fixture
def fix_task_data() -> dict[str, object]:
    """Sample `Task` dataclass input mapping."""
    uid = uuid4()

    now = datetime.now(tz=timezone.utc)
    return {
        "name": "do something",
        "user_id": uid,
        "id": uuid4(),
        "description": "desc",
        "ts_acomplished": now,
        "ts_deadline": now,
    }


class FakeSession:
    """Lightweight fake session used by tests."""

    def __init__(self, execute_result: object | None = None) -> None:
        """Initialize FakeSession with optional execute_result."""
        self.added: list[object] = []
        self._execute_result = execute_result

    def add(self, obj: object) -> None:
        """Add an object to the session."""
        self.added.append(obj)

    def execute(self, _stmt: object) -> object:
        """Execute a statement and return a result object."""
        class _ScalarResult:
            def __init__(self, data: object) -> None:
                self._data = data

            def scalars(self) -> "_ScalarResult":
                return self

            def all(self) -> object:
                return self._data

        return _ScalarResult(self._execute_result)


@pytest.fixture
def fix_fake_session() -> type[FakeSession]:
    """Provide the `FakeSession` class to tests so they can instantiate it."""
    return FakeSession
