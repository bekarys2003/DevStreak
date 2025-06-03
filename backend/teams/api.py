# teams/api.py  (new file)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Team, TeamDailyContribution

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_xp_to_team(request, team_name):
    """
    POST /api/teams/<team_name>/add-xp/
    Body: {"delta": 3}
    Increments the requesting user's TeamDailyContribution.xp by `delta` for today.
    """
    delta = request.data.get("delta", 0)
    if not isinstance(delta, int):
        return Response({"detail": "Invalid delta"}, status=400)

    today = timezone.localdate()
    team = get_object_or_404(Team, name=team_name)

    # Ensure the user is a member of this team:
    if not team.members.filter(pk=request.user.id).exists():
        return Response({"detail": "Not a member of this team."}, status=403)

    # Upsert (team, user, today):
    tdc, created = TeamDailyContribution.objects.get_or_create(
        team=team,
        user=request.user,
        date=today,
        defaults={"xp": delta},
    )
    if not created:
        tdc.xp += delta
        tdc.save()

    # Broadcast the change so WebSocket clients re-fetch:
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer

    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        f"team_{team.name}",
        {"type": "team_xp_update"},
    )

    return Response({"xp": tdc.xp}, status=200)
