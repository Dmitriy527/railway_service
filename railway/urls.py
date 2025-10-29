from django.urls import path, include
from rest_framework import routers

from railway.views import TrainTypeViewSet, StationViewSet, TrainViewSet, RouteViewSet

router = routers.DefaultRouter()
router.register("traintypes", TrainTypeViewSet)
router.register("stations", StationViewSet)
router.register("trains", TrainViewSet)
router.register("routes", RouteViewSet)
urlpatterns = [
    path("", include(router.urls)),
]

app_name = "railway"