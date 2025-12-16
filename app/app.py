"""Flask application factory and request session management.

Exports `create_app` which wires DB session lifecycle hooks and the
minimal HTTP routes used by the demo application.
"""

from uuid import UUID

from flask import Flask, Response, g, make_response, render_template, request, session
from sqlalchemy.exc import IntegrityError

from app.utils.db.crud import bulk_insert, delete_where, fetch_where, update_where
from app.utils.db.database import BaseDB
from app.utils.db.models import Task, TaskTable, UserTable
from app.utils.logger import logger


def create_app(db: BaseDB, template_folder: str = "templates") -> Flask:
    """Create and configure the Flask application instance.

    Registers request lifecycle handlers that provide a scoped DB session
    via `flask.g` and defines the basic routes used by the UI.
    """
    app = Flask(__name__, template_folder=template_folder)

    start_session_management(app, db)

    @app.route("/", methods=["GET"])
    def home() -> str:
        """Render the home page showing the current user's tasks.

        The function uses a placeholder admin login for demo purposes.
        """
        # Placeholder for user login and auth
        result = fetch_where(
            session=g.db_session, table=UserTable, filter_map={"name": ["admin"]}
        )
        session["uid"] = result[0].id

        # Load all Tasks of the User
        tasks = fetch_where(
            session=g.db_session,
            table=TaskTable,
            filter_map={"user_id": [session["uid"]]},
        )

        return render_template("index.html", tasks=tasks)

    @app.route("/task_list", methods=["GET"])
    def task_list() -> str:
        tasks = fetch_where(
            session=g.db_session,
            table=TaskTable,
            filter_map={"user_id": [session["uid"]]},
        )

        return render_template("/partials/task_list.html", tasks=tasks)

    @app.route("/search_tasks", methods=["GET"])
    def search_tasks() -> str:
        search_string = request.args.get("search")
        if search_string:
            tasks = search_tasks(
                g.db_session, user_id=session["uid"], search_string=search_string
            )

            return render_template("/partials/task_list.html", tasks=tasks)

        return task_list()

    @app.route("/show_add_task", methods=["GET"])
    def show_add_task() -> str:
        return render_template("partials/task_popup.html", show_popup=True)

    @app.route("/add_task", methods=["POST"])
    def add_task() -> Response:
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

    @app.route("/close_add_task", methods=["GET"])
    def close_add_task() -> str:
        return render_template("partials/task_popup.html", show_popup=False)

    @app.route("/delete-task/<task_id>", methods=["DELETE"])
    def delete_task(task_id: str) -> Response:
        task_uid = UUID(task_id)
        delete_where(g.db_session, TaskTable, match_col={"id": task_uid})

        response = make_response("", 204)
        response.headers["HX-Trigger"] = "newTask"

        return response

    @app.route("/show_edit_task/<task_id>", methods=["GET"])
    def show_edit_task(task_id: str) -> str:
        """Fetch the specific task and open the popup in 'Edit' mode."""
        task_uid = UUID(task_id)

        # Fetch the existing task to pre-fill the form
        tasks = fetch_where(
            session=g.db_session, table=TaskTable, filter_map={"id": [task_uid]}
        )

        if not tasks:
            # Handle edge case where task isn't found
            return "", 404

        # Render the same popup, but pass the 'task' object
        return render_template(
            "partials/task_popup.html", show_popup=True, task=tasks[0]
        )

    @app.route("/edit_task/<task_id>", methods=["POST"])
    def edit_task(task_id: str) -> Response:
        """Process the update and close the popup."""
        task_uid = UUID(task_id)

        # Prepare the update data
        updates = {
            "name": request.form.get("name"),
            "description": request.form.get("description"),
        }

        # Perform the update
        update_where(
            session=g.db_session,
            table=TaskTable,
            match_cols={"id": task_uid},
            updates=updates,
        )

        # Close the popup
        response = make_response(
            render_template("partials/task_popup.html", show_popup=False)
        )

        # Trigger 'newTask' to reload the list via HTMX
        response.headers["HX-Trigger"] = "newTask"

        return response

    return app


def start_session_management(app: Flask, db: BaseDB) -> None:
    """Register hooks to create and teardown DB sessions per request.

    Adds `before_request` and `teardown_request` handlers that manage
    a scoped SQLAlchemy session on `flask.g`.
    """

    @app.before_request
    def before_request() -> None:
        """Create a new session before each request."""
        g.db_session = db.session()

    @app.teardown_request
    def teardown_request(exception) -> None:
        """Remove the session after the request is finished."""
        if exception:
            g.db_session.rollback()
        else:
            try:
                g.db_session.commit()
            except IntegrityError as ie:
                g.db_session.rollback()
                logger.error(f"IntegrityError occurred: {ie}")

        g.db_session.close()
