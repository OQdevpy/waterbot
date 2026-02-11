"""
Критическая бизнес-логика: расчёт ближайшей доступной даты доставки.

Правила:
- До 17:00 — можно назначить на сегодня
- После 17:00 — только со следующего дня
- Исключаются выходные (сб, вс) и праздники
- Проверяется лимит района и общий лимит (331)
"""

from datetime import date, datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus
from app.models.district import DistrictLimit
from app.models.holiday import Holiday
from app.config import get_settings

settings = get_settings()

TOTAL_DAILY_LIMIT = 331

CANCELLED_STATUSES = {OrderStatus.cancelled}


async def get_district_limit(db: AsyncSession, district: str) -> int:
    """Получить дневной лимит для района."""
    result = await db.execute(
        select(DistrictLimit.max_per_day).where(
            DistrictLimit.district == district,
            DistrictLimit.is_active.is_(True),
        )
    )
    limit = result.scalar_one_or_none()
    if limit is None:
        # Район «Прочие»
        result = await db.execute(
            select(DistrictLimit.max_per_day).where(
                DistrictLimit.district == "Прочие",
                DistrictLimit.is_active.is_(True),
            )
        )
        limit = result.scalar_one_or_none()
    return limit or 91


async def get_orders_count_for_date(
    db: AsyncSession, target_date: date, district: str | None = None
) -> int:
    """Подсчитать сумму бутылей на дату (по району или всего)."""
    query = select(func.coalesce(func.sum(Order.total_qty), 0)).where(
        Order.delivery_date == target_date,
        Order.status.notin_(CANCELLED_STATUSES),
    )
    if district:
        from app.models.address import Address

        query = query.join(Address, Order.address_id == Address.id).where(
            Address.district == district
        )
    result = await db.execute(query)
    return result.scalar_one()


async def is_holiday(db: AsyncSession, target_date: date) -> bool:
    """Проверить, является ли дата праздником."""
    result = await db.execute(
        select(Holiday.id).where(Holiday.date == target_date)
    )
    return result.scalar_one_or_none() is not None


def is_weekend(target_date: date) -> bool:
    """Проверить, является ли дата выходным (сб=5, вс=6)."""
    return target_date.weekday() in (5, 6)


async def calculate_nearest_delivery_date(
    db: AsyncSession,
    district: str,
    qty: int,
    start_date: date | None = None,
) -> dict:
    """
    Рассчитать ближайшую доступную дату доставки.

    Возвращает dict:
        delivery_date: date
        district_remaining: int
        total_remaining: int
    """
    now = datetime.now()

    if start_date is None:
        if now.hour < settings.ORDER_CUTOFF_HOUR:
            start_date = now.date()
        else:
            start_date = now.date() + timedelta(days=1)

    district_limit = await get_district_limit(db, district)
    current_date = start_date

    # Ищем максимум 60 дней вперёд
    for _ in range(60):
        if is_weekend(current_date):
            current_date += timedelta(days=1)
            continue

        if await is_holiday(db, current_date):
            current_date += timedelta(days=1)
            continue

        district_used = await get_orders_count_for_date(db, current_date, district)
        total_used = await get_orders_count_for_date(db, current_date)

        district_available = district_limit - district_used
        total_available = TOTAL_DAILY_LIMIT - total_used

        if district_available >= qty and total_available >= qty:
            return {
                "delivery_date": current_date,
                "district_remaining": district_available - qty,
                "total_remaining": total_available - qty,
            }

        current_date += timedelta(days=1)

    raise ValueError("Не удалось найти доступную дату доставки в ближайшие 60 дней")
