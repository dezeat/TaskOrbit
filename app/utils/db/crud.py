"""..."""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Sequence

from sqlalchemy import delete, select, update

if TYPE_CHECKING:
    from sqlalchemy.engine import Row
    from sqlalchemy.orm import Session

    from app.utils.db.models import BaseModel, BaseTable


def insert(session: Session, table: type[BaseTable], data: list[BaseModel]) -> None:
    """Insert a new task into the database."""
    for model in data:
        new_row = table(**asdict(model))
        session.add(new_row)


def select_all(session: Session, table: type[BaseTable]) -> list[BaseTable]:
    """..."""
    return session.query(table).all()


def select_(
    session: Session, table: type[BaseTable], ids: list[str]
) -> Sequence[Row[tuple[BaseTable]]]:
    """..."""
    return session.execute(select(table).where(table.id.in_(ids))).all()


def update_(
    session: Session, table: type[BaseTable], match_col: str, updates: dict[str, str]
) -> None:
    """Update an existing task in the database."""
    session.execute(
        update(table).where(getattr(table, match_col).in_(match_col)).values(**updates)
    )


def delete_(session: Session, table: type[BaseTable], match_col: str) -> None:
    """..."""
    session.execute(delete(table).where(getattr(table, match_col).in_(match_col)))
