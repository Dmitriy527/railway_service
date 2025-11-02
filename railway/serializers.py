from rest_framework import serializers

from railway.models import TrainType, Station, Train, Route, Journey
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


class TrainRetriveSerializer(TrainSerializer):
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
