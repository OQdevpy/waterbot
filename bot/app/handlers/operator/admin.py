"""Админ-команды."""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.operator import operator_menu_keyboard
from app.services.api_client import api_client

router = Router()


@router.message(Command("operator"))
async def cmd_operator(message: Message, db_user: dict | None):
    """Переключение в операторский режим."""
    if not db_user:
        await message.answer("Вы не зарегистрированы.")
        return

    # Проверяем роль через backend (упрощённо — по наличию пользователя)
    await message.answer(
        "⚙️ <b>Панель оператора</b>\n\n"
        "Выберите действие:",
        parse_mode="HTML",
        reply_markup=operator_menu_keyboard(),
    )


@router.message(F.text == "⚙️ Управление районами")
async def manage_districts(message: Message):
    districts = await api_client.get_districts()

    if not districts:
        await message.answer("Нет данных о районах.")
        return

    text = "🏘 <b>Районы и лимиты:</b>\n\n"
    for d in districts:
        status = "✅" if d.get("is_active") else "❌"
        text += f"{status} {d['district']}: {d['max_per_day']} бут./день\n"

    await message.answer(text, parse_mode="HTML")
