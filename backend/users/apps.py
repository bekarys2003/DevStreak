from django.apps import AppConfig
from django.apps import AppConfig

class UsersConfig(AppConfig):
    name = "users"
    default_auto_field = 'django.db.models.BigAutoField'
    def ready(self):
        # import signal handlers
        import users.signals

