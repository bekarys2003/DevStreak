# teams/consumers.py

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import sync_to_async

class TeamXPConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # 1) Grab team_name from the URL kwargs
        team_name = self.scope['url_route']['kwargs'].get("team_name")

        # 2) If no valid team_name, reject *before* accepting
        if not team_name:
            await self.close(code=4001)
            return

        # 3) Now accept the WebSocket handshake
        await self.accept()

        # 4) Build and store the group name
        self.group_name = f"team_{team_name}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        # 5) Fetch initial data (today’s XP for that team)
        from .views import compute_daily_xp_leaderboard_for_team
        initial_data = await sync_to_async(compute_daily_xp_leaderboard_for_team)(team_name)

        # 6) Send it as JSON
        await self.send_json(initial_data)

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def team_xp_update(self, event):
        team_name = self.scope['url_route']['kwargs'].get("team_name")
        from .views import compute_daily_xp_leaderboard_for_team

        fresh_board = await sync_to_async(compute_daily_xp_leaderboard_for_team)(team_name)
        await self.send_json(fresh_board)
