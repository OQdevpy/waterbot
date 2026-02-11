"""HTTP-клиент для взаимодействия с backend API."""

import logging
from typing import Any

import aiohttp

from app.config import get_bot_settings

logger = logging.getLogger(__name__)
settings = get_bot_settings()

BASE_URL = f"{settings.BACKEND_URL}/api/v1"


class ApiClient:
    def __init__(self):
        self._session: aiohttp.ClientSession | None = None

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(
        self, method: str, path: str, **kwargs
    ) -> dict | list | None:
        session = await self.get_session()
        url = f"{BASE_URL}{path}"
        try:
            async with session.request(method, url, **kwargs) as resp:
                if resp.status == 204:
                    return None
                data = await resp.json()
                if resp.status >= 400:
                    logger.error(f"API error {resp.status}: {data}")
                    return {"error": data.get("detail", "Ошибка сервера")}
                return data
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return {"error": str(e)}

    # === Пользователи ===
    async def get_user(self, telegram_id: int) -> dict | None:
        result = await self._request("GET", f"/users/tg/{telegram_id}")
        if result and "error" in result:
            return None
        return result

    async def register_user(self, telegram_id: int, name: str, phone: str) -> dict:
        return await self._request(
            "POST",
            "/users/",
            json={"telegram_id": telegram_id, "name": name, "phone": phone},
        )

    async def update_user(self, telegram_id: int, **kwargs) -> dict:
        return await self._request(
            "PATCH", f"/users/tg/{telegram_id}", json=kwargs
        )

    # === Адреса ===
    async def get_addresses(self, telegram_id: int) -> list:
        result = await self._request("GET", f"/addresses/user/{telegram_id}")
        if isinstance(result, dict) and "error" in result:
            return []
        return result or []

    async def add_address(self, telegram_id: int, **kwargs) -> dict:
        return await self._request(
            "POST", f"/addresses/user/{telegram_id}", json=kwargs
        )

    async def delete_address(self, address_id: int) -> None:
        await self._request("DELETE", f"/addresses/{address_id}")

    async def set_default_address(self, address_id: int) -> dict:
        return await self._request("POST", f"/addresses/{address_id}/default")

    # === Заказы ===
    async def create_order(
        self, telegram_id: int, address_id: int, jv_qty: int, lv_qty: int,
        comment: str | None = None,
    ) -> dict:
        data = {
            "address_id": address_id,
            "jv_qty": jv_qty,
            "lv_qty": lv_qty,
        }
        if comment:
            data["comment"] = comment
        return await self._request(
            "POST", f"/orders/user/{telegram_id}", json=data
        )

    async def get_orders(
        self, telegram_id: int, limit: int = 20, offset: int = 0
    ) -> dict:
        return await self._request(
            "GET",
            f"/orders/user/{telegram_id}",
            params={"limit": limit, "offset": offset},
        )

    async def get_active_order(self, telegram_id: int) -> dict | None:
        result = await self._request("GET", f"/orders/user/{telegram_id}/active")
        if result and "error" in result:
            return None
        return result

    async def get_last_completed(self, telegram_id: int) -> dict | None:
        result = await self._request(
            "GET", f"/orders/user/{telegram_id}/last-completed"
        )
        if result and "error" in result:
            return None
        return result

    async def get_order(self, order_id: int) -> dict | None:
        result = await self._request("GET", f"/orders/{order_id}")
        if result and "error" in result:
            return None
        return result

    async def update_order(self, order_id: int, **kwargs) -> dict:
        return await self._request("PATCH", f"/orders/{order_id}", json=kwargs)

    # === Оператор ===
    async def get_new_orders(self) -> list:
        result = await self._request("GET", "/operator/orders/new")
        if isinstance(result, dict) and "error" in result:
            return []
        return result or []

    async def confirm_order(self, order_id: int, operator_tg_id: int) -> dict:
        return await self._request(
            "POST",
            f"/operator/orders/{order_id}/confirm",
            params={"operator_telegram_id": operator_tg_id},
        )

    async def cancel_order(self, order_id: int, comment: str = "") -> dict:
        return await self._request(
            "POST",
            f"/operator/orders/{order_id}/cancel",
            json={"status": "cancelled", "comment": comment},
        )

    async def reschedule_order(
        self, order_id: int, delivery_date: str, comment: str = ""
    ) -> dict:
        return await self._request(
            "POST",
            f"/operator/orders/{order_id}/reschedule",
            json={
                "status": "rescheduled",
                "delivery_date": delivery_date,
                "comment": comment,
            },
        )

    async def complete_order(self, order_id: int) -> dict:
        return await self._request(
            "POST", f"/operator/orders/{order_id}/complete"
        )

    async def start_delivery(self, order_id: int) -> dict:
        return await self._request(
            "POST", f"/operator/orders/{order_id}/deliver"
        )

    async def get_client_history(self, user_id: int, limit: int = 5) -> list:
        result = await self._request(
            "GET", f"/operator/client/{user_id}/history", params={"limit": limit}
        )
        if isinstance(result, dict) and "error" in result:
            return []
        return result or []

    # === Районы ===
    async def get_districts(self) -> list:
        result = await self._request("GET", "/districts/")
        if isinstance(result, dict) and "error" in result:
            return []
        return result or []

    async def calculate_date(self, district: str, qty: int) -> dict | None:
        result = await self._request(
            "GET",
            "/districts/calculate-date",
            params={"district": district, "qty": qty},
        )
        if result and "error" in result:
            return None
        return result


api_client = ApiClient()
