# teams/urls.py

from django.urls import path
from .views import create_team, team_leaderboard
from .api import add_xp_to_team

urlpatterns = [
    path("create/", create_team, name="teams-create"),
    path("<str:team_name>/leaderboard/", team_leaderboard, name="teams-leaderboard"),
    path("<str:team_name>/add-xp/", add_xp_to_team, name="teams-add-xp"),

]
