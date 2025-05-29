# users/tests/test_leaderboard.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from users.models import GitHubProfile
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch

User = get_user_model()

class LeaderboardTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # create two users and their GitHubProfiles
        self.user1 = User.objects.create_user(username="alice", email="a@example.com")
        self.user2 = User.objects.create_user(username="bob",   email="b@example.com")
        GitHubProfile.objects.create(user=self.user1, access_token="token-alice")
        GitHubProfile.objects.create(user=self.user2, access_token="token-bob")

        # issue a valid JWT for alice
        refresh = RefreshToken.for_user(self.user1)
        access = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

    @patch('users.views.compute_daily_commits')
    def test_leaderboard_endpoint(self, mock_compute):
        # stub compute_daily_commits to return tuples of commits counts
        mock_compute.return_value = [
            {'username': 'alice', 'commits': 5},
            {'username': 'bob',   'commits': 3},
        ]

        url = reverse('users-leaderboard')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # your leaderboard view returns exactly that array
        self.assertEqual(resp.json(), mock_compute.return_value)

    @patch('core.github_api.GitHubAPIClient.fetch_user_contribution_calendar')
    def test_streak_endpoint(self, mock_calendar):
        # simulate Alice had 3 consecutive days, Bob 0
        mock_calendar.side_effect = [
            # first call for alice
            [
                {'date': '2025-05-28', 'count': 1},
                {'date': '2025-05-27', 'count': 1},
                {'date': '2025-05-26', 'count': 1},
                # earlier days omitted
            ],
            # second call for bob
            [],
        ]

        url = reverse('users-streak')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # since we authenticate as alice, we only get her streak
        self.assertEqual(resp.json(), {'streak': 3})

    def test_unauthorized_access(self):
        # drop credentials
        self.client.credentials()
        for name in ['users-leaderboard', 'users-streak']:
            resp = self.client.get(reverse(name))
            self.assertEqual(resp.status_code, 401)
