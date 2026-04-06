"""
Attendance app configuration
"""
from django.apps import AppConfig


class AttendanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api.attendance'
    verbose_name = 'Attendance Management'

    def ready(self):
        """Import signals when app is ready"""
        try:
            import api.attendance.signals  # noqa
        except ImportError:
            pass
