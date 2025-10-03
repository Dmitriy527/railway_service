from django.urls import path, include
from rest_framework import routers

from railway.views import TrainTypeViewSet, StationViewSet

router = routers.DefaultRouter()
router.register("traintypes", TrainTypeViewSet)
router.register("stations", StationViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "railway"