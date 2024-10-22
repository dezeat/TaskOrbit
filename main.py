"""..."""

import sys
from pathlib import Path

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, scoped_session

from app import app
from app.utils.db.config import DBConfigFactory
from app.utils.db.crud import insert, select_
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
            "description": "To solidfiy knowledge, write basic webapp.",
        },
        {
            "user_id": uid_admin,
            "name": "Develop Frontend",
            "description": "You do it for the BE, but you need to know basics of FE.",
        },
    ]


    # Insert Task Data
    tasks = [Task.from_dict(task) for task in task_data]
    insert(session=session, table=TaskTable, data=tasks)
    db_session_handler(session)

def db_session_handler(session: scoped_session[Session] ) -> None:
    """..."""
    try:
        session.commit()
    except IntegrityError as ie:
        session.rollback()
        logger.error(f"IntegrityError occurred: {ie}")


def main(filepath: Path) -> None:
    """Entry-point of TaskOrbit app."""
    # DB Initialization
    db_config = DBConfigFactory().from_filepath(filepath)
    db = db_factory(db_config)
    populate_db(db)

    flask_server = app.create_app(db)
    flask_server.config["SECRET_KEY"] = "your_secret_key"
    
    flask_server.run()


if __name__ == "__main__":
    """..."""
    default_db_path = "app/utils/db/default_db_config.yaml"
    db_config_path = default_db_path if len(sys.argv) < 2 else sys.argv[1]  # noqa: PLR2004

    main(Path(db_config_path))
