"""SQLAlchemy ORM models and utility classes for a task management application."""

from abc import abstractmethod
from datetime import datetime
from uuid import UUID as UUIDTYPE

from flask_login import UserMixin  # type: ignore  # noqa: PGH003
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
        server_default=func.now(),
        sort_order=9999,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
        server_default=func.now(),
        server_onupdate=func.now(),
        sort_order=10000,
    )

    @abstractmethod
    def __repr__(self) -> str:
        """Return a string representation of the object."""


# 2. Inherit from UserMixin
class UserTable(UserMixin, BaseTable):
    """Database model for storing user information."""

    __tablename__ = "user"

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    last_login_ts: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)

    # One-to-Many relationship with TaskTable
    # 'tasks' is plural (User has many tasks) -> Correct
    tasks: Mapped[list["TaskTable"]] = relationship(back_populates="user")

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
    # 3. Renamed to 'user' (singular)
    user: Mapped["UserTable"] = relationship(back_populates="tasks")

    def __repr__(self) -> str:
        """Return a string representation of the TaskTable object."""
        return (
            f"TaskTable(id={self.id}, name='{self.name}',"
            f" ts_deadline={self.ts_deadline})"
        )
