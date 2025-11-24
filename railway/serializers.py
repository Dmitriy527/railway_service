from dataclasses import fields

from django.conf.global_settings import AUTH_USER_MODEL
from django.contrib.auth.models import User
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
        queryset=TrainType.objects.all(),
        slug_field="name"
    )


class TrainRetrieveSerializer(TrainSerializer):
    train_type = TrainTypeSerializer()



class RouteSerializer(serializers.ModelSerializer):
    source = Station.objects.all()
    destination = Station.objects.all()
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

    class Meta:
        model = Journey
        fields = "__all__"


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


class OrderListSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field="username",
    )
    class Meta:
        model = Order
        fields = "__all__"


class OrderCreateSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    class Meta:
        model = Order
        fields = "__all__"


class TicketListSerializer(serializers.ModelSerializer):
    journey = JourneyListSerializer()
    order = OrderListSerializer()

    class Meta:
        model = Ticket
        fields = "__all__"


class TicketCreateSerializer(serializers.ModelSerializer):
    journey = JourneySerializer
    order = Order.objects.all()
    class Meta:
        model = Ticket
        fields = "__all__"
