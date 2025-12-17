"""Pydantic schemas describing API payloads for users and tasks.

These use Pydantic v2 `from_attributes` conversion to accept ORM objects
directly when building DTOs for templates and API responses.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserSchema(BaseModel):
    """Schema for user objects exposed by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID | None = None
    name: str
    hashed_password: str
    last_login_ts: datetime | None = None


class TaskSchema(BaseModel):
    """Schema for task objects exposed by the API."""

    model_config = ConfigDict(from_attributes=True)
    id: UUID | None = None
    user_id: UUID
    name: str
    description: str | None = None
    ts_acomplished: datetime | None = None
    ts_deadline: datetime | None = None
