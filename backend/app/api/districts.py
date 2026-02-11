from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.district import DistrictLimit
from app.models.holiday import Holiday
from app.schemas.district import (
    DistrictLimitOut,
    DistrictLimitUpdate,
    HolidayCreate,
    HolidayOut,
    DeliveryDateResponse,
)
from app.services.delivery_date_service import calculate_nearest_delivery_date

router = APIRouter()


@router.get("/", response_model=list[DistrictLimitOut])
async def list_districts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DistrictLimit).order_by(DistrictLimit.district))
    return list(result.scalars().all())


@router.patch("/{district_id}", response_model=DistrictLimitOut)
async def update_district(
    district_id: int, data: DistrictLimitUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(DistrictLimit).where(DistrictLimit.id == district_id)
    )
    district = result.scalar_one_or_none()
    if not district:
        raise HTTPException(404, "Район не найден")
    if data.max_per_day:
        district.max_per_day = data.max_per_day
    if data.is_active is not None:
        district.is_active = data.is_active
    await db.flush()
    return district


@router.get("/holidays", response_model=list[HolidayOut])
async def list_holidays(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Holiday).order_by(Holiday.date))
    return list(result.scalars().all())


@router.post("/holidays", response_model=HolidayOut, status_code=201)
async def add_holiday(data: HolidayCreate, db: AsyncSession = Depends(get_db)):
    holiday = Holiday(date=data.date, description=data.description)
    db.add(holiday)
    await db.flush()
    return holiday


@router.get("/calculate-date", response_model=DeliveryDateResponse)
async def calc_delivery_date(
    district: str,
    qty: int = 1,
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await calculate_nearest_delivery_date(db, district, qty)
        return DeliveryDateResponse(district=district, **result)
    except ValueError as e:
        raise HTTPException(400, str(e))
