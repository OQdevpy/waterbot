"""Точка запуска Telegram-бота."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from app.config import get_bot_settings
from app.middlewares.auth import AuthMiddleware
from app.middlewares.throttling import ThrottlingMiddleware
from app.handlers.start import router as start_router
from app.handlers.client.new_order import router as new_order_router
from app.handlers.client.repeat_order import router as repeat_order_router
from app.handlers.client.edit_order import router as edit_order_router
from app.handlers.client.addresses import router as addresses_router
from app.handlers.client.history import router as history_router
from app.handlers.operator.orders import router as operator_orders_router
from app.handlers.operator.admin import router as admin_router
from app.services.api_client import api_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    settings = get_bot_settings()

    if not settings.BOT_TOKEN:
        logger.error("BOT_TOKEN не указан! Укажите в .env")
        return

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    redis_client = Redis.from_url(settings.redis_url)
    storage = RedisStorage(redis=redis_client)
    dp = Dispatcher(storage=storage)

    # Middleware — throttling первым, потом auth
    dp.message.middleware(ThrottlingMiddleware(rate_limit=0.5))
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    # Handlers — порядок важен
    dp.include_router(start_router)
    dp.include_router(new_order_router)
    dp.include_router(repeat_order_router)
    dp.include_router(edit_order_router)
    dp.include_router(addresses_router)
    dp.include_router(history_router)
    dp.include_router(operator_orders_router)
    dp.include_router(admin_router)

    logger.info("Бот запускается...")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await api_client.close()
        await redis_client.aclose()
        await bot.session.close()
        logger.info("Бот остановлен.")


if __name__ == "__main__":
    asyncio.run(main())
