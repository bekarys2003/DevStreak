import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
app = Celery('backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.timezone = 'America/Vancouver'   # add this if not already set
app.conf.enable_utc = True

# schedule both broadcasts every 15′
app.conf.beat_schedule = {
    'broadcast-daily-commits-every-15-minutes': {
        'task': 'users.tasks.broadcast_daily_commits_task',
        'schedule': crontab(minute='*/15'),
    },
    'broadcast-streak-leaderboard-every-15-minutes': {
        'task': 'users.tasks.broadcast_streak_leaderboard_task',
        'schedule': crontab(minute='*/15'),
    },
    'fetch-and-record-commits-every-15-minutes': {
        'task': 'users.tasks.fetch_and_record_commits',
        'schedule': crontab(minute='*/15'),
    },
    'broadcast-midnight-xp-reset': {
        'task': 'users.tasks.broadcast_daily_commits_task',
        # midnight *in the timezone above*
        'schedule': crontab(minute=0, hour=0),
    },
}
