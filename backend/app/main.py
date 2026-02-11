from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine, Base
from app.api.router import api_router


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: создаём таблицы и заполняем fixtures
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from app.fixtures.seed import seed_database
    await seed_database()

    yield

    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="WaterDeliveryBot API",
    description="API для управления заказами доставки воды",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
