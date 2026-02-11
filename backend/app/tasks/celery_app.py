from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "water_delivery",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Периодические задачи
celery_app.conf.beat_schedule = {
    "check-stale-orders-reminder": {
        "task": "app.tasks.notification_tasks.send_reminder_for_stale_orders",
        "schedule": crontab(minute="*/30"),  # каждые 30 минут
    },
    "auto-cancel-old-orders": {
        "task": "app.tasks.auto_cancel_tasks.auto_cancel_stale_orders",
        "schedule": crontab(minute="*/15"),  # каждые 15 минут
    },
}

celery_app.autodiscover_tasks(["app.tasks"])
