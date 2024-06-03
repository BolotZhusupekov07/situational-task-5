from rest_framework import serializers

from sensor.models import Sensor


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = [
            "id",
            "title",
            "type",
            "status",
            "model",
            "installation_date",
        ]
        read_only_fields = ["id"]
