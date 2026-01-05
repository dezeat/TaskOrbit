"""Flask application factory and database configuration.

This module implements the Application Factory pattern for Flask, initializing
the WSGI application and wiring it to the SQLAlchemy database layer. It uses
the "Extension Pattern" for database objects, defining the engine and session
factory globally to allow for safe imports across the application (avoiding
circular dependencies), while binding them to the specific application instance
during creation.
"""

from __future__ import annotations

from flask import Flask, g
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker

from app.config import get_config
from app.models import BaseTable
from app.routes import bp as main_bp
from app.utils.logger import logger

app_config = get_config()

# Define the database engine globally to allow models and routes to import it
# without circular dependency issues.
engine = create_engine(
    url=app_config.SQLALCHEMY_DATABASE_URI,
    echo=app_config.DB_ECHO,
    pool_pre_ping=True,
)

# Create a thread-safe session factory.
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


def create_app(template_folder: str = "templates") -> Flask:
    """Create and configure the Flask application instance.

    This factory function initializes the Flask app, loads configuration from
    the environment-aware settings module, and registers blueprints and database
    hooks. Using a factory allows for creating multiple independent app instances,
    which is essential for unit testing.

    Args:
        template_folder: Path to the templates directory (defaults to "templates").

    Returns:
        A fully configured Flask application instance ready to serve requests.
    """
    app = Flask(__name__, template_folder=template_folder)

    app.config["SECRET_KEY"] = app_config.FLASK_SECRET
    app.config["SQLALCHEMY_DATABASE_URI"] = app_config.SQLALCHEMY_DATABASE_URI

    _init_db(app)

    app.register_blueprint(main_bp)

    return app


def _init_db(app: Flask) -> None:
    """Register database lifecycle hooks and ensure schema existence.

    This helper performs two critical functions:
    1.  **Schema Initialization:** It attempts to connect to the database and
        create tables defined in `BaseTable` if they do not exist. This serves
        as a basic migration strategy for development.
    2.  **Session Lifecycle:** It attaches hooks to the Flask request lifecycle
        to ensure database sessions are cleanly opened and closed.

    Raises:
        Exception: If the database connection check fails, preventing the
        application from starting in a broken state.
    """
    with app.app_context():
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            BaseTable.metadata.create_all(bind=engine)

        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    @app.before_request
    def add_session_to_g() -> None:
        """Alias the scoped session to `g.db_session` for request access.

        While `db_session` is globally importable, aliasing it to `flask.g`
        allows consistent access patterns across the application and maintains
        compatibility with legacy code or extensions expecting `g.db_session`.
        """
        g.db_session = db_session

    @app.teardown_appcontext
    def shutdown_session(exception: BaseException | None) -> None:  # noqa: ARG001
        """Remove the database session at the end of the request or app context.

        This ensures that the connection is returned to the connection pool
        cleanly. Crucially, this function does *not* implicitly commit transactions.
        Commits must be explicit within route handlers to prevent unintended data
        persistence (e.g., during failed logic or read-only operations).
        """
        db_session.remove()
