from django.apps import AppConfig
import logging
import threading
import os
from django.db import connection

logger = logging.getLogger(__name__)


class IrrigationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'irrigation'

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)
        self._pid = None

    def ready(self):
        # Pre-load AI models when Django starts
        from irrigation.services.knowledge.guide_bot import IrrigationGuide
        self.guide_system = IrrigationGuide()
        # Only initialize once per process
        if not hasattr(self, '_pid') or self._pid != os.getpid():
            self._pid = os.getpid()
            logger.info(f"App ready in PID {os.getpid()}")

            # Initialize MQTT in main process only (not in Celery workers)
            if not os.environ.get('CELERY_WORKER_PID'):
                from .mqtt_service import mqtt_client
                # Start MQTT in a separate thread after a short delay
                timer = threading.Timer(5.0, mqtt_client.initialize)
                timer.daemon = True
                timer.start()
                logger.info("MQTT service initialization scheduled")

