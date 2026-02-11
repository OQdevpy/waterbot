from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.address import AddressCreate, AddressUpdate, AddressOut
from app.services.address_service import (
    get_addresses_by_user,
    get_address_by_id,
    create_address,
    update_address,
    delete_address,
    set_default_address,
)
from app.services.user_service import get_user_by_telegram_id

router = APIRouter()


@router.get("/user/{telegram_id}", response_model=list[AddressOut])
async def list_addresses(telegram_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    return await get_addresses_by_user(db, user.id)


@router.post("/user/{telegram_id}", response_model=AddressOut, status_code=201)
async def add_address(
    telegram_id: int, data: AddressCreate, db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    try:
        addr = await create_address(db, user.id, **data.model_dump())
        return addr
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.patch("/{address_id}", response_model=AddressOut)
async def patch_address(
    address_id: int, data: AddressUpdate, db: AsyncSession = Depends(get_db)
):
    addr = await get_address_by_id(db, address_id)
    if not addr:
        raise HTTPException(404, "Адрес не найден")
    updated = await update_address(db, addr, **data.model_dump(exclude_unset=True))
    return updated


@router.delete("/{address_id}", status_code=204)
async def remove_address(address_id: int, db: AsyncSession = Depends(get_db)):
    addr = await get_address_by_id(db, address_id)
    if not addr:
        raise HTTPException(404, "Адрес не найден")
    await delete_address(db, addr)


@router.post("/{address_id}/default", status_code=200)
async def make_default(address_id: int, db: AsyncSession = Depends(get_db)):
    addr = await get_address_by_id(db, address_id)
    if not addr:
        raise HTTPException(404, "Адрес не найден")
    await set_default_address(db, addr.user_id, address_id)
    return {"ok": True}
