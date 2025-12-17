"""Entrypoint for the TaskOrbit application."""

from app.app import create_app
from app.config import get_config
from app.utils.logger import logger


def main() -> None:
    """Main entrypoint to start the Flask server."""
    app_config = get_config()
    flask_server = create_app()

    logger.info(
        f"Starting server on {app_config.FLASK_HOST}:{app_config.FLASK_PORT} "
        f"(Debug: {app_config.FLASK_DEBUG})"
    )

    flask_server.run(
        host=app_config.FLASK_HOST,
        port=app_config.FLASK_PORT,
        debug=app_config.FLASK_DEBUG,
    )


if __name__ == "__main__":
    main()
