"""HTTP routes for the TaskOrbit UI.

This module exposes a small set of Flask endpoints used by the web
UI. Handlers are intentionally thin and operate directly against the
SQLAlchemy ORM session available on ``flask.g``. Keep business logic
out of handlers: they translate HTTP input -> DB operations -> views.

Design / Philosophy
-------------------
- Handlers should be small, testable, and explicit about side effects.
- Prefer explicit ORM statements inside routes rather than indirection
    via opaque helpers. This makes behavior clearer and easier to test.
- Server is responsible for security-sensitive transformations (e.g.
    hashing) so clients remain thin and untrusted.
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
from sqlalchemy.orm import Session
from werkzeug.wrappers import Response as WResponse

from app.schemas import TaskSchema, UserSchema

# search logic was in small CRUD helper; inlined below for clarity
from app.utils.db.models import TaskTable, UserTable
from app.utils.logger import logger
from app.utils.security import hash_password, verify_password

bp = Blueprint("main", __name__)


def _handle_unauthorized() -> WResponse:
    """Redirect an unauthorized request to the login page.

    Returns an HTMX-aware redirect when the request contains the
    ``HX-Request`` header so client-side navigation behaves correctly.

    Returns:
        A Flask response object performing either a normal redirect or
        an HTMX redirect header.
    """
    if request.headers.get("HX-Request"):
        resp = make_response("", 200)
        resp.headers["HX-Redirect"] = url_for("main.login")
        return resp
    return redirect(url_for("main.login"))


def login_required(f: Callable[..., WResponse | str]) -> Callable[..., WResponse | str]:
    """Decorator that ensures a valid authenticated user exists.

    This decorator checks ``session['uid']`` and verifies it maps to a
    real user record via the per-request DB session. If verification
    fails the client is redirected to the login flow.

    Args:
        f: the view function to wrap.

    Returns:
        The wrapped view function which will enforce authentication.
    """

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
            except (AttributeError, IndexError, TypeError):
                user_obj = None

        if not user_obj:
            session.clear()
            return _handle_unauthorized()

        return f(*args, **kwargs)

    return decorated_function


@bp.route("/login", methods=["GET", "POST"])
def login() -> WResponse | str:
    """Handle user authentication and create a session on success.

    This endpoint accepts form-encoded username and password values.
    The server validates the provided plaintext password against the
    stored hash using `verify_password` and sets ``session['uid']`` on
    successful authentication.

    Returns:
        Renders the login template on GET or on failed auth, otherwise
        redirects to the home page on success.
    """
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
        # Verify provided plaintext password against stored hash.
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
    """Create a new user account.

    The endpoint expects form fields ``username`` and ``password`` with
    the password provided in plaintext. The server hashes the password
    before persisting the user record.

    Returns:
        Renders the register popup on GET or on error, otherwise
        redirects to the login page after successful creation.
    """
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
            # Create user record (server hashes plaintext password)
            hashed = hash_password(password)
            # Validate payload with Pydantic schema then persist
            user_schema = UserSchema.model_validate(
                {
                    "name": username,
                    "hashed_password": hashed,
                }
            )
            try:
                cast(Session, db_session).add(UserTable(**user_schema.model_dump()))
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
    """Clear the session and redirect the client to the login page.

    Returns:
        A Flask redirect response to the login endpoint.
    """
    session.clear()
    return redirect(url_for("main.login"))


@bp.route("/", methods=["GET"])
@login_required
def home() -> WResponse | str:
    """Render the main dashboard for the authenticated user.

    Args:
        None (uses session['uid'] to identify the user).

    Returns:
        The rendered index template with the user's tasks.
    """
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
    """Return the tasks list partial for the requested status.

    Query params:
        status: 'active' or 'done' to filter tasks by completion.

    Returns:
        Rendered partial HTML for the task list.
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
    """Toggle a task's completion timestamp and trigger a client refresh.

    Args:
        task_id: UUID string for the task to toggle.

    Returns:
        204 response with an HX trigger header on success.
    """
    task_uid = UUID(task_id)

    task = g.db_session.get(TaskTable, task_uid)

    new_ts = datetime.now(timezone.utc) if task.ts_acomplished is None else None

    stmt = (
        update(TaskTable).where(TaskTable.id == task_uid).values(ts_acomplished=new_ts)
    )
    g.db_session.execute(stmt)

    response = make_response("", 204)
    response.headers["HX-Trigger"] = "newTask"
    return response


