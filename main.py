"""..."""

import sys
from pathlib import Path

from app import app
from app.utils.db.config import DBConfigFactory
from app.utils.db.database import db_factory


def main(filepath: Path) -> None:
    """Entry-point of TaskOrbit app."""
    # DB Initialization
    db_config = DBConfigFactory().from_filepath(filepath)

    db = db_factory(db_config)

    flask_server = app.create_app(db)
    flask_server.run()


if __name__ == "__main__":
    """..."""
    default_db_path = "app/utils/db/default_db_config.yaml"

    db_config_path = default_db_path if len(sys.argv) < 2 else sys.argv[1]  # noqa: PLR2004

    main(Path(db_config_path))
