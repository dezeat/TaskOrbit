"""Here all the Init stuff happens."""

import inspect as insp
import logging

from pydantic.dataclasses import dataclass
from sqlalchemy import Engine, MetaData, create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql.schema import Table

from app import models
from app.db_utils.config import DatabaseType


@dataclass
class SetUp:
    config: T

    @property
    def url(self) -> str:
        """..."""
        return self.config.url

    @property
    def engine(self) -> Engine:
        """..."""
        return create_engine(self.url, echo=True)

    @property
    def session(self) -> Session:
        """..."""
        return Session(self.engine)

    @property
    def tables(self) -> dict[str, Table]:
        """..."""
        classes = insp.getmembers(models, insp.isclass)
        return {
            class_name: classtable
            for class_name, classtable in classes
            if "Table" in class_name
        }

    def _is_reachable(self) -> bool:
        """Check if the database is reachable."""
        try:
            with self.engine.connect() as connection:
                connection.execute("SELECT 1")
            return True

        except SQLAlchemyError as e:
            msg = f"Database connection failed: {e}"
            logging.info(msg)
            return False

    def _is_table_exist(self, table_name: str) -> bool:
        """..."""
        inspector = inspect(self.engine)
        return inspector.has_table(table_name)

    def _create_table(self, table: Table) -> None:
        """..."""
        metadata = MetaData()
        metadata.create_all(self.engine, tables=[table])

    def _create_tables_if_not_exist(self) -> None:
        """ ..."""
        for table_name, table in self.tables.items():
            if not self._is_table_exist(table_name):
                self._create_table(table)

    def _setup_db(self) -> None:
        """..."""
        models.BaseTable.metadata.create_all(self.engine)

    def set_up_db(self) -> None:
        """..."""
        # if db not there and not sqllite
        if not self._is_reachable():
            if self.config.type == DatabaseType.SQLLITE:
                self._setup_db()
            else:
                msg = "Database is not reachable"
                raise ConnectionError(msg)

        elif not self._do_tables_exist():
            self._setup_db()
