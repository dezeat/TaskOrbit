"""Pydantic schemas describing API payloads for users and tasks.

These use Pydantic v2 `from_attributes` conversion to accept ORM objects
directly when building DTOs for templates and API responses.

Security Note:
    User schemas are split into `UserCreate` (input) and `UserPublic` (output)
    to prevent accidental leakage of sensitive fields like password hashes.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    """Shared user properties."""

    name: str = Field(min_length=1, max_length=50)


class UserCreate(UserBase):
    """Schema for registering a new user (Input).

    Contains sensitive information (password) that should never be returned
    to the client.
    """

    password: str = Field(min_length=8, description="Raw plaintext password")


class UserPublic(UserBase):
    """Schema for user objects exposed by the API (Output).

    Safe for frontend consumption. Excludes password hashes.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    last_login_ts: datetime | None = None


class TaskSchema(BaseModel):
    """Schema for task objects exposed by the API.

    Used for both input validation (creation/editing) and output serialization.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str = Field(min_length=1)
    description: str | None = None
    ts_acomplished: datetime | None = None
    ts_deadline: datetime | None = None
