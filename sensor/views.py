from rest_framework import viewsets

from sensor.models import Sensor
from sensor.serializers import SensorSerializer
from rest_framework.permissions import IsAuthenticated


class SensorViewSet(viewsets.ModelViewSet):
    serializer_class = SensorSerializer
    model = Sensor
    queryset = Sensor.objects.all().order_by("-title")
    permission_classes = [IsAuthenticated]