"""Database seeding utility.

This script populates the database with initial data (admin user, sample tasks).
Run this independently of the main application server.
"""

import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, scoped_session

# Adjust imports to ensure they work when run as a module
from app.utils.db.config import DBConfigFactory, LocalDBConfig, ServerDBConfig
from app.utils.db.database import BaseDB, PostgresDB, SQLiteDB
from app.utils.db.models import TaskTable, UserTable
from app.utils.logger import logger
from app.utils.security import hash_password


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
    # Hash admin password server-side using PBKDF2 and store algorithm+salt+hash
    admin_plain = "admin"
    admin_hashed = hash_password(admin_plain)
    user_data = {"name": "admin", "hashed_password": admin_hashed}

    # Check if user exists first
    existing_admin = session.scalars(
        select(UserTable).where(UserTable.name == "admin")
    ).all()
    if not existing_admin:
        # Insert new admin user directly using ORM
        session.add(UserTable(**user_data))
        db_session_handler(session)
    else:
        logger.info("User 'admin' already exists.")

    # 2. Fetch Admin ID for relations
    # We fetch again to ensure we have the persistent ID
    admin_result = session.scalars(
        select(UserTable).where(UserTable.name == "admin")
    ).all()
    if not admin_result:
        logger.error("Failed to retrieve admin user after creation.")
        return

    uid_admin = admin_result[0].id

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

    # Insert plain dicts for tasks directly
    for td in task_data:
        session.add(TaskTable(**td))
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
    if isinstance(db_config, LocalDBConfig):
        db = SQLiteDB.setup(db_config)
    elif isinstance(db_config, ServerDBConfig):
        if db_config.type == db_config.type.POSTGRESQL:
            db = PostgresDB.setup(db_config)
        else:
            msg = "Unsupported server DB type for seeding"
            raise RuntimeError(msg)

    populate_db(db)


if __name__ == "__main__":
    # Allow running as a script: python -m app.utils.db.seed <config_path>
    default_db_path = "app/utils/db/default_db_config.yaml"
    path_arg = sys.argv[1] if len(sys.argv) > 1 else default_db_path

    run_seed(path_arg)
