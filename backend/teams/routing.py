# teams/routing.py

from django.urls import re_path
from .consumers import TeamXPConsumer

websocket_urlpatterns = [
    # 1) catch “/ws/team-xp/” exactly (no <team_name>)
    re_path(
        r"^ws/team\-xp/$",
        TeamXPConsumer.as_asgi(),
    ),

    # 2) catch “/ws/team-xp/<team_name>/”
    re_path(
        r"^ws/team\-xp/(?P<team_name>[A-Za-z0-9_-]+)/$",
        TeamXPConsumer.as_asgi(),
    ),
]
