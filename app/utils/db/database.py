"""Here all the Init stuff happens."""

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
    """..."""

    config: BaseDBConfig
    _valid_db_type: ClassVar[DatabaseType]
    _engine: ClassVar[Engine | None] = None
    _tables: ClassVar[dict[str, models.BaseTable] | None] = None
    _metadata: ClassVar[MetaData | None] = None

    @classmethod
    def engine(cls) -> Engine:
        """..."""
        if cls._engine is None:
            cls._engine = create_engine(cls.config.url, echo=True)
        return cls._engine

    @classmethod
    def tables(cls) -> dict[str, models.BaseTable]:
        """..."""
        if cls._tables is None:
            classes = insp.getmembers(models, insp.isclass)
            cls._tables = {
                class_object.__tablename__: class_object
                for class_name, class_object in classes
                if "Table" in class_name and "Base" not in class_name
            }
        return cls._tables

    @classmethod
    def metadata(cls) -> MetaData:
        """..."""
        if cls._metadata is None:
            cls._metadata = MetaData()
        return cls._metadata

    @classmethod
    def session(cls) -> scoped_session[Session]:
        """..."""
        return scoped_session(sessionmaker(bind=cls.engine()))

    @classmethod
    def _table_exist(cls, table_name: str) -> bool:
        """..."""
        inspector = inspect(cls.engine())
        return inspector.has_table(table_name)

    @classmethod
    def _create_table(cls, table_object: models.BaseTable) -> None:
        """..."""
        table_object.__table__.create(cls.engine())  # type: ignore  # noqa: PGH003

    @classmethod
    def _create_tables_if_not_exist(cls) -> None:
        """..."""
        for table_name, table_object in cls.tables().items():
            if not cls._table_exist(table_name):
                logger.info(f"Table: {table_name} not found in {cls.config.name}")
                cls._create_table(table_object)
                logger.info(f"Table: {table_name} created in {cls.config.name}")
            else:
                logger.info(f"Table: {table_name} already present in {cls.config.name}")

    @classmethod
    def _create_all_tables(cls) -> None:
        """..."""
        cls.metadata().create_all(cls.engine())
        logger.info(f"All specified tables created in {cls.config.name}")

    @classmethod
    def setup(cls, config: BaseDBConfigType) -> type["BaseDB"]:
        """Template method for setting up the database."""
        cls.config = config
        cls._check_conn()
        cls._create_tables_if_not_exist()
        return cls

    @classmethod
    @abstractmethod
    def _check_conn(cls) -> bool:
        """..."""


class SQLiteDB(BaseDB[LocalDBConfig]):
    """..."""

    config: LocalDBConfig
    _valid_db_type: ClassVar[DatabaseType] = DatabaseType.SQLLITE

    @classmethod
    def _check_conn(cls) -> bool:
        """Checks if the SQLite database file exists."""
        _exists = Path(cls.config.url).is_file()

        if not _exists:
            cls.engine()
            msg = f"SQLlite db-file not found in {cls.config.url}. Created new."
            logger.info(msg)

        return _exists


class PostgresDB(BaseDB[ServerDBConfig]):
    """..."""

    config: ServerDBConfig
    _valid_db_type: ClassVar[DatabaseType] = DatabaseType.POSTGRESQL

    @classmethod
    def _check_conn(cls) -> bool:
        """Checks if the database is reachable by executing a simple query."""
        try:
            cls.engine().connect().execute(text("SELECT 1"))
            return True  # noqa: TRY300

        except SQLAlchemyError as e:
            msg = f"Database connection failed: {e}"
            raise DBSetupError(msg) from e


def db_factory(config: BaseDBConfig) -> type[BaseDB]:
    """..."""
    if isinstance(config, LocalDBConfig):
        return SQLiteDB.setup(config)

    if isinstance(config, ServerDBConfig):
        if config.type == DatabaseType.POSTGRESQL:
            return PostgresDB.setup(config)

        if config.type == DatabaseType.MYSQL:
            pass

    config_types = [cls.__name__ for cls in BaseDBConfig.__subclasses__()]
    msg = "DBConfig needs to be of type " f"{" ,".join(config_types)}"
    raise DBSetupError(msg)
