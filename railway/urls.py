from django.urls import path, include
from rest_framework import routers

from railway.views import TrainTypeViewSet, StationViewSet, TrainViewSet, RouteViewSet, JourneyViewSet, OrderViewSet, \
    TicketViewSet, OrderViewSet2

router = routers.DefaultRouter()
router.register("traintypes", TrainTypeViewSet)
router.register("stations", StationViewSet)
router.register("trains", TrainViewSet)
router.register("routes", RouteViewSet)
router.register("journeys", JourneyViewSet)
router.register("orders", OrderViewSet2)
router.register("tickets", TicketViewSet)
urlpatterns = [
    path("", include(router.urls)),
]

app_name = "railway"