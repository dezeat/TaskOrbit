"""..."""

from flask import Flask, g, render_template, request, session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session, sessionmaker

from app.utils.db import crud
from app.utils.db.database import BaseDB
from app.utils.db.models import Task, TaskTable, User, UserTable
from app.utils.logger import logger


def create_app(db: BaseDB, template_folder: str = "templates") -> Flask:
def create_app(db: BaseDB, template_folder: str = "templates") -> Flask:
    """..."""
    app = Flask(__name__, template_folder=template_folder)

    start_session_management(app, db)

    @app.route("/", methods=["GET", "POST"])
    def home() -> str:
        """..."""
        # Placeholder for user login and auth
        uid_admin = crud.select_(
            session=g.db_session, table=UserTable, where_in_map={"name": ["admin"]}
        )
        session["uid"] = uid_admin

        if request.method == "GET":
            # Load all Tasks of the User
            tasks = crud.select_(
                session=g.db_session, table=TaskTable, where_in_map={"user_id": [session["uid"]]}
            )
            
        return render_template("index.html")

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
