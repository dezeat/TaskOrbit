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
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from werkzeug.wrappers import Response as WResponse

from app.utils.db.crud import (
    bulk_insert,
    delete_where,
    fetch_user_tasks,
    fetch_where,
    update_where,
)
from app.utils.db.crud import (
    search_tasks as crud_search_tasks,
)
from app.utils.db.models import Task, TaskTable, User, UserTable
from app.utils.db.models import User as UserModel
from app.utils.logger import logger

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
            users = fetch_where(
                session=g.db_session,
                table=UserTable,
                filter_map={"id": [session["uid"]]},
            )
        except (SQLAlchemyError, AttributeError, KeyError, TypeError) as exc:
            logger.exception("Error validating session user: %s", exc)
            session.clear()
            return _handle_unauthorized()

        if not users:
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
    users = fetch_where(
        session=cast(Session, db_session),
        table=UserTable,
        filter_map={"name": [username]},
    )

    response: WResponse | str | None = None
    if not users:
        response = make_response("User not found", 200)
    else:
        user = cast(User, users[0])
        # Expect the client to send an already-hashed password string.
        if not password or password != user.hashed_password:
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
        existing = fetch_where(
            session=cast(Session, db_session),
            table=UserTable,
            filter_map={"name": [username]},
        )
        if existing:
            result = render_template(
                "partials/register_popup.html", error="User exists"
            )
        else:
            # Create user record (dataclass expected by bulk_insert)
            user = UserModel(name=username, hashed_password=password)
            try:
                bulk_insert(
                    session=cast(Session, db_session),
                    table=UserTable,
                    data=[user],
                )
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

    tasks = fetch_user_tasks(
        session=g.db_session, user_id=session["uid"], completed=is_completed
    )

    return render_template("index.html", tasks=tasks, current_tab=status)


@bp.route("/task_list", methods=["GET"])
@login_required
def task_list() -> WResponse | str:
    """Return the tasks list partial for the requested status."""
    status = request.args.get("status", "active")
    is_completed = status == "done"

    tasks = fetch_user_tasks(
        session=g.db_session, user_id=session["uid"], completed=is_completed
    )

    return render_template("/partials/task_list.html", tasks=tasks, current_tab=status)


@bp.route("/toggle_task/<task_id>", methods=["POST"])
@login_required
def toggle_task(task_id: str) -> WResponse:
    """Toggle a task's completion timestamp and trigger a client reload."""
    task_uid = UUID(task_id)

    task = cast(Task, fetch_where(g.db_session, TaskTable, {"id": [task_uid]})[0])

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
    task = Task(
        user_id=session["uid"],
        name=request.form.get("name") or "",
        description=request.form.get("description"),
    )

    bulk_insert(session=g.db_session, table=TaskTable, data=[task])

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

    tasks = fetch_where(
        session=g.db_session, table=TaskTable, filter_map={"id": [task_uid]}
    )

    if not tasks:
        return make_response("", 404)

    return render_template("partials/task_popup.html", show_popup=True, task=tasks[0])


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
