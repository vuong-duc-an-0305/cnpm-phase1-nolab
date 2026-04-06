"""
Celery configuration for BE_coffee project
Phase 3: Background tasks for async report generation
"""
import os
from celery import Celery
from decouple import config

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BE_coffee.settings')

# Create Celery app
app = Celery('BE_coffee')

# Configure Celery using settings from Django settings.py with 'CELERY_' prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Redis broker configuration
REDIS_HOST = config('REDIS_HOST', default='localhost')
REDIS_PORT = config('REDIS_PORT', default='6379')
REDIS_DB = config('REDIS_DB', default='0')

app.conf.broker_url = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
app.conf.result_backend = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# Additional Celery settings
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Ho_Chi_Minh',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f'Request: {self.request!r}')
