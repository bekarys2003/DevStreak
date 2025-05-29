from django.urls import re_path
from .consumers import DailyCommitsConsumer

websocket_urlpatterns = [
    re_path(r'ws/daily-commits/$', DailyCommitsConsumer.as_asgi()),
]