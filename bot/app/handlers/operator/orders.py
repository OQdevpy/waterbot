"""Операторская часть: управление заказами."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.keyboards.operator import operator_menu_keyboard, order_actions_keyboard
from app.keyboards.client import cancel_keyboard
from app.services.api_client import api_client
from app.states.order_states import RescheduleStates
from app.utils.formatters import format_order_for_operator

router = Router()


@router.message(F.text == "📋 Новые заказы")
async def list_new_orders(message: Message):
    orders = await api_client.get_new_orders()

    if not orders:
        await message.answer(
            "Нет новых заказов.",
            reply_markup=operator_menu_keyboard(),
        )
        return

    for order in orders:
        text = format_order_for_operator(order)
        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=order_actions_keyboard(order["id"]),
        )


# === Подтвердить ===
@router.callback_query(F.data.startswith("op_confirm_"))
async def confirm_order(callback: CallbackQuery):
    order_id = int(callback.data.replace("op_confirm_", ""))
    result = await api_client.confirm_order(order_id, callback.from_user.id)

    if isinstance(result, dict) and "error" in result:
        await callback.answer(f"Ошибка: {result['error']}", show_alert=True)
        return

    await callback.message.edit_text(
        callback.message.text + "\n\n✅ <b>ПОДТВЕРЖДЁН</b>",
        parse_mode="HTML",
    )
    await callback.answer("Заказ подтверждён!")


# === Отменить ===
@router.callback_query(F.data.startswith("op_cancel_"))
async def cancel_order(callback: CallbackQuery):
    order_id = int(callback.data.replace("op_cancel_", ""))
    result = await api_client.cancel_order(order_id, "Отменён оператором")

    if isinstance(result, dict) and "error" in result:
        await callback.answer(f"Ошибка: {result['error']}", show_alert=True)
        return

    await callback.message.edit_text(
        callback.message.text + "\n\n❌ <b>ОТМЕНЁН</b>",
        parse_mode="HTML",
    )
    await callback.answer("Заказ отменён!")


# === Перенести дату ===
@router.callback_query(F.data.startswith("op_reschedule_"))
async def reschedule_start(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.replace("op_reschedule_", ""))
    await state.update_data(reschedule_order_id=order_id)
    await callback.message.answer(
        "📅 Введите новую дату доставки (ГГГГ-ММ-ДД):",
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(RescheduleStates.enter_date)
    await callback.answer()


@router.message(RescheduleStates.enter_date)
async def reschedule_date(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Отменено.", reply_markup=operator_menu_keyboard())
        return

    date_str = message.text.strip()

    # Валидация даты
    from datetime import datetime
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        await message.answer("❌ Неверный формат. Введите дату в формате ГГГГ-ММ-ДД:")
        return

    data = await state.get_data()
    order_id = data["reschedule_order_id"]

    result = await api_client.reschedule_order(order_id, date_str, "Перенесён оператором")
    await state.clear()

    if isinstance(result, dict) and "error" in result:
        await message.answer(f"❌ {result['error']}", reply_markup=operator_menu_keyboard())
    else:
        await message.answer(
            f"📅 Дата заказа №{order_id} перенесена на {date_str}",
            reply_markup=operator_menu_keyboard(),
        )


# === В доставку ===
@router.callback_query(F.data.startswith("op_deliver_"))
async def deliver_order(callback: CallbackQuery):
    order_id = int(callback.data.replace("op_deliver_", ""))
    result = await api_client.start_delivery(order_id)

    if isinstance(result, dict) and "error" in result:
        await callback.answer(f"Ошибка: {result['error']}", show_alert=True)
        return

    await callback.message.edit_text(
        callback.message.text + "\n\n🚚 <b>В ДОСТАВКЕ</b>",
        parse_mode="HTML",
    )
    await callback.answer("Заказ отправлен в доставку!")


# === Выполнен ===
@router.callback_query(F.data.startswith("op_complete_"))
async def complete_order(callback: CallbackQuery):
    order_id = int(callback.data.replace("op_complete_", ""))
    result = await api_client.complete_order(order_id)

    if isinstance(result, dict) and "error" in result:
        await callback.answer(f"Ошибка: {result['error']}", show_alert=True)
        return

    await callback.message.edit_text(
        callback.message.text + "\n\n✔️ <b>ВЫПОЛНЕН</b>",
        parse_mode="HTML",
    )
    await callback.answer("Заказ выполнен!")


# === Связаться с клиентом ===
@router.callback_query(F.data.startswith("op_contact_"))
async def contact_client(callback: CallbackQuery):
    order_id = int(callback.data.replace("op_contact_", ""))
    order = await api_client.get_order(order_id)

    if not order:
        await callback.answer("Заказ не найден", show_alert=True)
        return

    user = await api_client.get_user(order.get("user_id", 0))
    # Получаем историю клиента
    history = await api_client.get_client_history(order["user_id"], limit=5)

    text = f"📞 <b>Информация о клиенте:</b>\n\n"
    if user:
        text += f"👤 {user.get('name', '—')}\n📱 {user.get('phone', '—')}\n\n"

    if history:
        text += "<b>Последние заказы:</b>\n"
        for h in history:
            text += f"  №{h['id']} | {h.get('delivery_date', '—')} | {h['total_qty']} бут. | {h['status']}\n"

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()
