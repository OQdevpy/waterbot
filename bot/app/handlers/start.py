"""Обработчик /start и регистрация."""

import re

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards.client import main_menu_keyboard, phone_keyboard, cancel_keyboard
from app.services.api_client import api_client
from app.states.order_states import RegistrationStates

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext, db_user: dict | None):
    await state.clear()

    if db_user:
        await message.answer(
            f"👋 Добро пожаловать, <b>{db_user['name']}</b>!\n\n"
            f"Выберите действие:",
            reply_markup=main_menu_keyboard(is_registered=True),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            "👋 Добро пожаловать в службу доставки воды!\n\n"
            "Для оформления заказа необходимо зарегистрироваться.\n"
            "Введите ваше <b>ФИО</b>:",
            parse_mode="HTML",
            reply_markup=cancel_keyboard(),
        )
        await state.set_state(RegistrationStates.name)


@router.message(RegistrationStates.name)
async def process_name(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "Регистрация отменена.",
            reply_markup=main_menu_keyboard(is_registered=False),
        )
        return

    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Пожалуйста, введите корректное ФИО (минимум 2 символа):")
        return

    await state.update_data(name=name)
    await message.answer(
        "📱 Отправьте ваш номер телефона (кнопкой ниже или вручную):",
        reply_markup=phone_keyboard(),
    )
    await state.set_state(RegistrationStates.phone)


@router.message(RegistrationStates.phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = f"+{phone}"
    await _complete_registration(message, state, phone)


@router.message(RegistrationStates.phone)
async def process_phone_text(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "Регистрация отменена.",
            reply_markup=main_menu_keyboard(is_registered=False),
        )
        return

    phone = message.text.strip()
    # Простая валидация
    phone_clean = re.sub(r"[\s\-\(\)]", "", phone)
    if not re.match(r"^\+?\d{10,15}$", phone_clean):
        await message.answer(
            "❌ Некорректный номер. Введите номер в формате +79001234567:"
        )
        return

    if not phone_clean.startswith("+"):
        phone_clean = f"+{phone_clean}"

    await _complete_registration(message, state, phone_clean)


async def _complete_registration(message: Message, state: FSMContext, phone: str):
    data = await state.get_data()
    name = data["name"]
    telegram_id = message.from_user.id

    result = await api_client.register_user(telegram_id, name, phone)

    if result and "error" in result:
        await message.answer(f"❌ Ошибка регистрации: {result['error']}")
        return

    await state.clear()
    await message.answer(
        f"✅ Регистрация завершена!\n\n"
        f"👤 {name}\n📱 {phone}\n\n"
        f"Теперь вы можете оформить заказ.",
        reply_markup=main_menu_keyboard(is_registered=True),
        parse_mode="HTML",
    )
