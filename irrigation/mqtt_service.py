import threading
import paho.mqtt.client as mqtt
from django.conf import settings
import json
import logging
import os
from .db_utils import acquire_connection
from django.db import close_old_connections

logger = logging.getLogger(__name__)


class MQTTClient:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.pid = os.getpid()
                    cls._instance.initialized = False
        elif cls._instance.pid != os.getpid():
            # Handle fork case
            with cls._lock:
                if cls._instance.initialized:
                    cls._instance.disconnect()
                cls._instance = super().__new__(cls)
                cls._instance.pid = os.getpid()
                cls._instance.initialized = False
        return cls._instance

    def initialize(self):
        if not self.initialized:
            self.client = mqtt.Client()
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASS)
            self.client.connect(settings.MQTT_HOST, settings.MQTT_PORT)
            self.client.loop_start()
            self.initialized = True
            logger.info(f"MQTT initialized in PID {os.getpid()}")

    def disconnect(self):
        if hasattr(self, 'client') and self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.initialized = False

    def on_connect(self, client, userdata, flags, rc):
        logger.info(f"MQTT Connected in PID {os.getpid()} (Code {rc})")
        client.subscribe("irrigation/sensor/data")

    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            self.save_sensor_data(data)
        except Exception as e:
            logger.error(f"MQTT Error in PID {os.getpid()}: {e}")
        finally:
            close_old_connections()

    def save_sensor_data(self, data):
        from .models import SensorData
        try:
            with acquire_connection() as connection:
                SensorData.objects.using(connection.alias).create(
                    temperature=data.get('temp'),
                    humidity=data.get('humidity'),
                    soil_moisture=data.get('moisture'),
                    pump_status=data.get('pump'),
                    valve_status=data.get('valve')
                )
        except Exception as e:
            logger.error(f"Database Error in PID {os.getpid()}: {e}")
        finally:
            close_old_connections()


# Initialize without automatically starting
mqtt_client = MQTTClient()