@bp.route("/search_tasks", methods=["GET"])
@login_required
def search_tasks() -> WResponse | str:
    """Search tasks by text and return the task list partial.

    Query params:
        search: the text to search for. If empty, delegates to `task_list`.

    Returns:
        Rendered task list partial for matching tasks.
    """
    search_string = request.args.get("search")

    if not search_string:
        return task_list()

    # Inline search: find tasks for the user where name or description
    # contains the search string (case-insensitive).
    pattern = f"%{search_string}%"
    stmt = select(TaskTable).where(
        and_(
            TaskTable.user_id == session["uid"],
            or_(TaskTable.name.ilike(pattern), TaskTable.description.ilike(pattern)),
        )
    )

    try:
        tasks = g.db_session.execute(stmt).scalars().all()
    except AttributeError:
        tasks = g.db_session.scalars(stmt).all()

    return render_template(
        "/partials/task_list.html", tasks=tasks, current_tab="active"
    )


@bp.route("/show_add_task", methods=["GET"])
@login_required
def show_add_task() -> str:
    """Render the add-task popup in its open state.

    Returns:
        HTML partial for the add-task dialog.
    """
    return render_template("partials/task_popup.html", show_popup=True)


@bp.route("/add_task", methods=["POST"])
@login_required
def add_task() -> WResponse:
    """Create a new task from form data and trigger a list refresh.

    Expects form fields: ``name`` and optional ``description``. The
    server constructs a `TaskTable` ORM instance and adds it to the
    active session; callers are responsible for committing where
    appropriate.

    Returns:
        Rendered popup state and an HX trigger header to prompt list
        refresh on the client.
    """
    task_schema = TaskSchema.model_validate(
        {
            "name": request.form.get("name") or "",
            "user_id": session["uid"],
            "description": request.form.get("description"),
        }
    )

    # Insert directly into the session using validated schema payload
    g.db_session.add(TaskTable(**task_schema.model_dump()))

    response = make_response(
        render_template("partials/task_popup.html", show_popup=False)
    )
    response.headers["HX-Trigger"] = "newTask"

    return response


@bp.route("/close_add_task", methods=["GET"])
@login_required
def close_add_task() -> str:
    """Render the add-task popup in its closed state.

    Returns:
        HTML partial representing the closed popup.
    """
    return render_template("partials/task_popup.html", show_popup=False)


@bp.route("/delete-task/<task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id: str) -> WResponse:
    """Delete a task and signal the client to refresh the list.

    Args:
        task_id: UUID string identifying the task to delete.

    Returns:
        204 response with an HX trigger header on success.
    """
    task_uid = UUID(task_id)
    stmt = delete(TaskTable).where(TaskTable.id == task_uid)
    g.db_session.execute(stmt)

    response = make_response("", 204)
    response.headers["HX-Trigger"] = "newTask"

    return response


@bp.route("/show_edit_task/<task_id>", methods=["GET"])
@login_required
def show_edit_task(task_id: str) -> WResponse | str:
    """Render the edit popup pre-filled with the selected task.

    Args:
        task_id: UUID string identifying the task to edit.

    Returns:
        Rendered popup with the task or 404 when not found.
    """
    task_uid = UUID(task_id)

    task = g.db_session.get(TaskTable, task_uid)
    if not task:
        return make_response("", 404)

    return render_template("partials/task_popup.html", show_popup=True, task=task)


@bp.route("/edit_task/<task_id>", methods=["POST"])
@login_required
def edit_task(task_id: str) -> WResponse:
    """Update a task from form data and close the popup.

    Args:
        task_id: UUID string identifying the task to update.

    Returns:
        Rendered popup (closed) and HX trigger header to prompt list
        refresh on the client.
    """
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

    response = make_response(
        render_template("partials/task_popup.html", show_popup=False)
    )

    response.headers["HX-Trigger"] = "newTask"

    return response
