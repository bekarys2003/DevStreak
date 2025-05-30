# backend/users/tests/test_tasks.py

from django.test import TestCase
from unittest.mock import patch, MagicMock
import users.tasks as tasks_module
from users.tasks import broadcast_daily_commits_task
tasks_module.async_to_sync = lambda fn: fn

class BroadcastTasksTest(TestCase):
    @patch('users.tasks.get_channel_layer')
    @patch('users.tasks.compute_daily_xp_leaderboard')
    def test_broadcast_daily_commits_task(self, mock_compute, mock_get_layer):
        # Arrange
        # 1) compute_daily_xp_leaderboard returns a dummy leaderboard
        dummy_board = [
            {'username': 'alice', 'commits': 5},
            {'username': 'bob',   'commits': 3},
        ]
        mock_compute.return_value = dummy_board

        # 2) Prepare a fake channel layer with a spy on group_send
        fake_layer = MagicMock()
        mock_get_layer.return_value = fake_layer

        # Act
        result = broadcast_daily_commits_task()

        # Assert
        mock_compute.assert_called_once()  # we computed the board
        fake_layer.group_send.assert_called_once_with(
            'daily_commits',
            {
                'type': 'daily_commits_update',
                'data': dummy_board,
            }
        )
        # The task should return a success message mentioning the number of entries
        self.assertIn('Broadcasted 2 entries', result)
