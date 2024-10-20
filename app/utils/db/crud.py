"""..."""

from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING, Sequence, TypeVar, cast

from sqlalchemy import delete, select, update

from app.utils.db.models import MODEL_MAP, BaseModel

if TYPE_CHECKING:
    from sqlalchemy.engine import Row
    from sqlalchemy.orm import Session

    from app.utils.db.models import BaseTable


BaseModelType = TypeVar("BaseModelType", bound=BaseModel)


def insert(session: Session, table: type[BaseTable], data: Sequence[BaseModel]) -> None:
    """Insert a new task into the database."""
    for model in data:
        new_row = table(**asdict(model))
        session.add(new_row)


def select_all(session: Session, table: type[BaseTable]) -> list[BaseTable]:
    """..."""
    return session.query(table).all()


def select_(
    session: Session, table: type[BaseTable], where_in_map: dict[str, list[str]]
) -> list[BaseModel]:
    """..."""
    select_col, select_val = next(iter(where_in_map.items()))
    result = session.execute(
        select(table).where(getattr(table, select_col).in_(select_val))
    ).all()

    return serialize_output(result)


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
# comment

def serialize_output(data: Sequence[Row[tuple[BaseTable]]]) -> list[BaseModel]:
    """..."""
    return [
        (MODEL_MAP[type(table_model).__name__]).from_dict(table_model.to_dict())
        for row in data
        for table_model in row
        if type(table_model).__name__ in MODEL_MAP
    ]
