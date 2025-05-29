# users/tasks.py
from asgiref.sync    import async_to_sync
from channels.layers import get_channel_layer
from celery          import shared_task
from users.views     import compute_daily_commits

@shared_task
def broadcast_daily_commits_task():
    data = compute_daily_commits()
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        "daily_commits",
        {"type": "daily_commits_update", "data": data}
    )
    return f"Broadcasted {len(data)} entries"
