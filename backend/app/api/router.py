from fastapi import APIRouter

from app.api.users import router as users_router
from app.api.addresses import router as addresses_router
from app.api.orders import router as orders_router
from app.api.districts import router as districts_router
from app.api.operator import router as operator_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(users_router, prefix="/users", tags=["Пользователи"])
api_router.include_router(addresses_router, prefix="/addresses", tags=["Адреса"])
api_router.include_router(orders_router, prefix="/orders", tags=["Заказы"])
api_router.include_router(districts_router, prefix="/districts", tags=["Районы"])
api_router.include_router(operator_router, prefix="/operator", tags=["Оператор"])
