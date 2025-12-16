"""Tests for database configuration resolution."""

import pytest

from app.utils.db.config import (
    DBConfigFactory,
    LocalDBConfig,
    ServerDBConfig,
)
from app.utils.exceptions import DBConfigError


def test_local_dbconfig_url_and_echo_injected(fix_local_cfg: dict[str, str]) -> None:
    """Local config resolves and has echo injected."""
    resolved = DBConfigFactory._resolve_db_config(fix_local_cfg)

    assert isinstance(resolved, LocalDBConfig)
    assert resolved.echo is False
    assert resolved.url.startswith("sqlite:///")


def test_server_dbconfig_url(fix_server_cfg: dict[str, object]) -> None:
    """Server config resolves to a full SQLAlchemy URL."""
    resolved = DBConfigFactory._resolve_db_config(fix_server_cfg)

    assert isinstance(resolved, ServerDBConfig)
    assert "postgresql+" in resolved.url
    assert ":5432/" in resolved.url


def test_missing_type_raises() -> None:
    """Missing type in config raises DBConfigError."""
    with pytest.raises(DBConfigError):
        DBConfigFactory._resolve_db_config({})


def test_invalid_type_raises() -> None:
    """Invalid type in config raises DBConfigError."""
    with pytest.raises(DBConfigError):
        DBConfigFactory._resolve_db_config({"type": "unsupported"})
