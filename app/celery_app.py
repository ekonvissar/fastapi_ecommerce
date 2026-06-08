from celery import Celery

from app.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery = Celery(
    "fastapi_ecommerce",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
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
