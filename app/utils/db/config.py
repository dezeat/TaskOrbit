"""Database configuration dataclasses and a factory for YAML configs.

Defines typed dataclasses for local and server DB configuration and a
factory to load those from YAML files.
"""

from abc import abstractmethod
from enum import StrEnum
from pathlib import Path
from typing import Any, ClassVar, cast

import yaml
from pydantic import field_validator, model_validator
from pydantic.dataclasses import dataclass

from app.utils.exceptions import DBConfigError


class DatabaseType(StrEnum):
    """Enum for different database types."""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


@dataclass
class BaseDBConfig:
    """Base class for database configuration.

    Attributes:
        type (str): The type of the database.
        host (str): The host/path.
        name (str): The name of the database.
        echo (bool): Whether to log SQL statements (SQLAlchemy Echo).
    """

    type: str
    host: str
    name: str
    echo: bool  # Added echo field
    possible_types: ClassVar[list[DatabaseType]]
    _required_fields: ClassVar[list[str]]

    @property
    def get_db_type(self) -> DatabaseType:
        """Get the DatabaseType instance from the string representation."""
        return next(db_type for db_type in DatabaseType if db_type.value == self.type)

    @classmethod
    def from_dict(cls, config_dict: dict[str, object]) -> "BaseDBConfig":
        """Create a database configuration instance from a dictionary."""
        coerced: dict[str, object] = {}

        # Coerce values according to dataclass annotations, ignoring ClassVars
        for name, ann in cls.__annotations__.items():
            # Skip class variables
            if name in ("possible_types", "_required_fields"):
                continue

            raw = config_dict.get(name)

            if ann is bool:
                if isinstance(raw, bool):
                    coerced[name] = raw
                elif isinstance(raw, str):
                    coerced[name] = raw.lower() in ("1", "true", "yes", "on")
                # If missing or wrong type, default to False
                else:
                    coerced[name] = False

            elif ann is int:
                if isinstance(raw, int):
                    coerced[name] = raw
                elif isinstance(raw, str) and raw.isdigit():
                    coerced[name] = int(raw)
                else:
                    coerced[name] = 0

            elif ann is str:
                coerced[name] = str(raw) if raw is not None else ""

        # Call the class as `Any` to avoid mypy constructor signature checks,
        # then cast back to `BaseDBConfig` for the declared return type.
        inst = cast(Any, cls)(**coerced)
        return cast(BaseDBConfig, inst)

    @classmethod
    @model_validator(mode="before")
    def _validate_required_fields(cls, db_config: dict[str, str]) -> dict[str, str]:
        """Validate that all required fields are present in the given configuration."""
        missing_fields = [
            field for field in cls._required_fields if field not in db_config
        ]
        if missing_fields:
            msg = f"These fields are missing in config: {', '.join(missing_fields)}"
            raise DBConfigError(msg)
        return db_config

    @classmethod
    def _validate_int_field(cls, v: str) -> str:
        """Validate that a given value is a valid integer."""
        if not v:
            msg = f"Integer field {v} cannot be empty."
            raise DBConfigError(msg)

        if not v.isdigit():
            msg = f"Integer field {v} contains non-digit chars."
            raise DBConfigError(msg)

        return v

    @classmethod
    def _validate_str_field(cls, v: str) -> str:
        """Validate that a given value is a valid string."""
        if not v:
            msg = f"String field {v} cannot be empty."
            raise DBConfigError(msg)

        if v != v.lower():
            msg = f"String field {v} must be lower case."
            raise DBConfigError(msg)

        return v

    @classmethod
    @abstractmethod
    def _validate_str_fields(cls, v: str) -> str:
        """Validate string fields for the concrete DB config class."""

    @property
    @abstractmethod
    def url(self) -> str:
        """Return a SQLAlchemy-compatible connection URL for the config."""


@dataclass
class LocalDBConfig(BaseDBConfig):
    """Configuration for local database connections."""

    possible_types: ClassVar[list[DatabaseType]] = [DatabaseType.SQLITE]
    _required_fields: ClassVar[list[str]] = ["type", "host", "name"]

    @field_validator("type", "url", "name", mode="before")
    @classmethod
    def _validate_str_fields(cls, v: str) -> str:
        if isinstance(v, str):
            return cls._validate_str_field(v)
        return v

    @property
    def url(self) -> str:
        """Return the SQLite connection URL for a local DB config."""
        path = Path(self.host) / self.name
        return f"sqlite:///{path.as_posix()}"


@dataclass
class ServerDBConfig(BaseDBConfig):
    """Configuration for server-based database connections."""

    user: str
    pw: str
    port: int
    driver: str
    dialect: str
    possible_types: ClassVar[list[DatabaseType]] = [
        DatabaseType.MYSQL,
        DatabaseType.POSTGRESQL,
    ]
    _required_fields: ClassVar[list[str]] = [
        "type",
        "url",
        "name",
        "user",
        "pw",
        "port",
        "driver",
    ]

    @field_validator("type", "name", "url", "user", "pw", "driver", mode="before")
    @classmethod
    def _validate_str_fields(cls, v: str) -> str:
        if isinstance(v, str):
            return cls._validate_str_field(v)
        return v

    @field_validator("port", mode="before")
    @classmethod
    def _validate_int_fields(cls, v: str) -> str:
        if isinstance(v, str):
            return cls._validate_int_field(v)
        return v

    @property
    def url(self) -> str:
        """Return the SQLAlchemy connection URL for server DB configs."""
        return f"{self.dialect}+{self.driver}://{self.user}:{self.pw}@{self.host}:{self.port}/{self.name}"


class DBConfigFactory:
    """Factory class for creating database configuration instances."""

    @classmethod
    def _resolve_db_config(cls, config_dict: dict[str, object]) -> BaseDBConfig:
        """Resolve and create db configuration instance based on provided dictionary."""
        db_type_str = config_dict.get("type")
        if not db_type_str:
            msg = "DB-Type must be provided."
            raise DBConfigError(msg)
        if not isinstance(db_type_str, str):
            db_type_str = str(db_type_str)
            config_dict["type"] = db_type_str

        # --- FIX: Inject default echo=False if not present ---
        if "echo" not in config_dict:
            config_dict["echo"] = False
        elif isinstance(config_dict["echo"], str):
            val = config_dict["echo"].lower()
            config_dict["echo"] = val in ("1", "true", "yes", "on")
        # ----------------------------------------------------

        try:
            db_type = DatabaseType(db_type_str)
        except ValueError as e:
            possible_types = (
                LocalDBConfig.possible_types + ServerDBConfig.possible_types
            )
            msg = (
                "Config type must be one of: "
                f"{', '.join(t.value for t in possible_types)}"
            )
            raise DBConfigError(msg) from e

        if db_type in LocalDBConfig.possible_types:
            return LocalDBConfig.from_dict(config_dict)

        if db_type in ServerDBConfig.possible_types:
            return ServerDBConfig.from_dict(config_dict)

        msg = f"Unsupported DB type encountered: {db_type.value}"
        raise DBConfigError(msg)

    def from_filepath(self, filepath: Path) -> BaseDBConfig:
        """Load database configuration from a YAML file."""
        with filepath.open() as file:
            db_config = yaml.safe_load(file)
        # Ensure the config dict is typed as dict[str, object]
        return self._resolve_db_config(dict(db_config))
