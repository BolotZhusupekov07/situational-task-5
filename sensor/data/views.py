from rest_framework import viewsets

from sensor.data.models import SensorData
from sensor.data.serializers import SensorDataSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

class SensorDataViewSet(viewsets.ModelViewSet):
    serializer_class = SensorDataSerializer
    model = SensorData
    queryset = SensorData.objects.all().order_by("-date")
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["sensor"]
    permission_classes = [IsAuthenticated]
