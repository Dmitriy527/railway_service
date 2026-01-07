from django.test import TestCase
from django.contrib.auth import get_user_model


from railway.models import TrainType, Station, Train, Route, Journey, Order, Ticket
from railway.serializers import (
    TrainTypeSerializer,
    StationSerializer,
    TrainSerializer,
    TrainListSerializer,
    TrainUpdateCreateSerializer,
    TrainRetrieveSerializer,
    RouteUpdateCreateSerializer,
    RouteStringSerializer,
    JourneyListSerializer,
    JourneyRetrieveSerializer,
    JourneySerializer,
    TicketSerializer,
    TicketListSerializer,
    OrderSerializer,
    OrderListSerializer,
)
from user.models import Crew

User = get_user_model()


class TrainTypeSerializerTest(TestCase):
    def setUp(self):
        # Create a test train type for use in tests
        self.train_type = TrainType.objects.create(name="Express")

    def test_train_type_serializer_fields(self):
        """Test verifies that the serializer returns the correct fields for the train type"""
        serializer = TrainTypeSerializer(instance=self.train_type)
        data = serializer.data

        self.assertEqual(set(data.keys()), {"id", "name"})
        self.assertEqual(data["name"], "Express")

    def test_train_type_serializer_create(self):
        """Test verifies the creation of a new train type through the serializer"""
        data = {"name": "Regional"}
        serializer = TrainTypeSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        train_type = serializer.save()
        self.assertEqual(train_type.name, "Regional")


class StationSerializerTest(TestCase):
    def setUp(self):
        # Create a test station with coordinates
        self.station = Station.objects.create(
            name="Kyiv Central", latitude=50.4501, longitude=30.5234
        )

    def test_station_serializer_fields(self):
        """Test verifies the correctness of fields and their values in the station serializer"""
        serializer = StationSerializer(instance=self.station)
        data = serializer.data

        self.assertEqual(set(data.keys()), {"id", "name", "latitude", "longitude"})
        self.assertEqual(data["name"], "Kyiv Central")
        self.assertEqual(float(data["latitude"]), 50.4501)
        self.assertEqual(float(data["longitude"]), 30.5234)

    def test_station_serializer_create(self):
        """Test verifies the creation of a new station through the serializer"""
        data = {"name": "Lviv", "latitude": 49.8397, "longitude": 24.0297}
        serializer = StationSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        station = serializer.save()
        self.assertEqual(station.name, "Lviv")


class TrainSerializerTest(TestCase):
    def setUp(self):
        # Create a test train type and the train itself
        self.train_type = TrainType.objects.create(name="Express")
        self.train = Train.objects.create(
            name="Train 001",
            cargo_num=10,
            place_in_cargo=50,
            train_type=self.train_type,
        )

    def test_train_serializer_fields(self):
        """Test verifies the presence of basic fields in the base train serializer"""
        serializer = TrainSerializer(instance=self.train)
        data = serializer.data

        self.assertIn("id", data)
        self.assertIn("name", data)
        self.assertIn("cargo_num", data)
        self.assertIn("place_in_cargo", data)

    def test_train_list_serializer(self):
        """Test verifies the serializer for train list with SlugRelatedField for type"""
        serializer = TrainListSerializer(instance=self.train)
        data = serializer.data

        self.assertEqual(
            data["train_type"], "Express"
        )  # Verify that type is output as string

    def test_train_update_create_serializer(self):
        """Test verifies the serializer for updating and creating a train"""
        data = {
            "name": "Train 002",
            "cargo_num": 12,
            "place_in_cargo": 60,
            "train_type": "Express",  # Use type name instead of ID
        }
        serializer = TrainUpdateCreateSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        train = serializer.save()
        self.assertEqual(train.name, "Train 002")
        self.assertEqual(
            train.train_type, self.train_type
        )  # Verify that type is correctly linked

    def test_train_retrieve_serializer(self):
        """Test verifies the serializer for detailed train view with nested type object"""
        serializer = TrainRetrieveSerializer(instance=self.train)
        data = serializer.data

        self.assertIsInstance(
            data["train_type"], dict
        )  # Verify that type is an object
        self.assertEqual(data["train_type"]["name"], "Express")


