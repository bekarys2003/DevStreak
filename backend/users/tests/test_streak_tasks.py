# users/tests/test_streak_tasks.py
from django.test import TestCase
from unittest.mock import patch, MagicMock

from users.tasks import (
    broadcast_streak_leaderboard_task,
    CACHE_KEY_STREAK,
)

class BroadcastStreakTaskTest(TestCase):
    @patch('users.tasks.compute_streak_leaderboard')
    @patch('users.tasks.get_channel_layer')
    @patch('users.tasks.cache')
    def test_broadcast_streak_leaderboard_task(self, mock_cache, mock_get_layer, mock_compute):
        # Arrange
        dummy = [
            {'username': 'alice', 'streak': 4},
            {'username': 'bob',   'streak': 1},
        ]
        mock_compute.return_value = dummy

        fake_layer = MagicMock()
        mock_get_layer.return_value = fake_layer

        # Act
        result = broadcast_streak_leaderboard_task()

        # Assert: compute called
        mock_compute.assert_called_once()

        # WS broadcast
        fake_layer.group_send.assert_called_once_with(
            'streak_leaderboard',
            {'type': 'streak_leaderboard_update', 'data': dummy}
        )

        # cache.set with 900s
        mock_cache.set.assert_called_once_with(
            CACHE_KEY_STREAK, dummy, timeout=900
        )

        self.assertIn('Broadcasted 2 streak entries', result)
