"""App configuration module."""

from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import cast

from pydantic import MySQLDsn, PostgresDsn, computed_field
from pydantic_settings import (  # type: ignore  # noqa: PGH003
    BaseSettings,
    SettingsConfigDict,
)


class DatabaseType(StrEnum):
    """Supported database backend types."""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


class AppConfig(BaseSettings):
    """Application configuration schema.

    Automatically loads values from environment variables or a `.env` file.
    """

    # Read values from the project's `.env` file by default
    # Allow/ignore extra env vars (like POSTGRES_*) so local docker envs
    # won't cause validation errors when they are present in the environment.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    FLASK_HOST: str = "127.0.0.1"
    FLASK_PORT: int = 5000
    FLASK_DEBUG: bool = True
    FLASK_SECRET: str = "dev-secret-key"

    DB_TYPE: DatabaseType = DatabaseType.SQLITE
    DB_NAME: str = "taskorbit.db"

    # For SQLite: Acts as the directory path (e.g., "app" or ".").
    # For Server DBs: Acts as the network hostname (e.g., "localhost").
    DB_HOST: str = "."
    DB_PORT: int | None = None
    DB_USER: str | None = None
    DB_PASS: str | None = None
    DB_ECHO: bool = False

    # Schema/Prefix for table isolation
    # PostgreSQL: Schema name (e.g., "taskorbit")
    # SQLite: Table prefix (e.g., "taskorbit_")
    DB_SCHEMA: str = "taskorbit"

    @computed_field
    def sqlalchemy_database_uri(self) -> str:
        """Construct the SQLAlchemy connection string.

        Logic:
        - SQLite: Joins `DB_HOST` (dir) and `DB_NAME` (file) to create the path.
        - Server: Uses standard user:pass@host:port/db_name format.
        """
        if self.DB_TYPE == DatabaseType.SQLITE:
            # Use Path to correctly join the folder (host) and filename (name)
            db_path = Path(self.DB_HOST) / self.DB_NAME
            return f"sqlite:///{db_path.as_posix()}"

        if not self.DB_USER or not self.DB_PASS:
            msg = f"{self.DB_TYPE} requires DB_USER and DB_PASS."
            raise ValueError(msg)

        if self.DB_TYPE == DatabaseType.POSTGRESQL:
            # Add schema as query parameter for PostgreSQL
            base_uri = str(
                PostgresDsn.build(
                    scheme="postgresql+psycopg2",
                    username=self.DB_USER,
                    password=self.DB_PASS,
                    host=self.DB_HOST,
                    port=self.DB_PORT,
                    path=self.DB_NAME,
                )
            )
            # Append schema as query parameter if specified
            if self.DB_SCHEMA:
                return f"{base_uri}?options=-c%20search_path%3D{self.DB_SCHEMA}"
            return base_uri

        if self.DB_TYPE == DatabaseType.MYSQL:
            return str(
                MySQLDsn.build(
                    scheme="mysql+pymysql",
                    username=self.DB_USER,
                    password=self.DB_PASS,
                    host=self.DB_HOST,
                    port=self.DB_PORT,
                    path=self.DB_NAME,
                )
            )

        msg = f"Unsupported DB_TYPE: {self.DB_TYPE}"
        raise ValueError(msg)

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:  # noqa: N802
        """Alias for uppercase method for compatibility with Flask/SQLAlchemy."""
        return cast(str, self.sqlalchemy_database_uri)


@lru_cache
def get_config() -> AppConfig:
    """Return a cached singleton of AppConfig to avoid re-reading env vars."""
    return AppConfig()
