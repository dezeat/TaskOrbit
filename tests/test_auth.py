"""Tests for registration and login password handling."""

from typing import Any

import pytest
from flask import Flask

from app.utils.db.models import User


@pytest.fixture
def fix_mock_db_no_user(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    """Patch DB functions to simulate no existing user and capture inserted user."""
    created: dict[str, object] = {}

    def _fake_fetch_where(
        session: object,  # noqa: ARG001
        table: object,  # noqa: ARG001
        filter_map: dict[str, object],  # noqa: ARG001
    ) -> list:
        return []

    def _fake_bulk_insert(session: object, table: object, data: list[object]) -> None:  # noqa: ARG001
        created["user"] = data[0]

    monkeypatch.setattr("app.routes.fetch_where", _fake_fetch_where)
    monkeypatch.setattr("app.routes.bulk_insert", _fake_bulk_insert)
    return created


@pytest.fixture
def fix_fake_user() -> User:
    """Return a sample `User` dataclass instance for login tests."""
    return User(name="foo", hashed_password="bar")  # noqa: S106


@pytest.fixture
def fix_mock_db_with_user(monkeypatch: pytest.MonkeyPatch, fix_fake_user: User) -> None:
    """Patch DB fetch to return the provided `fix_fake_user` for name lookups."""

    def _fake_fetch_where(
        session: object,  # noqa: ARG001
        table: object,  # noqa: ARG001
        filter_map: dict[str, object],
    ) -> list:
        name_val = filter_map.get("name")
        if isinstance(name_val, list) and fix_fake_user.name in name_val:
            return [fix_fake_user]
        return []

    monkeypatch.setattr("app.routes.fetch_where", _fake_fetch_where)


def test_register_creates_user(
    fix_app: Flask, fix_mock_db_no_user: dict[str, Any]
) -> None:
    """Register creates a new `User` record via the DB helper."""
    client = fix_app.test_client()
    resp = client.post("/register", data={"username": "foo", "password": "bar"})
    assert resp.status_code in (301, 302)
    assert "/login" in resp.headers.get("Location", "")
    assert "user" in fix_mock_db_no_user
    assert fix_mock_db_no_user["user"].name == "foo"
    assert fix_mock_db_no_user["user"].hashed_password == "bar"  # noqa: S105


@pytest.mark.usefixtures("fix_mock_db_with_user")
def test_login_rejects_wrong_password(fix_app: Flask, fix_fake_user: User) -> None:
    """Login rejects an incorrect hashed password."""
    client = fix_app.test_client()
    resp = client.post(
        "/login", data={"username": fix_fake_user.name, "password": "baz"}
    )
    assert resp.status_code == 200
    assert b"Invalid password" in resp.data


@pytest.mark.usefixtures("fix_mock_db_with_user")
def test_login_accepts_correct_password(fix_app: Flask, fix_fake_user: User) -> None:
    """Login accepts the correct hashed password and redirects."""
    client = fix_app.test_client()
    resp = client.post(
        "/login",
        data={
            "username": fix_fake_user.name,
            "password": fix_fake_user.hashed_password,
        },
    )
    assert resp.status_code in (301, 302)
