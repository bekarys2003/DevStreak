# users/tests/test_commits_tasks.py
from django.test import TestCase
from unittest.mock import patch, MagicMock

from users.tasks import (
    broadcast_daily_commits_task,
    CACHE_KEY_COMMITS,
)

class BroadcastCommitsTaskTest(TestCase):
    @patch('users.tasks.compute_daily_commits')
    @patch('users.tasks.get_channel_layer')
    @patch('users.tasks.cache')
    def test_broadcast_daily_commits_task(self, mock_cache, mock_get_layer, mock_compute):
        # Arrange
        dummy = [
            {'username': 'alice', 'commits': 7},
            {'username': 'bob',   'commits': 2},
        ]
        mock_compute.return_value = dummy

        fake_layer = MagicMock()
        mock_get_layer.return_value = fake_layer

        # Act
        result = broadcast_daily_commits_task()

        # Assert compute was called
        mock_compute.assert_called_once()

        # Assert we pushed to the WS group
        fake_layer.group_send.assert_called_once_with(
            'daily_commits',
            {'type': 'daily_commits_update', 'data': dummy}
        )

        # Assert we set the cache for 15 minutes
        mock_cache.set.assert_called_once_with(
            CACHE_KEY_COMMITS, dummy, timeout=15 * 60
        )

        # And that the return string mentions 2 entries
        self.assertIn('Broadcasted 2 entries', result)
