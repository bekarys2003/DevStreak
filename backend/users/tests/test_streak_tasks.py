# backend/users/tests/test_streak_tasks.py

from django.test import TestCase
from unittest.mock import patch, MagicMock
import users.tasks as tasks_module
from users.tasks import broadcast_streak_leaderboard_task

# Prevent async_to_sync from trying to await our MagicMocks
tasks_module.async_to_sync = lambda fn: fn

class BroadcastStreakTasksTest(TestCase):
    @patch('users.tasks.get_channel_layer')
    @patch('users.tasks.compute_streak_leaderboard')
    @patch('django.core.cache.cache.set')
    def test_broadcast_streak_leaderboard_task(self, mock_cache_set, mock_compute, mock_get_layer):
        # Arrange
        dummy_data = [
            {'username': 'alice', 'streak': 5},
            {'username': 'bob',   'streak': 3},
        ]
        mock_compute.return_value = dummy_data

        fake_layer = MagicMock()
        mock_get_layer.return_value = fake_layer

        # Act
        result = broadcast_streak_leaderboard_task()

        # Assert compute_streak_leaderboard was called
        mock_compute.assert_called_once()

        # Assert we cached the result under the right key
        from users.tasks import CACHE_KEY
        mock_cache_set.assert_called_once_with(CACHE_KEY, dummy_data, None)

        # Assert we broadcast on the correct group
        fake_layer.group_send.assert_called_once_with(
            'streak_leaderboard',
            {
                'type': 'streak_leaderboard_update',
                'data': dummy_data,
            }
        )

        # And the task returns a summary message
        self.assertIn('Broadcasted 2 streak entries', result)
