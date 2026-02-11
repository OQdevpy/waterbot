"""Управление адресами клиента."""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.keyboards.client import main_menu_keyboard, cancel_keyboard, addresses_keyboard
from app.services.api_client import api_client
from app.states.order_states import AddAddressStates
from app.utils.formatters import format_address

router = Router()


@router.message(F.text == "📍 Мои адреса")
async def my_addresses(message: Message, db_user: dict | None):
    if not db_user:
        await message.answer("Сначала зарегистрируйтесь: /start")
        return

    addresses = await api_client.get_addresses(message.from_user.id)

    if not addresses:
        await message.answer(
            "У вас нет сохранённых адресов.\n"
            "Они будут добавлены при оформлении заказа.",
            reply_markup=main_menu_keyboard(),
        )
        return

    text = "📍 <b>Ваши адреса:</b>\n\n"
    for i, addr in enumerate(addresses, 1):
        text += f"{i}. {format_address(addr)}\n"

    text += "\nНажмите на адрес для действий:"

    buttons = []
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    for addr in addresses:
        default = "⭐ " if addr.get("is_default") else ""
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{default}{addr['city']}, {addr['street']}",
                    callback_data=f"manage_addr_{addr['id']}",
                ),
            ]
        )

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )


@router.callback_query(F.data.startswith("manage_addr_"))
async def manage_address(callback: CallbackQuery):
    address_id = int(callback.data.replace("manage_addr_", ""))

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⭐ Сделать основным",
                    callback_data=f"setdefault_{address_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"deladdr_{address_id}",
                ),
            ],
        ]
    )

    await callback.message.answer("Выберите действие:", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("setdefault_"))
async def set_default(callback: CallbackQuery):
    address_id = int(callback.data.replace("setdefault_", ""))
    await api_client.set_default_address(address_id)
    await callback.message.answer(
        "⭐ Адрес установлен как основной.",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("deladdr_"))
async def delete_addr(callback: CallbackQuery):
    address_id = int(callback.data.replace("deladdr_", ""))
    await api_client.delete_address(address_id)
    await callback.message.answer(
        "🗑 Адрес удалён.",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()
