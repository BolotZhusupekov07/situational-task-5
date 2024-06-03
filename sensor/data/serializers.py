from rest_framework import serializers

from sensor.data.models import SensorData


class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = [
            "id",
            "sensor",
            "temperature",
            "humidity",
            "wind_speed",
            "date",
        ]
        read_only_fields = ["id", "date"]
