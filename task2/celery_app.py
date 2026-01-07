from celery import Celery
from celery.schedules import crontab
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery(
    "task2",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["task2.tasks"]
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    broker_connection_retry_on_startup=True,
)

# Automatical launch every 5 minutes
app.conf.beat_schedule = {
    "fetch-users-every-5-minutes": {
        "task": "task2.tasks.fetch_and_save_users",
        "schedule": crontab(minute="*/5"),
    },
}