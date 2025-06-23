from django.apps import AppConfig
import os


class IrrigationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'irrigation'

    def ready(self):
        # Import tasks to ensure they're registered
        from . import tasks  # noqa

        if os.environ.get('RUN_MAIN'):
            from .mqtt_service import client
            self.mqtt_client = client
