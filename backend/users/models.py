from django.db import models

# Create your models here.
from django.conf import settings

class GitHubProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    access_token = models.TextField()