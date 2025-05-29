# users/consumers.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class DailyCommitsConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # 1) Accept & join the group
        await self.accept()
        await self.channel_layer.group_add('daily_commits', self.channel_name)

        # 2) Send the current leaderboard
        data = await self._compute_leaderboard()
        await self.send_json(data)

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard('daily_commits', self.channel_name)

    async def daily_commits_update(self, event):
        """
        Handler for group_send with type='daily_commits_update'.
        Simply re-compute (or you could use event['data']) and send it.
        """
        # Option A: use the payload sent in event
        # await self.send_json(event['data'])

        # Option B: recompute here
        data = await self._compute_leaderboard()
        await self.send_json(data)

    async def _compute_leaderboard(self):
        """
        Helper to call your sync compute_daily_commits() from users.views.
        """
        from asgiref.sync import sync_to_async
        from users.views import compute_daily_commits

        return await sync_to_async(compute_daily_commits)()
