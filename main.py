"""..."""

import sys
from pathlib import Path

from app import app
from app.db_utils.config import DBConfigFactory
from app.db_utils.database import db_factory


def main(filepath: Path) -> None:
    """Entry-point of TaskOrbit app."""
    # DB Initialization
    db_config = DBConfigFactory().from_filepath(filepath)

    db = db_factory(db_config)
    db_engine = db.engine()

    flask_server = app.create_app(template_folder="templates")
    flask_server.run()


if __name__ == "__main__":
    """..."""
    db_config_path = "app/default_db_config.yaml" if len(sys.argv) < 2 else sys.argv[1]  # noqa: PLR2004

    main(Path(db_config_path))
