from dataclasses import fields

from django.conf.global_settings import AUTH_USER_MODEL
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers

from railway.models import TrainType, Station, Train, Route, Journey, Order, Ticket
from user.models import Crew
from user.serializers import CrewSerializer


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = "__all__"


class TrainListSerializer(TrainSerializer):
    train_type = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True,
    )


class TrainUpdateCreateSerializer(TrainSerializer):
    train_type = serializers.SlugRelatedField(
        queryset=TrainType.objects.all(),
        slug_field="name",
    )


class TrainRetrieveSerializer(TrainSerializer):
    train_type = TrainTypeSerializer()



class RouteUpdateCreateSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        queryset=Station.objects.all(),
        slug_field="name",
    )
    destination = serializers.SlugRelatedField(
        queryset=Station.objects.all(),
        slug_field="name",
    )
    class Meta:
        model = Route
        fields = "__all__"


class RouteStringSerializer(serializers.ModelSerializer):
    source = serializers.StringRelatedField()
    destination = serializers.StringRelatedField()

    class Meta:
        model = Route
        fields = "__all__"


class JourneyListSerializer(serializers.ModelSerializer):
    users = serializers.StringRelatedField(many=True)
    route = serializers.StringRelatedField()
    train = serializers.StringRelatedField()
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Journey
        fields = "__all__"


class JourneyRetrieveSerializer(JourneyListSerializer):
    sold_tickets = serializers.StringRelatedField(
        many=True,
        read_only=True,
        source="tickets"
    )

    class Meta:
        model = Journey
        fields = ("users", "route", "train", "departure_time", "arrival_time","sold_tickets")


class JourneySerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Crew.objects.all().select_related(),
    )
    route = serializers.PrimaryKeyRelatedField(
        queryset=Route.objects.all().select_related("source", "destination"),
    )
    train = serializers.PrimaryKeyRelatedField(
        queryset=Train.objects.all().select_related("train_type"),
    )

    class Meta:
        model = Journey
        fields = "__all__"



class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "cargo", "seat", "journey"]


class TicketListSerializer(serializers.ModelSerializer):
    journey = JourneyListSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = "__all__"


class TicketCreateSerializer(serializers.ModelSerializer):
    journey = JourneySerializer
    order = Order.objects.all()
    class Meta:
        model = Ticket
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, allow_empty=False)
    class Meta:
        model = Order
        fields = ["id", "created_at", "tickets"]

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop('tickets')
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(read_only=True, many=True)

