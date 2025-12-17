"""Database seeding utility.

This module populates the database with initial dataset requirements.
It initializes its own database connection to avoid circular import issues
with the main application.

Usage:
    Run as a module from the project root:
    $ python -m development.seed
"""

import sys
from uuid import UUID

from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.utils.logger import logger
from app.utils.models import BaseTable, TaskTable, UserTable
from app.utils.security import hash_password

DB_URL = "sqlite:///taskorbit.db"


def get_db_session() -> Session:
    """Create a standalone database session for seeding."""
    engine = create_engine(DB_URL)

    # Ensure tables exist
    BaseTable.metadata.create_all(engine)

    # Create a session factory
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return session_local()


def seed_users(session: Session) -> UUID:
    """Ensure the default admin user exists."""
    admin_name = "admin"
    logger.info(f"Checking for user: '{admin_name}'...")

    existing_admin = session.scalar(
        select(UserTable).where(UserTable.name == admin_name)
    )

    if existing_admin:
        logger.info(f"User '{admin_name}' already exists.")
        return existing_admin.id

    hashed_pw = hash_password("admin")
    new_admin = UserTable(name=admin_name, hashed_password=hashed_pw)

    session.add(new_admin)
    session.flush()

    logger.info(f"Created new user: '{admin_name}'")
    return new_admin.id


def seed_tasks(session: Session, user_id: UUID) -> None:
    """Populate sample tasks."""
    tasks_data = [
        {
            "name": "Refactor Database",
            "description": "Switch to Extension Pattern in Flask",
        },
        {
            "name": "Update Seed Script",
            "description": "Remove YAML config dependency",
        },
    ]

    count = 0
    for task in tasks_data:
        exists = session.scalar(
            select(TaskTable).where(
                TaskTable.user_id == user_id,
                TaskTable.name == task["name"],
            )
        )

        if not exists:
            new_task = TaskTable(
                user_id=user_id,
                name=task["name"],
                description=task["description"],
            )
            session.add(new_task)
            count += 1

    if count > 0:
        logger.info(f"Seeded {count} new tasks.")
    else:
        logger.info("No new tasks required seeding.")


def run_seed() -> None:
    """Orchestrate the seeding process."""
    logger.info("🌱 Starting database seeding (Standalone Mode)...")

    session = get_db_session()

    try:
        user_id = seed_users(session)
        seed_tasks(session, user_id)

        session.commit()
        logger.info("✅ Database seeding completed successfully.")

    except IntegrityError as ie:
        session.rollback()
        logger.error(f"Integrity Error: {ie}")
        sys.exit(1)
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database Error: {e}")
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    run_seed()
