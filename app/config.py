"""App configuration module."""

from enum import StrEnum
from functools import lru_cache
from pathlib import Path

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

    # This configuration disables .env file reading
    model_config = SettingsConfigDict(env_file=None)

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

    @property
    @computed_field
    def SQLALCHEMY_DATABASE_URI(self) -> str:  # noqa: N802
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
            return str(
                PostgresDsn.build(
                    scheme="postgresql+psycopg2",
                    username=self.DB_USER,
                    password=self.DB_PASS,
                    host=self.DB_HOST,
                    port=self.DB_PORT,
                    path=self.DB_NAME,
                )
            )

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


@lru_cache
def get_config() -> AppConfig:
    """Return a cached singleton of AppConfig to avoid re-reading env vars."""
    return AppConfig()
