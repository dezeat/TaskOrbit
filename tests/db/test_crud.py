"""Tests for database CRUD utility functions."""

from collections.abc import Callable
from dataclasses import dataclass
from types import SimpleNamespace
from uuid import uuid4

import pytest
from _pytest.monkeypatch import MonkeyPatch

from app.utils.db import crud
from app.utils.db.models import Task, User


@pytest.fixture
def fix_fake_session() -> type[object]:
    """Provide a lightweight fake session class for CRUD tests."""

    class FakeSession:
        def __init__(self, execute_result: object | None = None) -> None:
            self.added: list[object] = []
            self._execute_result = execute_result

        def add(self, obj: object) -> None:
            self.added.append(obj)

        def execute(self, _stmt: object) -> object:
            class _ScalarResult:
                def __init__(self, data: object) -> None:
                    self._data = data

                def scalars(self) -> "_ScalarResult":
                    return self

                def all(self) -> object:
                    return self._data

            return _ScalarResult(self._execute_result)

    return FakeSession


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
    """update_where validates match arg presence."""
    sess = fix_fake_session()

    with pytest.raises(ValueError, match=".*"):
        crud.update_where(sess, object, {}, {})


def test_delete_where_requires_non_empty(fix_fake_session: Callable[..., type]) -> None:
    """delete_where validates match arg presence."""
    sess = fix_fake_session()

    with pytest.raises(ValueError, match=".*"):
        crud.delete_where(sess, object, {})


def test_serialize_output_handles_various_shapes(
    monkeypatch: MonkeyPatch, fix_user_data: dict[str, str]
) -> None:
    """serialize_output converts ORM-like items into dataclass models."""
    # create lightweight distinct fake row types to avoid colliding class names
    user_row = type("UserRow", (), {})
    task_row = type("TaskRow", (), {})

    u = user_row()
    u.name = fix_user_data["name"]
    u.hashed_password = fix_user_data["hashed_password"]
    u.to_dict = lambda: {"name": u.name, "hashed_password": u.hashed_password}

    t = task_row()
    t.name = "do"
    t.user_id = uuid4()
    t.to_dict = lambda: {"name": t.name, "user_id": t.user_id}

    # map the runtime class names to expected dataclass constructors
    monkeypatch.setitem(crud.MODEL_MAP, user_row.__name__, User)
    monkeypatch.setitem(crud.MODEL_MAP, task_row.__name__, Task)

    # covered by more specific tests below


def test_serialize_output_single_instance(
    monkeypatch: MonkeyPatch, fix_user_data: dict[str, str]
) -> None:
    """serialize_output handles a single object instance."""
    user_row = type("UserRow", (), {})
    u = user_row()
    u.name = fix_user_data["name"]
    u.hashed_password = fix_user_data["hashed_password"]
    u.to_dict = lambda: {"name": u.name, "hashed_password": u.hashed_password}

    monkeypatch.setitem(crud.MODEL_MAP, user_row.__name__, User)

    out = crud.serialize_output(u)
    assert isinstance(out[0], User)
    assert out[0].name == fix_user_data["name"]


def test_serialize_output_tuple_like(
    monkeypatch: MonkeyPatch, fix_user_data: dict[str, str]
) -> None:
    """serialize_output handles tuple-like rows."""
    user_row = type("UserRow", (), {})
    u = user_row()
    u.name = fix_user_data["name"]
    u.hashed_password = fix_user_data["hashed_password"]
    u.to_dict = lambda: {"name": u.name, "hashed_password": u.hashed_password}

    monkeypatch.setitem(crud.MODEL_MAP, user_row.__name__, User)

    out = crud.serialize_output((u,))
    assert isinstance(out[0], User)


def test_serialize_output_mixed_sequence(
    monkeypatch: MonkeyPatch, fix_user_data: dict[str, str]
) -> None:
    """serialize_output handles mixed sequences of different row types."""
    user_row = type("UserRow", (), {})
    task_row = type("TaskRow", (), {})

    u = user_row()
    u.name = fix_user_data["name"]
    u.hashed_password = fix_user_data["hashed_password"]
    u.to_dict = lambda: {"name": u.name, "hashed_password": u.hashed_password}

    t = task_row()
    t.name = "do"
    t.user_id = uuid4()
    t.to_dict = lambda: {"name": t.name, "user_id": t.user_id}

    monkeypatch.setitem(crud.MODEL_MAP, user_row.__name__, User)
    monkeypatch.setitem(crud.MODEL_MAP, task_row.__name__, Task)

    out = crud.serialize_output([u, t])
    names = [item.name for item in out]
    assert fix_user_data["name"] in names
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
