"""Tests for Pydantic schemas used for DB payloads."""

from app.schemas import TaskSchema, UserSchema


def test_user_schema_validation_minimal(fix_user_data: dict[str, str]) -> None:
    """UserSchema validates minimal input and exposes expected fields."""
    u = UserSchema.model_validate(fix_user_data)

    assert u.hashed_password == fix_user_data["hashed_password"]
    assert u.name == fix_user_data["name"]
    assert u.id is None


def test_task_schema_validation_full(fix_task_data: dict[str, object]) -> None:
    """TaskSchema validates full input mapping correctly."""
    t = TaskSchema.model_validate(fix_task_data)

    assert t.name == "do something"
    assert t.user_id == fix_task_data["user_id"]
    assert t.id == fix_task_data["id"]
    assert t.description == "desc"
    assert t.ts_acomplished == fix_task_data["ts_acomplished"]
