from django.db import models

# Create your models here.
from django.conf import settings

class GitHubProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    access_token = models.TextField()


class DailyContribution(models.Model):
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date         = models.DateField()
    commit_count = models.IntegerField(default=0)
    xp           = models.IntegerField(default=0)  # new: total XP earned today


    class Meta:
        unique_together = ("user", "date")
        ordering        = ["-date", "user__username"]

    def __str__(self):
        return f"{self.user.username} @ {self.date}: {self.commit_count}"
