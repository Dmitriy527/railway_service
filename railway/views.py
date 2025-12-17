from django.db.models import Count, F
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication

from railway.models import TrainType, Station, Train, Route, Journey, Order, Ticket
from railway.permissions import IsAdminOrIsAuthenticatedReadOnly
from railway.serializers import (TrainTypeSerializer, StationSerializer, TrainSerializer, TrainListSerializer, \
                                 TrainRetrieveSerializer, RouteStringSerializer, JourneySerializer,
                                 JourneyListSerializer, \
                                 RouteUpdateCreateSerializer, \
                                 OrderListSerializer, TicketListSerializer, TicketCreateSerializer, \
                                 TrainUpdateCreateSerializer, OrderSerializer, JourneyRetrieveSerializer,
                                 TicketSerializer, )
                                 # OrderCreateSerializer)


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrIsAuthenticatedReadOnly,)


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all().select_related("train_type")
    serializer_class = TrainSerializer

    @staticmethod
    def _params_to_ints(query_string):
        return [int(str_id) for str_id in query_string.split(",")]

    def get_serializer_class(self) -> object:
        if self.action == "list":
            return TrainListSerializer
        elif self.action == "retrieve":
            return TrainRetrieveSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return TrainUpdateCreateSerializer
        else:
            return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset
        train_types = self.request.query_params.get("train_types")
        
        if train_types:
            train_types = self._params_to_ints(train_types)
            queryset = queryset.filter(train_type__in=train_types)

        return queryset.distinct()


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
            return JourneyRetrieveSerializer
        return JourneySerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in "list":
            queryset = (self.queryset.select_related(
                "route__source",
                "route__destination",
                "train__train_type"
            ).prefetch_related("users")
                        .annotate(
                tickets_available=F("train__cargo_num") * F("train__place_in_cargo")
                                  - Count("tickets")))
        if self.action in "retrieve":
            queryset = self.queryset.select_related(
                "route__source",
                "route__destination",
                "train__train_type"
            ).prefetch_related("users")

        return queryset


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().select_related("journey", "order")
    serializer_class = TicketCreateSerializer
    def get_queryset(self):
        queryset = self.queryset.select_related(
        "journey__route__source",
        "journey__route__destination",
        "journey__train__train_type",
        "journey__train",
        "journey",
        "order__user"
    ).prefetch_related(
        "journey__users").filter(order__user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        if self.action == "retrieve":
            return TicketListSerializer
        return self.serializer_class


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        if self.action == "list":
            queryset = queryset.select_related("user").prefetch_related(
                "tickets__journey__route__source",
                "tickets__journey__route__destination",
                "tickets__journey__train__train_type",
                "tickets__journey__train",
                "tickets__journey",
            ).prefetch_related(
                "tickets__journey__users")
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action == "list":
            serializer = OrderListSerializer
        return serializer