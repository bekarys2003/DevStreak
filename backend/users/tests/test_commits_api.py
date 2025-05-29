# users/tests/test_commits_api.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from unittest.mock import patch

from users.views import CACHE_KEY_COMMITS

class CommitsApiCachingTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create & authenticate a user + profile
        from django.contrib.auth import get_user_model
        from users.models import GitHubProfile
        User = get_user_model()
        self.user = User.objects.create_user(username='u', password='p')
        # stub a dummy token so view passes
        GitHubProfile.objects.create(user=self.user, access_token='tok')
        self.client.force_authenticate(self.user)

    @patch('users.views.compute_daily_commits')
    @patch('users.views.cache')
    def test_leaderboard_reads_cache_when_present(self, mock_cache, mock_compute):
        # Arrange: cache.get returns a canned list
        canned = [{'username': 'x', 'commits': 3}]
        mock_cache.get.return_value = canned

        # Act
        resp = self.client.get(reverse('users-leaderboard'))

        # Assert: we never recompute
        mock_compute.assert_not_called()
        # And we returned what was in the cache
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), canned)

    @patch('users.views.compute_daily_commits')
    @patch('users.views.cache')
    def test_leaderboard_computes_and_primes_on_miss(self, mock_cache, mock_compute):
        # Arrange: miss on cache
        mock_cache.get.return_value = None
        dummy = [{'username': 'y', 'commits': 5}]
        mock_compute.return_value = dummy

        # Act
        resp = self.client.get(reverse('users-leaderboard'))

        # Assert: we computed once
        mock_compute.assert_called_once()
        # and set into cache
        mock_cache.set.assert_called_once_with(CACHE_KEY_COMMITS, dummy, timeout=15*60)
        # and returned the computed data
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), dummy)
