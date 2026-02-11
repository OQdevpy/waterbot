from pydantic_settings import BaseSettings
from functools import lru_cache


class BotSettings(BaseSettings):
    BOT_TOKEN: str = "8085038360:AAFnO_9KBCVWzhNcMiFo-AST85edWZlW9m4"
    BACKEND_URL: str = "http://backend:8000"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_bot_settings() -> BotSettings:
    return BotSettings()
