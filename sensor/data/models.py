from django.utils import timezone
from django.db import models

from sensor.models import Sensor


class SensorData(models.Model):
    sensor = models.ForeignKey(Sensor, models.CASCADE)
    temperature = models.DecimalField(max_digits=10, decimal_places=2)
    humidity = models.DecimalField(max_digits=10, decimal_places=2)
    wind_speed = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
