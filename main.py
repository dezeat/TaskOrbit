"""Entrypoint for the TaskOrbit application.

Responsible for initializing the database connection and starting the Flask server.
"""

import os
import sys
from pathlib import Path

from app import app
from app.utils.db.config import DBConfigFactory
from app.utils.db.database import db_factory
from app.utils.logger import logger


def main(config_path: Path) -> None:
    """Initialize resources and run the Flask app."""
    # 1. Load Configuration
    if not config_path.exists():
        logger.error(f"Configuration file not found at {config_path}")
        sys.exit(1)

    db_config = DBConfigFactory().from_filepath(config_path)

    # 2. Setup Database Connection
    # This creates the engine but does NOT seed data.
    db = db_factory(db_config)
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