class RouteSerializerTest(TestCase):
    def setUp(self):
        # Create test stations and route
        self.source = Station.objects.create(
            name="Kyiv", latitude=50.4501, longitude=30.5234
        )
        self.destination = Station.objects.create(
            name="Lviv", latitude=49.8397, longitude=24.0297
        )
        self.route = Route.objects.create(
            source=self.source, destination=self.destination, distance=540
        )

    def test_route_update_create_serializer(self):
        """Test verifies the serializer for creating/updating route with station names"""
        data = {
            "source": "Kyiv",  # Use station name instead of ID
            "destination": "Lviv",
            "distance": 540,
        }
        serializer = RouteUpdateCreateSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        route = serializer.save()
        self.assertEqual(route.source, self.source)
        self.assertEqual(route.destination, self.destination)

    def test_route_string_serializer(self):
        """Test verifies the serializer for displaying route with string representations of stations"""
        serializer = RouteStringSerializer(instance=self.route)
        data = serializer.data

        self.assertEqual(
            data["source"], str(self.source)
        )  # Verify string representation
        self.assertEqual(data["destination"], str(self.destination))


class JourneySerializerTest(TestCase):
    def setUp(self):
        # Create all necessary objects for testing journey route
        self.user = User.objects.create_user(
            email="test@test.com", password="testpass123", username="testuser"
        )
        self.crew_member = Crew.objects.create(first_name="John", last_name="Doe")
        self.train_type = TrainType.objects.create(name="Express")
        self.train = Train.objects.create(
            name="Train 001",
            cargo_num=10,
            place_in_cargo=50,
            train_type=self.train_type,
        )
        self.source = Station.objects.create(
            name="Kyiv", latitude=50.4501, longitude=30.5234
        )
        self.destination = Station.objects.create(
            name="Lviv", latitude=49.8397, longitude=24.0297
        )
        self.route = Route.objects.create(
            source=self.source, destination=self.destination, distance=540
        )
        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time="2024-12-01T10:00:00Z",
            arrival_time="2024-12-01T16:00:00Z",
        )
        self.journey.users.add(self.crew_member)  # Add crew member to journey

    def test_journey_list_serializer(self):
        """Test verifies the serializer for journey list with number of available tickets"""
        from django.db.models import Count, F

        # Annotate journey with calculation of available tickets
        journey = Journey.objects.annotate(
            tickets_available=F("train__cargo_num") * F("train__place_in_cargo")
            - Count("tickets")
        ).get(pk=self.journey.pk)

        serializer = JourneyListSerializer(instance=journey)
        data = serializer.data

        self.assertIn("users", data)
        self.assertIn("route", data)
        self.assertIn("train", data)
        self.assertIn("tickets_available", data)
        self.assertEqual(
            data["tickets_available"], 500
        )  # 10 cars * 50 seats - 0 sold tickets

    def test_journey_retrieve_serializer(self):
        """Test verifies the serializer for detailed journey view with sold tickets"""
        serializer = JourneyRetrieveSerializer(instance=self.journey)
        data = serializer.data

        self.assertIn("users", data)
        self.assertIn("route", data)
        self.assertIn("train", data)
        self.assertIn("sold_tickets", data)  # Additional field with sold tickets

    def test_journey_serializer_create(self):
        """Test verifies the creation of a new journey through the serializer"""
        data = {
            "route": self.route.id,
            "train": self.train.id,
            "users": [self.crew_member.id],  # List of crew member IDs
            "departure_time": "2024-12-02T10:00:00Z",
            "arrival_time": "2024-12-02T16:00:00Z",
        }
        serializer = JourneySerializer(data=data)

        self.assertTrue(serializer.is_valid())
        journey = serializer.save()
        self.assertEqual(journey.route, self.route)
        self.assertEqual(journey.train, self.train)


