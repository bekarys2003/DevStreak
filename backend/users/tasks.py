from asgiref.sync     import async_to_sync
from channels.layers  import get_channel_layer
from celery           import shared_task
from django.core.cache import cache
from .views           import compute_daily_xp_leaderboard, compute_streak_leaderboard
from .models import GitHubProfile, DailyContribution
from core.github_api import GitHubAPIClient
from .services        import record_today_xp
from datetime import date

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



@shared_task
def fetch_and_record_commits():
    today = date.today()
    for profile in GitHubProfile.objects.select_related("user"):
        # 1) Fetch GitHub’s authoritative total for today
        data    = GitHubAPIClient(profile.access_token) \
                     .fetch_user_daily_contributions_local(
                         profile.user.username,
                         local_tz="America/Vancouver"
                     )
        total   = data.get("commits", 0)

        # 2) Load (or create) today’s record
        dc, created = DailyContribution.objects.get_or_create(
            user=profile.user,
            date=today,
            defaults={'commit_count': total, 'xp': total * 2}
        )

        if not created:
            # 3) Compute how many new commits we need to award
            old_commits = dc.commit_count
            delta_commits = total - old_commits

            if delta_commits > 0:
                # 4) Award only the difference
                record_today_xp(
                    profile.user,
                    xp_delta=delta_commits * 2,
                    commit_delta=delta_commits
                )
