from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.order import OrderOut, OrderStatusUpdate
from app.models.order import OrderStatus
from app.services.order_service import (
    get_new_orders,
    get_order_by_id,
    update_order_status,
    get_user_orders,
)

router = APIRouter()


@router.get("/orders/new", response_model=list[OrderOut])
async def list_new_orders(db: AsyncSession = Depends(get_db)):
    orders = await get_new_orders(db)
    return orders


@router.post("/orders/{order_id}/confirm", response_model=OrderOut)
async def confirm_order(
    order_id: int,
    operator_telegram_id: int = 0,
    db: AsyncSession = Depends(get_db),
):
    order = await get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(404, "Заказ не найден")
    if order.status != OrderStatus.new:
        raise HTTPException(400, "Можно подтвердить только новый заказ")

    from app.services.user_service import get_user_by_telegram_id

    operator = await get_user_by_telegram_id(db, operator_telegram_id)
    op_id = operator.id if operator else None

    updated = await update_order_status(
        db, order, OrderStatus.confirmed, operator_id=op_id
    )
    return updated


@router.post("/orders/{order_id}/cancel", response_model=OrderOut)
async def cancel_order(
    order_id: int,
    data: OrderStatusUpdate | None = None,
    db: AsyncSession = Depends(get_db),
):
    order = await get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(404, "Заказ не найден")
    if order.status in (OrderStatus.completed, OrderStatus.cancelled):
        raise HTTPException(400, "Невозможно отменить этот заказ")

    comment = data.comment if data else None
    updated = await update_order_status(
        db, order, OrderStatus.cancelled, comment=comment
    )
    return updated


@router.post("/orders/{order_id}/reschedule", response_model=OrderOut)
async def reschedule_order(
    order_id: int,
    data: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    order = await get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(404, "Заказ не найден")
    if not data.delivery_date:
        raise HTTPException(400, "Укажите новую дату доставки")

    updated = await update_order_status(
        db,
        order,
        OrderStatus.rescheduled,
        delivery_date=data.delivery_date,
        comment=data.comment,
    )
    return updated


@router.post("/orders/{order_id}/deliver", response_model=OrderOut)
async def start_delivery(order_id: int, db: AsyncSession = Depends(get_db)):
    order = await get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(404, "Заказ не найден")
    updated = await update_order_status(db, order, OrderStatus.in_delivery)
    return updated


@router.post("/orders/{order_id}/complete", response_model=OrderOut)
async def complete_order(order_id: int, db: AsyncSession = Depends(get_db)):
    order = await get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(404, "Заказ не найден")
    updated = await update_order_status(db, order, OrderStatus.completed)
    return updated


@router.get("/client/{user_id}/history", response_model=list[OrderOut])
async def client_history(
    user_id: int, limit: int = 5, db: AsyncSession = Depends(get_db)
):
    orders, _ = await get_user_orders(db, user_id, limit=limit)
    return orders
