"""..."""

import os
import sys
from pathlib import Path

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, scoped_session

from app import app
from app.utils.db.config import DBConfigFactory
from app.utils.db.crud import insert, select_, select_all
from app.utils.db.database import BaseDB, db_factory
from app.utils.db.models import BaseModel, Task, TaskTable, User, UserTable
from app.utils.logger import logger


def populate_db(db: BaseDB) -> None:
    """..."""
    session = db.session()

    # Add User
    user_data = {"name": "admin", "hashed_password": "admin"}
    user = User.from_dict(user_data)
    insert(session=session, table=UserTable, data=[user])
    db_session_handler(session)

    # Create Task-Data
    admin_result = select_(
        session=session, table=UserTable, filter_map={"name": ["admin"]}
    )
    db_session_handler(session)

    uid_admin = admin_result[0].id

    task_data = [
        {
            "user_id": uid_admin,
            "name": "Develop WebApp",
            "description": "Or is this my max character len",
        },
        {
            "user_id": uid_admin,
            "name": "Develop Frontend",
            "description": "Is this my max character len",
        },
    ]

    # Insert Task Data
    tasks = [Task.from_dict(task) for task in task_data]
    insert(session=session, table=TaskTable, data=tasks)
    db_session_handler(session)


def db_session_handler(session: scoped_session[Session]) -> None:
    """..."""
    try:
        session.commit()
    except IntegrityError as ie:
        session.rollback()
        logger.error(f"IntegrityError occurred: {ie}")


def main(filepath: Path, init_only: bool = False) -> None:
    """Entry-point of TaskOrbit app.

    If `init_only` is True, only initialize/seed the database and exit.
    """
    # DB Initialization
    db_config = DBConfigFactory().from_filepath(filepath)
    db = db_factory(db_config)

    if init_only:
        populate_db(db)
        return

    # Seed DB only if empty (prevents duplicate-seed errors on restart)
    session = db.session()
    try:
        existing_users = select_all(session=session, table=UserTable)
    finally:
        session.close()

    if not existing_users:
        populate_db(db)

    flask_server = app.create_app(db)
    flask_server.config["SECRET_KEY"] = "your_secret_key"

    # Read host/port/debug from environment for flexible dev runs
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug_env = os.getenv("FLASK_DEBUG", "1")
    debug = debug_env.lower() in ("1", "true", "yes", "on")

    flask_server.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    """..."""
    default_db_path = "app/utils/db/default_db_config.yaml"
    # Determine db config path and flags
    db_config_path = default_db_path if len(sys.argv) < 2 else sys.argv[1]  # noqa: PLR2004
    init_only = "--init-db" in sys.argv

    main(Path(db_config_path), init_only=init_only)
