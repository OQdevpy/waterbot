from datetime import datetime, date
from pydantic import BaseModel, Field, model_validator


class OrderCreate(BaseModel):
    address_id: int
    jv_qty: int = Field(ge=0, default=0)
    lv_qty: int = Field(ge=0, default=0)
    comment: str | None = None

    @model_validator(mode="after")
    def check_qty(self):
        if self.jv_qty + self.lv_qty < 1:
            raise ValueError("Общее количество (ЖВ + ЛВ) должно быть ≥ 1")
        return self


class OrderUpdate(BaseModel):
    jv_qty: int | None = Field(ge=0, default=None)
    lv_qty: int | None = Field(ge=0, default=None)
    comment: str | None = None


class OrderStatusUpdate(BaseModel):
    status: str
    comment: str | None = None
    delivery_date: date | None = None


class OrderOut(BaseModel):
    id: int
    user_id: int
    address_id: int | None
    jv_qty: int
    lv_qty: int
    total_qty: int
    delivery_date: date | None
    status: str
    comment: str | None
    created_at: datetime
    confirmed_at: datetime | None
    operator_id: int | None

    model_config = {"from_attributes": True}


class OrderListOut(BaseModel):
    orders: list[OrderOut]
    total: int
