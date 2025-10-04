from rest_framework import viewsets

from railway.models import TrainType, Station, Train
from railway.serializers import TrainTypeSerializer, StationSerializer, TrainSerializer, TrainListSerializer, \
    TrainRetriveSerializer


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer

    def get_serializer_class(self) -> object:
        serializer = self.serializer_class
        if self.action == "list":
            serializer = TrainListSerializer
        if self.action == "retrieve":
            serializer = TrainRetriveSerializer
        return serializer