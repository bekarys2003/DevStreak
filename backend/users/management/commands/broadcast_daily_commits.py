from django.core.management.base import BaseCommand
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from core.github_api import GitHubAPIClient
from users.models import GitHubProfile
from datetime import datetime, timedelta, timezone

class Command(BaseCommand):
    help = 'Broadcast the daily commits leaderboard to all WebSocket clients.'

    def handle(self, *args, **options):
        entries = []
        today = datetime.now(timezone.utc).date()

        for profile in GitHubProfile.objects.select_related('user').all():
            client = GitHubAPIClient(profile.access_token)
            data = client.fetch_user_daily_contributions(profile.user.username)
            entries.append({
                'username': profile.user.username,
                'commits': data['commits'],
            })

        # sort descending by commits
        entries.sort(key=lambda e: e['commits'], reverse=True)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'daily_commits',
            {
                'type': 'daily_commits_update',
                'data': entries
            }
        )
        self.stdout.write(self.style.SUCCESS('Broadcasted daily commits leaderboard.'))