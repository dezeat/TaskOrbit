"""Tests for registration and login password handling."""

from types import SimpleNamespace
from typing import Any

import pytest
from flask import Flask

pytestmark = pytest.mark.usefixtures("fix_db_and_auth")


@pytest.fixture
def fix_mock_db_no_user(
    monkeypatch: pytest.MonkeyPatch, fix_db_and_auth, fix_app: Flask
) -> dict[str, object]:
    """Patch DB functions to simulate no existing user and capture inserted user."""
    # Ensure no users are returned by the fake DB session
    fix_app._fake_db._scalars_result = []

    # Avoid invoking passlib during tests — make hashing deterministic
    monkeypatch.setattr("app.routes.hash_password", lambda p: f"hashed-{p}")

    # Return the fake DB session so tests can inspect `.added`
    return fix_app._fake_db


@pytest.fixture
def fix_fake_user() -> SimpleNamespace:
    """Return a sample `User` dataclass instance for login tests.

    Use a deterministic fake hashed value so tests can avoid invoking
    the real passlib hashing backend during fixture setup.
    """
    return SimpleNamespace(name="foo", hashed_password="hashed-bar", id="user-id")  # noqa: S106


@pytest.fixture
def fix_mock_db_with_user(
    monkeypatch: pytest.MonkeyPatch,
    fix_db_and_auth,
    fix_fake_user: User,
    fix_app: Flask,
) -> None:
    """Patch DB fetch to return the provided `fix_fake_user` for name lookups."""
    # Make the fake DB session return the user for name lookups
    fix_app._fake_db._scalars_result = [fix_fake_user]
    # Provide a simple verify implementation for tests
    monkeypatch.setattr(
        "app.routes.verify_password",
        lambda plain, hashed: hashed == f"hashed-{plain}",
    )


def test_register_creates_user(
    fix_app: Flask, fix_mock_db_no_user: dict[str, Any]
) -> None:
    """Register creates a new `User` record via the DB helper."""
    client = fix_app.test_client()
    resp = client.post("/register", data={"username": "foo", "password": "bar"})
    assert resp.status_code in (301, 302)
    assert "/login" in resp.headers.get("Location", "")
    # Inspect fake DB session `.added` entries
    added = fix_mock_db_no_user.added
    assert len(added) >= 1
    created = added[0]
    # ORM object attributes or dict-like payload
    if hasattr(created, "name"):
        assert created.name == "foo"
        assert getattr(created, "hashed_password", None) != "bar"
    else:
        assert created["name"] == "foo"
        assert created["hashed_password"] != "bar"


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
    # Send the raw password; server verifies against stored hash
    resp = client.post(
        "/login",
        data={"username": fix_fake_user.name, "password": "bar"},
    )
    assert resp.status_code in (301, 302)
