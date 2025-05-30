from asgiref.sync     import async_to_sync
from channels.layers  import get_channel_layer
from celery           import shared_task
from django.core.cache import cache
from .views           import compute_daily_xp_leaderboard, compute_streak_leaderboard
from .models import GitHubProfile
from core.github_api import GitHubAPIClient
from .services        import record_today_xp

CACHE_KEY_STREAK = 'streak_leaderboard'
CACHE_KEY_COMMITS  = 'daily_commits_leaderboard'

@shared_task
def broadcast_daily_commits_task():
    data = compute_daily_xp_leaderboard()
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


# users/tasks.py


@shared_task
def fetch_and_record_commits():
    for profile in GitHubProfile.objects.select_related("user"):
        data    = GitHubAPIClient(profile.access_token) \
                    .fetch_user_daily_contributions_local(
                        profile.user.username,
                        local_tz="America/Vancouver"
                    )
        commits = data.get("commits", 0)
        if commits:
            # LOGGING—add this temporarily
            print(f"[XP SYNC] {profile.user.username}: +{commits*2} XP, +{commits} commits")

            record_today_xp(
                profile.user,
                xp_delta=commits * 2,
                commit_delta=commits,
            )