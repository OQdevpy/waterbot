"""FSM для оформления нового заказа."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.keyboards.client import (
    addresses_keyboard,
    districts_keyboard,
    cancel_keyboard,
    skip_keyboard,
    confirm_order_keyboard,
    main_menu_keyboard,
)
from app.services.api_client import api_client
from app.states.order_states import NewOrderStates

router = Router()


@router.message(F.text == "📝 Новый заказ")
@router.message(F.text == "📝 Оформить заказ")
async def start_new_order(message: Message, state: FSMContext, db_user: dict | None):
    if not db_user:
        await message.answer(
            "Сначала зарегистрируйтесь: /start"
        )
        return

    await state.clear()
    addresses = await api_client.get_addresses(message.from_user.id)

    if addresses:
        await message.answer(
            "📍 Выберите адрес доставки или добавьте новый:",
            reply_markup=addresses_keyboard(addresses),
        )
        await state.set_state(NewOrderStates.select_address)
    else:
        await message.answer(
            "📍 У вас нет сохранённых адресов.\nВведите <b>город</b>:",
            parse_mode="HTML",
            reply_markup=cancel_keyboard(),
        )
        await state.set_state(NewOrderStates.enter_city)


@router.callback_query(NewOrderStates.select_address, F.data.startswith("addr_"))
async def select_address(callback: CallbackQuery, state: FSMContext):
    data = callback.data

    if data == "addr_new":
        await callback.message.answer(
            "📍 Введите <b>город</b>:",
            parse_mode="HTML",
            reply_markup=cancel_keyboard(),
        )
        await state.set_state(NewOrderStates.enter_city)
    else:
        address_id = int(data.replace("addr_", ""))
        await state.update_data(address_id=address_id)
        await callback.message.answer(
            "💧 Введите количество <b>ЖВ</b> (живая вода, 19л).\n"
            "Введите число (0 если не нужно):",
            parse_mode="HTML",
            reply_markup=cancel_keyboard(),
        )
        await state.set_state(NewOrderStates.enter_jv_qty)

    await callback.answer()


# === Ввод нового адреса ===

@router.message(NewOrderStates.enter_city)
async def enter_city(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Заказ отменён.", reply_markup=main_menu_keyboard())
        return

    await state.update_data(city=message.text.strip())

    districts = await api_client.get_districts()
    if districts:
        await message.answer(
            "🏘 Выберите <b>район</b>:",
            parse_mode="HTML",
            reply_markup=districts_keyboard(districts),
        )
    else:
        await message.answer(
            "🏘 Введите <b>район</b>:",
            parse_mode="HTML",
            reply_markup=cancel_keyboard(),
        )
    await state.set_state(NewOrderStates.enter_district)


@router.callback_query(NewOrderStates.enter_district, F.data.startswith("district_"))
async def select_district(callback: CallbackQuery, state: FSMContext):
    district = callback.data.replace("district_", "")
    await state.update_data(district=district)
    await callback.message.answer(
        "🏠 Введите <b>улицу</b>:",
        parse_mode="HTML",
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(NewOrderStates.enter_street)
    await callback.answer()


@router.message(NewOrderStates.enter_district)
async def enter_district_text(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Заказ отменён.", reply_markup=main_menu_keyboard())
        return

    await state.update_data(district=message.text.strip())
    await message.answer(
        "🏠 Введите <b>улицу</b>:",
        parse_mode="HTML",
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(NewOrderStates.enter_street)


@router.message(NewOrderStates.enter_street)
async def enter_street(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Заказ отменён.", reply_markup=main_menu_keyboard())
        return

    await state.update_data(street=message.text.strip())
    await message.answer(
        "🏢 Введите <b>дом / квартиру</b>:",
        parse_mode="HTML",
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(NewOrderStates.enter_house)


@router.message(NewOrderStates.enter_house)
async def enter_house(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Заказ отменён.", reply_markup=main_menu_keyboard())
        return

    await state.update_data(house=message.text.strip())

    # Создать адрес через API
    data = await state.get_data()
    result = await api_client.add_address(
        message.from_user.id,
        city=data["city"],
        district=data["district"],
        street=data["street"],
        house=data["house"],
    )

    if isinstance(result, dict) and "error" in result:
        await message.answer(f"❌ Ошибка: {result['error']}")
        await state.clear()
        return

    await state.update_data(address_id=result["id"])
    await message.answer(
        "💧 Введите количество <b>ЖВ</b> (живая вода, 19л).\n"
        "Введите число (0 если не нужно):",
        parse_mode="HTML",
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(NewOrderStates.enter_jv_qty)


# === Количество ===

@router.message(NewOrderStates.enter_jv_qty)
async def enter_jv_qty(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Заказ отменён.", reply_markup=main_menu_keyboard())
        return

    try:
        qty = int(message.text.strip())
        if qty < 0:
            raise ValueError
    except ValueError:
        await message.answer("Введите корректное число (0 или больше):")
        return

    await state.update_data(jv_qty=qty)
    await message.answer(
        "💧 Введите количество <b>ЛВ</b> (лечебная вода, 19л).\n"
        "Введите число (0 если не нужно):",
        parse_mode="HTML",
        reply_markup=cancel_keyboard(),
    )
    await state.set_state(NewOrderStates.enter_lv_qty)


@router.message(NewOrderStates.enter_lv_qty)
async def enter_lv_qty(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Заказ отменён.", reply_markup=main_menu_keyboard())
        return

    try:
        qty = int(message.text.strip())
        if qty < 0:
            raise ValueError
    except ValueError:
        await message.answer("Введите корректное число (0 или больше):")
        return

    data = await state.get_data()
    jv_qty = data.get("jv_qty", 0)

    if jv_qty + qty < 1:
        await message.answer("❌ Общее количество (ЖВ + ЛВ) должно быть минимум 1. Введите ЛВ:")
        return

    await state.update_data(lv_qty=qty)
    await message.answer(
        "💬 Добавьте <b>комментарий</b> к заказу (или нажмите «Пропустить»):",
        parse_mode="HTML",
        reply_markup=skip_keyboard(),
    )
    await state.set_state(NewOrderStates.enter_comment)


@router.message(NewOrderStates.enter_comment)
async def enter_comment(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Заказ отменён.", reply_markup=main_menu_keyboard())
        return

    comment = None if message.text == "⏭ Пропустить" else message.text.strip()
    await state.update_data(comment=comment)

    data = await state.get_data()
    summary = (
        f"📋 <b>Подтвердите заказ:</b>\n\n"
        f"💧 ЖВ: {data['jv_qty']}\n"
        f"💧 ЛВ: {data['lv_qty']}\n"
        f"📦 Всего: {data['jv_qty'] + data['lv_qty']}\n"
    )
    if comment:
        summary += f"💬 Комментарий: {comment}\n"

    await message.answer(summary, parse_mode="HTML", reply_markup=confirm_order_keyboard())
    await state.set_state(NewOrderStates.confirm)


@router.callback_query(NewOrderStates.confirm, F.data == "order_confirm")
async def confirm_new_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    result = await api_client.create_order(
        callback.from_user.id,
        address_id=data["address_id"],
        jv_qty=data["jv_qty"],
        lv_qty=data["lv_qty"],
        comment=data.get("comment"),
    )

    await state.clear()

    if isinstance(result, dict) and "error" in result:
        await callback.message.answer(
            f"❌ Ошибка: {result['error']}",
            reply_markup=main_menu_keyboard(),
        )
    else:
        await callback.message.answer(
            f"✅ <b>Ваш заказ №{result['id']} принят!</b>\n\n"
            f"📅 Предварительная дата доставки: <b>{result.get('delivery_date', '—')}</b>\n"
            f"💧 ЖВ: {result['jv_qty']} | ЛВ: {result['lv_qty']}\n\n"
            f"Оператор свяжется с вами для подтверждения.",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )

    await callback.answer()


@router.callback_query(NewOrderStates.confirm, F.data == "order_cancel")
async def cancel_new_order(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "❌ Заказ отменён.", reply_markup=main_menu_keyboard()
    )
    await callback.answer()
