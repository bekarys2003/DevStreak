from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async

class TeamXPConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # 1) Grab team_name from the URL kwargs
        team_name = self.scope["url_route"]["kwargs"].get("team_name")

        # 2) If no valid team_name, reject
        if not team_name:
            await self.close(code=4001)
            return

        # 3) Accept the WS handshake
        await self.accept()

        # 4) Join the group "team_<team_name>"
        self.group_name = f"team_{team_name}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        # 5) Fetch initial team leaderboard from TeamDailyContribution
        from .views import compute_daily_xp_leaderboard_for_team
        initial_data = await sync_to_async(
            compute_daily_xp_leaderboard_for_team
        )(team_name)

        # 6) Send it immediately as JSON
        await self.send_json(initial_data)

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def team_xp_update(self, event):
        # Re‐compute and resend whenever we get a "team_xp_update" event
        team_name = self.scope["url_route"]["kwargs"].get("team_name")
        from .views import compute_daily_xp_leaderboard_for_team

        fresh_board = await sync_to_async(
            compute_daily_xp_leaderboard_for_team
        )(team_name)
        await self.send_json(fresh_board)
