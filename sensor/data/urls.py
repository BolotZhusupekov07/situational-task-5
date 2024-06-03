from django.urls import include, path
from rest_framework.routers import DefaultRouter

from sensor.data import views

router = DefaultRouter()
router.register(
    r"api/sensors-data",
    views.SensorDataViewSet,
    basename="sensor-data",
)

urlpatterns = [path("", include(router.urls))]
