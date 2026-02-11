from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # База данных
    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_USER: str = "water_user"
    DB_PASS: str = "water_pass"
    DB_NAME: str = "water_db"

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    # Telegram
    BOT_TOKEN: str = ""
    ADMIN_CHAT_ID: int = 0

    # Google Sheets
    GOOGLE_SHEETS_CREDENTIALS: str = ""
    GOOGLE_SHEET_ID: str = ""

    # Приложение
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True

    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"

    # Бизнес-логика
    ORDER_CUTOFF_HOUR: int = 17  # после 17:00 — только на завтра
    ORDER_AUTO_CANCEL_HOURS: int = 24
    ORDER_REMINDER_HOURS: int = 2
    DUPLICATE_ORDER_MINUTES: int = 10

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
