"""Flask application factory and request session management.

Exports `create_app` which wires DB session lifecycle hooks and the
minimal HTTP routes used by the demo application.
"""

from flask import Flask, g
from sqlalchemy.exc import IntegrityError

from app.routes import bp as main_bp
from app.utils.db.database import BaseDB
from app.utils.logger import logger


def create_app(db: BaseDB, template_folder: str = "templates") -> Flask:
    """Create and configure the Flask application instance.

    Registers request lifecycle handlers that provide a scoped DB session
    via `flask.g` and defines the basic routes used by the UI.
    """
    app = Flask(__name__, template_folder=template_folder)

    _start_session_management(app, db)



    app.register_blueprint(main_bp)

    return app


def _start_session_management(app: Flask, db: BaseDB) -> None:
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
