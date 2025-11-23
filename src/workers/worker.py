"""Celery worker configuration."""

import sys
from pathlib import Path

from celery import Celery

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.config import settings  # noqa: E402

# Create Celery application
app = Celery(
    "gadget4_simulations",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["workers.tasks"],
)

# Configure Celery
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.max_simulation_time,
    task_soft_time_limit=settings.max_simulation_time - 60,
    worker_prefetch_multiplier=1,  # One task at a time for long-running simulations
    worker_max_tasks_per_child=5,  # Restart worker after 5 tasks to prevent memory leaks
)

if __name__ == "__main__":
    app.start()
