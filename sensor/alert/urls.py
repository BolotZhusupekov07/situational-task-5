from django.urls import include, path
from rest_framework.routers import DefaultRouter

from sensor.alert import views

router = DefaultRouter()
router.register(
    r"api/sensors-alerts",
    views.SensorAlertViewSet,
    basename="sensor-alerts",
)

urlpatterns = [path("", include(router.urls))]
