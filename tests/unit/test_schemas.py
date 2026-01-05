"""Unit tests for Pydantic user schemas.

These tests verify input validation for the user creation schema
``UserCreate``. The suite checks that invalid inputs (too-short
passwords or empty usernames) raise ``ValidationError`` and that valid
payloads are accepted. This enforces early validation at the boundary of
the application to reduce downstream errors and security issues.
"""

import pytest
from pydantic import ValidationError

from app.schemas import UserCreate


@pytest.mark.parametrize(
    ("username", "password"),
    [
        ("user", "short"),
        ("", "validPass123"),
    ],
)
def test_user_create_invalid(username: str, password: str) -> None:
    """Invalid payloads raise ``ValidationError``.

    Why: Prevents creation of accounts with insecure or missing fields at
    the schema level.
    """
    with pytest.raises(ValidationError):
        UserCreate(name=username, password=password)


def test_user_create_valid() -> None:
    """A correctly formed payload constructs a valid schema instance.

    Why: Confirms that legitimate registration data passes schema
    validation and that fields map as expected.
    """
    payload = {"name": "validUser", "password": "longEnoughPassword"}

    schema = UserCreate(**payload)

    assert schema.name == "validUser"
    assert schema.password == "longEnoughPassword"  # noqa: S105
