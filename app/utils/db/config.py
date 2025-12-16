"""Database configuration models and factory.

Defines Pydantic models for local and server DB configuration and a
factory to load those from YAML files.
"""

from abc import ABC, abstractmethod
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Literal, cast

import yaml
from pydantic import BaseModel, BeforeValidator, ValidationError

from app.utils.exceptions import DBConfigError


class DatabaseType(StrEnum):
    """Supported database types."""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


def _to_lower(v: object) -> object:
    """Ensure string values are lowercase."""
    return v.lower() if isinstance(v, str) else v


LowerCaseStr = Annotated[str, BeforeValidator(_to_lower)]


class BaseDBConfig(BaseModel, ABC):
    """Base model for DB configuration with auto-type coercion."""

    type: DatabaseType
    host: str
    name: LowerCaseStr
    echo: bool = False

    @property
    @abstractmethod
    def url(self) -> str:
        """Generate the SQLAlchemy-compatible connection URL."""


class LocalDBConfig(BaseDBConfig):
    """Configuration for local SQLite databases."""

    type: Literal[DatabaseType.SQLITE]

    @property
    def url(self) -> str:
        """Construct the SQLite connection string using host path and name."""
        path = Path(self.host) / self.name
        return f"sqlite:///{path.as_posix()}"


class ServerDBConfig(BaseDBConfig):
    """Configuration for server-based databases (MySQL/Postgres)."""

    type: Literal[DatabaseType.MYSQL, DatabaseType.POSTGRESQL]
    user: str
    pw: str
    port: int
    driver: LowerCaseStr
    dialect: LowerCaseStr

    @property
    def url(self) -> str:
        """Construct the server connection string with auth and network details."""
        return (
            f"{self.dialect}+{self.driver}://"
            f"{self.user}:{self.pw}@{self.host}:{self.port}/{self.name}"
        )


class DBConfigFactory:
    """Factory to load and validate DB configurations from files."""

    def from_filepath(self, filepath: Path) -> BaseDBConfig:
        """Load YAML config and return a validated config object."""
        if not filepath.exists():
            msg = f"Config file not found: {filepath}"
            raise DBConfigError(msg)

        try:
            with filepath.open("r") as f:
                raw_data = yaml.safe_load(f)
                data = (
                    cast(dict[str, object], raw_data)
                    if isinstance(raw_data, dict)
                    else {}
                )

        except yaml.YAMLError as e:
            msg = f"Invalid YAML in {filepath}"
            raise DBConfigError(msg) from e

        db_type = data.get("type")

        try:
            if db_type == DatabaseType.SQLITE:
                return LocalDBConfig.model_validate(data)
            return ServerDBConfig.model_validate(data)

        except ValidationError as e:
            msg = f"Configuration Error: {e}"
            raise DBConfigError(msg) from e
