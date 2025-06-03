# teams/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from users.models import DailyContribution
from .models import Team, TeamDailyContribution

@receiver(post_save, sender=DailyContribution)
def broadcast_and_record_team_xp(sender, instance, **kwargs):
    """
    Whenever any DailyContribution is saved (created or updated),
    copy that XP into TeamDailyContribution for each team the user belongs to,
    then send a "team_xp_update" event on that team’s channel group so any
    open WebSocket consumers will re‐fetch the new XP.
    """
    user = instance.user
    today = timezone.localdate()
    layer = get_channel_layer()

    # 1) For each team this user belongs to, upsert TeamDailyContribution:
    for team in user.teams.all():
        # Create or update the team‐scoped row
        tdc, created = TeamDailyContribution.objects.get_or_create(
            team=team,
            user=user,
            date=today,
            defaults={"xp": instance.xp},
        )
        if not created:
            # If it already existed, just overwrite xp
            tdc.xp = instance.xp
            tdc.save()

        # 2) Broadcast a "team_xp_update" event to the group named "team_<team_name>"
        group_name = f"team_{team.name}"
        async_to_sync(layer.group_send)(
            group_name,
            {"type": "team_xp_update"},
        )
