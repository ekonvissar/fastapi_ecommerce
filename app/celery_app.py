from celery import Celery

from app.config import settings

celery = Celery(
    "fastapi_ecommerce",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    broker_connection_retry_on_startup=True,
    include=["app.task"],
)

celery.conf.beat_schedule = {
    "run-me-background-task": {
        "task": "app.task.call_background_task",
        "schedule": 60.0,
        "args": ("Test text message",),
    }
}
