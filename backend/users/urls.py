from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import GitHubLoginAPIView, me, my_contributions, my_streak, leaderboard, streak_leaderboard, github_push_webhook

urlpatterns = [
    path('auth/github/', GitHubLoginAPIView.as_view(), name='github-login'),
    path('users/me/', me, name='users-me'),
    path('auth/refresh/',    TokenRefreshView.as_view(),  name='token-refresh'),
    path('users/contrib/', my_contributions, name='users-contrib'),
    path('users/streak/', my_streak, name='users-streak'),
    path('users/leaderboard/', leaderboard,   name='users-leaderboard'),
    path('users/streak-lb/', streak_leaderboard, name='users-streak-leaderboard'),
    path("webhooks/github/", github_push_webhook, name="github-push-webhook"),
]
