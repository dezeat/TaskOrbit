"""HTTP routes for the TaskOrbit UI.

This module exposes the Flask endpoints for the web interface. Handlers are
intentionally thin, translating HTTP input into direct SQLAlchemy ORM operations
against the session available on ``flask.g``.

Transaction Management:
-----------------------
This application uses an **Explicit Commit** pattern. The database session
is automatically opened and closed per request, but transactions are *not*
automatically committed.

Any route that modifies data (INSERT, UPDATE, DELETE) must explicitly call
``g.db_session.commit()``. This prevents accidental writes during read-only
operations and ensures that data is only persisted when the business logic
successfully completes.
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
from sqlalchemy import and_, delete, or_, select, update
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.wrappers import Response as WResponse

from app.schemas import TaskSchema, UserSchema
from app.utils.logger import logger
from app.utils.models import TaskTable, UserTable
from app.utils.security import hash_password, verify_password

bp = Blueprint("main", __name__)


def _handle_unauthorized() -> WResponse:
    """Redirect unauthorized requests to login, supporting HTMX headers."""
    if request.headers.get("HX-Request"):
        resp = make_response("", 200)
        resp.headers["HX-Redirect"] = url_for("main.login")
        return resp
    return redirect(url_for("main.login"))


def login_required(f: Callable[..., WResponse | str]) -> Callable[..., WResponse | str]:
    """Decorate routes to require a valid user session.

    Verifies that ``session['uid']`` exists and corresponds to a real user
    in the database. If verification fails, the session is cleared and the
    user is redirected.
    """

    @wraps(f)
    def decorated_function(*args: object, **kwargs: object) -> WResponse | str:
        if "uid" not in session:
            return _handle_unauthorized()

        try:
            user_obj = g.db_session.get(UserTable, session["uid"])
        except (SQLAlchemyError, AttributeError, KeyError, TypeError) as exc:
            logger.exception("Error validating session user: %s", exc)
            session.clear()
            return _handle_unauthorized()

        if not user_obj:
            session.clear()
            return _handle_unauthorized()

        return f(*args, **kwargs)

    return decorated_function


@bp.route("/login", methods=["GET", "POST"])
def login() -> WResponse | str:
    """Authenticate a user and establish a session.

    On POST, verifies the username and password against the database.
    If successful, sets the user ID in the encrypted client session.
    """
    if request.method == "GET":
        try:
            return render_template("login.html")
        except TemplateNotFound:
            return "Login"

    username = request.form.get("username")
    password = request.form.get("password")

    users = g.db_session.scalars(
        select(UserTable).where(UserTable.name == username)
    ).all()

    response: WResponse | str | None = None
    if not users:
        response = make_response("User not found", 200)
    else:
        user = users[0]
        if not password or not verify_password(password, user.hashed_password):
            response = make_response("Invalid password", 200)
        else:
            session["uid"] = user.id
            return redirect(url_for("main.home"))

    if response is not None:
        return render_template(
            "login.html",
            error=(
                response.get_data().decode() if hasattr(response, "get_data") else None
            ),
        )

    return None


@bp.route("/register", methods=["GET", "POST"])
def register() -> WResponse | str:
    """Register a new user account.

    Validates that the username is unique. If valid, hashes the password
    server-side, persists the new user, and commits the transaction.
    """
    result: WResponse | str | None = None

    if request.method == "GET":
        return render_template("partials/register_popup.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        result = render_template("partials/register_popup.html", error="Missing fields")
    else:
        existing = g.db_session.scalars(
            select(UserTable).where(UserTable.name == username)
        ).first()

        if existing:
            result = render_template(
                "partials/register_popup.html", error="User exists"
            )
        else:
            hashed = hash_password(password)
            user_schema = UserSchema.model_validate(
                {"name": username, "hashed_password": hashed}
            )
            try:
                g.db_session.add(UserTable(**user_schema.model_dump()))
                g.db_session.commit()
                result = redirect(url_for("main.login"))
            except SQLAlchemyError as exc:
                g.db_session.rollback()
                logger.exception("Error creating user: %s", exc)
                result = render_template(
                    "partials/register_popup.html", error="Could not create user"
                )

    if result is None:
        result = make_response("", 200)

    return result


@bp.route("/logout")
def logout() -> WResponse:
    """Clear the client session and redirect to login."""
    session.clear()
    return redirect(url_for("main.login"))


@bp.route("/", methods=["GET"])
@login_required
def home() -> WResponse | str:
    """Display the main task dashboard.

    Fetches tasks associated with the current user, filtered by the
    optional 'status' query parameter (active vs done).
    """
    status = request.args.get("status", "active")
    is_completed = status == "done"

    stmt = select(TaskTable).where(TaskTable.user_id == UUID(str(session["uid"])))
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
    """Return the task list HTML partial.

    Used by HTMX to refresh the list without reloading the full page.
    Supports filtering via the 'status' query parameter.
    """
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
    """Toggle the completion status of a task.

    Updates the `ts_acomplished` timestamp. If the task is done, it resets
    it to None (active); otherwise, it sets it to the current UTC time.
    """
    task_uid = UUID(task_id)
    task = g.db_session.get(TaskTable, task_uid)

    if task:
        new_ts = datetime.now(timezone.utc) if task.ts_acomplished is None else None
        task.ts_acomplished = new_ts
        g.db_session.commit()

    response = make_response("", 204)
    response.headers["HX-Trigger"] = "newTask"
    return response


@bp.route("/search_tasks", methods=["GET"])
@login_required
def search_tasks() -> WResponse | str:
    """Filter tasks by a search string.

    Performs a case-insensitive search on both task name and description.
    """
    search_string = request.args.get("search")

    if not search_string:
        return task_list()

    pattern = f"%{search_string}%"
    stmt = select(TaskTable).where(
        and_(
            TaskTable.user_id == session["uid"],
            or_(TaskTable.name.ilike(pattern), TaskTable.description.ilike(pattern)),
        )
    )
    tasks = g.db_session.scalars(stmt).all()

    return render_template(
        "/partials/task_list.html", tasks=tasks, current_tab="active"
    )


@bp.route("/show_add_task", methods=["GET"])
@login_required
def show_add_task() -> str:
    """Return the 'Add Task' modal partial."""
    return render_template("partials/task_popup.html", show_popup=True)


@bp.route("/add_task", methods=["POST"])
@login_required
def add_task() -> WResponse:
    """Create and persist a new task.

    Validates input using `TaskSchema`, adds the record to the session,
    and commits the transaction. Returns an empty response with an HTMX
    trigger to refresh the list.
    """
    task_schema = TaskSchema.model_validate(
        {
            "name": request.form.get("name") or "",
            "user_id": session["uid"],
            "description": request.form.get("description"),
        }
    )

    g.db_session.add(TaskTable(**task_schema.model_dump()))
    g.db_session.commit()

    response = make_response(
        render_template("partials/task_popup.html", show_popup=False)
    )
    response.headers["HX-Trigger"] = "newTask"
    return response


@bp.route("/close_add_task", methods=["GET"])
@login_required
def close_add_task() -> str:
    """Return the closed state of the task modal."""
    return render_template("partials/task_popup.html", show_popup=False)


@bp.route("/delete-task/<task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id: str) -> WResponse:
    """Permanently delete a task."""
    task_uid = UUID(task_id)
    stmt = delete(TaskTable).where(TaskTable.id == task_uid)
    g.db_session.execute(stmt)
    g.db_session.commit()

    response = make_response("", 204)
    response.headers["HX-Trigger"] = "newTask"
    return response


@bp.route("/show_edit_task/<task_id>", methods=["GET"])
@login_required
def show_edit_task(task_id: str) -> WResponse | str:
    """Return the 'Edit Task' modal partial pre-filled with data."""
    task_uid = UUID(task_id)
    task = g.db_session.get(TaskTable, task_uid)
    if not task:
        return make_response("", 404)

    return render_template("partials/task_popup.html", show_popup=True, task=task)


@bp.route("/edit_task/<task_id>", methods=["POST"])
@login_required
def edit_task(task_id: str) -> WResponse:
    """Update an existing task's details."""
    task_uid = UUID(task_id)

    updates = {
        "name": request.form.get("name") or "",
        "description": request.form.get("description"),
    }

    stmt = (
        update(TaskTable)
        .where(TaskTable.id == task_uid)
        .values(**cast(dict[str, object], updates))
    )
    g.db_session.execute(stmt)
    g.db_session.commit()

    response = make_response(
        render_template("partials/task_popup.html", show_popup=False)
    )
    response.headers["HX-Trigger"] = "newTask"
    return response
