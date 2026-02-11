"""Форматирование сообщений для бота."""


def format_order_info(order: dict, address: dict | None = None) -> str:
    """Форматирование информации о заказе."""
    status_map = {
        "new": "🆕 Новый",
        "confirmed": "✅ Подтверждён",
        "rescheduled": "📅 Перенесён",
        "in_delivery": "🚚 В доставке",
        "completed": "✔️ Выполнен",
        "cancelled": "❌ Отменён",
        "draft": "📝 Черновик",
        "payment_pending": "💳 Ожидание оплаты",
        "paid": "💰 Оплачен",
    }

    status = status_map.get(order.get("status", ""), order.get("status", ""))

    lines = [
        f"<b>Заказ №{order['id']}</b>",
        f"Статус: {status}",
        f"💧 ЖВ: {order['jv_qty']} | ЛВ: {order['lv_qty']} | Всего: {order['total_qty']}",
        f"📅 Дата доставки: {order.get('delivery_date') or '—'}",
    ]

    if address:
        lines.append(
            f"📍 {address.get('city', '')}, {address.get('district', '')}, "
            f"{address.get('street', '')}, {address.get('house', '')}"
        )

    if order.get("comment"):
        lines.append(f"💬 {order['comment']}")

    lines.append(f"🕐 Создан: {order.get('created_at', '')[:16]}")

    return "\n".join(lines)


def format_order_for_operator(order: dict, user: dict = None) -> str:
    """Форматирование заказа для оператора."""
    lines = [
        f"📦 <b>Заказ №{order['id']}</b>",
    ]

    if user:
        client_type = "Постоянный" if user.get("phone") else "Новый"
        lines.append(f"👤 {user.get('name', '—')} ({client_type})")
        lines.append(f"📱 {user.get('phone', '—')}")

    lines.extend([
        f"💧 ЖВ: {order['jv_qty']} | ЛВ: {order['lv_qty']} | Всего: {order['total_qty']}",
        f"📅 Предложенная дата: {order.get('delivery_date') or '—'}",
    ])

    if order.get("comment"):
        lines.append(f"💬 {order['comment']}")

    return "\n".join(lines)


def format_address(address: dict) -> str:
    """Форматирование адреса."""
    default = "⭐ " if address.get("is_default") else ""
    return (
        f"{default}{address['city']}, {address['district']}, "
        f"{address['street']}, {address['house']}"
    )
