"""SQLAlchemy ORM models and utility classes for a task management application."""

from abc import ABC, abstractmethod
from dataclasses import field
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
        return {
            key: value
            for key, value in self.__dict__.items()
            if key in [attr for attr in dir(self) if not attr.startswith("_")]
        }

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
    """Abstract base class for application data models."""

    name: str

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseModel":
        """Construct and return a dataclass model from a dictionary.

        Must be implemented by concrete model classes.
        """


@dataclass
class User(BaseModel):
    """Data model for user-related information."""

    hashed_password: str
    id: UUIDTYPE | None = None
    last_login_ts: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "User":
        """Create a `User` dataclass from a mapping of attributes.

        Expects `name` and `hashed_password` keys; other fields are optional.
        """
        return cls(
            name=data["name"],
            id=data.get("id"),
            hashed_password=data["hashed_password"],
            last_login_ts=data.get("last_login_ts"),
        )


@dataclass
class Task(BaseModel):
    """Data model for task-related information."""

    user_id: UUIDTYPE
    id: UUIDTYPE | None = None
    description: str | None = None
    ts_acomplished: datetime | None = None
    ts_deadline: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        """Create a `Task` dataclass from a mapping of attributes."""
        return cls(
            name=data["name"],
            id=data.get("id"),
            user_id=data["user_id"],
            description=data.get("description"),
            ts_acomplished=data.get("ts_acomplished"),
            ts_deadline=data.get("ts_deadline"),
        )


MODEL_MAP = {"UserTable": User, "TaskTable": Task}
