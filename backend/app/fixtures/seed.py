"""
Заполнение БД тестовыми данными (fixtures).
Запускается автоматически при первом старте, если БД пустая.
"""

import asyncio
from datetime import date, datetime, timedelta

from sqlalchemy import select, func

from app.database import async_session
from app.models.user import User, UserRole, RoleEnum
from app.models.address import Address
from app.models.order import Order, OrderStatus
from app.models.district import DistrictLimit
from app.models.holiday import Holiday


async def seed_database():
    async with async_session() as db:
        # Проверяем, есть ли уже данные
        count = await db.execute(select(func.count(User.id)))
        if count.scalar_one() > 0:
            print("БД уже содержит данные, пропуск seed")
            return

        print("Заполнение БД тестовыми данными...")

        # === Районы и лимиты ===
        districts = [
            DistrictLimit(district="Шахтёрск + посёлки", max_per_day=140, is_active=True),
            DistrictLimit(district="Зугрэс", max_per_day=50, is_active=True),
            DistrictLimit(district="Торез", max_per_day=50, is_active=True),
            DistrictLimit(district="Прочие", max_per_day=91, is_active=True),
        ]
        db.add_all(districts)
        await db.flush()

        # === Праздники ===
        today = date.today()
        holidays = [
            Holiday(date=date(today.year, 1, 1), description="Новый год"),
            Holiday(date=date(today.year, 1, 7), description="Рождество"),
            Holiday(date=date(today.year, 3, 8), description="Международный женский день"),
            Holiday(date=date(today.year, 5, 1), description="Праздник весны и труда"),
            Holiday(date=date(today.year, 5, 9), description="День Победы"),
        ]
        db.add_all(holidays)
        await db.flush()

        # === Пользователи ===
        client1 = User(telegram_id=111111, name="Иванов Иван Иванович", phone="+79001234567")
        client2 = User(telegram_id=222222, name="Петрова Мария Сергеевна", phone="+79009876543")
        operator1 = User(telegram_id=333333, name="Сидоров Алексей Петрович", phone="+79005551234")
        admin1 = User(telegram_id=444444, name="Козлов Дмитрий Андреевич", phone="+79005559876")

        db.add_all([client1, client2, operator1, admin1])
        await db.flush()

        # === Роли ===
        roles = [
            UserRole(user_id=client1.id, role=RoleEnum.client),
            UserRole(user_id=client2.id, role=RoleEnum.client),
            UserRole(user_id=operator1.id, role=RoleEnum.operator),
            UserRole(user_id=admin1.id, role=RoleEnum.admin),
            UserRole(user_id=admin1.id, role=RoleEnum.operator),
        ]
        db.add_all(roles)
        await db.flush()

        # === Адреса ===
        addr1 = Address(
            user_id=client1.id,
            city="Шахтёрск",
            district="Шахтёрск + посёлки",
            street="ул. Ленина",
            house="15, кв. 3",
            is_default=True,
        )
        addr2 = Address(
            user_id=client1.id,
            city="Шахтёрск",
            district="Шахтёрск + посёлки",
            street="ул. Мира",
            house="42",
            is_default=False,
        )
        addr3 = Address(
            user_id=client2.id,
            city="Зугрэс",
            district="Зугрэс",
            street="пр. Победы",
            house="7, кв. 12",
            is_default=True,
        )
        db.add_all([addr1, addr2, addr3])
        await db.flush()

        # === Заказы ===
        now = datetime.now()
        orders = [
            Order(
                user_id=client1.id,
                address_id=addr1.id,
                jv_qty=3,
                lv_qty=2,
                total_qty=5,
                delivery_date=today + timedelta(days=1),
                status=OrderStatus.new,
                comment="Позвонить за час до доставки",
                created_at=now - timedelta(hours=1),
            ),
            Order(
                user_id=client1.id,
                address_id=addr1.id,
                jv_qty=5,
                lv_qty=0,
                total_qty=5,
                delivery_date=today - timedelta(days=3),
                status=OrderStatus.completed,
                created_at=now - timedelta(days=4),
                confirmed_at=now - timedelta(days=4, hours=-2),
                operator_id=operator1.id,
            ),
            Order(
                user_id=client2.id,
                address_id=addr3.id,
                jv_qty=2,
                lv_qty=2,
                total_qty=4,
                delivery_date=today,
                status=OrderStatus.confirmed,
                created_at=now - timedelta(days=1),
                confirmed_at=now - timedelta(hours=20),
                operator_id=operator1.id,
            ),
            Order(
                user_id=client1.id,
                address_id=addr2.id,
                jv_qty=1,
                lv_qty=1,
                total_qty=2,
                delivery_date=today - timedelta(days=7),
                status=OrderStatus.cancelled,
                comment="Клиент отменил",
                created_at=now - timedelta(days=8),
            ),
            Order(
                user_id=client2.id,
                address_id=addr3.id,
                jv_qty=4,
                lv_qty=1,
                total_qty=5,
                delivery_date=today - timedelta(days=10),
                status=OrderStatus.completed,
                created_at=now - timedelta(days=11),
                confirmed_at=now - timedelta(days=11, hours=-3),
                operator_id=operator1.id,
            ),
        ]
        db.add_all(orders)
        await db.commit()

        print("Тестовые данные успешно загружены!")
        print(f"  Клиенты: {client1.name}, {client2.name}")
        print(f"  Оператор: {operator1.name}")
        print(f"  Админ: {admin1.name}")
        print(f"  Районы: {len(districts)}")
        print(f"  Праздники: {len(holidays)}")
        print(f"  Адреса: 3")
        print(f"  Заказы: {len(orders)}")


if __name__ == "__main__":
    asyncio.run(seed_database())
