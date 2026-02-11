from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def operator_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📋 Новые заказы"),
                KeyboardButton(text="📊 Все заказы"),
            ],
            [
                KeyboardButton(text="⚙️ Управление районами"),
            ],
        ],
        resize_keyboard=True,
    )


def order_actions_keyboard(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить", callback_data=f"op_confirm_{order_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Отменить", callback_data=f"op_cancel_{order_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📅 Перенести дату",
                    callback_data=f"op_reschedule_{order_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🚚 В доставку",
                    callback_data=f"op_deliver_{order_id}",
                ),
                InlineKeyboardButton(
                    text="✔️ Выполнен",
                    callback_data=f"op_complete_{order_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📞 Связаться с клиентом",
                    callback_data=f"op_contact_{order_id}",
                ),
            ],
        ]
    )
