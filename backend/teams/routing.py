from django.urls import re_path
from .consumers import TeamXPConsumer

websocket_urlpatterns = [
    # 1) Match "/ws/team-xp/" (no <team_name>) so connect() sees team_name=None and rejects
    re_path(r"^ws/team\-xp/$", TeamXPConsumer.as_asgi()),

    # 2) Match "/ws/team-xp/<team_name>/"
    re_path(
        r"^ws/team\-xp/(?P<team_name>[A-Za-z0-9_-]+)/$",
        TeamXPConsumer.as_asgi(),
    ),
]
