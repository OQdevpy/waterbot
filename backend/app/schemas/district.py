from pydantic import BaseModel, Field
from datetime import date


class DistrictLimitOut(BaseModel):
    id: int
    district: str
    max_per_day: int
    is_active: bool

    model_config = {"from_attributes": True}


class DistrictLimitUpdate(BaseModel):
    max_per_day: int = Field(gt=0)
    is_active: bool | None = None


class HolidayCreate(BaseModel):
    date: date
    description: str | None = None


class HolidayOut(BaseModel):
    id: int
    date: date
    description: str | None

    model_config = {"from_attributes": True}


class DeliveryDateResponse(BaseModel):
    delivery_date: date
    district: str
    district_remaining: int
    total_remaining: int
