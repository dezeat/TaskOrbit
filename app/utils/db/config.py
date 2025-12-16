"""Database configuration models and factory.

Defines Pydantic models for local and server DB configuration and a
factory to load those from YAML files.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Literal, cast

import yaml
from pydantic import BaseModel, BeforeValidator, ValidationError

# Support static type checking for `pydantic-settings` while providing a
# runtime fallback when the package is not installed. This keeps behavior
# predictable in tests and in minimal environments.
if TYPE_CHECKING:
    from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore
else:
    try:
        from pydantic_settings import BaseSettings, SettingsConfigDict
    except Exception:

        class SettingsConfigDict(dict):
            """Tiny stand-in for pydantic SettingsConfigDict used in tests."""

        class BaseSettings:  # very small fallback that reads from env vars
            """Minimal fallback which populates annotated attributes from env."""

            def __init__(self, **_kwargs) -> None:
                """Populate annotated attributes from environment variables.

                This minimal fallback reads attributes named in the subclass
                annotations and sets them to the corresponding environment
                variable value or ``None`` when absent.
                """
                annotations = getattr(self, "__annotations__", {})
                for name in annotations:
                    setattr(self, name, os.environ.get(name, None))


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

    @staticmethod
    def _resolve_db_config(data: dict[str, object]) -> BaseDBConfig:
        """Resolve a raw mapping into a typed DB config instance.

        This helper mirrors the logic used when loading from file and is
        provided for testability.
        """
        db_type = data.get("type")

        try:
            if db_type == DatabaseType.SQLITE:
                return LocalDBConfig.model_validate(data)

            return ServerDBConfig.model_validate(data)

        except ValidationError as e:
            msg = f"Configuration Error: {e}"
            raise DBConfigError(msg) from e

    def from_filepath(self, filepath: Path) -> BaseDBConfig:
        """Load YAML config and return a validated config object."""
        # Prefer explicit file; if missing attempt to load from environment
        if not filepath.exists():
            # Attempt to resolve from environment using pydantic-settings if available
            env_cfg = self._resolve_from_env()
            if env_cfg is not None:
                return env_cfg

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

    def _resolve_from_env(self) -> BaseDBConfig | None:  # noqa: C901 - helper is intentionally verbose
        """Attempt to build a DB config from environment variables.

        This provides a lightweight integration with 12-factor env-driven
        configuration. If required env vars are missing, return None so the
        caller can fallback to file-based loading.
        """

        # Use pydantic-settings `Settings` if environment variables present.
        class Settings(BaseSettings):
            DB_TYPE: str | None
            DB_HOST: str | None
            DB_NAME: str | None
            DB_USER: str | None = None
            DB_PW: str | None = None
            DB_PORT: int | None = None
            DB_DRIVER: str | None = None
            DB_DIALECT: str | None = None
            DB_ECHO: bool = False

            model_config = SettingsConfigDict(env_file=".env", extra="ignore")

            def sqlalchemy_url(self) -> str | None:
                if not self.DB_TYPE or not self.DB_HOST or not self.DB_NAME:
                    return None
                if self.DB_TYPE == "sqlite":
                    path = Path(self.DB_HOST) / self.DB_NAME
                    return f"sqlite:///{path.as_posix()}"

                dialect = self.DB_DIALECT or self.DB_TYPE
                driver = f"+{self.DB_DRIVER}" if self.DB_DRIVER else ""
                user = self.DB_USER or ""
                pw = self.DB_PW or ""
                port = f":{self.DB_PORT}" if self.DB_PORT else ""
                return f"{dialect}{driver}://{user}:{pw}@{self.DB_HOST}{port}/{self.DB_NAME}"

        settings = Settings()
        if not settings.DB_TYPE or not settings.DB_HOST or not settings.DB_NAME:
            return None

        data: dict[str, object] = {
            "type": settings.DB_TYPE,
            "host": settings.DB_HOST,
            "name": settings.DB_NAME,
            "echo": bool(settings.DB_ECHO),
        }

        if settings.DB_USER:
            data["user"] = settings.DB_USER
        if settings.DB_PW:
            data["pw"] = settings.DB_PW
        if settings.DB_PORT:
            data["port"] = settings.DB_PORT
        if settings.DB_DRIVER:
            data["driver"] = settings.DB_DRIVER
        if settings.DB_DIALECT:
            data["dialect"] = settings.DB_DIALECT

        try:
            return self._resolve_db_config(data)
        except DBConfigError:
            return None

    # Provide a small helper to access pydantic Settings externally if desired
    @staticmethod
    def load_settings() -> BaseSettings | None:
        """Return a Settings instance if available, otherwise `None`."""
        try:

            class Settings(BaseSettings):
                DB_TYPE: str | None
                DB_HOST: str | None
                DB_NAME: str | None
                DB_USER: str | None = None
                DB_PW: str | None = None
                DB_PORT: int | None = None
                DB_DRIVER: str | None = None
                DB_DIALECT: str | None = None
                DB_ECHO: bool = False

                model_config = SettingsConfigDict(env_file=".env", extra="ignore")

            return Settings()
        except (ImportError, ModuleNotFoundError):
            return None
