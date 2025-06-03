from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions    import IsAuthenticated
from rest_framework.response       import Response
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Team, TeamDailyContribution
from users.models import DailyContribution  # still needed for create_team signal logic

User = get_user_model()

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_team(request):
    """
    POST /api/teams/create/  (body: {"name": "my_team", "members": ["alice", "bob"]})
    Creates a new Team, adds request.user + any valid usernames.
    """
    name = request.data.get("name")
    members = request.data.get("members", [])

    if not name:
        return Response({"detail": "Missing team name"}, status=400)
    if Team.objects.filter(name=name).exists():
        return Response({"detail": "Team already exists"}, status=400)

    team = Team.objects.create(name=name)
    team.members.add(request.user)

    for username in members:
        try:
            user = User.objects.get(username=username)
            team.members.add(user)
        except User.DoesNotExist:
            continue

    return Response({"team": team.name}, status=201)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def team_leaderboard(request, team_name):
    """
    GET /api/teams/<team_name>/leaderboard/
    Returns [{"username": "...", "xp": ...}, …] from TeamDailyContribution for today.
    """
    try:
        team = Team.objects.get(name=team_name)
    except Team.DoesNotExist:
        return Response({"detail": "Team not found."}, status=404)

    if not team.members.filter(id=request.user.id).exists():
        return Response({"detail": "Not a member of this team."}, status=403)

    today = timezone.localdate()
    qs = (
        TeamDailyContribution.objects
          .filter(date=today, team=team)
          .select_related("user")
    )
    entries = [{"username": dc.user.username, "xp": dc.xp} for dc in qs]
    entries.sort(key=lambda e: e["xp"], reverse=True)
    return Response(entries)


def compute_daily_xp_leaderboard_for_team(team_name: str):
    """
    Returns a Python list [{"username": "...", "xp": ...}, …]
    for today’s XP inside this team.
    """
    from .models import TeamDailyContribution

    today = timezone.localdate()
    try:
        team = Team.objects.get(name=team_name)
    except Team.DoesNotExist:
        return []

    qs = (
        TeamDailyContribution.objects
          .filter(date=today, team=team)
          .select_related("user")
    )
    entries = [{"username": dc.user.username, "xp": dc.xp} for dc in qs]
    entries.sort(key=lambda e: e["xp"], reverse=True)
    return entries
