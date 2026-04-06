from django.apps import apps
from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver


DEFAULT_GROUPS = (
    ('admin', {
        'is_staff': True,
    }),
    ('cashier', {
        'is_staff': False,
    }),
)


@receiver(post_migrate)
def ensure_default_groups(sender, **kwargs):
    """Create default user groups after migrations run for this app."""
    app_config = apps.get_app_config('accounts')
    if sender != app_config:
        return

    for group_name, _ in DEFAULT_GROUPS:
        Group.objects.get_or_create(name=group_name)
