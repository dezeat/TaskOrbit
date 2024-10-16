"""..."""

import sys
from pathlib import Path

from app import app
from app.databases.config import DBConfigFactory


def main(filepath: Path) -> None:
    """Entry-point of TaskOrbit app."""
    # DB Initialization
    db_config = DBConfigFactory().from_filepath(filepath)

    # Afterwards I Expect a db connection with two tables user, tasks
    db_session = start_up_db(db_config)

    flask_server = app.create_app(template_folder="templates", db = db_session)
    flask_server.run()


if __name__ == "__main__":
    """..."""
    db_config_path = "app/default_db_config.yaml" if len(sys.argv) < 2 else sys.argv[1]  # noqa: PLR2004

    main(Path(db_config_path))
