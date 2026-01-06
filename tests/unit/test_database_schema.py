"""Unit tests for database schema and table prefix functionality."""

from collections.abc import Callable
from typing import Any as TypingAny

from app.config import DatabaseType


class TestDatabaseSchemaConfig:
    """Tests for schema and prefix configuration."""

    def test_postgresql_schema_in_connection_string(
        self,
        mock_env_config: Callable[[dict[str, str]], None],  # Updated fixture name
        fix_config: Callable[[], TypingAny],
    ) -> None:
        """Test that PostgreSQL connection string includes schema parameter."""
        mock_env_config(
            {
                "DB_TYPE": "postgresql",
                "DB_SCHEMA": "test_schema",
                "DB_HOST": "localhost",
                "DB_USER": "testuser",
                "DB_PASS": "testpass",
                "DB_NAME": "testdb",
            }
        )

        config = fix_config()

        assert config.DB_TYPE == DatabaseType.POSTGRESQL
        assert config.DB_SCHEMA == "test_schema"

        uri = config.SQLALCHEMY_DATABASE_URI
        assert "search_path" in uri
        assert "test_schema" in uri

    def test_default_schema_value(
        self,
        mock_env_config: Callable[[dict[str, str]], None],
        fix_config: Callable[[], TypingAny],
    ) -> None:
        """Test that default DB_SCHEMA is 'taskorbit'."""
        mock_env_config({})  # Reset environment to defaults
        config = fix_config()
        assert config.DB_SCHEMA == "taskorbit"

    def test_sqlite_connection_string_format(
        self,
        mock_env_config: Callable[[dict[str, str]], None],  # Updated fixture name
        fix_config: Callable[[], TypingAny],
    ) -> None:
        """Test SQLite connection string format."""
        mock_env_config(
            {
                "DB_TYPE": "sqlite",
                "DB_NAME": "test.db",
                "DB_HOST": ".",
            }
        )

        config = fix_config()
        uri = config.SQLALCHEMY_DATABASE_URI

        assert uri.startswith("sqlite:///")
        assert "test.db" in uri
