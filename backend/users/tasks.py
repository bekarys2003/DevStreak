from asgiref.sync     import async_to_sync
from channels.layers  import get_channel_layer
from celery           import shared_task
from django.core.cache import cache
from .views           import compute_daily_commits, compute_streak_leaderboard
from users.views import compute_streak_leaderboard

CACHE_KEY_STREAK = 'streak_leaderboard'
CACHE_KEY_COMMITS  = 'daily_commits_leaderboard'

@shared_task
def broadcast_daily_commits_task():
    data = compute_daily_commits()
    # 1) broadcast over WebSocket
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        "daily_commits",
        {"type": "daily_commits_update", "data": data}
    )

    # 2) cache the REST‐fallback leaderboard for 15 min
    cache.set(CACHE_KEY_COMMITS, data, timeout=15 * 60)

    return f"Broadcasted {len(data)} entries"

@shared_task(name='broadcast_streak_leaderboard_task')
def broadcast_streak_leaderboard_task():
    entries = compute_streak_leaderboard()
    layer   = get_channel_layer()
    async_to_sync(layer.group_send)(
        'streak_leaderboard',
        {'type': 'streak_leaderboard_update', 'data': entries}
    )
    cache.set(CACHE_KEY_STREAK, entries, timeout=15*60)
    return f'Broadcasted {len(entries)} streak entries'
