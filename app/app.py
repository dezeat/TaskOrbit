"""..."""

from flask import Flask, Response, g, make_response, render_template, request, session
from sqlalchemy.exc import IntegrityError

from app.utils.db.crud import filter_tasks, insert, select_
from app.utils.db.database import BaseDB
from app.utils.db.models import Task, TaskTable, UserTable
from app.utils.logger import logger


def create_app(db: BaseDB, template_folder: str = "templates") -> Flask:
    """..."""
    app = Flask(__name__, template_folder=template_folder)

    start_session_management(app, db)

    @app.route("/", methods=["GET"])
    def home() -> str:
        """..."""
        # Placeholder for user login and auth
        result = select_(
            session=g.db_session, table=UserTable, filter_map={"name": ["admin"]}
        )
        session["uid"] = result[0].id

        # Load all Tasks of the User
        tasks = select_(
            session=g.db_session,
            table=TaskTable,
            filter_map={"user_id": [session["uid"]]},
        )

        return render_template("index.html", tasks=tasks)

    @app.route("/task_list", methods=["GET"])
    def task_list() -> str:
        tasks = select_(
            session=g.db_session,
            table=TaskTable,
            filter_map={"user_id": [session["uid"]]},
        )

        return render_template("/partials/task_list.html", tasks=tasks)

    @app.route("/search_tasks", methods=["GET"])
    def search_tasks() -> str:
        search_string = request.args.get("search")
        if search_string:
            tasks = filter_tasks(
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

        insert(session=g.db_session, table=TaskTable, data=[task])

        response = make_response(
            render_template("partials/task_popup.html", show_popup=False)
        )
        response.headers["HX-Trigger"] = "newTask"

        return response

    @app.route("/close_add_task", methods=["GET"])
    def close_add_task() -> str:
        return render_template("partials/task_popup.html", show_popup=False)

    return app


def start_session_management(app: Flask, db: BaseDB) -> None:
    """..."""

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
