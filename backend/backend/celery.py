import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

# 1) Broker: Redis in our compose network
app.conf.broker_url = 'redis://redis:6379/0'

# 2) (Optional) If you have Celery-specific settings in Django settings.py:
app.config_from_object('django.conf:settings', namespace='CELERY')

# 3) Auto-discover tasks in your apps
app.autodiscover_tasks()

# 4) Beat schedule to broadcast every 15 minutes
app.conf.beat_schedule = {
    'broadcast-daily-commits-every-15-minutes': {
        'task': 'users.tasks.broadcast_daily_commits_task',
        'schedule': crontab(minute='*/15'),
    },
}
