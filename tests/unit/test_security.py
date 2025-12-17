"""Unit tests for password hashing and verification.

These tests exercise the functions in ``app.utils.security`` to ensure the
password hashing strategy produces a non-reversible hash and that the
verification function correctly accepts valid passwords and rejects
invalid guesses. We cover multiple sample passwords to increase
confidence across input shapes (alphanumeric, punctuation, numeric).
"""

import pytest

from app.utils.security import hash_password, verify_password


@pytest.mark.parametrize(
    "password",
    [
        "securePassword123!",
        "another_phrase",
        "88888888",
    ],
)
def test_password_hashing_success(password: str) -> None:
    """Hashing produces a different value and verifies correctly.

    Why: Prevents storing plaintext and ensures the verification routine
    accepts the original password while the stored hash is not equal to
    the plaintext input.
    """
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True


def test_password_verification_failure() -> None:
    """Verification returns False for incorrect password guesses.

    Why: Ensures that wrong inputs are rejected and the verification API
    does not false-positive authenticate.
    """
    password = "secret"  # noqa: S105
    hashed = hash_password(password)

    is_valid = verify_password("wrong_guess", hashed)

    assert is_valid is False
