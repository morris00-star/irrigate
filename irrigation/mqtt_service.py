import paho.mqtt.client as mqtt
from django.conf import settings
import json
from .models import SensorData  # Update with your model


def on_connect(client, userdata, flags, rc):
    print(f"MQTT Connected (Code {rc})")
    client.subscribe("irrigation/sensor/data")


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        SensorData.objects.create(
            temperature=data.get('temp'),
            humidity=data.get('humidity'),
            soil_moisture=data.get('moisture'),
            pump_status=data.get('pump'),
            valve_status=data.get('valve')
        )
    except Exception as e:
        print(f"MQTT Error: {e}")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASS)
client.connect(settings.MQTT_HOST, settings.MQTT_PORT)
client.loop_start()
