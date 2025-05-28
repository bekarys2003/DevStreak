from django.urls import path
from .views import GitHubLoginAPIView

urlpatterns = [
    path('auth/github/', GitHubLoginAPIView.as_view(), name='github-login'),
]
