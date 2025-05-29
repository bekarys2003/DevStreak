# backend/users/tests/test_streak_api.py

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from users.models import GitHubProfile
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch
from datetime import datetime, timedelta, timezone

User = get_user_model()

class StreakEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username="alice", email="a@example.com")
        self.user2 = User.objects.create_user(username="bob",   email="b@example.com")
        GitHubProfile.objects.create(user=self.user1, access_token="token-alice")
        GitHubProfile.objects.create(user=self.user2, access_token="token-bob")

        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    @patch('users.views.GitHubAPIClient.fetch_user_contribution_calendar')
    def test_streak_endpoint_returns_user_streak(self, mock_fetch):
        # Build a 4-day streak ending today in UTC
        today = datetime.now(timezone.utc).date()
        dates = [
            today - timedelta(days=i)
            for i in range(0, 5)  # today, yesterday, ... 4 days ago
        ]
        # counts: [1,1,1,1,0] => streak of 4
        mock_fetch.return_value = [
            {"date": dates[0].isoformat(), "count": 1},
            {"date": dates[1].isoformat(), "count": 1},
            {"date": dates[2].isoformat(), "count": 1},
            {"date": dates[3].isoformat(), "count": 1},
            {"date": dates[4].isoformat(), "count": 0},
        ]

        url  = reverse('users-streak')
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {'streak': 4})
        mock_fetch.assert_called_once_with('alice', days=365)

    def test_streak_endpoint_unauthorized(self):
        self.client.credentials()  # remove auth
        url  = reverse('users-streak')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 401)
