# teams/apps.py

from django.apps import AppConfig

class TeamsConfig(AppConfig):
    name = "teams"

    def ready(self):
        # this ensures signals.py is imported on startup
        import teams.signals  # noqa: F401
