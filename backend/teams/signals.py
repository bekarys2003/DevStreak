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
    → REMOVE (or COMMENT OUT) the code that blindly copies instance.xp into TeamDailyContribution.
      Instead, we’ll simply broadcast an update on each affected team so that clients re-fetch their
      team XP when the user’s global xp changes—but we will no longer automatically overwrite team xp.
    """
    user = instance.user
    today = timezone.localdate()
    layer = get_channel_layer()

    # We still want to broadcast so clients re-fetch, but we do NOT want to copy global→team:
    for team in user.teams.all():
        # If you no longer want any automated copying at all, comment out the next block:
        #
        # tdc, created = TeamDailyContribution.objects.get_or_create(
        #     team=team,
        #     user=user,
        #     date=today,
        #     defaults={"xp": instance.xp},
        # )
        # if not created:
        #     # previously: tdc.xp = instance.xp; tdc.save()
        #     pass

        # Broadcast a "team_xp_update" so that connected WebSocket consumers will fetch
        # the (now‐separate) team xp from the database.
        group_name = f"team_{team.name}"
        async_to_sync(layer.group_send)(
            group_name,
            {"type": "team_xp_update"},
        )
