# teams/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from users.models import DailyContribution
from .models import Team, TeamDailyContribution
from django.utils import timezone

@receiver(post_save, sender=DailyContribution)
def broadcast_and_record_team_xp(sender, instance, created, **kwargs):
    """
    Whenever a global DailyContribution is created/updated, we:
      1) Copy (or increment) that XP into each TeamDailyContribution
         row for that user in each team they belong to.
      2) Broadcast a 'team_xp_update' event for each team so WebSocket
         consumers can re-fetch the team leaderboard.
    """
    user = instance.user
    today = timezone.localdate()
    layer = get_channel_layer()

    # 1) For every team the user belongs to, update that team's daily XP row
    for team in user.teams.all():
        # If a row already exists for (team, user, today), update it.
        # Otherwise create it fresh.
        tdc, _ = TeamDailyContribution.objects.get_or_create(
            team=team,
            user=user,
            date=today,
            defaults={"xp": instance.xp},
        )
        if not _:
            # Already existed → just set xp to the global daily xp (or add, depending on your logic)
            tdc.xp = instance.xp
            tdc.save()

        # 2) Broadcast to the group "team_<team_name>" using event type "team_xp_update"
        group_name = f"team_{team.name}"
        async_to_sync(layer.group_send)(
            group_name,
            {"type": "team_xp_update"}
        )
