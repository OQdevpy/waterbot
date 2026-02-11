import asyncio
import logging

import httpx

from app.tasks.celery_app import celery_app
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

BOT_API = f"https://api.telegram.org/bot{settings.BOT_TOKEN}"


def send_telegram_message(chat_id: int, text: str, reply_markup: dict | None = None):
    """Отправить сообщение через Telegram Bot API."""
    if not settings.BOT_TOKEN:
        logger.warning("BOT_TOKEN не настроен, пропуск отправки")
        return

    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        import json
        payload["reply_markup"] = json.dumps(reply_markup)

    try:
        resp = httpx.post(f"{BOT_API}/sendMessage", json=payload, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"Ошибка отправки в Telegram: {e}")


@celery_app.task(name="app.tasks.notification_tasks.notify_operators_new_order")
def notify_operators_new_order(order_id: int, order_info: str, operator_ids: list[int]):
    """Уведомить операторов о новом заказе."""
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Подтвердить", "callback_data": f"confirm_{order_id}"},
                {"text": "❌ Отменить", "callback_data": f"cancel_{order_id}"},
            ],
            [
                {"text": "📅 Перенести", "callback_data": f"reschedule_{order_id}"},
            ],
        ]
    }

    text = f"🆕 <b>Новый заказ №{order_id}</b>\n\n{order_info}"

    for op_id in operator_ids:
        send_telegram_message(op_id, text, keyboard)


@celery_app.task(name="app.tasks.notification_tasks.notify_client")
def notify_client(chat_id: int, text: str):
    """Отправить уведомление клиенту."""
    send_telegram_message(chat_id, text)


@celery_app.task(name="app.tasks.notification_tasks.send_reminder_for_stale_orders")
def send_reminder_for_stale_orders():
    """Повторное уведомление операторам через 2 часа."""
    from app.database import async_session
    from app.services.order_service import get_stale_orders
    from app.services.user_service import get_operators

    async def _run():
        async with async_session() as db:
            stale = await get_stale_orders(db, hours=settings.ORDER_REMINDER_HOURS)
            if not stale:
                return
            operators = await get_operators(db)
            op_tg_ids = [op.telegram_id for op in operators]

            for order in stale:
                text = (
                    f"⏰ <b>Напоминание!</b>\n"
                    f"Заказ №{order.id} ожидает подтверждения уже более 2 часов."
                )
                for op_id in op_tg_ids:
                    send_telegram_message(op_id, text)

    asyncio.run(_run())