class TicketSerializerTest(TestCase):
    def setUp(self):
        # Create all objects for testing tickets
        self.user = User.objects.create_user(
            email="test@test.com", password="testpass123", username="testuser"
        )
        self.train_type = TrainType.objects.create(name="Express")
        self.train = Train.objects.create(
            name="Train 001",
            cargo_num=10,
            place_in_cargo=50,
            train_type=self.train_type,
        )
        self.source = Station.objects.create(
            name="Kyiv", latitude=50.4501, longitude=30.5234
        )
        self.destination = Station.objects.create(
            name="Lviv", latitude=49.8397, longitude=24.0297
        )
        self.route = Route.objects.create(
            source=self.source, destination=self.destination, distance=540
        )
        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time="2024-12-01T10:00:00Z",
            arrival_time="2024-12-01T16:00:00Z",
        )
        self.order = Order.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            cargo=1, seat=10, journey=self.journey, order=self.order
        )

    def test_ticket_serializer_fields(self):
        """Test verifies the base ticket serializer with basic fields"""
        serializer = TicketSerializer(instance=self.ticket)
        data = serializer.data

        self.assertEqual(set(data.keys()), {"id", "cargo", "seat", "journey"})
        self.assertEqual(data["cargo"], 1)
        self.assertEqual(data["seat"], 10)

    def test_ticket_list_serializer(self):
        """Test verifies the serializer for ticket list with detailed journey information"""
        serializer = TicketListSerializer(instance=self.ticket)
        data = serializer.data

        self.assertIn("journey", data)
        self.assertIsInstance(
            data["journey"], dict
        )  # Verify that journey is an object


class OrderSerializerTest(TestCase):
    def setUp(self):
        # Create all objects for testing orders
        self.user = User.objects.create_user(
            email="test@test.com", password="testpass123", username="testuser"
        )
        self.train_type = TrainType.objects.create(name="Express")
        self.train = Train.objects.create(
            name="Train 001",
            cargo_num=10,
            place_in_cargo=50,
            train_type=self.train_type,
        )
        self.source = Station.objects.create(
            name="Kyiv", latitude=50.4501, longitude=30.5234
        )
        self.destination = Station.objects.create(
            name="Lviv", latitude=49.8397, longitude=24.0297
        )
        self.route = Route.objects.create(
            source=self.source, destination=self.destination, distance=540
        )
        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time="2024-12-01T10:00:00Z",
            arrival_time="2024-12-01T16:00:00Z",
        )

    def test_order_serializer_create_with_tickets(self):
        """Test verifies the creation of an order with tickets through transaction"""
        data = {
            "user": self.user.id,
            "tickets": [
                {"cargo": 1, "seat": 10, "journey": self.journey.id},
                {"cargo": 1, "seat": 11, "journey": self.journey.id},
            ],
        }
        serializer = OrderSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        # Our OrderSerializer does not have 'user' field in Meta.fields,
        # so we pass it separately
        order = serializer.save(user=self.user)

        self.assertEqual(order.tickets.count(), 2)
        self.assertEqual(order.user, self.user)

    def test_order_serializer_empty_tickets_invalid(self):
        """Test verifies that an order without tickets is invalid"""
        data = {"user": self.user.id, "tickets": []}  # Empty tickets list
        serializer = OrderSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("tickets", serializer.errors)

    def test_order_list_serializer(self):
        """Test verifies the serializer for order list with detailed ticket information"""
        order = Order.objects.create(user=self.user)
        Ticket.objects.create(cargo=1, seat=10, journey=self.journey, order=order)

        serializer = OrderListSerializer(instance=order)
        data = serializer.data

        self.assertIn("tickets", data)
        self.assertIsInstance(data["tickets"], list)
        self.assertEqual(
            len(data["tickets"]), 1
        )  # Verify the number of tickets in the order