"""Tests for database models."""
from app.utils.db.models import Task, User


def test_user_from_dict_minimal(fix_user_data: dict[str, str]) -> None:
    """User.from_dict constructs minimal User dataclass."""
    u = User.from_dict(fix_user_data)

    assert u.name == "alice"
    assert u.hashed_password == "pw"  # noqa: S105
    assert u.id is None


def test_task_from_dict_full(fix_task_data: dict[str, object]) -> None:
    """Task.from_dict maps all provided fields."""
    t = Task.from_dict(fix_task_data)

    assert t.name == "do something"
    assert t.user_id == fix_task_data["user_id"]
    assert t.id == fix_task_data["id"]
    assert t.description == "desc"
    assert t.ts_acomplished == fix_task_data["ts_acomplished"]
