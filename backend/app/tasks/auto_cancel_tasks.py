import asyncio
import logging

from app.tasks.celery_app import celery_app
from app.tasks.notification_tasks import send_telegram_message
from app.config import get_settings
from app.services.sheets_service import sync_order_to_sheet, prepare_order_data

logger = logging.getLogger(__name__)
settings = get_settings()


@celery_app.task(name="app.tasks.auto_cancel_tasks.auto_cancel_stale_orders")
def auto_cancel_stale_orders():
    """Автоматическая отмена заказов старше 24 часов в статусе new."""
    from app.database import async_session
    from app.services.order_service import get_stale_orders, update_order_status
    from app.models.order import OrderStatus

    async def _run():
        async with async_session() as db:
            stale = await get_stale_orders(
                db, hours=settings.ORDER_AUTO_CANCEL_HOURS
            )
            for order in stale:
                await update_order_status(
                    db,
                    order,
                    OrderStatus.cancelled,
                    comment="Автоматическая отмена: нет подтверждения в течение 24 часов",
                )

                # Уведомить клиента
                if order.user:
                    send_telegram_message(
                        order.user.telegram_id,
                        f"❌ Ваш заказ №{order.id} был автоматически отменён, "
                        f"так как не был подтверждён оператором в течение 24 часов.\n"
                        f"Пожалуйста, оформите новый заказ.",
                    )

                # Синхронизация с Google Sheets
                data = prepare_order_data(order, order.user, order.address)
                sync_order_to_sheet(data)

            await db.commit()

    asyncio.run(_run())
