from rest_framework import viewsets

from sensor.alert.models import SensorAlert
from sensor.alert.serializers import SensorAlertSerializer
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend


class SensorAlertViewSet(viewsets.ModelViewSet):
    serializer_class = SensorAlertSerializer
    model = SensorAlert
    queryset = SensorAlert.objects.all().order_by("-date")
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["sensor"]
    permission_classes = [IsAuthenticated]