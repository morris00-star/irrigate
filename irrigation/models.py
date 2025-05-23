from django.conf import settings
from django.db import models


class SensorData(models.Model):
    temperature = models.FloatField()
    humidity = models.FloatField()
    moisture = models.IntegerField(default=0)
    pump_status = models.BooleanField(default=False)
    valve_status = models.BooleanField(default=False)
    threshold = models.IntegerField(default=30)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Sensor Data at {self.timestamp}"


class ControlCommand(models.Model):
    pump_status = models.BooleanField(default=False)
    valve_status = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Control Command at {self.timestamp}"


class Threshold(models.Model):
    """
    Model to store the moisture threshold for irrigation.
    """
    threshold = models.IntegerField(default=50)  # Default threshold is 30%
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Threshold: {self.threshold}% (User: {self.user})"

