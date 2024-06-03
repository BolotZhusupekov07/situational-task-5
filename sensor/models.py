from django.db import models


class SensorType(models.TextChoices):
    OUTDOOR = "OUTDOOR", "Outdoor"
    INDOOR = "INDOOR", "Indoor"
    ALL_PURPOSE = "ALL_PURPOSE", "All Purpose"


class SensorStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    DAMAGED = "DAMAGED", "Damaged"
    IN_REPAIR = "IN_REPAIR", "In Repair"


class Sensor(models.Model):
    title = models.CharField(max_length=255)
    type = models.CharField(
        choices=SensorType.choices, default=SensorType.ALL_PURPOSE
    )
    status = models.CharField(
        choices=SensorStatus.choices, default=SensorStatus.ACTIVE
    )
    model = models.CharField(max_length=255)
    installation_date = models.DateTimeField()
