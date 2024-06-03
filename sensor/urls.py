from django.urls import include, path
from rest_framework.routers import DefaultRouter

from sensor import views
from sensor.data.urls import router as data_router
from sensor.alert.urls import router as alerts_router

router = DefaultRouter()
router.register(
    r"api/sensors", views.SensorViewSet, basename="sensor"
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(data_router.urls)),
    path("", include(alerts_router.urls)),
]
