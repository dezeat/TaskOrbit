"""Database engine and table setup helpers.

Provides `BaseDB` and concrete backends that manage engines, sessions and
table creation for the application.
"""

from __future__ import annotations

import inspect as insp
from abc import abstractmethod
from pathlib import Path
from typing import ClassVar, Generic, TypeVar

from pydantic.dataclasses import dataclass
from sqlalchemy import Engine, MetaData, create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from app.utils.db import models
from app.utils.db.config import (
    BaseDBConfig,
    DatabaseType,
    LocalDBConfig,
    ServerDBConfig,
)
from app.utils.exceptions import DBSetupError
from app.utils.logger import logger

BaseDBConfigType = TypeVar("BaseDBConfigType", bound=BaseDBConfig)


@dataclass
class BaseDB(Generic[BaseDBConfigType]):
    """Abstract base for database wrappers providing setup helpers."""

    config: BaseDBConfig
    _valid_db_type: ClassVar[DatabaseType]
    _engine: ClassVar[Engine | None] = None
    _tables: ClassVar[dict[str, type[models.BaseTable]] | None] = None
    _metadata: ClassVar[MetaData | None] = None

    @classmethod
    def engine(cls) -> Engine:
        """Return the SQLAlchemy engine for this DB, creating it if needed."""
        if cls._engine is None:
            # --- FIX: Use the echo setting from config ---
            cls._engine = create_engine(cls.config.url, echo=cls.config.echo)
        return cls._engine

    @classmethod
    def tables(cls) -> dict[str, type[models.BaseTable]]:
        """Discover and return a mapping of table name to ORM table class."""
        if cls._tables is None:
            classes = insp.getmembers(models, insp.isclass)
            tbls: dict[str, type[models.BaseTable]] = {}
            for class_name, class_object in classes:
                if "Table" in class_name and "Base" not in class_name and isinstance(
                    class_object, type
                ):
                    tbls[class_object.__tablename__] = class_object  # type: ignore[attr-defined]
            cls._tables = tbls
        return cls._tables

    @classmethod
    def metadata(cls) -> MetaData:
        """Return a MetaData object used for creating tables when needed."""
        if cls._metadata is None:
            cls._metadata = MetaData()
        return cls._metadata

    @classmethod
    def session(cls) -> scoped_session[Session]:
        """Return a scoped SQLAlchemy session factory bound to the engine."""
        return scoped_session(sessionmaker(bind=cls.engine()))

    @classmethod
    def _table_exist(cls, table_name: str) -> bool:
        """Return True if the named table exists in the configured DB."""
        inspector = inspect(cls.engine())
        return inspector.has_table(table_name)

    @classmethod
    def _create_table(cls, table_object: type[models.BaseTable]) -> None:
        """Create a single table object on the configured engine."""
        table_object.__table__.create(cls.engine())  # type: ignore  # noqa: PGH003

    @classmethod
    def _create_tables_if_not_exist(cls) -> None:
        """Create all declared tables that are missing from the database."""
        for table_name, table_object in cls.tables().items():
            if not cls._table_exist(table_name):
                logger.info(f"Table: {table_name} not found in {cls.config.name}")
                cls._create_table(table_object)
                logger.info(f"Table: {table_name} created in {cls.config.name}")
            else:
                logger.info(f"Table: {table_name} already present in {cls.config.name}")

    @classmethod
    def _create_all_tables(cls) -> None:
        """Create all tables using SQLAlchemy metadata for the engine."""
        cls.metadata().create_all(cls.engine())
        logger.info(f"All specified tables created in {cls.config.name}")

    @classmethod
    def setup(cls, config: BaseDBConfigType) -> type[BaseDB]:
        """Template method for setting up the database."""
        cls.config = config
        cls._check_conn()
        cls._create_tables_if_not_exist()
        return cls

    @classmethod
    @abstractmethod
    def _check_conn(cls) -> bool:
        """Verify that the database is reachable and return connection state."""


class SQLiteDB(BaseDB[LocalDBConfig]):
    """SQLite backend implementation for local file databases."""

    config: LocalDBConfig
    _valid_db_type: ClassVar[DatabaseType] = DatabaseType.SQLITE

    @classmethod
    def _check_conn(cls) -> bool:
        """Checks if the SQLite database file exists."""
        # --- FIX: Clean path string for correct file checking ---
        db_path_str = cls.config.url.replace("sqlite:///", "")

        # Handle absolute paths edge case (sqlite:////)
        if cls.config.url.startswith("sqlite:////"):
            db_path_str = cls.config.url.replace("sqlite:////", "/")

        _exists = Path(db_path_str).is_file()

        if not _exists:
            cls.engine().connect()  # Triggers file creation
            msg = f"Sqlite db-file not found at {db_path_str}. Created new."
            logger.info(msg)

        return _exists


class PostgresDB(BaseDB[ServerDBConfig]):
    """Postgres backend implementation that verifies connectivity."""

    config: ServerDBConfig
    _valid_db_type: ClassVar[DatabaseType] = DatabaseType.POSTGRESQL

    @classmethod
    def _check_conn(cls) -> bool:
        """Checks if the database is reachable by executing a simple query."""
        try:
            cls.engine().connect().execute(text("SELECT 1"))
        except SQLAlchemyError as e:
            msg = f"Database connection failed: {e}"
            raise DBSetupError(msg) from e
        else:
            return True


def db_factory(config: BaseDBConfig) -> type[BaseDB]:
    """Return a configured `BaseDB` subclass for the given config."""
    if isinstance(config, LocalDBConfig):
        return SQLiteDB.setup(config)

    if isinstance(config, ServerDBConfig):
        if config.type == DatabaseType.POSTGRESQL:
            return PostgresDB.setup(config)

        if config.type == DatabaseType.MYSQL:
            pass

    config_types = [cls.__name__ for cls in BaseDBConfig.__subclasses__()]
    msg = "DBConfig needs to be of type " + ", ".join(config_types)
    raise DBSetupError(msg)
