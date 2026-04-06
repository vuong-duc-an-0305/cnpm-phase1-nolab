from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.accounts'

    def ready(self):
        # Import signal handlers to ensure default groups are created
        from . import signals  # noqa: F401
