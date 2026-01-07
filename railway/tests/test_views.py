from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from datetime import timedelta

from railway.models import (
    TrainType,
    Station,
    Train,
    Route,
    Journey,
    Order,
    Ticket,
)

User = get_user_model()


def sample_train_type(**params):
    """Creates a test train type"""
    defaults = {"name": "Express"}
    defaults.update(params)
    return TrainType.objects.create(**defaults)


def sample_station(**params):
    """Creates a test station"""
    defaults = {
        "name": "Test Station",
        "latitude": 50.4501,
        "longitude": 30.5234,
    }
    defaults.update(params)
    return Station.objects.create(**defaults)


def sample_train(train_type=None, **params):
    """Creates a test train"""
    if train_type is None:
        train_type = sample_train_type()
    defaults = {
        "name": "Train 001",
        "cargo_num": 10,
        "place_in_cargo": 50,
        "train_type": train_type,
    }
    defaults.update(params)
    return Train.objects.create(**defaults)


def sample_route(source=None, destination=None, **params):
    """Creates a test route"""
    if source is None:
        source = sample_station(name="Source")
    if destination is None:
        destination = sample_station(name="Destination")
    defaults = {
        "source": source,
        "destination": destination,
        "distance": 100,
    }
    defaults.update(params)
    return Route.objects.create(**defaults)


def sample_journey(route=None, train=None, **params):
    """Creates a test journey"""
    if route is None:
        route = sample_route()
    if train is None:
        train = sample_train()
    defaults = {
        "route": route,
        "train": train,
        "departure_time": timezone.now() + timedelta(days=1),
        "arrival_time": timezone.now() + timedelta(days=1, hours=2),
    }
    defaults.update(params)
    return Journey.objects.create(**defaults)


class TrainTypeViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="user",
            email="user@test.com",
            password="testpass123",
        )
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="adminpass123",
        )

    def test_list_train_types_as_authenticated_user(self):
        """Test viewing train types by authenticated users"""
        self.client.force_authenticate(user=self.user)
        sample_train_type(name="Express")
        sample_train_type(name="Regional")

        url = reverse("railway:traintype-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        if isinstance(res.data, dict) and "results" in res.data:
            self.assertEqual(len(res.data["results"]), 2)
        else:
            self.assertEqual(len(res.data), 2)

    def test_list_train_types_unauthenticated(self):
        """Test that unauthenticated users cannot view train types"""
        url = reverse("railway:traintype-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_train_type_as_admin(self):
        """Test creating a train type by an administrator"""
        self.client.force_authenticate(user=self.admin)
        url = reverse("railway:traintype-list")
        payload = {"name": "High Speed"}

        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(TrainType.objects.filter(name="High Speed").exists())

    def test_create_train_type_as_regular_user(self):
        """Test that regular users cannot create train types"""
        self.client.force_authenticate(user=self.user)
        url = reverse("railway:traintype-list")
        payload = {"name": "High Speed"}

        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class StationViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="user",
            email="user@test.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

    def test_list_stations(self):
        """Test viewing the list of stations"""
        sample_station(name="Kyiv")
        sample_station(name="Lviv")

        url = reverse("railway:station-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        if isinstance(res.data, dict) and "results" in res.data:
            self.assertEqual(len(res.data["results"]), 2)
        else:
            self.assertEqual(len(res.data), 2)

    def test_create_station(self):
        """Test creating a station"""
        url = reverse("railway:station-list")
        payload = {
            "name": "Odesa",
            "latitude": 46.4825,
            "longitude": 30.7233,
        }

        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Station.objects.filter(name="Odesa").exists())

    def test_retrieve_station(self):
        """Test retrieving details of a specific station"""
        station = sample_station(name="Kharkiv")

        url = reverse("railway:station-detail", args=[station.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], "Kharkiv")


class TrainViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="user",
            email="user@test.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)
        self.train_type = sample_train_type(name="Express")

    def test_list_trains(self):
        """Test viewing the list of trains"""
        sample_train(name="Train 001", train_type=self.train_type)
        sample_train(name="Train 002", train_type=self.train_type)

        url = reverse("railway:train-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        if isinstance(res.data, dict) and "results" in res.data:
            self.assertEqual(len(res.data["results"]), 2)
        else:
            self.assertEqual(len(res.data), 2)

    def test_filter_trains_by_type(self):
        """Test filtering trains by type"""
        train_type2 = sample_train_type(name="Regional")
        sample_train(name="Express Train", train_type=self.train_type)
        sample_train(name="Regional Train", train_type=train_type2)

        url = reverse("railway:train-list")
        res = self.client.get(url, {"train_types": str(self.train_type.id)})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        if isinstance(res.data, dict) and "results" in res.data:
            self.assertEqual(len(res.data["results"]), 1)
            self.assertEqual(res.data["results"][0]["name"], "Express Train")
        else:
            self.assertEqual(len(res.data), 1)
            self.assertEqual(res.data[0]["name"], "Express Train")

    def test_retrieve_train(self):
        """Test retrieving details of a specific train"""
        train = sample_train(name="Train 001", train_type=self.train_type)

        url = reverse("railway:train-detail", args=[train.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["name"], "Train 001")

    def test_create_train(self):
        """Test creating a train"""
        url = reverse("railway:train-list")
        payload = {
            "name": "New Train",
            "cargo_num": 12,
            "place_in_cargo": 60,
            "train_type": self.train_type.name,
        }

        res = self.client.post(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Train.objects.filter(name="New Train").exists())


class RouteViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="user",
            email="user@test.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)
        self.source = sample_station(name="Kyiv")
        self.destination = sample_station(name="Lviv")

    def test_list_routes(self):
        """Test viewing the list of routes"""
        sample_route(source=self.source, destination=self.destination)

        url = reverse("railway:route-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        if isinstance(res.data, dict) and "results" in res.data:
            self.assertEqual(len(res.data["results"]), 1)
        else:
            self.assertEqual(len(res.data), 1)

    def test_create_route(self):
        """Test creating a route"""
        url = reverse("railway:route-list")
        payload = {
            "source": self.source.name,
            "destination": self.destination.name,
            "distance": 150,
        }

        res = self.client.post(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Route.objects.filter(
                source=self.source, destination=self.destination
            ).exists()
        )

    def test_retrieve_route(self):
        """Test retrieving details of a specific route"""
        route = sample_route(source=self.source, destination=self.destination)

        url = reverse("railway:route-detail", args=[route.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("source", res.data)
        self.assertIn("destination", res.data)


class JourneyViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="user",
            email="user@test.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)
        self.train_type = sample_train_type()
        self.source = sample_station(name="Source")
        self.destination = sample_station(name="Destination")
        self.train = sample_train(train_type=self.train_type)
        self.route = sample_route(source=self.source, destination=self.destination)

    def test_list_journeys(self):
        """Test viewing the list of journeys"""
        sample_journey(route=self.route, train=self.train)

        url = reverse("railway:journey-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertIn("tickets_available", res.data["results"][0])

    def test_create_journey(self):
        """Test creating a journey"""
        url = reverse("railway:journey-list")
        departure = timezone.now() + timedelta(days=2)
        arrival = departure + timedelta(hours=3)

        payload = {
            "route": self.route.id,
            "train": self.train.id,
            "departure_time": departure.isoformat(),
            "arrival_time": arrival.isoformat(),
        }

        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Journey.objects.count(), 1)

    def test_retrieve_journey(self):
        """Test retrieving details of a specific journey"""
        journey = sample_journey(route=self.route, train=self.train)

        url = reverse("railway:journey-detail", args=[journey.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("route", res.data)
        self.assertIn("train", res.data)


class TicketViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="user",
            email="user@test.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)
        self.journey = sample_journey()
        self.order = Order.objects.create(user=self.user)

    def test_list_tickets_for_user(self):
        """Test viewing tickets for an authenticated user"""
        Ticket.objects.create(cargo=1, seat=1, journey=self.journey, order=self.order)

        url = reverse("railway:ticket-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        if isinstance(res.data, dict) and "results" in res.data:
            self.assertEqual(len(res.data["results"]), 1)
        else:
            self.assertEqual(len(res.data), 1)

    def test_user_can_only_see_own_tickets(self):
        """Test that users can only see their own tickets"""
        other_user = User.objects.create_user(
            username="other",
            email="other@test.com",
            password="testpass123",
        )
        other_order = Order.objects.create(user=other_user)
        Ticket.objects.create(cargo=1, seat=1, journey=self.journey, order=other_order)
        Ticket.objects.create(cargo=2, seat=2, journey=self.journey, order=self.order)

        url = reverse("railway:ticket-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        if isinstance(res.data, dict) and "results" in res.data:
            self.assertEqual(len(res.data["results"]), 1)
        else:
            self.assertEqual(len(res.data), 1)

    def test_create_ticket(self):
        """Test creating a ticket"""
        url = reverse("railway:ticket-list")
        payload = {
            "cargo": 1,
            "seat": 10,
            "journey": self.journey.id,
            "order": self.order.id,
        }

        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.count(), 1)


class OrderViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="user",
            email="user@test.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)
        self.journey = sample_journey()

    def test_list_orders_for_user(self):
        """Test viewing orders for an authenticated user"""
        Order.objects.create(user=self.user)

        url = reverse("railway:order-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)

    def test_user_can_only_see_own_orders(self):
        """Test that users can only see their own orders"""
        other_user = User.objects.create_user(
            username="other",
            email="other@test.com",
            password="testpass123",
        )
        Order.objects.create(user=other_user)
        Order.objects.create(user=self.user)

        url = reverse("railway:order-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)

    def test_create_order(self):
        """Test creating an order"""
        url = reverse("railway:order-list")
        payload = {
            "tickets": [
                {
                    "cargo": 1,
                    "seat": 1,
                    "journey": self.journey.id,
                }
            ]
        }

        res = self.client.post(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.user, self.user)

    def test_retrieve_order(self):
        """Test retrieving details of a specific order"""
        order = Order.objects.create(user=self.user)

        url = reverse("railway:order-detail", args=[order.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cannot_access_orders(self):
        """Test that unauthenticated users cannot access orders"""
        self.client.force_authenticate(user=None)

        url = reverse("railway:order-list")
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class IntegrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="user",
            email="user@test.com",
            password="testpass123",
        )
        self.client.force_authenticate(user=self.user)

    def test_complete_booking_flow(self):
        """Test the complete ticket booking flow"""
        train_type = sample_train_type(name="Express")
        train = sample_train(train_type=train_type, cargo_num=5, place_in_cargo=20)
        route = sample_route()
        journey = sample_journey(route=route, train=train)

        url = reverse("railway:order-list")
        payload = {
            "tickets": [
                {
                    "cargo": 1,
                    "seat": 5,
                    "journey": journey.id,
                }
            ]
        }

        res = self.client.post(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Ticket.objects.count(), 1)

        ticket = Ticket.objects.first()
        self.assertEqual(ticket.cargo, 1)
        self.assertEqual(ticket.seat, 5)
        self.assertEqual(ticket.journey, journey)
        self.assertEqual(ticket.order.user, self.user)