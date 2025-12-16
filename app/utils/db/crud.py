"""CRUD helpers for TaskOrbit using SQLAlchemy.

This module provides small utilities to insert, select, update and delete
rows and to convert query results into the application's pydantic/dataclass
models. Functions are defensive about the shape of inputs and the form of
SQLAlchemy results (scalar vs row tuples).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, is_dataclass
from typing import TYPE_CHECKING

from sqlalchemy import and_, delete, or_, select, update

from app.utils.db.models import MODEL_MAP, BaseModel, TaskTable

if TYPE_CHECKING:
    from uuid import UUID as UUIDTYPE

    from sqlalchemy.orm import Session, scoped_session

    from app.utils.db.models import BaseTable


def bulk_insert(
    session: Session | scoped_session[Session],
    table: type[BaseTable],
    data: Sequence[object],
) -> None:
    """Insert dataclass instances or dicts into `table`.

    Accepts an iterable of dataclass instances (converted with `asdict`) or
    plain dicts. The function adds ORM objects to the session but does not
    commit; transaction control is left to the caller.
    """
    for item in data:
        # `is_dataclass` can be True for both dataclass types and instances.
        # Ensure we only call `asdict` on an instance.
        if is_dataclass(item) and not isinstance(item, type):
            payload = asdict(item)
        elif isinstance(item, dict):
            payload = item
        else:
            msg = "items to insert must be dataclasses or dicts"
            raise TypeError(msg)

        session.add(table(**payload))


def search_tasks(
    session: Session | scoped_session[Session], user_id: UUIDTYPE, search_string: str
) -> list[BaseModel]:
    """Return tasks for `user_id` that match `search_string` (case-insensitive).

    Uses SQL `ILIKE` semantics via `ilike` to perform a flexible search on
    `name` and `description` columns.
    """
    pattern = f"%{search_string}%"
    stmt = select(TaskTable).where(
        and_(
            TaskTable.user_id == user_id,
            or_(TaskTable.name.ilike(pattern), TaskTable.description.ilike(pattern)),
        )
    )

    rows = session.execute(stmt).scalars().all()
    return serialize_output(rows)


def fetch_all(
    session: Session | scoped_session[Session],
    table: type[BaseTable],
) -> list[BaseModel]:
    """Return all rows from `table` converted to application models."""
    rows = session.execute(select(table)).scalars().all()
    return serialize_output(rows)


def fetch_where(
    session: Session | scoped_session[Session],
    table: type[BaseTable],
    filter_map: dict[str, Sequence[object]],
) -> list[BaseModel]:
    """Select rows matching `filter_map` and return converted model objects.

    `filter_map` maps column names to sequences of allowed values. Multiple
    column filters are combined with AND semantics.
    """
    conditions = []
    for col, vals in filter_map.items():
        col_attr = getattr(table, col)
        if isinstance(vals, Sequence) and not isinstance(vals, (str, bytes)):
            if len(vals) == 1:
                conditions.append(col_attr == vals[0])
            else:
                conditions.append(col_attr.in_(vals))
        else:
            conditions.append(col_attr == vals)

    stmt = select(table).where(and_(*conditions)) if conditions else select(table)
    rows = session.execute(stmt).scalars().all()
    return serialize_output(rows)


def fetch_user_tasks(
    session: Session | scoped_session[Session], user_id: UUIDTYPE, *, completed: bool
) -> list[BaseModel]:
    """Fetch tasks based on completion status (ts_acomplished is None or Not None)."""
    stmt = select(TaskTable).where(TaskTable.user_id == user_id)

    if completed:
        stmt = stmt.where(TaskTable.ts_acomplished.is_not(None))
        stmt = stmt.order_by(TaskTable.ts_acomplished.desc())
    else:
        stmt = stmt.where(TaskTable.ts_acomplished.is_(None))
        stmt = stmt.order_by(TaskTable.name.asc())

    rows = session.execute(stmt).scalars().all()
    return serialize_output(rows)


def update_where(
    session: Session | scoped_session[Session],
    table: type[BaseTable],
    match_cols: dict[str, object],
    updates: dict[str, object],
) -> None:
    """Update rows in `table` matching `match_cols` with values from `updates`.

    `match_cols` is a dict of column->value used to build the WHERE clause.
    Transaction commit is left to the caller.
    """
    if not match_cols:
        msg = "match_cols must contain at least one column condition"
        raise ValueError(msg)

    where_conditions = [getattr(table, k) == v for k, v in match_cols.items()]
    stmt = update(table).where(and_(*where_conditions)).values(**updates)
    session.execute(stmt)


def delete_where(
    session: Session | scoped_session[Session],
    table: type[BaseTable],
    match_col: dict[str, object],
) -> None:
    """Delete rows from `table` matching the provided column/value mapping.

    `match_col` must be a mapping of column name to match value(s). Multiple
    items are ANDed together.
    """
    if not match_col:
        msg = "match_col must contain at least one condition"
        raise ValueError(msg)

    conditions = [getattr(table, k) == v for k, v in match_col.items()]
    stmt = delete(table).where(and_(*conditions))
    session.execute(stmt)


def serialize_output(
    data: BaseTable
    | Sequence[BaseTable]
    | tuple[BaseTable, ...]
    | Sequence[tuple[BaseTable, ...]],
) -> list[BaseModel]:
    """Convert SQLAlchemy ORM results into application dataclass models.

    Accepts a sequence of scalar ORM objects, a sequence of Row/tuple results,
    or a single ORM instance. Uses `MODEL_MAP` to map table classes to
    dataclass constructors.
    """
    results: list[BaseModel] = []

    # Normalize single-object input
    if not isinstance(data, Sequence) or isinstance(data, (str, bytes)):
        data = [data]

    for item in data:
        # If SQLAlchemy returned a Row/tuple, iterate its elements
        candidates = item if isinstance(item, tuple) else (item,)
        for table_model in candidates:
            if table_model is None:
                continue
            model_name = type(table_model).__name__
            if model_name in MODEL_MAP:
                results.append(MODEL_MAP[model_name].from_dict(table_model.to_dict()))

    return results
