from datetime import datetime
from pydantic import BaseModel, Field


class AddressCreate(BaseModel):
    city: str = Field(min_length=1, max_length=100)
    district: str = Field(min_length=1, max_length=100)
    street: str = Field(min_length=1, max_length=255)
    house: str = Field(min_length=1, max_length=50)
    is_default: bool = False


class AddressUpdate(BaseModel):
    city: str | None = None
    district: str | None = None
    street: str | None = None
    house: str | None = None
    is_default: bool | None = None


class AddressOut(BaseModel):
    id: int
    user_id: int
    city: str
    district: str
    street: str
    house: str
    is_default: bool
    created_at: datetime

    model_config = {"from_attributes": True}
