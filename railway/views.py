from rest_framework import viewsets

from railway.models import TrainType, Station, Train, Route, Journey, Order, Ticket
from railway.serializers import TrainTypeSerializer, StationSerializer, TrainSerializer, TrainListSerializer, \
    TrainRetrieveSerializer, RouteStringSerializer, JourneySerializer, JourneyListSerializer, \
    RouteUpdateCreateSerializer, \
    OrderListSerializer, TicketListSerializer, OrderCreateSerializer, TicketCreateSerializer, \
    TrainUpdateCreateSerializer, OrderSerializer


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
        if self.action == "list":
            return TrainListSerializer
        elif self.action == "retrieve":
            return TrainRetrieveSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return TrainUpdateCreateSerializer
        else:
            return self.serializer_class


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related("source", "destination")
    serializer_class = RouteStringSerializer

    def get_serializer_class(self) -> object:
        serializer = self.serializer_class
        if self.action == "list":
            serializer = self.serializer_class
        elif self.action in ["create", "update", "partial_update"]:
            serializer = RouteUpdateCreateSerializer
        return serializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()

    def get_serializer_class(self) -> object:
        if self.action == "list":
            return JourneyListSerializer
        if self.action == "create":
            return JourneySerializer
        if self.action == "retrieve":
            return JourneyListSerializer
        return JourneySerializer

    def get_queryset(self):
        queryset = self.queryset.select_related(
            "route__source",
            "route__destination",
            "train__train_type"
        ).prefetch_related("users")
        return queryset


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().select_related("user")
    serializer_class = OrderCreateSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return self.serializer_class


class TicketViewSet(viewsets.ModelViewSet):
    # queryset = Ticket.objects.all().select_related("journey", "order")
    queryset = Ticket.objects.select_related(
        "journey__route__source",
        "journey__route__destination",
        "journey__train__train_type",
        "journey__train",
        "journey",
        "order__user"
    ).prefetch_related(
        "journey__users")
    serializer_class = TicketCreateSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        if self.action == "retrieve":
            return TicketListSerializer
        return self.serializer_class


class OrderViewSet2(viewsets.ModelViewSet):
    queryset = Order.objects.all().select_related()
    serializer_class = OrderSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)