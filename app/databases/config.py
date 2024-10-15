from abc import abstractmethod
from enum import StrEnum
from pathlib import Path
from typing import ClassVar

import yaml
from pydantic import dataclass, field_validator, model_validator

from app.exceptions import DBConfigError


class DatabaseType(StrEnum):
    """Enum for different database types."""

    SQLLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    # "AZURE_SQL = "azure_sql""


@dataclass
class BaseDBConfig:
    """Base class for database configuration.

    Attributes:
        type (DatabaseType): The type of the database.
        url (str): The URL for the database connection.
        name (str): The name of the database.
        possible_types (ClassVar[list[DatabaseType]]): Possible types for db-configs.
        _required_fields (ClassVar[list[str]]): Required fields for db-configs.
    """

    type: DatabaseType
    url: str
    name: str
    possible_types: ClassVar[list[DatabaseType]]
    _required_fields: ClassVar[list[str]]

    @classmethod
    @model_validator
    def _validate_required_fields(cls, db_config: dict[str, str]) -> dict[str, str]:
        """Validate that all required fields are present in the given configuration.

        Args:
            cls: The class being validated.
            db_config (dict[str, str]): The database configuration dictionary.

        Returns:
            dict[str, str]: The validated configuration dictionary.
        """
        missing_fields = [
            field for field in cls._required_fields if field not in db_config
        ]
        if missing_fields:
            msg = f"These fields are missing in config: {', '.join(missing_fields)}"
            raise DBConfigError(msg)
        return db_config

    @classmethod
    def _validate_int_field(cls, v: str) -> str:
        """Validate that a given value is a valid integer.

        Args:
            cls: The class being validated.
            v (str): The value to validate.

        Returns:
            str: The validated integer value as a string.
        """
        if not v:
            msg = f"Integer field {v} cannot be empty."
            raise DBConfigError(msg)

        if not v.isdigit():
            msg = f"Integer field {v} contains non-digit chars."
            raise DBConfigError(msg)

        return v

    @classmethod
    def _validate_str_field(cls, v: str) -> str:
        """Validate that a given value is a valid string.

        Args:
            cls: The class being validated.
            v (str): The value to validate.

        Returns:
            str: The validated string value.
        """
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
        """Wrapper method for running all validation checks on string fields."""


@dataclass
class LocalDBConfig(BaseDBConfig):
    """Configuration for local database connections.

    Attributes:
        possible_types (ClassVar[list[DatabaseType]]): Possible types for db-configs.
        _required_fields (ClassVar[list[str]]): Required fields for local-db-configs.
    """

    possible_types: ClassVar[list[DatabaseType]] = [DatabaseType.SQLLITE]
    _required_fields: ClassVar[list[str]] = ["type", "url", "name"]

    @field_validator("type", "url", "name", mode="before")
    @classmethod
    def _validate_str_fields(cls, v: str) -> str:
        """Validate string fields for local database configuration.

        Args:
            cls: The class being validated.
            v (str): The value to validate.

        Returns:
            str: The validated string value.
        """
        return cls._validate_str_field(v)


@dataclass
class ServerDBConfig(BaseDBConfig):
    """Configuration for server-based database connections.

    Attributes:
        user (str): The username for database authentication.
        pw (str): The password for database authentication.
        port (int): The port number for the database connection.
        driver (str): The database driver to use.
        possible_types (ClassVar[list[DatabaseType]]): Possible types for db-configs.
        _required_fields (ClassVar[list[str]]): Required fields for server-db-configs
    """

    user: str
    pw: str
    port: int
    driver: str
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
        """Validate string fields for server database configuration.

        Args:
            cls: The class being validated.
            v (str): The value to validate.

        Returns:
            str: The validated string value.
        """
        return cls._validate_str_field(v)

    @field_validator("port", mode="before")
    @classmethod
    def _validate_int_fields(cls, v: str) -> str:
        """Validate the port field for server database configuration.

        Args:
            cls: The class being validated.
            v (str): The value to validate.

        Returns:
            str: The validated port value as a string.
        """
        return cls._validate_int_field(v)


class DBConfigFactory:
    """Factory class for creating database configuration instances."""

    @classmethod
    def _resolve_db_config(cls, config_dict: dict[str, str]) -> BaseDBConfig:
        """Resolve and create db configuration instance based on provided dictionary.

        Args:
            cls: The class being validated.
            config_dict (dict[str, str]): The database configuration dictionary.

        Returns:
            BaseDBConfig: An instance of the appropriate database configuration class.
        """
        if "type" not in config_dict:
            msg = "DB-Type must be provided."
            raise DBConfigError(msg)

        if config_dict["type"] in LocalDBConfig.possible_types:
            return LocalDBConfig(**config_dict)

        elif config_dict["type"] in ServerDBConfig.possible_types:  # noqa: RET505
            return ServerDBConfig(**config_dict)

        else:
            possible_types = (
                LocalDBConfig.possible_types + ServerDBConfig.possible_types
            )
            msg = f"Config type must be of {', '.join(
                db_type.value for db_type in possible_types)}"
            raise DBConfigError(msg)

    def from_filepath(self, filepath: Path) -> BaseDBConfig:
        """Load database configuration from a YAML file.

        Args:
            filepath (Path): The path to the YAML configuration file.

        Returns:
            BaseDBConfig: An instance of the loaded database configuration.
        """
        with filepath.open() as file:
            db_config = yaml.safe_load(file)

        return self.from_dict(db_config)

    def from_dict(self, config_dict: dict[str, str]) -> BaseDBConfig:
        """Create a database configuration instance from a dictionary.

        Args:
            config_dict (dict[str, str]): The database configuration dictionary.

        Returns:
            BaseDBConfig: An instance of the created database configuration.
        """
        return self._resolve_db_config(config_dict)
