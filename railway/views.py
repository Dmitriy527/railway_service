from rest_framework import viewsets

from railway.models import TrainType, Station, Train, Route
from railway.serializers import TrainTypeSerializer, StationSerializer, TrainSerializer, TrainListSerializer, \
    TrainRetriveSerializer, RouteSerializer


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all().select_related("train_type")
    serializer_class = TrainSerializer

    def get_serializer_class(self) -> object:
        serializer = self.serializer_class
        if self.action == "list":
            serializer = TrainListSerializer
        if self.action == "retrieve":
            serializer = TrainRetriveSerializer
        return serializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related("source", "destination")
    serializer_class = RouteSerializer