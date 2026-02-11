"""История заказов и статус текущего заказа."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from app.keyboards.client import main_menu_keyboard, order_history_keyboard
from app.services.api_client import api_client
from app.utils.formatters import format_order_info

router = Router()


@router.message(F.text == "📋 История заказов")
async def order_history(message: Message, db_user: dict | None):
    if not db_user:
        await message.answer("Сначала зарегистрируйтесь: /start")
        return

    result = await api_client.get_orders(message.from_user.id, limit=20, offset=0)

    if not result or not result.get("orders"):
        await message.answer(
            "У вас пока нет заказов.",
            reply_markup=main_menu_keyboard(),
        )
        return

    orders = result["orders"]
    total = result["total"]

    await message.answer(
        f"📋 <b>История заказов</b> ({total} всего):\n\n"
        f"Нажмите на заказ для подробностей:",
        parse_mode="HTML",
        reply_markup=order_history_keyboard(orders, offset=0),
    )


@router.callback_query(F.data.startswith("history_offset_"))
async def history_page(callback: CallbackQuery):
    offset = int(callback.data.replace("history_offset_", ""))
    telegram_id = callback.from_user.id

    result = await api_client.get_orders(telegram_id, limit=20, offset=offset)
    if not result or not result.get("orders"):
        await callback.answer("Нет больше заказов")
        return

    orders = result["orders"]

    await callback.message.edit_reply_markup(
        reply_markup=order_history_keyboard(orders, offset=offset)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("order_view_"))
async def view_order(callback: CallbackQuery):
    order_id = int(callback.data.replace("order_view_", ""))
    order = await api_client.get_order(order_id)

    if not order:
        await callback.answer("Заказ не найден")
        return

    await callback.message.answer(
        format_order_info(order),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(F.text == "📊 Статус заказа")
async def order_status(message: Message, db_user: dict | None):
    if not db_user:
        await message.answer("Сначала зарегистрируйтесь: /start")
        return

    active = await api_client.get_active_order(message.from_user.id)

    if not active:
        await message.answer(
            "У вас нет активного заказа.",
            reply_markup=main_menu_keyboard(),
        )
        return

    await message.answer(
        format_order_info(active),
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )
