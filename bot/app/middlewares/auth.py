"""Middleware для проверки авторизации."""

from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from app.services.api_client import api_client


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any],
    ) -> Any:
        telegram_id = event.from_user.id
        user = await api_client.get_user(telegram_id)
        data["db_user"] = user
        return await handler(event, data)
