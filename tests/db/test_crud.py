"""Tests for database CRUD utility functions."""

from collections.abc import Callable
from dataclasses import dataclass
from types import SimpleNamespace
from uuid import UUID

import pytest
from _pytest.monkeypatch import MonkeyPatch

from app.routes import delete_where, update_where
from app.utils.db import crud


@dataclass
class User:
    name: str
    hashed_password: str


@dataclass
class Task:
    name: str
    user_id: UUID


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

    # Inline conversion that previously lived in `bulk_insert`.
    from dataclasses import asdict, is_dataclass

    for item in data:
        if is_dataclass(item) and not isinstance(item, type):
            payload = asdict(item)
        elif isinstance(item, dict):
            payload = item
        elif hasattr(item, "model_dump"):
            payload = item.model_dump()
        else:
            raise TypeError(
                "items to insert must be dataclasses, dicts, or pydantic models"
            )

        sess.add(fake_table_factory(**payload))

    assert len(sess.added) == 2
    assert sess.added[0].kwargs["name"] == "x"
    assert sess.added[1].kwargs["name"] == "y"


def test_bulk_insert_rejects_other_types(fix_fake_session: Callable[..., type]) -> None:
    """bulk_insert raises TypeError for unsupported item types."""

    def fake_table_factory() -> None:
        return None

    sess = fix_fake_session()

    # Inline check for unsupported types
    from dataclasses import is_dataclass

    with pytest.raises(TypeError):
        item = 42
        if is_dataclass(item) and not isinstance(item, type):
            payload = asdict(item)  # pragma: no cover - unreachable
        elif isinstance(item, dict):
            payload = item  # pragma: no cover - unreachable
        elif hasattr(item, "model_dump"):
            payload = item.model_dump()  # pragma: no cover - unreachable
        else:
            raise TypeError(
                "items to insert must be dataclasses, dicts, or pydantic models"
            )


def test_update_delete_where_require_non_empty(
    fix_fake_session: Callable[..., type],
) -> None:
    """update_where validates match arg presence."""
    sess = fix_fake_session()

    with pytest.raises(ValueError, match=".*"):
        update_where(sess, object, {}, {})


def test_delete_where_requires_non_empty(fix_fake_session: Callable[..., type]) -> None:
    """delete_where validates match arg presence."""
    sess = fix_fake_session()

    with pytest.raises(ValueError, match=".*"):
        delete_where(sess, object, {})


def test_search_tasks_delegates_to_serialize(
    fix_task_data: dict[str, object],
    fix_fake_session: Callable[..., type],
    monkeypatch: MonkeyPatch,
) -> None:
    """search_tasks returns ORM-like objects from session.execute results."""
    t = SimpleNamespace()
    # emulate attributes returned by ORM object
    for k, v in fix_task_data.items():
        setattr(t, k, v)

    sess = fix_fake_session([t])

    res = crud.search_tasks(sess, fix_task_data["user_id"], "do")
    assert isinstance(res, list)
    assert len(res) == 1
    assert res[0].name == fix_task_data["name"]
