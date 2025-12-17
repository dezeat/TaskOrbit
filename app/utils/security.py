"""Security utilities for password hashing and verification.

This module handles password security using the standard `bcrypt` library.
We strictly replace `passlib` (which is unmaintained) with direct `bcrypt` calls.
To bypass Bcrypt's 72-byte input limit, we pre-hash all passwords using SHA-256.
"""

import hashlib

import bcrypt


def _pre_hash(password: str) -> bytes:
    """Normalize password length using SHA-256.

    Bcrypt has a hard limit of 72 bytes. Passing a longer password causes a
    ValueError. To support passwords of any length, we hash the input with
    SHA-256 first, which produces a fixed-length 64-byte string (safe for Bcrypt).
    """
    # 1. Hash the password to SHA-256 (returns a 64-char hex string)
    normalized_pwd = hashlib.sha256(password.encode("utf-8")).hexdigest()

    # 2. Encode to bytes (required by the bcrypt library)
    return normalized_pwd.encode("utf-8")


def hash_password(password: str) -> str:
    """Hash a plaintext password securely.

    Args:
        password: The plaintext password (any length).

    Returns:
        The salted and hashed password string (e.g. '$2b$12$...').
    """
    pwd_bytes = _pre_hash(password)
    salt = bcrypt.gensalt()

    # hashpw returns bytes; we decode to utf-8 string for database storage
    hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored hash.

    Args:
        plain_password: The plaintext password provided by the user.
        hashed_password: The stored bcrypt hash string.

    Returns:
        True if the password matches, False otherwise.
    """
    try:
        pwd_bytes = _pre_hash(plain_password)
        hash_bytes = hashed_password.encode("utf-8")

        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except (ValueError, TypeError):
        # Handles malformed hashes or incompatible encoding
        return False
