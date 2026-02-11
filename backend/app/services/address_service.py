from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.address import Address


async def get_addresses_by_user(db: AsyncSession, user_id: int) -> list[Address]:
    result = await db.execute(
        select(Address)
        .where(Address.user_id == user_id)
        .order_by(Address.is_default.desc(), Address.created_at.desc())
    )
    return list(result.scalars().all())


async def get_address_by_id(db: AsyncSession, address_id: int) -> Address | None:
    result = await db.execute(select(Address).where(Address.id == address_id))
    return result.scalar_one_or_none()


async def create_address(db: AsyncSession, user_id: int, **kwargs) -> Address:
    # Если это первый адрес, делаем по умолчанию
    existing = await get_addresses_by_user(db, user_id)
    if not existing:
        kwargs["is_default"] = True

    # Лимит 10 адресов
    if len(existing) >= 10:
        raise ValueError("Максимум 10 адресов")

    address = Address(user_id=user_id, **kwargs)
    db.add(address)
    await db.flush()
    return address


async def update_address(db: AsyncSession, address: Address, **kwargs) -> Address:
    for key, value in kwargs.items():
        if value is not None and hasattr(address, key):
            setattr(address, key, value)
    await db.flush()
    return address


async def delete_address(db: AsyncSession, address: Address) -> None:
    await db.delete(address)
    await db.flush()


async def set_default_address(
    db: AsyncSession, user_id: int, address_id: int
) -> None:
    # Снять default со всех
    addresses = await get_addresses_by_user(db, user_id)
    for addr in addresses:
        addr.is_default = addr.id == address_id
    await db.flush()
