"""Редактирование текущего неподтверждённого заказа."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.keyboards.client import edit_order_keyboard, main_menu_keyboard, cancel_keyboard
from app.services.api_client import api_client
from app.states.order_states import EditOrderStates
from app.utils.formatters import format_order_info

router = Router()


@router.message(F.text == "✏️ Редактировать заказ")
async def edit_order_start(message: Message, state: FSMContext, db_user: dict | None):
    if not db_user:
        await message.answer("Сначала зарегистрируйтесь: /start")
        return

    active = await api_client.get_active_order(message.from_user.id)
    if not active:
        await message.answer(
            "У вас нет активного заказа для редактирования.",
            reply_markup=main_menu_keyboard(),
        )
        return

    if active["status"] != "new":
        await message.answer(
            "Редактировать можно только заказ в статусе «Новый».",
            reply_markup=main_menu_keyboard(),
        )
        return

    await state.update_data(order_id=active["id"])

    info = format_order_info(active)
    await message.answer(
        f"{info}\n\n✏️ Что хотите изменить?",
        parse_mode="HTML",
        reply_markup=edit_order_keyboard(),
    )
    await state.set_state(EditOrderStates.select_field)


@router.callback_query(EditOrderStates.select_field, F.data == "edit_jv")
async def edit_jv(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Введите новое количество <b>ЖВ</b>:",
        parse_mode="HTML",
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(EditOrderStates.enter_jv_qty)
    await callback.answer()


@router.callback_query(EditOrderStates.select_field, F.data == "edit_lv")
async def edit_lv(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Введите новое количество <b>ЛВ</b>:",
        parse_mode="HTML",
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(EditOrderStates.enter_lv_qty)
    await callback.answer()


@router.callback_query(EditOrderStates.select_field, F.data == "edit_comment")
async def edit_comment_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Введите новый <b>комментарий</b>:",
        parse_mode="HTML",
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(EditOrderStates.enter_comment)
    await callback.answer()


@router.callback_query(EditOrderStates.select_field, F.data == "edit_cancel")
async def edit_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "Редактирование отменено.",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()


@router.message(EditOrderStates.enter_jv_qty)
async def process_edit_jv(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Отменено.", reply_markup=main_menu_keyboard())
        return

    try:
        qty = int(message.text.strip())
        if qty < 0:
            raise ValueError
    except ValueError:
        await message.answer("Введите корректное число:")
        return

    data = await state.get_data()
    result = await api_client.update_order(data["order_id"], jv_qty=qty)
    await state.clear()

    if isinstance(result, dict) and "error" in result:
        await message.answer(f"❌ {result['error']}", reply_markup=main_menu_keyboard())
    else:
        await message.answer(
            f"✅ ЖВ обновлено. Новая дата: {result.get('delivery_date', '—')}",
            reply_markup=main_menu_keyboard(),
        )


@router.message(EditOrderStates.enter_lv_qty)
async def process_edit_lv(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Отменено.", reply_markup=main_menu_keyboard())
        return

    try:
        qty = int(message.text.strip())
        if qty < 0:
            raise ValueError
    except ValueError:
        await message.answer("Введите корректное число:")
        return

    data = await state.get_data()
    result = await api_client.update_order(data["order_id"], lv_qty=qty)
    await state.clear()

    if isinstance(result, dict) and "error" in result:
        await message.answer(f"❌ {result['error']}", reply_markup=main_menu_keyboard())
    else:
        await message.answer(
            f"✅ ЛВ обновлено. Новая дата: {result.get('delivery_date', '—')}",
            reply_markup=main_menu_keyboard(),
        )


@router.message(EditOrderStates.enter_comment)
async def process_edit_comment(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Отменено.", reply_markup=main_menu_keyboard())
        return

    data = await state.get_data()
    result = await api_client.update_order(data["order_id"], comment=message.text.strip())
    await state.clear()

    if isinstance(result, dict) and "error" in result:
        await message.answer(f"❌ {result['error']}", reply_markup=main_menu_keyboard())
    else:
        await message.answer("✅ Комментарий обновлён.", reply_markup=main_menu_keyboard())
