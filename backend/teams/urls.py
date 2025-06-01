# teams/urls.py

from django.urls import path
from .views import create_team, team_leaderboard

urlpatterns = [
    path("create/", create_team, name="teams-create"),
    path("<str:team_name>/leaderboard/", team_leaderboard, name="teams-leaderboard"),
]
