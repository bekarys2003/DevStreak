from django.urls import path
from .views import GitHubLoginAPIView, me

urlpatterns = [
    path('auth/github/', GitHubLoginAPIView.as_view(), name='github-login'),
    path('users/me/', me, name='users-me'),
]
