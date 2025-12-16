"""Database seeding utility.

This script populates the database with initial data (admin user, sample tasks).
Run this independently of the main application server.
"""

import hashlib
import sys
from pathlib import Path
from typing import cast

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, scoped_session

# Adjust imports to ensure they work when run as a module
from app.utils.db.config import DBConfigFactory
from app.utils.db.crud import bulk_insert, fetch_where
from app.utils.db.database import BaseDB, db_factory
from app.utils.db.models import Task, TaskTable, User, UserTable
from app.utils.logger import logger


def db_session_handler(session: scoped_session[Session]) -> None:
    """Commit the session or rollback on integrity errors."""
    try:
        session.commit()
        logger.info("Data committed successfully.")
    except IntegrityError as ie:
        session.rollback()
        logger.warning(f"IntegrityError (entry likely exists): {ie}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database error: {e}")


def populate_db(db: type[BaseDB]) -> None:
    """Populate the database with an admin user and sample tasks."""
    logger.info("Starting database seeding...")
    session = db.session()

    # 1. Add Admin User
    # Passwords are stored as client-side SHA-256 hex digests.
    # Hash the default admin password so login (which expects a hashed value)
    # will work when the client sends the SHA-256 of 'admin'.
    admin_plain = "admin"
    admin_hashed = hashlib.sha256(admin_plain.encode("utf-8")).hexdigest()
    user_data = {"name": "admin", "hashed_password": admin_hashed}
    user = User.from_dict(user_data)

    # Check if user exists first to reduce log noise (optional but clean)
    existing_admin = fetch_where(session, UserTable, {"name": ["admin"]})
    if not existing_admin:
        bulk_insert(session=session, table=UserTable, data=[user])
        db_session_handler(session)
    else:
        logger.info("User 'admin' already exists.")

    # 2. Fetch Admin ID for relations
    # We fetch again to ensure we have the persistent ID
    admin_result = fetch_where(
        session=session, table=UserTable, filter_map={"name": ["admin"]}
    )

    if not admin_result:
        logger.error("Failed to retrieve admin user after creation.")
        return

    uid_admin = cast("User", admin_result[0]).id

    # 3. Create Task Data
    task_data = [
        {
            "user_id": uid_admin,
            "name": "Develop WebApp",
            "description": "Setup basic Flask structure",
        },
        {
            "user_id": uid_admin,
            "name": "Develop Frontend",
            "description": "React or Jinja templates?",
        },
    ]

    tasks = [Task.from_dict(task) for task in task_data]
    bulk_insert(session=session, table=TaskTable, data=tasks)
    db_session_handler(session)

    session.close()
    logger.info("Database seeding completed.")


def run_seed(config_path: str) -> None:
    """Entry point for the seeder."""
    filepath = Path(config_path)
    if not filepath.exists():
        logger.error(f"Config file not found: {filepath}")
        sys.exit(1)

    # Initialize DB connection
    db_config = DBConfigFactory().from_filepath(filepath)
    db = db_factory(db_config)

    populate_db(db)


if __name__ == "__main__":
    # Allow running as a script: python -m app.utils.db.seed <config_path>
    default_db_path = "app/utils/db/default_db_config.yaml"
    path_arg = sys.argv[1] if len(sys.argv) > 1 else default_db_path

    run_seed(path_arg)
