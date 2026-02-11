from datetime import date, timedelta

import pytest
import pytest_asyncio

from app.services.delivery_date_service import (
    calculate_nearest_delivery_date,
    is_weekend,
)


def test_is_weekend():
    # Понедельник
    monday = date(2025, 1, 6)
    assert not is_weekend(monday)

    # Суббота
    saturday = date(2025, 1, 4)
    assert is_weekend(saturday)

    # Воскресенье
    sunday = date(2025, 1, 5)
    assert is_weekend(sunday)


@pytest.mark.asyncio
async def test_calculate_nearest_delivery_date_basic(db_session):
    """Тест: базовый расчёт даты."""
    # Стартуем с понедельника
    start = date(2025, 1, 6)
    result = await calculate_nearest_delivery_date(
        db_session, "Шахтёрск + посёлки", 5, start_date=start
    )
    assert result["delivery_date"] == start
    assert result["district_remaining"] == 135
    assert result["total_remaining"] == 326


@pytest.mark.asyncio
async def test_skip_weekends(db_session):
    """Тест: пропуск выходных."""
    # Стартуем с субботы
    saturday = date(2025, 1, 4)
    result = await calculate_nearest_delivery_date(
        db_session, "Зугрэс", 10, start_date=saturday
    )
    # Должен перескочить на понедельник
    assert result["delivery_date"] == date(2025, 1, 6)


@pytest.mark.asyncio
async def test_skip_holidays(db_session):
    """Тест: пропуск праздников."""
    new_year = date(2025, 1, 1)  # Среда
    result = await calculate_nearest_delivery_date(
        db_session, "Торез", 5, start_date=new_year
    )
    # 1 января — праздник, 2 января — следующий рабочий день
    assert result["delivery_date"] == date(2025, 1, 2)


@pytest.mark.asyncio
async def test_unknown_district_uses_default(db_session):
    """Тест: неизвестный район использует лимит «Прочие»."""
    start = date(2025, 1, 6)
    result = await calculate_nearest_delivery_date(
        db_session, "Неизвестный район", 5, start_date=start
    )
    assert result["delivery_date"] == start
    assert result["district_remaining"] == 86  # 91 - 5
