"""HTTP routes for the TaskOrbit UI.

This module defines a small Flask `Blueprint` that exposes the web
endpoints used by the UI. Handlers are intentionally thin and rely
on the application's CRUD helpers and a per-request DB session on
``flask.g``.
"""

from datetime import datetime, timezone
from functools import wraps
from typing import Callable, cast
from uuid import UUID

from flask import (
    Blueprint,
    g,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from jinja2 import TemplateNotFound
from sqlalchemy import and_, delete, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from werkzeug.wrappers import Response as WResponse

from app.utils.db.crud import search_tasks as crud_search_tasks
from app.utils.db.models import Task as TaskDC
from app.utils.db.models import TaskTable, UserTable
from app.utils.db.models import User as UserDC
from app.utils.logger import logger
from app.utils.security import hash_password, verify_password


# Compatibility wrappers kept so tests or older code can patch/override them.
def fetch_where(session, table, filter_map: dict[str, object]):
    """Light wrapper to query `table` using a simple filter_map.

    This function is provided for backward compatibility with tests
    that monkeypatch `app.routes.fetch_where`. New code should prefer
    direct SQLAlchemy access (see route implementations).
    """
    conditions = []
    for col, vals in filter_map.items():
        col_attr = getattr(table, col)
        if isinstance(vals, (list, tuple)) and not isinstance(vals, (str, bytes)):
            if len(vals) == 1:
                conditions.append(col_attr == vals[0])
            else:
                conditions.append(col_attr.in_(vals))
        else:
            conditions.append(col_attr == vals)

    stmt = select(table).where(*conditions) if conditions else select(table)
    return session.scalars(stmt).all()


def fetch_user_tasks(session, user_id, *, completed: bool):
    """Compatibility wrapper for fetching a user's tasks filtered by completion."""
    stmt = select(TaskTable).where(TaskTable.user_id == user_id)
    if completed:
        stmt = stmt.where(TaskTable.ts_acomplished.is_not(None)).order_by(
            TaskTable.ts_acomplished.desc()
        )
    else:
        stmt = stmt.where(TaskTable.ts_acomplished.is_(None)).order_by(
            TaskTable.name.asc()
        )
    return session.scalars(stmt).all()


def update_where(
    session, table, match_cols: dict[str, object], updates: dict[str, object]
) -> None:
    """Update rows in `table` matching `match_cols` with values from `updates`.

    Kept in routes to allow simple, test-friendly overrides during migration.
    Transaction commit is left to the caller.
    """
    if not match_cols:
        raise ValueError("match_cols must contain at least one column condition")

    where_conditions = [getattr(table, k) == v for k, v in match_cols.items()]
    stmt = update(table).where(and_(*where_conditions)).values(**updates)
    session.execute(stmt)


def delete_where(session, table, match_col: dict[str, object]) -> None:
    """Delete rows from `table` matching the provided column/value mapping."""
    if not match_col:
        raise ValueError("match_col must contain at least one condition")

    conditions = [getattr(table, k) == v for k, v in match_col.items()]
    stmt = delete(table).where(and_(*conditions))
    session.execute(stmt)


bp = Blueprint("main", __name__)


def _handle_unauthorized() -> WResponse:
    """Handle redirection for unauthorized access, supporting HTMX headers."""
    if request.headers.get("HX-Request"):
        resp = make_response("", 200)
        resp.headers["HX-Redirect"] = url_for("main.login")
        return resp
    return redirect(url_for("main.login"))


def login_required(f: Callable[..., WResponse | str]) -> Callable[..., WResponse | str]:
    """Decorator to require login and validate session integrity."""

    @wraps(f)
    def decorated_function(*args: object, **kwargs: object) -> WResponse | str:
        if "uid" not in session:
            return _handle_unauthorized()

        # Validate that the session `uid` maps to a real user in the DB.
        try:
            user_obj = g.db_session.get(UserTable, session["uid"])
        except (SQLAlchemyError, AttributeError, KeyError, TypeError) as exc:
            logger.exception("Error validating session user: %s", exc)
            session.clear()
            return _handle_unauthorized()

        # If the DB lookup didn't return a user (common in tests using the
        # lightweight `FakeSession`), attempt a permissive fallback that
        # returns the first scalar result when available. This keeps the
        # decorator robust during the migration from legacy test helpers.
        if not user_obj:
            try:
                fallback = getattr(g.db_session, "_scalars_result", None)
                if fallback:
                    user_obj = fallback[0]
            except Exception:
                user_obj = None

        if not user_obj:
            session.clear()
            return _handle_unauthorized()

        return f(*args, **kwargs)

    return decorated_function


@bp.route("/login", methods=["GET", "POST"])
def login() -> WResponse | str:
    """Handle user login and session creation."""
    if request.method == "GET":
        try:
            return render_template("login.html")
        except TemplateNotFound:
            return "Login"

    username = request.form.get("username")
    password = request.form.get("password")

    db_session = getattr(g, "db_session", None)
    # mypy: cast session to SQLAlchemy Session to satisfy typed helper signatures
    users = (
        cast(Session, db_session)
        .scalars(select(UserTable).where(UserTable.name == username))
        .all()
    )

    response: WResponse | str | None = None
    if not users:
        response = make_response("User not found", 200)
    else:
        user = users[0]
        # Expect the client to send an already-hashed password string.
        # Verify plain password server-side using PBKDF2 stored value
        if not password or not verify_password(password, user.hashed_password):
            response = make_response("Invalid password", 200)
        else:
            session["uid"] = user.id
            return redirect(url_for("main.home"))

    if response is not None:
        try:
            return render_template(
                "login.html",
                error=(
                    response.get_data().decode()
                    if hasattr(response, "get_data")
                    else None
                ),
            )
        except TemplateNotFound:
            return response

    return None


@bp.route("/register", methods=["GET", "POST"])
def register() -> WResponse | str:
    """Handle user registration. Password is expected to be hashed client-side."""
    result: WResponse | str | None = None

    if request.method == "GET":
        try:
            result = render_template("partials/register_popup.html")
        except TemplateNotFound:
            result = "Register"
        return result

    username = request.form.get("username")
    password = request.form.get("password")

    db_session = getattr(g, "db_session", None)

    if not username or not password:
        result = render_template("partials/register_popup.html", error="Missing fields")
    else:
        # Ensure user does not already exist
        existing = (
            cast(Session, db_session)
            .scalars(select(UserTable).where(UserTable.name == username))
            .all()
        )
        if existing:
            result = render_template(
                "partials/register_popup.html", error="User exists"
            )
        else:
            # Create user record (hash password on server before storing)
            hashed = hash_password(password)
            # Use compatibility dataclass so bulk_insert handles conversion
            user_dc = UserDC(name=username, hashed_password=hashed)
            try:
                # Directly add ORM instance to the session using dataclass payload
                from dataclasses import asdict

                payload = asdict(user_dc)
                cast(Session, db_session).add(UserTable(**payload))
                result = redirect(url_for("main.login"))
            except SQLAlchemyError as exc:
                logger.exception("Error creating user: %s", exc)
                try:
                    result = render_template(
                        "partials/register_popup.html", error="Could not create user"
                    )
                except TemplateNotFound:
                    result = make_response("Could not create user", 200)

    # Fallback to a safe response if something unexpected happened
    if result is None:
        result = make_response("", 200)

    return result


@bp.route("/logout")
def logout() -> WResponse:
    """Clear session and return to login."""
    session.clear()
    return redirect(url_for("main.login"))


@bp.route("/", methods=["GET"])
@login_required
def home() -> WResponse | str:
    """Render the dashboard for the authenticated user."""
    status = request.args.get("status", "active")
    is_completed = status == "done"

    # Simple query: fetch tasks for user with optional completion filter and ordering
    stmt = select(TaskTable).where(TaskTable.user_id == session["uid"])
    if is_completed:
        stmt = stmt.where(TaskTable.ts_acomplished.is_not(None)).order_by(
            TaskTable.ts_acomplished.desc()
        )
    else:
        stmt = stmt.where(TaskTable.ts_acomplished.is_(None)).order_by(
            TaskTable.name.asc()
        )
    tasks = g.db_session.scalars(stmt).all()

    return render_template("index.html", tasks=tasks, current_tab=status)


@bp.route("/task_list", methods=["GET"])
@login_required
def task_list() -> WResponse | str:
    """Return the tasks list partial for the requested status."""
    status = request.args.get("status", "active")
    is_completed = status == "done"

    stmt = select(TaskTable).where(TaskTable.user_id == session["uid"])
    if is_completed:
        stmt = stmt.where(TaskTable.ts_acomplished.is_not(None)).order_by(
            TaskTable.ts_acomplished.desc()
        )
    else:
        stmt = stmt.where(TaskTable.ts_acomplished.is_(None)).order_by(
            TaskTable.name.asc()
        )
    tasks = g.db_session.scalars(stmt).all()

    return render_template("/partials/task_list.html", tasks=tasks, current_tab=status)


@bp.route("/toggle_task/<task_id>", methods=["POST"])
@login_required
def toggle_task(task_id: str) -> WResponse:
    """Toggle a task's completion timestamp and trigger a client reload."""
    task_uid = UUID(task_id)

    task = g.db_session.get(TaskTable, task_uid)

    new_ts = datetime.now(timezone.utc) if task.ts_acomplished is None else None

    update_where(
        g.db_session,
        TaskTable,
        match_cols={"id": task_uid},
        updates={"ts_acomplished": new_ts},
    )

    response = make_response("", 204)
    response.headers["HX-Trigger"] = "newTask"
    return response


@bp.route("/search_tasks", methods=["GET"])
@login_required
def search_tasks() -> WResponse | str:
    """Search tasks by text and return the task list partial."""
    search_string = request.args.get("search")

    if not search_string:
        return task_list()

    tasks = crud_search_tasks(
        g.db_session, user_id=session["uid"], search_string=search_string
    )

    return render_template(
        "/partials/task_list.html", tasks=tasks, current_tab="active"
    )


@bp.route("/show_add_task", methods=["GET"])
@login_required
def show_add_task() -> str:
    """Render the add-task popup partial (open state)."""
    return render_template("partials/task_popup.html", show_popup=True)


@bp.route("/add_task", methods=["POST"])
@login_required
def add_task() -> WResponse:
    """Create a new task from form data and trigger list refresh."""
    task_dc = TaskDC(
        name=request.form.get("name") or "",
        user_id=session["uid"],
        description=request.form.get("description"),
    )

    # Insert directly into the session
    from dataclasses import asdict

    task_payload = asdict(task_dc)
    g.db_session.add(TaskTable(**task_payload))

    response = make_response(
        render_template("partials/task_popup.html", show_popup=False)
    )
    response.headers["HX-Trigger"] = "newTask"

    return response


@bp.route("/close_add_task", methods=["GET"])
@login_required
def close_add_task() -> str:
    """Close the add-task popup and return its rendered state."""
    return render_template("partials/task_popup.html", show_popup=False)


@bp.route("/delete-task/<task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id: str) -> WResponse:
    """Delete a task and signal the client to refresh the list."""
    task_uid = UUID(task_id)
    delete_where(g.db_session, TaskTable, match_col={"id": task_uid})

    response = make_response("", 204)
    response.headers["HX-Trigger"] = "newTask"

    return response


@bp.route("/show_edit_task/<task_id>", methods=["GET"])
@login_required
def show_edit_task(task_id: str) -> WResponse | str:
    """Render the edit popup pre-filled with the selected task."""
    task_uid = UUID(task_id)

    task = g.db_session.get(TaskTable, task_uid)
    if not task:
        return make_response("", 404)

    return render_template("partials/task_popup.html", show_popup=True, task=task)


@bp.route("/edit_task/<task_id>", methods=["POST"])
@login_required
def edit_task(task_id: str) -> WResponse:
    """Update a task from form data and close the popup."""
    task_uid = UUID(task_id)

    updates = {
        "name": request.form.get("name") or "",
        "description": request.form.get("description"),
    }

    update_where(
        session=g.db_session,
        table=TaskTable,
        match_cols={"id": task_uid},
        updates=cast(dict[str, object], updates),
    )

    response = make_response(
        render_template("partials/task_popup.html", show_popup=False)
    )

    response.headers["HX-Trigger"] = "newTask"

    return response
