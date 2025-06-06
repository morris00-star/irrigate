from django.apps import AppConfig


class IrrigationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'irrigation'

    def ready(self):
        # Import tasks to ensure they're registered
        from . import tasks  # noqa
