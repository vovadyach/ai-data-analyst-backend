import uuid as uuid_lib
from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: uuid_lib.UUID
    email: str
    first_name: str
    last_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    is_admin: bool
    avatar_url: str | None = None

    model_config = {"from_attributes": True}
