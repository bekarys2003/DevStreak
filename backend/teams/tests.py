# teams/tests.py

import json
import asyncio
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer

from backend.asgi import application   # Your ASGI application
from users.models import DailyContribution, GitHubProfile
from teams.models import Team

User = get_user_model()

# teams/tests.py (at the very top, before any imports)

import warnings

warnings.filterwarnings("ignore", message="Task was destroyed but it is pending")
warnings.filterwarnings("ignore", message="Event loop is closed")

# ------------------------------------------------------------------------------
# HTTP/REST tests for the Team endpoints
# ------------------------------------------------------------------------------
import atexit, asyncio
from channels.layers import get_channel_layer

def _close_any_remaining_channel_layer():
    try:
        layer = get_channel_layer()
        loop = asyncio.get_event_loop()
        if layer is not None and hasattr(layer, "close") and not loop.is_closed():
            loop.run_until_complete(layer.close())
    except Exception:
        pass

atexit.register(_close_any_remaining_channel_layer)

class TeamRESTTests(TestCase):
    def setUp(self):
        # Create three users: alice, bob, charlie
        self.alice = User.objects.create_user(
            username="alice", email="alice@example.com", password="pass"
        )
        self.bob = User.objects.create_user(
            username="bob", email="bob@example.com", password="pass"
        )
        self.charlie = User.objects.create_user(
            username="charlie", email="charlie@example.com", password="pass"
        )

        # Create a dummy GitHubProfile for each user
        for u in (self.alice, self.bob, self.charlie):
            GitHubProfile.objects.create(user=u, access_token="dummy_token")

        # Generate a valid JWT access token for alice (using SimpleJWT)
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.alice)
        self.alice_access = str(refresh.access_token)
        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {self.alice_access}"}

    def test_create_team_success_and_ignore_invalid_username(self):
        url = reverse("teams-create")
        payload = {"name": "team1", "members": ["bob", "nonexistentuser"]}

        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth_headers
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"team": "team1"})

        team = Team.objects.get(name="team1")
        members = set(team.members.all())
        self.assertIn(self.alice, members)
        self.assertIn(self.bob, members)
        self.assertNotIn(self.charlie, members)

    def test_create_team_duplicate_name_returns_400(self):
        Team.objects.create(name="dup_team")
        url = reverse("teams-create")
        payload = {"name": "dup_team", "members": []}

        resp = self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth_headers
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("detail", resp.json())

    def test_rest_leaderboard_missing_team_returns_404(self):
        missing_url = reverse("teams-leaderboard", kwargs={"team_name": "no_such"})
        resp = self.client.get(missing_url, **self.auth_headers)
        self.assertEqual(resp.status_code, 404)

    def test_rest_leaderboard_non_member_returns_403(self):
        team = Team.objects.create(name="teamA")
        team.members.add(self.alice, self.bob)

        from rest_framework_simplejwt.tokens import RefreshToken
        refresh_charlie = RefreshToken.for_user(self.charlie)
        charlie_access = str(refresh_charlie.access_token)
        headers_charlie = {"HTTP_AUTHORIZATION": f"Bearer {charlie_access}"}

        url = reverse("teams-leaderboard", kwargs={"team_name": "teamA"})
        resp = self.client.get(url, **headers_charlie)
        self.assertEqual(resp.status_code, 403)

    def test_rest_leaderboard_returns_empty_list_if_no_contributions(self):
        team = Team.objects.create(name="teamB")
        team.members.add(self.alice, self.bob)

        url = reverse("teams-leaderboard", kwargs={"team_name": "teamB"})
        resp = self.client.get(url, **self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), [])

    def test_rest_leaderboard_shows_only_today_xp_sorted(self):
        team = Team.objects.create(name="teamC")
        team.members.add(self.alice, self.bob)

        today = date.today()
        DailyContribution.objects.create(
            user=self.alice, date=today, commit_count=3, xp=5
        )
        DailyContribution.objects.create(
            user=self.bob, date=today, commit_count=1, xp=3
        )

        url = reverse("teams-leaderboard", kwargs={"team_name": "teamC"})
        resp = self.client.get(url, **self.auth_headers)
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["username"], "alice")
        self.assertEqual(data[0]["xp"], 5)
        self.assertEqual(data[1]["username"], "bob")
        self.assertEqual(data[1]["xp"], 3)

    def test_rest_leaderboard_ignores_contributions_not_from_today(self):
        team = Team.objects.create(name="teamD")
        team.members.add(self.alice, self.bob)

        yesterday = date.today().replace(day=date.today().day - 1)
        DailyContribution.objects.create(
            user=self.bob, date=yesterday, commit_count=2, xp=4
        )
        DailyContribution.objects.create(
            user=self.alice, date=date.today(), commit_count=1, xp=2
        )

        url = reverse("teams-leaderboard", kwargs={"team_name": "teamD"})
        resp = self.client.get(url, **self.auth_headers)
        self.assertEqual(resp.status_code, 200)

        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["username"], "alice")
        self.assertEqual(data[0]["xp"], 2)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Close the default InMemoryChannelLayer created at import time
        layer = get_channel_layer()
        loop = asyncio.get_event_loop()
        if not loop.is_closed() and hasattr(layer, "close"):
            loop.run_until_complete(layer.close())


