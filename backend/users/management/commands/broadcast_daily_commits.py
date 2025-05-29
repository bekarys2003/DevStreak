# backend/users/management/commands/broadcast_daily_commits.py

from django.core.management.base import BaseCommand
from asgiref.sync       import async_to_sync
from channels.layers    import get_channel_layer
from users.views        import compute_daily_commits

class Command(BaseCommand):
    help = "Broadcast today's commits leaderboard to WebSocket clients"

    def handle(self, *args, **options):
        leaderboard = compute_daily_commits()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "daily_commits",
            {
                "type": "daily_commits_update",
                "data": leaderboard,
            }
        )
        self.stdout.write(self.style.SUCCESS(
            f"Broadcasted {len(leaderboard)} entries: {leaderboard}"
        ))
