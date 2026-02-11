from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, UserRole, RoleEnum


async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int) -> User | None:
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(
        select(User)
        .options(selectinload(User.roles))
        .where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    telegram_id: int,
    name: str,
    phone: str | None = None,
) -> User:
    user = User(telegram_id=telegram_id, name=name, phone=phone)
    db.add(user)
    await db.flush()
    # Роль клиента по умолчанию
    role = UserRole(user_id=user.id, role=RoleEnum.client)
    db.add(role)
    await db.flush()
    return user


async def update_user(db: AsyncSession, user: User, **kwargs) -> User:
    for key, value in kwargs.items():
        if value is not None and hasattr(user, key):
            setattr(user, key, value)
    await db.flush()
    return user


async def get_operators(db: AsyncSession) -> list[User]:
    result = await db.execute(
        select(User)
        .join(UserRole)
        .where(UserRole.role.in_([RoleEnum.operator, RoleEnum.admin]))
    )
    return list(result.scalars().all())


async def has_role(db: AsyncSession, user_id: int, role: RoleEnum) -> bool:
    result = await db.execute(
        select(UserRole.id).where(
            UserRole.user_id == user_id,
            UserRole.role == role,
        )
    )
    return result.scalar_one_or_none() is not None
