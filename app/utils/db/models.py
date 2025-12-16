"""SQLAlchemy ORM models and utility classes for a task management application."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
from uuid import UUID as UUIDTYPE

from pydantic.dataclasses import dataclass
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as UUIDCOLUMN
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from uuid6 import uuid7


class BaseTable(DeclarativeBase):
    """Base class for database tables, providing common fields for all models."""

    id: Mapped[UUIDTYPE] = mapped_column(
        "uuid",
        UUIDCOLUMN(as_uuid=True),
        primary_key=True,
        default=uuid7,
        nullable=False,
        sort_order=-1000,
    )
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),  # Use SQLAlchemy's built-in function
        sort_order=9999,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
        server_default=func.now(),  # Use SQLAlchemy's built-in function
        server_onupdate=func.now(),  # Use SQLAlchemy's built-in function
        sort_order=10000,
    )

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow dict of public ORM attributes for the instance."""
        # Deprecated: prefer Pydantic `from_attributes` conversion or direct
        # ORM attribute access. Keep a minimal dict helper for backward
        # compatibility but avoid relying on this for new code.
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    @abstractmethod
    def __repr__(self) -> str:
        """Return a string representation of the object."""


class UserTable(BaseTable):
    """Database model for storing user information."""

    __tablename__ = "user"

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    last_login_ts: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)

    # One-to-Many relationship with TaskTable
    tasks: Mapped[list["TaskTable"]] = relationship(back_populates="users")

    def __repr__(self) -> str:
        """Return a string representation of the UserTable object."""
        return (
            f"UserTable(id={self.id}, name='{self.name}',"
            f" last_login_ts={self.last_login_ts})"
        )


class TaskTable(BaseTable):
    """Database model for storing task details."""

    __tablename__ = "task"

    user_id: Mapped[UUIDTYPE] = mapped_column(ForeignKey("user.uuid"))
    description: Mapped[str] = mapped_column(nullable=True)
    ts_acomplished: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    ts_deadline: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)

    # Many-to-One relationship with UserTable
    users: Mapped["UserTable"] = relationship(back_populates="tasks")

    def __repr__(self) -> str:
        """Return a string representation of the TaskTable object."""
        return (
            f"TaskTable(id={self.id}, name='{self.name}',"
            f" ts_deadline={self.ts_deadline})"
        )


@dataclass
class BaseModel(ABC):
    """Legacy placeholder removed — application now uses Pydantic schemas
    and direct ORM objects. This class remains only for import compatibility
    with older code/tests and should be removed in a future cleanup.
    """


# Legacy dataclass-based models and `MODEL_MAP` have been removed.
# Use the ORM classes in this module together with Pydantic schemas
# (see `app/schemas.py`) for serialization and API payloads.


# Backwards-compatible lightweight dataclasses for tests and imports.
from dataclasses import dataclass
from typing import Any


@dataclass
class User:
    """Light compatibility dataclass mirroring legacy shape used in tests."""

    name: str
    hashed_password: str
    id: Any = None

    @staticmethod
    def from_dict(d: dict[str, object]) -> "User":
        return User(
            name=d.get("name", ""),
            hashed_password=d.get("hashed_password", ""),
            id=d.get("id"),
        )


@dataclass
class Task:
    """Light compatibility dataclass mirroring legacy shape used in tests."""

    name: str
    user_id: Any | None = None
    id: Any | None = None
    description: str | None = None
    ts_acomplished: Any | None = None

    @staticmethod
    def from_dict(d: dict[str, object]) -> "Task":
        return Task(
            name=d.get("name", ""),
            user_id=d.get("user_id"),
            id=d.get("id"),
            description=d.get("description"),
            ts_acomplished=d.get("ts_acomplished"),
        )