# ------------------------------------------------------------------------------
# WebSocket tests for TeamXPConsumer
# ------------------------------------------------------------------------------

@override_settings(
    CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
)
class TeamWebsocketTests(TransactionTestCase):
    """
    A TransactionTestCase that drives WebsocketCommunicator via an explicit event loop.
    """

    def setUp(self):
        # Create a fresh event loop and make it the current loop:
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        # Close only the override-settings InMemoryChannelLayer
        layer = get_channel_layer()
        self.loop.run_until_complete(layer.close())

        # Then close this test’s event loop
        self.loop.close()
        asyncio.set_event_loop(None)

    async def _create_communicator(self, path):
        return WebsocketCommunicator(application, path)

    def test_team_xp_consumer_initial_and_broadcast(self):
        # 1) Create two users
        alice = User.objects.create_user(
            username="alice_ws", email="a@example.com", password="pass"
        )
        bob = User.objects.create_user(
            username="bob_ws", email="b@example.com", password="pass"
        )

        # 2) Create GitHubProfile for both
        GitHubProfile.objects.create(user=alice, access_token="dummy")
        GitHubProfile.objects.create(user=bob, access_token="dummy")

        # 3) Create a team and add both members
        team = Team.objects.create(name="live_team")
        team.members.add(alice, bob)

        # 4) Give alice xp today, bob none yet
        today = date.today()
        DailyContribution.objects.create(user=alice, date=today, commit_count=2, xp=4)

        # 5) Build the WebSocket URL
        ws_path = f"/ws/team-xp/{team.name}/"

        # 6) Instantiate communicator inside the running loop
        communicator = self.loop.run_until_complete(
            self._create_communicator(ws_path)
        )

        # 7) Connect (returns (connected_bool, protocol))
        connected, _ = self.loop.run_until_complete(communicator.connect())
        self.assertTrue(connected)

        # 8) On initial connect, the consumer should send current leaderboard:
        initial_payload = self.loop.run_until_complete(
            communicator.receive_json_from(timeout=1)
        )
        # Only alice appears, with xp=4
        self.assertEqual(initial_payload, [{"username": "alice_ws", "xp": 4}])

        # 9) Now create Bob’s xp row and broadcast via group_send
        DailyContribution.objects.create(user=bob, date=today, commit_count=1, xp=2)

        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer as get_override_layer

        override_layer = get_override_layer()
        async_to_sync(override_layer.group_send)(
            f"team_{team.name}",
            {"type": "team_xp_update"},
        )

        # 10) Expect updated leaderboard (alice then bob)
        updated_payload = self.loop.run_until_complete(
            communicator.receive_json_from(timeout=1)
        )
        self.assertEqual(
            updated_payload,
            [
                {"username": "alice_ws", "xp": 4},
                {"username": "bob_ws",   "xp": 2},
            ],
        )

        # 11) Finally disconnect
        self.loop.run_until_complete(communicator.disconnect())

    def test_consumer_rejects_invalid_url(self):
        communicator = self.loop.run_until_complete(
            self._create_communicator("/ws/team-xp/")
        )

        connected, _ = self.loop.run_until_complete(communicator.connect())
        self.assertFalse(connected)

