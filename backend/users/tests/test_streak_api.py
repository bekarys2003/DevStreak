# users/tests/test_streak_api.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from unittest.mock import patch

from users.views import CACHE_KEY_STREAK

class StreakApiCachingTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        from django.contrib.auth import get_user_model
        from users.models import GitHubProfile
        User = get_user_model()
        self.user = User.objects.create_user(username='u2', password='p2')
        GitHubProfile.objects.create(user=self.user, access_token='tok2')
        self.client.force_authenticate(self.user)

    @patch('users.views.compute_streak_leaderboard')
    @patch('users.views.cache')
    def test_streak_lift_from_cache(self, mock_cache, mock_compute):
        canned = [{'username': 'z', 'streak': 7}]
        mock_cache.get.return_value = canned

        resp = self.client.get(reverse('users-streak-leaderboard'))

        mock_compute.assert_not_called()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), canned)

    @patch('users.views.compute_streak_leaderboard')
    @patch('users.views.cache')
    def test_streak_compute_on_miss(self, mock_cache, mock_compute):
        mock_cache.get.return_value = None
        dummy = [{'username': 'w', 'streak': 2}]
        mock_compute.return_value = dummy

        resp = self.client.get(reverse('users-streak-leaderboard'))

        mock_compute.assert_called_once()
        mock_cache.set.assert_called_once_with(CACHE_KEY_STREAK, dummy, timeout=15*60)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), dummy)
