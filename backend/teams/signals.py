# teams/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from users.models import DailyContribution
from .models import Team

@receiver(post_save, sender=DailyContribution)
def broadcast_team_xp_update(sender, instance, **kwargs):
    """
    Whenever a DailyContribution is created/updated,
    push that user's new XP to each team they belong to.
    """
    layer = get_channel_layer()
    user = instance.user

    for team in user.teams.all():
        # 1) Broadcast into the same group that TeamXPConsumer joined:
        group_name = f"team_{team.name}"

        # 2) Use event type "team_xp_update" (so consumer.team_xp_update(...) is called)
        async_to_sync(layer.group_send)(
            group_name,
            {"type": "team_xp_update"}
        )
