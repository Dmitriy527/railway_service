from rest_framework import serializers

from railway.models import TrainType, Station, Train


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
