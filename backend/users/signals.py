from django.db.models.signals import post_save
from django.dispatch         import receiver
from asgiref.sync            import async_to_sync
from channels.layers         import get_channel_layer

from .models import DailyContribution
from .models import GitHubProfile
from .views    import compute_daily_commits
from .tasks    import CACHE_KEY_COMMITS

@receiver(post_save, sender=DailyContribution)
def broadcast_single_commit_update(sender, instance, **kwargs):
    """
    Whenever a DailyContribution is created or updated, push that user's new count
    to all WebSocket clients listening on 'daily_commits'.
    """
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        "daily_commits",
        {
            "type": "daily_commits_update",
            "data": [{
                "username": instance.user.username,
                "commits":  instance.commit_count,
            }]
        }
    )
    board = compute_daily_commits()
    cache.set(CACHE_KEY_COMMITS, board, timeout=15 * 60)


@receiver(post_save, sender=GitHubProfile)
def record_today_commits(sender, instance, **kwargs):
    """
    Hook that runs after a GitHubProfile is saved.
    For example, immediately recompute & cache today’s leaderboard.
    """
    # e.g. prime the cache so celery beat tasks have fresh data
    data = compute_daily_commits()
    # store into cache if you like:
    from django.core.cache import cache
    cache.set('daily_commits_leaderboard', data, timeout=15 * 60)


@receiver(post_save, sender=DailyContribution)
def broadcast_single_commit_update(sender, instance, **kwargs):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        "daily_commits",
        {
            "type": "daily_commits_update",
            "data": [{
                "username": instance.user.username,
                "commits":  instance.commit_count,
            }]
        }
    )