import pytest

from app.schemas.order import OrderCreate


def test_order_create_validation():
    """Тест: валидация минимального количества."""
    with pytest.raises(ValueError):
        OrderCreate(address_id=1, jv_qty=0, lv_qty=0)


def test_order_create_valid():
    """Тест: валидный заказ."""
    order = OrderCreate(address_id=1, jv_qty=3, lv_qty=2)
    assert order.jv_qty == 3
    assert order.lv_qty == 2


def test_order_create_jv_only():
    """Тест: только ЖВ."""
    order = OrderCreate(address_id=1, jv_qty=5, lv_qty=0)
    assert order.jv_qty == 5


def test_order_create_lv_only():
    """Тест: только ЛВ."""
    order = OrderCreate(address_id=1, jv_qty=0, lv_qty=3)
    assert order.lv_qty == 3
