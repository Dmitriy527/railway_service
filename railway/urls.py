from django.urls import path, include
from rest_framework import routers

from railway.views import (TrainTypeViewSet, StationViewSet, TrainViewSet, RouteViewSet, JourneyViewSet, \
    TicketViewSet, OrderViewSet, )
                           # OrderViewSet

router = routers.DefaultRouter()
router.register("traintypes", TrainTypeViewSet)
router.register("stations", StationViewSet)
router.register("trains", TrainViewSet)
router.register("routes", RouteViewSet)
router.register("journeys", JourneyViewSet)
router.register("orders", OrderViewSet)
router.register("tickets", TicketViewSet)
urlpatterns = [
    path("", include(router.urls)),
]

app_name = "railway"