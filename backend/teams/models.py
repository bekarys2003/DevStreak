from django.db import models

# Create your models here.
# teams/models.py

from django.conf import settings

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="teams"
    )

    def __str__(self):
        return self.name
