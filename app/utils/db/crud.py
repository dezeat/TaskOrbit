"""CRUD helpers for TaskOrbit using SQLAlchemy.

This module provides small utilities to insert, select, update and delete
rows and to convert query results into the application's pydantic/dataclass
models. Functions are defensive about the shape of inputs and the form of
SQLAlchemy results (scalar vs row tuples).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import and_, or_, select

from app.utils.db.models import TaskTable

if TYPE_CHECKING:
    from uuid import UUID as UUIDTYPE

    from sqlalchemy.orm import Session, scoped_session


def search_tasks(
    session: Session | scoped_session[Session], user_id: UUIDTYPE, search_string: str
) -> list[object]:
    """Return tasks for `user_id` that match `search_string` (case-insensitive)."""
    pattern = f"%{search_string}%"
    stmt = select(TaskTable).where(
        and_(
            TaskTable.user_id == user_id,
            or_(TaskTable.name.ilike(pattern), TaskTable.description.ilike(pattern)),
        )
    )

    try:
        return session.execute(stmt).scalars().all()
    except AttributeError:
        return session.scalars(stmt).all()
