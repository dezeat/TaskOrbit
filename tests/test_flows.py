"""Integration-style tests for critical task flows: add/edit/delete and errors."""

from types import SimpleNamespace
from uuid import uuid4

import pytest
from flask import Flask

pytestmark = pytest.mark.usefixtures(
    "fix_db_and_auth", "fix_stub_render", "fix_fetch_default"
)


@pytest.fixture
def fix_bulk_insert_capture(monkeypatch: pytest.MonkeyPatch, fix_app: Flask) -> object:
    """Return the fake DB session so tests can inspect `.added`."""
    return fix_app._fake_db


@pytest.fixture
def fix_update_capture(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    """Capture `match_cols` and `updates` passed to `update_where`.

    The returned dict will contain keys `match_cols` and `updates` after the
    patched function is called by the application code.
    """
    captured: dict[str, object] = {}

    def _fake_update_where(
        session: object,  # noqa: ARG001
        table: object,  # noqa: ARG001
        match_cols: dict[str, object],
        updates: dict[str, object],
    ) -> None:
        captured["match_cols"] = match_cols
        captured["updates"] = updates

    monkeypatch.setattr("app.routes.update_where", _fake_update_where)
    return captured


@pytest.fixture
def fix_delete_capture(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    """Capture the `match_col` arg passed to `delete_where`.

    Tests can assert that the expected identifier was supplied for deletion.
    """
    called: dict[str, object] = {}

    def _fake_delete_where(
        session: object,  # noqa: ARG001
        table: object,  # noqa: ARG001
        match_col: dict[str, object],
    ) -> None:
        called["match_col"] = match_col

    monkeypatch.setattr("app.routes.delete_where", _fake_delete_where)
    return called


@pytest.fixture
def fix_crud_search_capture(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    """Capture arguments passed to `crud_search_tasks`.

    The returned map will contain `user_id` and `search_string` after call.
    """
    called: dict[str, object] = {}

    def _fake_crud_search_tasks(
        session: object,  # noqa: ARG001
        user_id: object,
        search_string: str,
    ) -> list[object]:
        called["user_id"] = user_id
        called["search_string"] = search_string
        return []

    monkeypatch.setattr("app.routes.crud_search_tasks", _fake_crud_search_tasks)
    return called


@pytest.fixture
def fix_fetch_task_for_toggle(
    monkeypatch: pytest.MonkeyPatch, fix_db_and_auth, request: pytest.FixtureRequest
) -> None:
    """Return a simple task-like object when the view looks up a task by id.

    This fixture ensures route handlers that query for a task by id receive a
    minimal object with the expected attributes.
    """

    class _SimpleTask:
        def __init__(self, id_val: str) -> None:
            self.id = id_val
            self.completed = False
            self.name = "foo"
            self.description = "bar"
            self.ts_acomplished = None

    fix_app = request.getfixturevalue("fix_app")
    # emulate a task for id lookups
    fix_app._fake_db._scalars_result = [_SimpleTask("toggle-id")]

    # Ensure `get` returns the task for TaskTable lookups and a user for
    # UserTable lookups to keep session validation working.
    def _fake_get(table: object, key: object) -> object | None:
        name = getattr(table, "__name__", "")
        if name == "TaskTable":
            return _SimpleTask(key)
        if name == "UserTable":
            return SimpleNamespace(
                name="foo", hashed_password="hashed-bar", id="user-id"
            )
        return None

    monkeypatch.setattr(fix_app._fake_db, "get", _fake_get, raising=False)

    def _fake_fetch_where(
        session: object,  # noqa: ARG001
        table: object,  # noqa: ARG001
        filter_map: dict[str, object],
    ) -> list[object]:
        if filter_map.get("id"):
            id_val = (
                filter_map.get("id")[0]
                if isinstance(filter_map.get("id"), list)
                else filter_map.get("id")
            )
            return [_SimpleTask(id_val)]
        return []

    monkeypatch.setattr("app.routes.fetch_where", _fake_fetch_where)


@pytest.fixture
def fix_fetch_no_task(
    monkeypatch: pytest.MonkeyPatch, fix_db_and_auth, request: pytest.FixtureRequest
) -> None:
    """Ensure fetches return no tasks (used for not-found flows)."""
    fix_app = request.getfixturevalue("fix_app")
    # Provide a valid user for session validation but no tasks for lookups.
    fix_app._fake_db._scalars_result = [
        SimpleNamespace(name="foo", hashed_password="hashed-bar", id="user-id")
    ]

    def _fake_get(table: object, key: object) -> object | None:
        name = getattr(table, "__name__", "")
        if name == "UserTable":
            return fix_app._fake_db._scalars_result[0]
        return None

    monkeypatch.setattr(fix_app._fake_db, "get", _fake_get, raising=False)

    def _fake_fetch_where(
        session: object, table: object, filter_map: dict[str, object]
    ) -> list[object]:
        return []

    monkeypatch.setattr("app.routes.fetch_where", _fake_fetch_where)


def test_add_task_creates_and_triggers(fix_app: Flask, fix_bulk_insert_capture) -> None:
    """POST /add_task calls `bulk_insert` and returns an HX trigger."""
    client = fix_app.test_client()
    created = fix_bulk_insert_capture

    from uuid import uuid4 as _uuid4

    with client.session_transaction() as sess:
        sess["uid"] = str(_uuid4())

    resp = client.post("/add_task", data={"name": "foo", "description": "bar"})

    assert resp.status_code == 200
    assert resp.headers.get("HX-Trigger") == "newTask"
    # Inspect the fake DB session for the added TaskTable instance
    added = created.added
    assert len(added) >= 1
    new_item = added[0]
    assert getattr(new_item, "name", None) == "foo"
    assert getattr(new_item, "description", None) == "bar"


def test_edit_task_updates_and_triggers(
    fix_app: Flask, fix_update_capture: dict[str, object]
) -> None:
    """POST /edit_task/<id> calls `update_where` with provided updates."""
    client = fix_app.test_client()
    captured = fix_update_capture

    task_id = str(uuid4())
    with client.session_transaction() as sess:
        sess["uid"] = str(uuid4())

    resp = client.post(
        f"/edit_task/{task_id}", data={"name": "foo", "description": "baz"}
    )

    assert resp.status_code == 200
    assert resp.headers.get("HX-Trigger") == "newTask"
    assert "match_cols" in captured
    assert "id" in captured["match_cols"]
    assert captured["updates"]["name"] == "foo"


def test_delete_task_calls_delete_and_returns_204(
    fix_app: Flask, fix_delete_capture: dict[str, object]
) -> None:
    """DELETE /delete-task/<id> invokes `delete_where` and returns 204 with trigger."""
    client = fix_app.test_client()
    called = fix_delete_capture

    tid = str(uuid4())
    with client.session_transaction() as sess:
        sess["uid"] = str(uuid4())

    resp = client.open(f"/delete-task/{tid}", method="DELETE")

    assert resp.status_code == 204
    assert resp.headers.get("HX-Trigger") == "newTask"
    assert "match_col" in called


@pytest.mark.usefixtures("fix_fetch_no_task")
def test_show_edit_task_not_found_returns_404(
    fix_app: Flask,
) -> None:
    """GET /show_edit_task/<id> returns 404 when the task isn't found."""
    client = fix_app.test_client()
    tid = str(uuid4())
    with client.session_transaction() as sess:
        sess["uid"] = str(uuid4())

    resp = client.get(f"/show_edit_task/{tid}")
    assert resp.status_code == 404


@pytest.mark.usefixtures("fix_fetch_task_for_toggle")
def test_toggle_task_toggles_and_triggers(
    fix_app: Flask, fix_update_capture: dict[str, object]
) -> None:
    """POST /toggle_task/<id> flips completion and triggers HX event."""
    client = fix_app.test_client()
    captured = fix_update_capture

    tid = str(uuid4())
    with client.session_transaction() as sess:
        sess["uid"] = str(uuid4())

    resp = client.post(f"/toggle_task/{tid}")
    assert resp.status_code == 204
    assert resp.headers.get("HX-Trigger") == "newTask"
    assert "match_cols" in captured


def test_search_tasks_calls_crud_search_and_renders(
    fix_app: Flask, fix_crud_search_capture: dict[str, object]
) -> None:
    """GET /search_tasks with query invokes `crud_search_tasks` and renders partial."""
    client = fix_app.test_client()
    called = fix_crud_search_capture

    with client.session_transaction() as sess:
        sess["uid"] = str(uuid4())

    resp = client.get("/search_tasks", query_string={"search": "term"})
    assert resp.status_code == 200
    assert called.get("search_string") == "term"


def test_logout_clears_session_and_redirects(fix_app: Flask) -> None:
    """GET /logout clears the session and redirects to login."""
    client = fix_app.test_client()

    with client.session_transaction() as sess:
        sess["uid"] = str(uuid4())

    resp = client.get("/logout")
    assert resp.status_code in (301, 302)
    assert "/login" in resp.headers.get("Location", "")
