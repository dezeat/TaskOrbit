from datetime import datetime, timezone
from uuid import uuid4

import pytest


@pytest.fixture
def fix_task_data() -> dict[str, object]:
    """Sample `Task` dataclass input mapping used across db tests."""
    now = datetime.now(tz=timezone.utc)

    return {
        "name": "do something",
        "user_id": uuid4(),
        "id": uuid4(),
        "description": "desc",
        "ts_acomplished": now,
        "ts_deadline": now,
    }


@pytest.fixture
def fix_user_data() -> dict[str, str]:
    """Sample `User` dataclass input mapping shared by db tests."""
    return {"name": "foo", "hashed_password": "bar"}
