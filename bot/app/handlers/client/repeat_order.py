"""Повторить последний успешный заказ."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.keyboards.client import (
    confirm_order_keyboard,
    main_menu_keyboard,
    skip_keyboard,
)
from app.services.api_client import api_client
from app.states.order_states import NewOrderStates
from app.utils.formatters import format_order_info

router = Router()


@router.message(F.text == "🔄 Повторить заказ")
async def repeat_order(message: Message, state: FSMContext, db_user: dict | None):
    if not db_user:
        await message.answer("Сначала зарегистрируйтесь: /start")
        return

    last = await api_client.get_last_completed(message.from_user.id)
    if not last:
        await message.answer(
            "У вас нет выполненных заказов для повторения.",
            reply_markup=main_menu_keyboard(),
        )
        return

    await state.update_data(
        address_id=last["address_id"],
        jv_qty=last["jv_qty"],
        lv_qty=last["lv_qty"],
    )

    await message.answer(
        f"🔄 <b>Повторение последнего заказа:</b>\n\n"
        f"💧 ЖВ: {last['jv_qty']} | ЛВ: {last['lv_qty']}\n\n"
        f"💬 Добавьте комментарий (или «Пропустить»):",
        parse_mode="HTML",
        reply_markup=skip_keyboard(),
    )
    await state.set_state(NewOrderStates.enter_comment)
