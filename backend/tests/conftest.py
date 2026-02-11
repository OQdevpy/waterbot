import asyncio
from datetime import date

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.database import Base
from app.models.district import DistrictLimit
from app.models.holiday import Holiday


TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_maker() as session:
        # Заполнить базовые данные для тестов
        districts = [
            DistrictLimit(district="Шахтёрск + посёлки", max_per_day=140, is_active=True),
            DistrictLimit(district="Зугрэс", max_per_day=50, is_active=True),
            DistrictLimit(district="Торез", max_per_day=50, is_active=True),
            DistrictLimit(district="Прочие", max_per_day=91, is_active=True),
        ]
        session.add_all(districts)

        holidays = [
            Holiday(date=date(2025, 1, 1), description="Новый год"),
        ]
        session.add_all(holidays)
        await session.commit()

        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
