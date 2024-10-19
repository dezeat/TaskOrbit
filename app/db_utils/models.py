"""SQLAlchemy ORM models and utility classes for a task management application."""

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID as UUIDTYPE

from pydantic.dataclasses import dataclass
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as UUIDCOLUMN
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql.expression import FunctionElement
from uuid6 import uuid7


class UtcNow(FunctionElement):
    """Represents the current UTC timestamp for default and update operations."""
    type = DateTime()
    inherit_cache = True


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
    description: Mapped[str] = mapped_column(nullable=False)
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


class BaseModel(ABC):
    """Abstract base class for application data models."""

    name: str


@dataclass
class User(BaseModel):
    """Data model for user-related information."""

    hashed_password: str
    last_login_ts: datetime | None = None


@dataclass
class Task(BaseModel):
    """Data model for task-related information."""

    user_id: int
    description: str
    ts_acomplished: datetime | None = None
    ts_deadline: datetime | None = None
