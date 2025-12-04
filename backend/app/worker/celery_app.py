from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.task_routes = {
    "app.worker.tasks.generate_morning_report": "main-queue",
    "app.worker.tasks.fetch_stock_prices": "main-queue",
}

celery_app.conf.beat_schedule = {
    "fetch-prices-every-minute": {
        "task": "app.worker.tasks.fetch_stock_prices",
        "schedule": 60.0, # Every 60 seconds
        "args": (["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],)
    },
}

celery_app.conf.update(task_track_started=True)

