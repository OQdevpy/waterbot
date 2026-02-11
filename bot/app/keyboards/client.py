from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def main_menu_keyboard(is_registered: bool = True) -> ReplyKeyboardMarkup:
    if not is_registered:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📝 Оформить заказ")],
            ],
            resize_keyboard=True,
        )

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📝 Новый заказ"),
                KeyboardButton(text="🔄 Повторить заказ"),
            ],
            [
                KeyboardButton(text="✏️ Редактировать заказ"),
                KeyboardButton(text="📊 Статус заказа"),
            ],
            [
                KeyboardButton(text="📍 Мои адреса"),
                KeyboardButton(text="📋 История заказов"),
            ],
        ],
        resize_keyboard=True,
    )


def phone_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Отправить номер", request_contact=True)],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
    )


def skip_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏭ Пропустить")],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def confirm_order_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data="order_confirm"),
                InlineKeyboardButton(text="❌ Отменить", callback_data="order_cancel"),
            ],
        ]
    )


def addresses_keyboard(addresses: list) -> InlineKeyboardMarkup:
    buttons = []
    for addr in addresses:
        text = f"📍 {addr['city']}, {addr['street']}, {addr['house']}"
        if addr.get("is_default"):
            text = f"⭐ {text}"
        buttons.append(
            [InlineKeyboardButton(text=text, callback_data=f"addr_{addr['id']}")]
        )
    buttons.append(
        [InlineKeyboardButton(text="➕ Новый адрес", callback_data="addr_new")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def districts_keyboard(districts: list) -> InlineKeyboardMarkup:
    buttons = []
    for d in districts:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=d["district"],
                    callback_data=f"district_{d['district']}",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def order_history_keyboard(orders: list, offset: int = 0) -> InlineKeyboardMarkup:
    buttons = []
    for o in orders:
        status_emoji = {
            "new": "🆕",
            "confirmed": "✅",
            "rescheduled": "📅",
            "in_delivery": "🚚",
            "completed": "✔️",
            "cancelled": "❌",
        }.get(o["status"], "❓")
        text = f"{status_emoji} №{o['id']} | ЖВ:{o['jv_qty']} ЛВ:{o['lv_qty']} | {o['delivery_date'] or '—'}"
        buttons.append(
            [InlineKeyboardButton(text=text, callback_data=f"order_view_{o['id']}")]
        )

    nav = []
    if offset > 0:
        nav.append(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"history_offset_{offset - 20}")
        )
    if len(orders) == 20:
        nav.append(
            InlineKeyboardButton(text="➡️ Далее", callback_data=f"history_offset_{offset + 20}")
        )
    if nav:
        buttons.append(nav)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def edit_order_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💧 ЖВ", callback_data="edit_jv"),
                InlineKeyboardButton(text="💧 ЛВ", callback_data="edit_lv"),
            ],
            [
                InlineKeyboardButton(text="💬 Комментарий", callback_data="edit_comment"),
            ],
            [
                InlineKeyboardButton(text="❌ Отмена", callback_data="edit_cancel"),
            ],
        ]
    )
