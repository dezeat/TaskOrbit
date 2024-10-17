"""Here all the Init stuff happens."""

import inspect as insp
import logging

from pydantic.dataclasses import dataclass
from sqlalchemy import Engine, MetaData, create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.sql.schema import Table

from app.db_utils import models
from app.db_utils.config import BaseDBConfig

metadata = MetaData()

@dataclass
class DBSetUp:
    """..."""
    config: BaseDBConfig

    @property
    def url(self) -> str:
        """Returns the database connection URL from the config."""
        return self.config.url

    @property
    def engine(self) -> Engine:
        """Creates and returns a SQLAlchemy Engine instance."""
        return create_engine(self.url, echo=True)

    @property
    def session(self) -> Session:
        """Creates and returns a SQLAlchemy Session instance."""
        return Session(self.engine)
    
    @property
    def tables(self) -> dict[str, Table]:
        """Returns a dict of table names and SQLAlchemy Table instances."""
        classes = insp.getmembers(models, insp.isclass)
        return {
            class_name: classtable
            for class_name, classtable in classes
            if "Table" in class_name
        }


    def _is_reachable(self) -> bool:
        """Checks if the database is reachable by executing a simple query."""
        try:
            self.engine.connect().execute(text("SELECT 1"))
            return True  # noqa: TRY300

        except SQLAlchemyError as e:
            msg = f"Database connection failed: {e}"
            logging.info(msg)
            return False

    def _is_table_exist(self, table_name: str) -> bool:
        """Checks if a table with the given name exists in the database."""
        inspector = inspect(self.engine)
        return inspector.has_table(table_name)

    def _create_table(self, table: Table) -> None:
        """Creates a table in the database using the given SQLAlchemy Table instance."""
        metadata.create_all(self.engine, tables=[table])

    def _create_tables_if_not_exist(self) -> None:
        """Creates tables in the database if they do not already exist."""
        for table_name, table in self.tables.items():
            if not self._is_table_exist(table_name):
                self._create_table(table)

    def _setup_db(self) -> None:
        """Sets up the database by creating all tables defined in models.BaseTable."""
        models.BaseTable.metadata.create_all(self.engine)

    def run(self) -> None:
        """Sets up database by checking reachability and creating tables if needed."""
        # if not self._is_reachable():
        #     if self.config.type == DatabaseType.SQLLITE:
        #         self._setup_db()
        #     else:
        #         msg = "Database is not reachable"
        #         raise ConnectionError(msg)
        # else:
        # self._create_tables_if_not_exist()
        self._setup_db()
