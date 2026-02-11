from datetime import datetime, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderLog, OrderStatus
from app.models.address import Address
from app.services.delivery_date_service import calculate_nearest_delivery_date
from app.config import get_settings

settings = get_settings()


async def create_order(
    db: AsyncSession,
    user_id: int,
    address_id: int,
    jv_qty: int,
    lv_qty: int,
    comment: str | None = None,
) -> Order:
    # Защита от дублей (10 мин)
    ten_min_ago = datetime.now() - timedelta(minutes=settings.DUPLICATE_ORDER_MINUTES)
    existing = await db.execute(
        select(Order).where(
            Order.user_id == user_id,
            Order.address_id == address_id,
            Order.jv_qty == jv_qty,
            Order.lv_qty == lv_qty,
            Order.created_at >= ten_min_ago,
            Order.status != OrderStatus.cancelled,
        )
    )
    if existing.scalar_one_or_none():
        raise ValueError("Дубликат заказа. Подождите 10 минут.")

    total_qty = jv_qty + lv_qty

    # Получить район из адреса
    address = await db.execute(select(Address).where(Address.id == address_id))
    addr = address.scalar_one_or_none()
    if not addr:
        raise ValueError("Адрес не найден")

    # Рассчитать дату
    date_info = await calculate_nearest_delivery_date(
        db, addr.district, total_qty
    )

    order = Order(
        user_id=user_id,
        address_id=address_id,
        jv_qty=jv_qty,
        lv_qty=lv_qty,
        total_qty=total_qty,
        delivery_date=date_info["delivery_date"],
        status=OrderStatus.new,
        comment=comment,
    )
    db.add(order)
    await db.flush()

    # Лог
    log = OrderLog(
        order_id=order.id,
        action="created",
        new_status=OrderStatus.new.value,
    )
    db.add(log)
    await db.flush()

    return order


async def get_order_by_id(db: AsyncSession, order_id: int) -> Order | None:
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.address), selectinload(Order.user))
        .where(Order.id == order_id)
    )
    return result.scalar_one_or_none()


async def get_user_orders(
    db: AsyncSession, user_id: int, limit: int = 20, offset: int = 0
) -> tuple[list[Order], int]:
    # Подсчёт
    count_q = select(func.count(Order.id)).where(Order.user_id == user_id)
    total = (await db.execute(count_q)).scalar_one()

    # Заказы
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.address))
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all()), total


async def get_active_order(db: AsyncSession, user_id: int) -> Order | None:
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.address))
        .where(
            Order.user_id == user_id,
            Order.status.in_([
                OrderStatus.new,
                OrderStatus.confirmed,
                OrderStatus.rescheduled,
                OrderStatus.in_delivery,
            ]),
        )
        .order_by(Order.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_last_completed_order(db: AsyncSession, user_id: int) -> Order | None:
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.address))
        .where(
            Order.user_id == user_id,
            Order.status == OrderStatus.completed,
        )
        .order_by(Order.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def update_order_status(
    db: AsyncSession,
    order: Order,
    new_status: OrderStatus,
    operator_id: int | None = None,
    comment: str | None = None,
    delivery_date=None,
) -> Order:
    old_status = order.status
    order.status = new_status

    if new_status == OrderStatus.confirmed:
        order.confirmed_at = datetime.now()
    if delivery_date:
        order.delivery_date = delivery_date
    if operator_id:
        order.operator_id = operator_id

    log = OrderLog(
        order_id=order.id,
        action="status_change",
        old_status=old_status.value,
        new_status=new_status.value,
        operator_id=operator_id,
        comment=comment,
    )
    db.add(log)
    await db.flush()
    return order


async def update_order(
    db: AsyncSession,
    order: Order,
    jv_qty: int | None = None,
    lv_qty: int | None = None,
    comment: str | None = None,
) -> Order:
    if order.status != OrderStatus.new:
        raise ValueError("Редактировать можно только заказ в статусе «Новый»")

    if jv_qty is not None:
        order.jv_qty = jv_qty
    if lv_qty is not None:
        order.lv_qty = lv_qty
    order.total_qty = order.jv_qty + order.lv_qty

    if order.total_qty < 1:
        raise ValueError("Общее количество (ЖВ + ЛВ) должно быть ≥ 1")

    if comment is not None:
        order.comment = comment

    # Пересчёт даты
    address = await db.execute(select(Address).where(Address.id == order.address_id))
    addr = address.scalar_one()
    date_info = await calculate_nearest_delivery_date(
        db, addr.district, order.total_qty
    )
    order.delivery_date = date_info["delivery_date"]

    log = OrderLog(
        order_id=order.id,
        action="edited",
        comment=f"ЖВ={order.jv_qty}, ЛВ={order.lv_qty}",
    )
    db.add(log)
    await db.flush()
    return order


async def get_new_orders(db: AsyncSession) -> list[Order]:
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.address),
            selectinload(Order.user),
        )
        .where(Order.status == OrderStatus.new)
        .order_by(Order.created_at.asc())
    )
    return list(result.scalars().all())


async def get_stale_orders(db: AsyncSession, hours: int) -> list[Order]:
    """Заказы в статусе new старше N часов."""
    threshold = datetime.now() - timedelta(hours=hours)
    result = await db.execute(
        select(Order).where(
            Order.status == OrderStatus.new,
            Order.created_at <= threshold,
        )
    )
    return list(result.scalars().all())
