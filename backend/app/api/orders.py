from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.order import OrderCreate, OrderUpdate, OrderOut, OrderListOut
from app.services.order_service import (
    create_order,
    get_order_by_id,
    get_user_orders,
    get_active_order,
    get_last_completed_order,
    update_order,
)
from app.services.user_service import get_user_by_telegram_id

router = APIRouter()


@router.post("/user/{telegram_id}", response_model=OrderOut, status_code=201)
async def new_order(
    telegram_id: int, data: OrderCreate, db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    try:
        order = await create_order(
            db, user.id, data.address_id, data.jv_qty, data.lv_qty, data.comment
        )
        return order
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/user/{telegram_id}", response_model=OrderListOut)
async def list_orders(
    telegram_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    user = await get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    orders, total = await get_user_orders(db, user.id, limit, offset)
    return OrderListOut(orders=orders, total=total)


@router.get("/user/{telegram_id}/active", response_model=OrderOut | None)
async def active_order(telegram_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    order = await get_active_order(db, user.id)
    return order


@router.get("/user/{telegram_id}/last-completed", response_model=OrderOut | None)
async def last_completed(telegram_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    order = await get_last_completed_order(db, user.id)
    return order


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    order = await get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(404, "Заказ не найден")
    return order


@router.patch("/{order_id}", response_model=OrderOut)
async def edit_order(
    order_id: int, data: OrderUpdate, db: AsyncSession = Depends(get_db)
):
    order = await get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(404, "Заказ не найден")
    try:
        updated = await update_order(
            db, order, **data.model_dump(exclude_unset=True)
        )
        return updated
    except ValueError as e:
        raise HTTPException(400, str(e))
