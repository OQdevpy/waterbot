from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.services.user_service import (
    get_user_by_telegram_id,
    create_user,
    update_user,
)

router = APIRouter()


@router.post("/", response_model=UserOut, status_code=201)
async def register_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await get_user_by_telegram_id(db, data.telegram_id)
    if existing:
        raise HTTPException(400, "Пользователь уже зарегистрирован")
    user = await create_user(db, data.telegram_id, data.name, data.phone)
    return user


@router.get("/tg/{telegram_id}", response_model=UserOut)
async def get_user(telegram_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    return user


@router.patch("/tg/{telegram_id}", response_model=UserOut)
async def patch_user(
    telegram_id: int, data: UserUpdate, db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    updated = await update_user(db, user, **data.model_dump(exclude_unset=True))
    return updated
