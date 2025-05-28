from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import GitHubLoginAPIView, me, my_contributions, my_streak

urlpatterns = [
    path('auth/github/', GitHubLoginAPIView.as_view(), name='github-login'),
    path('users/me/', me, name='users-me'),
    path('auth/refresh/',    TokenRefreshView.as_view(),  name='token-refresh'),
    path('users/contrib/', my_contributions, name='users-contrib'),
    path('users/streak/', my_streak, name='users-streak'),

]
