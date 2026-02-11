from datetime import datetime
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    telegram_id: int
    phone: str | None = None
    name: str = Field(min_length=2, max_length=255)


class UserUpdate(BaseModel):
    phone: str | None = None
    name: str | None = None


class UserOut(BaseModel):
    id: int
    telegram_id: int
    phone: str | None
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserRoleOut(BaseModel):
    id: int
    user_id: int
    role: str

    model_config = {"from_attributes": True}
