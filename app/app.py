"""..."""

from flask import Flask, g, render_template
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session, sessionmaker

from app.utils.db import crud, models
from app.utils.db.database import BaseDB
from app.utils.logger import logger


def create_app(db: BaseDB, template_folder: str = "templates") -> Flask:
    """..."""
    app = Flask(__name__, template_folder=template_folder)

    start_session_management(app, db)

    @app.route("/")
    def home() -> str:
        """..."""
        user = {"name": "admin", "hashed_password": "admin"}
        admin = models.User.from_dict(user)
        crud.insert(
            session=g.db_session, table=models.UserTable, data=[admin]
        )
        return render_template("index.html")

    return app


def start_session_management(app: Flask, db: BaseDB) -> None:
    """..."""
    session = scoped_session(sessionmaker(bind=db.engine()))

    @app.before_request
    def before_request() -> None:
        """Create a new session before each request."""
        g.db_session = session()

    @app.teardown_request
    def teardown_request(exception: Exception) -> None:
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
