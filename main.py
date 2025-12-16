"""Entrypoint for the TaskOrbit application.

Responsible for initializing the database connection and starting the Flask server.
"""

import os
import sys
from pathlib import Path

from app import app
from app.utils.db.config import DBConfigFactory, LocalDBConfig, ServerDBConfig
from app.utils.db.database import PostgresDB, SQLiteDB
from app.utils.logger import logger


def main(config_path: Path) -> None:
    """Initialize resources and run the Flask app."""
    # 1. Load Configuration (file preferred, fall back to environment)
    try:
        db_config = DBConfigFactory().from_filepath(config_path)
    except Exception as e:
        logger.warning(
            "Config file missing or invalid, attempting env-based config: %s", e
        )
        try:
            db_config = DBConfigFactory()._resolve_from_env()
            if db_config is None:
                raise RuntimeError("No DB configuration available from env")
        except Exception as exc:
            logger.error("Failed to resolve DB configuration: %s", exc)
            sys.exit(1)

    # 2. Setup Database Connection (create engine and tables)
    if isinstance(db_config, LocalDBConfig):
        db = SQLiteDB.setup(db_config)
    elif isinstance(db_config, ServerDBConfig):
        if db_config.type == db_config.type.POSTGRESQL:
            db = PostgresDB.setup(db_config)
        else:
            raise RuntimeError("Unsupported server DB type for startup")

    logger.info(f"Database engine initialized for: {db_config.name}")

    # 3. Create Flask Application
    flask_server = app.create_app(db)

    # Ideally, load this from env vars
    flask_server.config["SECRET_KEY"] = os.getenv("FLASK_SECRET", "dev_secret_key")

    # 4. Configuration for Server Run
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5000"))

    # Robust debug check
    debug_mode = os.getenv("FLASK_DEBUG", "1").lower() in ("1", "true", "yes", "on")

    logger.info(f"Starting server on {host}:{port} (Debug: {debug_mode})")

    flask_server.run(host=host, port=port, debug=debug_mode)


if __name__ == "__main__":
    # Default config path
    default_path = "app/utils/db/default_db_config.yaml"

    # Check command line args
    arg_path = sys.argv[1] if len(sys.argv) > 1 else default_path

    main(Path(arg_path))
