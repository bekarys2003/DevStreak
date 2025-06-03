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
    # ← Add this print at the top to verify the signal is firing:
    print(f"[teams.signals] post_save fired: user={instance.user.username}, xp={instance.xp}")

    user = instance.user
    today = timezone.localdate()
    layer = get_channel_layer()

    for team in user.teams.all():
        tdc, created = TeamDailyContribution.objects.get_or_create(
            team=team,
            user=user,
            date=today,
            defaults={"xp": instance.xp},
        )
        if not created:
            tdc.xp = instance.xp
            tdc.save()

        group_name = f"team_{team.name}"
        async_to_sync(layer.group_send)(
            group_name,
            {"type": "team_xp_update"},
        )
