# teams/models.py

from django.conf import settings
from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="teams")

    def __str__(self):
        return self.name

class TeamDailyContribution(models.Model):
    """
    Stores XP for a given user *within a specific team* on a given date.
    This lets each user have one XP value for global/daily, and another
    (or many others) for team-specific leaderboards.
    """
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="daily_contributions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    xp = models.IntegerField(default=0)
    # (Optionally: commit_count, etc., if you want to mirror DailyContribution structure)

    class Meta:
        unique_together = ("team", "user", "date")
        ordering = ["-xp"]  # default ordering by xp descending

    def __str__(self):
        return f"{self.user.username} in {self.team.name} on {self.date}: {self.xp}xp"
