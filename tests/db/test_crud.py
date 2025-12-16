"""Tests for database CRUD utility functions."""
from collections.abc import Callable
from dataclasses import dataclass
from types import SimpleNamespace
from uuid import uuid4

import pytest
from _pytest.monkeypatch import MonkeyPatch

from app.utils.db import crud
from app.utils.db.models import Task, User


def test_bulk_insert_accepts_dataclass_and_dict(
    fix_fake_session: Callable[..., type],
) -> None:
    """bulk_insert adds created table objects to the session."""

    @dataclass
    class SimpleDC:
        name: str

    def fake_table_factory(**kwargs: dict[str, object]) -> SimpleNamespace:
        return SimpleNamespace(kwargs=kwargs)

    sess = fix_fake_session()

    dc = SimpleDC(name="x")
    data = [dc, {"name": "y"}]

    crud.bulk_insert(sess, fake_table_factory, data)

    assert len(sess.added) == 2
    assert sess.added[0].kwargs["name"] == "x"
    assert sess.added[1].kwargs["name"] == "y"


def test_bulk_insert_rejects_other_types(fix_fake_session: Callable[..., type]) -> None:
    """bulk_insert raises TypeError for unsupported item types."""

    def fake_table_factory() -> None:
        return None

    sess = fix_fake_session()

    with pytest.raises(TypeError):
        crud.bulk_insert(sess, fake_table_factory, [42])


def test_update_delete_where_require_non_empty(
    fix_fake_session: Callable[..., type],
) -> None:
    """update_where and delete_where validate match arg presence."""
    sess = fix_fake_session()

    with pytest.raises(ValueError, match=".*"):
        crud.update_where(sess, object, {}, {})

    with pytest.raises(ValueError, match=".*"):
        crud.delete_where(sess, object, {})


def test_serialize_output_handles_various_shapes(monkeypatch: MonkeyPatch) -> None:
    """serialize_output converts ORM-like items into dataclass models."""
    # create lightweight distinct fake row types to avoid colliding class names
    user_row = type("UserRow", (), {})
    task_row = type("TaskRow", (), {})

    u = user_row()
    u.name = "alice"
    u.hashed_password = "pw"  # noqa: S105
    u.to_dict = lambda: {"name": u.name, "hashed_password": u.hashed_password}


    t = task_row()
    t.name = "do"
    t.user_id = uuid4()
    t.to_dict = lambda: {"name": t.name, "user_id": t.user_id}

    # map the runtime class names to expected dataclass constructors
    monkeypatch.setitem(crud.MODEL_MAP, user_row.__name__, User)
    monkeypatch.setitem(crud.MODEL_MAP, task_row.__name__, Task)

    # single instance
    out = crud.serialize_output(u)
    assert isinstance(out[0], User)
    assert out[0].name == "alice"

    # tuple-like row
    out = crud.serialize_output((u,))
    assert isinstance(out[0], User)

    # mixed sequence
    out = crud.serialize_output([u, t])
    names = [item.name for item in out]
    assert "alice" in names
    assert "do" in names


def test_search_tasks_delegates_to_serialize(
    fix_task_data: dict[str, object],
    fix_fake_session: Callable[..., type],
    monkeypatch: MonkeyPatch,
) -> None:
    """search_tasks returns serialized models from session.execute results."""
    # create a fake ORM-like object (no TaskTable class defined)
    t = SimpleNamespace()
    t.to_dict = lambda: fix_task_data

    # ensure MODEL_MAP maps this object's class name to Task
    monkeypatch.setitem(crud.MODEL_MAP, t.__class__.__name__, Task)

    sess = fix_fake_session([t])

    res = crud.search_tasks(sess, fix_task_data["user_id"], "do")
    assert isinstance(res, list)
    assert len(res) == 1
    assert isinstance(res[0], Task)
