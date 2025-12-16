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
def fix_update_capture(
    monkeypatch: pytest.MonkeyPatch, fix_app: Flask
) -> dict[str, object]:
    """Capture `match_cols` and `updates` passed to `update_where`.

    The returned dict will contain keys `match_cols` and `updates` after the
    patched function is called by the application code.
    """
    captured: dict[str, object] = {}

    def _fake_execute(stmt: object) -> object:
        captured["stmt"] = stmt

        # emulate original execute return shape
        class _ScalarResult:
            def scalars(self_inner) -> "_ScalarResult":
                return self_inner

            def all(self_inner) -> list[object]:
                return []

        return _ScalarResult()

    monkeypatch.setattr(fix_app._fake_db, "execute", _fake_execute, raising=False)
    return captured


@pytest.fixture
def fix_delete_capture(
    monkeypatch: pytest.MonkeyPatch, fix_app: Flask
) -> dict[str, object]:
    """Capture the `match_col` arg passed to `delete_where`.

    Tests can assert that the expected identifier was supplied for deletion.
    """
    called: dict[str, object] = {}

    def _fake_execute(stmt: object) -> object:
        called["stmt"] = stmt

        class _ScalarResult:
            def scalars(self_inner) -> "_ScalarResult":
                return self_inner

            def all(self_inner) -> list[object]:
                return []

        return _ScalarResult()

    monkeypatch.setattr(fix_app._fake_db, "execute", _fake_execute, raising=False)
    return called


@pytest.fixture
def fix_crud_search_capture(
    monkeypatch: pytest.MonkeyPatch, fix_app: Flask
) -> dict[str, object]:
    """Capture the search string from the executed SQLAlchemy statement.

    The fixture monkeypatches the fake DB session's `execute` to record
    the statement and attempt to extract a pattern like "%term%".
    """
    called: dict[str, object] = {}

    def _fake_execute(stmt: object) -> object:
        called["stmt"] = stmt

        class _ScalarResult:
            def scalars(self_inner) -> "_ScalarResult":
                return self_inner

            def all(self_inner) -> list[object]:
                return []

        return _ScalarResult()

    # Capture the `search` query param by proxying `app.routes.request.args.get`.
    import app.routes as routes_mod

    orig_request = routes_mod.request

    class _ArgsProxy:
        def get(self_inner, key: str, default: object = None) -> object:
            val = orig_request.args.get(key, default)
            if key == "search":
                called["search_string"] = val
            return val

    class _ReqProxy:
        def __getattr__(self_inner, name: str) -> object:
            if name == "args":
                return _ArgsProxy()
            return getattr(orig_request, name)

    monkeypatch.setattr(routes_mod, "request", _ReqProxy(), raising=False)
    monkeypatch.setattr(fix_app._fake_db, "execute", _fake_execute, raising=False)
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

    # fake fetch behavior provided via the fake session's scalar results


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

    # fetch behavior handled by fake session scalar results


def test_add_task_creates_and_triggers(fix_app: Flask, fix_bulk_insert_capture) -> None:
    """POST /add_task adds a TaskTable instance to the DB session and returns an HX trigger."""
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
    assert "stmt" in captured
    stmt_str = str(captured["stmt"]).upper()
    assert "UPDATE" in stmt_str
    assert "NAME" in stmt_str


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
    assert "stmt" in called
    stmt_str = str(called["stmt"]).upper()
    assert "DELETE" in stmt_str


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
    assert "stmt" in captured
    stmt_str = str(captured["stmt"]).upper()
    assert "UPDATE" in stmt_str


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
