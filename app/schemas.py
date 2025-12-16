from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID]
    name: str
    hashed_password: str
    last_login_ts: Optional[datetime]


class TaskSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID]
    user_id: UUID
    name: str
    description: Optional[str]
    ts_acomplished: Optional[datetime]
    ts_deadline: Optional[datetime]
