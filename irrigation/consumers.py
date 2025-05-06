import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import SensorData


class SensorDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("sensor_data", self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("sensor_data", self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        await self.channel_layer.group_send(
            "sensor_data",
            {
                'type': 'sensor_data_message',
                'message': message
            }
        )

    async def sensor_data_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def get_latest_data(self):
        latest_data = SensorData.objects.latest('timestamp')
        next_schedule = IrrigationSchedule.objects.filter(user=self.scope['user']).order_by('start_time').first()
        return {
            'soil_moisture': latest_data.soil_moisture,
            'temperature': latest_data.temperature,
            'humidity': latest_data.humidity,
            'timestamp': latest_data.timestamp.isoformat(),
            'pump_status': 'On' if latest_data.soil_moisture < 50 else 'Off',
            'valve_status': 'Open' if latest_data.soil_moisture < 50 else 'Closed',
            'next_watering': next_schedule.start_time.strftime('%Y-%m-%d %H:%M') if next_schedule else 'Not scheduled'
        }
    