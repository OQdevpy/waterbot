"""Rate-limit middleware."""

from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

import time


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 0.5):
        self.rate_limit = rate_limit
        self._cache: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id
        now = time.time()
        last = self._cache.get(user_id, 0)

        if now - last < self.rate_limit:
            return  # Игнорируем слишком частые сообщения

        self._cache[user_id] = now
        return await handler(event, data)
