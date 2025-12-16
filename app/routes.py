"""HTTP routes for the TaskOrbit UI.

This module defines a small Flask `Blueprint` that exposes the web
endpoints used by the demo UI. Handlers are intentionally thin and rely
on the application's CRUD helpers and a per-request DB session on
``flask.g``.
"""

from datetime import datetime, timezone
from uuid import UUID

from flask import (
    Blueprint,
    Response,
    g,
    make_response,
    render_template,
    request,
    session,
)

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
from app.utils.db.models import Task, TaskTable, UserTable

bp = Blueprint("main", __name__)
"""Main application blueprint exposing task-related endpoints."""


@bp.route("/", methods=["GET"])
def home() -> str:
    """Render the home page for the demo admin user.

    Sets a placeholder `session['uid']` for demo auth and renders the
    main task list view.
    """
    result = fetch_where(
        session=g.db_session, table=UserTable, filter_map={"name": ["admin"]}
    )
    session["uid"] = result[0].id

    status = request.args.get("status", "active")

    is_completed = status == "done"
    tasks = fetch_user_tasks(
        session=g.db_session, user_id=session["uid"], completed=is_completed
    )

    return render_template("index.html", tasks=tasks, current_tab=status)


@bp.route("/task_list", methods=["GET"])
def task_list() -> str:
    """Return the tasks list partial for the requested status."""
    status = request.args.get("status", "active")
    is_completed = status == "done"

    tasks = fetch_user_tasks(
        session=g.db_session, user_id=session["uid"], completed=is_completed
    )

    return render_template(
        "/partials/task_list.html", tasks=tasks, current_tab=status
    )


@bp.route("/toggle_task/<task_id>", methods=["POST"])
def toggle_task(task_id: str) -> Response:
    """Toggle a task's completion timestamp and trigger a client reload."""
    task_uid = UUID(task_id)

    task = fetch_where(g.db_session, TaskTable, {"id": [task_uid]})[0]

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
def search_tasks() -> str:
    """Search tasks by text and return the task list partial."""
    search_string = request.args.get("search")
    if search_string:
        tasks = crud_search_tasks(
            g.db_session, user_id=session["uid"], search_string=search_string
        )

        return render_template("/partials/task_list.html", tasks=tasks)

    return task_list()


@bp.route("/show_add_task", methods=["GET"])
def show_add_task() -> str:
    """Render the add-task popup partial (open state)."""
    return render_template("partials/task_popup.html", show_popup=True)


@bp.route("/add_task", methods=["POST"])
def add_task() -> Response:
    """Create a new task from form data and trigger list refresh."""
    task = Task(
        user_id=session["uid"],
        name=request.form.get("name"),
        description=request.form.get("description"),
    )

    bulk_insert(session=g.db_session, table=TaskTable, data=[task])

    response = make_response(
        render_template("partials/task_popup.html", show_popup=False)
    )
    response.headers["HX-Trigger"] = "newTask"

    return response


@bp.route("/close_add_task", methods=["GET"])
def close_add_task() -> str:
    """Close the add-task popup and return its rendered state."""
    return render_template("partials/task_popup.html", show_popup=False)


@bp.route("/delete-task/<task_id>", methods=["DELETE"])
def delete_task(task_id: str) -> Response:
    """Delete a task and signal the client to refresh the list."""
    task_uid = UUID(task_id)
    delete_where(g.db_session, TaskTable, match_col={"id": task_uid})

    response = make_response("", 204)
    response.headers["HX-Trigger"] = "newTask"

    return response


@bp.route("/show_edit_task/<task_id>", methods=["GET"])
def show_edit_task(task_id: str) -> str:
    """Render the edit popup pre-filled with the selected task."""
    task_uid = UUID(task_id)

    tasks = fetch_where(
        session=g.db_session, table=TaskTable, filter_map={"id": [task_uid]}
    )

    if not tasks:
        return "", 404

    return render_template(
        "partials/task_popup.html", show_popup=True, task=tasks[0]
    )


@bp.route("/edit_task/<task_id>", methods=["POST"])
def edit_task(task_id: str) -> Response:
    """Update a task from form data and close the popup."""
    task_uid = UUID(task_id)

    updates = {
        "name": request.form.get("name"),
        "description": request.form.get("description"),
    }

    update_where(
        session=g.db_session,
        table=TaskTable,
        match_cols={"id": task_uid},
        updates=updates,
    )

    response = make_response(
        render_template("partials/task_popup.html", show_popup=False)
    )

    response.headers["HX-Trigger"] = "newTask"

    return response
