from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import GitHubLoginAPIView, me

urlpatterns = [
    path('auth/github/', GitHubLoginAPIView.as_view(), name='github-login'),
    path('users/me/', me, name='users-me'),
    path('auth/refresh/',    TokenRefreshView.as_view(),  name='token-refresh'),
]
