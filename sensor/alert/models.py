from django.db import models

from sensor.models import Sensor


class SensorAlert(models.Model):
    sensor = models.ForeignKey(Sensor, models.CASCADE)
    description = models.TextField()
    date = models.DateTimeField()
