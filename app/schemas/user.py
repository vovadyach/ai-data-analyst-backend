from datetime import datetime
import uuid as uuid_lib

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
    is_verified: bool

    model_config = {"from_attributes": True}
