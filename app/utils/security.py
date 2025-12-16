"""Server-side password hashing utilities using passlib + bcrypt.

This module exposes `hash_password` and `verify_password` used across the
application. It uses `passlib`'s `CryptContext` with the `bcrypt` scheme.
"""

from __future__ import annotations

from passlib.context import CryptContext

# Use bcrypt (work factor controlled by passlib). Keep deprecated="auto"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password and return the bcrypt hash string."""
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plaintext password against a stored hash."""
    try:
        return pwd_context.verify(password, hashed)
    except Exception:
        return False
