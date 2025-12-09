from celery import Celery
from celery.schedules import crontab
import os

# Initialize Celery
celery_app = Celery(
    "lean_construction",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    'morning-health-check': {
        'task': 'app.tasks.data_ingestion.morning_project_health_check',
        'schedule': crontab(hour=6, minute=0),  # 6 AM daily
    },
    'continuous-waste-detection': {
        'task': 'app.tasks.data_ingestion.detect_waste_patterns',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'progress-tracking': {
        'task': 'app.tasks.data_ingestion.update_project_progress',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    'weekly-analysis': {
        'task': 'app.tasks.analytics.weekly_strategic_analysis',
        'schedule': crontab(day_of_week=1, hour=7, minute=0),  # Monday 7 AM
    },
}

# Auto-discover tasks
celery_app.autodiscover_tasks(['app.tasks'])
