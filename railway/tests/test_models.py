from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from datetime import datetime, timedelta

from user.models import Crew
from railway.models import (
    Station,
    Route,
    TrainType,
    Train,
    Journey,
    Order,
    Ticket,
)

User = get_user_model()


class StationModelTest(TestCase):
    def setUp(self):
        self.station = Station.objects.create(
            name="Kyiv", latitude=50.4501, longitude=30.5234
        )

    def test_station_creation(self):
        """Test station creation"""
        self.assertEqual(self.station.name, "Kyiv")
        self.assertEqual(self.station.latitude, 50.4501)
        self.assertEqual(self.station.longitude, 30.5234)

    def test_station_str(self):
        """Test string representation"""
        self.assertEqual(str(self.station), "Kyiv")


class RouteModelTest(TestCase):
    def setUp(self):
        self.station1 = Station.objects.create(
            name="Kyiv", latitude=50.4501, longitude=30.5234
        )
        self.station2 = Station.objects.create(
            name="Lviv", latitude=49.8397, longitude=24.0297
        )
        self.route = Route.objects.create(
            source=self.station1, destination=self.station2, distance=540
        )

    def test_route_creation(self):
        """Test route creation"""
        self.assertEqual(self.route.source, self.station1)
        self.assertEqual(self.route.destination, self.station2)
        self.assertEqual(self.route.distance, 540)

    def test_route_str(self):
        """Test string representation"""
        expected = "Kyiv - Lviv: 540km."
        self.assertEqual(str(self.route), expected)

    def test_route_related_names(self):
        """Test related_name relationships"""
        self.assertIn(self.route, self.station1.source_routes.all())
        self.assertIn(self.route, self.station2.destination_routes.all())


class TrainTypeModelTest(TestCase):
    def setUp(self):
        self.train_type = TrainType.objects.create(name="Express")

    def test_train_type_creation(self):
        """Test train type creation"""
        self.assertEqual(self.train_type.name, "Express")

    def test_train_type_str(self):
        """Test string representation"""
        self.assertEqual(str(self.train_type), "Express")

    def test_train_type_unique(self):
        """Test train type name uniqueness"""
        with self.assertRaises(IntegrityError):
            TrainType.objects.create(name="Express")


class TrainModelTest(TestCase):
    def setUp(self):
        self.train_type = TrainType.objects.create(name="Intercity")
        self.train = Train.objects.create(
            name="IC-701", cargo_num=10, place_in_cargo=50, train_type=self.train_type
        )

    def test_train_creation(self):
        """Test train creation"""
        self.assertEqual(self.train.name, "IC-701")
        self.assertEqual(self.train.cargo_num, 10)
        self.assertEqual(self.train.place_in_cargo, 50)
        self.assertEqual(self.train.train_type, self.train_type)

    def test_train_str(self):
        """Test string representation"""
        expected = "IC-701: cargo: 10, place: 50"
        self.assertEqual(str(self.train), expected)

    def test_train_type_relation(self):
        """Test relationship with train type"""
        self.assertIn(self.train, self.train_type.trains.all())


class JourneyModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="crew@test.com", password="testpass123", username="testuser"
        )
        self.crew = Crew.objects.create(first_name="John", last_name="Doe")
        self.station1 = Station.objects.create(
            name="Kyiv", latitude=50.4501, longitude=30.5234
        )
        self.station2 = Station.objects.create(
            name="Lviv", latitude=49.8397, longitude=24.0297
        )
        self.route = Route.objects.create(
            source=self.station1, destination=self.station2, distance=540
        )
        self.train_type = TrainType.objects.create(name="Express")
        self.train = Train.objects.create(
            name="EX-101", cargo_num=8, place_in_cargo=60, train_type=self.train_type
        )
        self.departure = datetime.now()
        self.arrival = self.departure + timedelta(hours=6)
        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=self.departure,
            arrival_time=self.arrival,
        )
        self.journey.users.add(self.crew)

    def test_journey_creation(self):
        """Test journey creation"""
        self.assertEqual(self.journey.route, self.route)
        self.assertEqual(self.journey.train, self.train)
        self.assertEqual(self.journey.departure_time, self.departure)
        self.assertEqual(self.journey.arrival_time, self.arrival)

    def test_journey_crew_relation(self):
        """Test relationship with crew"""
        self.assertIn(self.crew, self.journey.users.all())
        self.assertIn(self.journey, self.crew.journeies.all())

    def test_journey_str(self):
        """Test string representation"""
        expected = f"{self.departure} - {self.arrival}"
        self.assertEqual(str(self.journey), expected)


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="customer@test.com", password="testpass123", username="testuser"
        )
        self.order = Order.objects.create(user=self.user)

    def test_order_creation(self):
        """Test order creation"""
        self.assertEqual(self.order.user, self.user)
        self.assertIsNotNone(self.order.created_at)

    def test_order_str(self):
        """Test string representation"""
        self.assertEqual(str(self.order), str(self.order.created_at))

    def test_order_auto_now_add(self):
        """Test automatic created_at setting"""
        self.assertIsNotNone(self.order.created_at)


class TicketModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="customer@test.com", password="testpass123", username="testuser"
        )
        self.crew = Crew.objects.create(first_name="Jane", last_name="Smith")
        self.station1 = Station.objects.create(
            name="Kyiv", latitude=50.4501, longitude=30.5234
        )
        self.station2 = Station.objects.create(
            name="Odesa", latitude=46.4825, longitude=30.7233
        )
        self.route = Route.objects.create(
            source=self.station1, destination=self.station2, distance=450
        )
        self.train_type = TrainType.objects.create(name="Regional")
        self.train = Train.objects.create(
            name="RE-201", cargo_num=5, place_in_cargo=40, train_type=self.train_type
        )
        self.departure = datetime.now()
        self.arrival = self.departure + timedelta(hours=5)
        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=self.departure,
            arrival_time=self.arrival,
        )
        self.order = Order.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            cargo=3, seat=15, journey=self.journey, order=self.order
        )

    def test_ticket_creation(self):
        """Test ticket creation"""
        self.assertEqual(self.ticket.cargo, 3)
        self.assertEqual(self.ticket.seat, 15)
        self.assertEqual(self.ticket.journey, self.journey)
        self.assertEqual(self.ticket.order, self.order)

    def test_ticket_str(self):
        """Test string representation"""
        self.assertEqual(str(self.ticket), "3 - 15")

    def test_ticket_unique_constraint(self):
        """Test uniqueness of cargo, seat, journey combination"""
        with self.assertRaises(IntegrityError):
            Ticket.objects.create(
                cargo=3, seat=15, journey=self.journey, order=self.order
            )

    def test_ticket_different_journey_allows_duplicate(self):
        """Test that the same seats can be booked on different journeys"""
        new_journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=self.departure + timedelta(days=1),
            arrival_time=self.arrival + timedelta(days=1),
        )
        ticket2 = Ticket.objects.create(
            cargo=3, seat=15, journey=new_journey, order=self.order
        )
        self.assertIsNotNone(ticket2.id)

    def test_validate_seat_valid(self):
        """Test validation of valid seat values"""
        try:
            Ticket.validate_seat(
                cargo=3,
                seat=20,
                cargo_num=5,
                place_in_cargo=40,
                error_to_raise=ValueError,
            )
        except ValueError:
            self.fail("validate_seat() raised ValueError unexpectedly!")

    def test_validate_seat_invalid_cargo_too_low(self):
        """Test validation of invalid cargo (value too low)"""
        with self.assertRaises(ValueError) as context:
            Ticket.validate_seat(
                cargo=0,
                seat=20,
                cargo_num=5,
                place_in_cargo=40,
                error_to_raise=ValueError,
            )
        self.assertIn("cargo must be between 1 and 5", str(context.exception))

    def test_validate_seat_invalid_cargo_too_high(self):
        """Test validation of invalid cargo (value too high)"""
        with self.assertRaises(ValueError) as context:
            Ticket.validate_seat(
                cargo=10,
                seat=20,
                cargo_num=5,
                place_in_cargo=40,
                error_to_raise=ValueError,
            )
        self.assertIn("cargo must be between 1 and 5", str(context.exception))

    def test_validate_seat_invalid_seat_too_low(self):
        """Test validation of invalid seat (value too low)"""
        with self.assertRaises(ValueError) as context:
            Ticket.validate_seat(
                cargo=3,
                seat=0,
                cargo_num=5,
                place_in_cargo=40,
                error_to_raise=ValueError,
            )
        self.assertIn("seat must be between 1 and 40", str(context.exception))

    def test_validate_seat_invalid_seat_too_high(self):
        """Test validation of invalid seat (value too high)"""
        with self.assertRaises(ValueError) as context:
            Ticket.validate_seat(
                cargo=3,
                seat=50,
                cargo_num=5,
                place_in_cargo=40,
                error_to_raise=ValueError,
            )
        self.assertIn("seat must be between 1 and 40", str(context.exception))

    def test_ticket_clean_valid(self):
        """Test clean() method with valid data"""
        try:
            self.ticket.clean()
        except ValueError:
            self.fail("clean() raised ValueError unexpectedly!")

    def test_ticket_clean_invalid(self):
        """Test clean() method with invalid data"""
        invalid_ticket = Ticket(
            cargo=10,  # train only has 5 cars
            seat=15,
            journey=self.journey,
            order=self.order,
        )
        with self.assertRaises(ValueError):
            invalid_ticket.clean()

    def test_ticket_ordering(self):
        """Test ticket ordering"""
        ticket2 = Ticket.objects.create(
            cargo=1, seat=10, journey=self.journey, order=self.order
        )
        ticket3 = Ticket.objects.create(
            cargo=3, seat=5, journey=self.journey, order=self.order
        )

        tickets = Ticket.objects.all()
        self.assertEqual(tickets[0], ticket2)  # cargo=1
        self.assertEqual(tickets[1], ticket3)  # cargo=3, seat=5
        self.assertEqual(tickets[2], self.ticket)  # cargo=3, seat=15


class ModelRelationshipsTest(TestCase):
    """Tests for checking relationships between models"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com", password="testpass123", username="testuser"
        )
        self.crew = Crew.objects.create(first_name="Test", last_name="Crew")
        self.station1 = Station.objects.create(
            name="Station1", latitude=50.0, longitude=30.0
        )
        self.station2 = Station.objects.create(
            name="Station2", latitude=51.0, longitude=31.0
        )
        self.route = Route.objects.create(
            source=self.station1, destination=self.station2, distance=100
        )
        self.train_type = TrainType.objects.create(name="TestType")
        self.train = Train.objects.create(
            name="TestTrain", cargo_num=3, place_in_cargo=30, train_type=self.train_type
        )
        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=datetime.now(),
            arrival_time=datetime.now() + timedelta(hours=2),
        )
        self.order = Order.objects.create(user=self.user)

    def test_cascade_delete_route(self):
        """Test cascade deletion of route"""
        journey_id = self.journey.id
        self.route.delete()
        self.assertFalse(Journey.objects.filter(id=journey_id).exists())

    def test_cascade_delete_train(self):
        """Test cascade deletion of train"""
        journey_id = self.journey.id
        self.train.delete()
        self.assertFalse(Journey.objects.filter(id=journey_id).exists())

    def test_cascade_delete_order(self):
        """Test cascade deletion of order with tickets"""
        ticket = Ticket.objects.create(
            cargo=1, seat=1, journey=self.journey, order=self.order
        )
        ticket_id = ticket.id
        self.order.delete()
        self.assertFalse(Ticket.objects.filter(id=ticket_id).exists())

    def test_cascade_delete_journey(self):
        """Test cascade deletion of journey with tickets"""
        ticket = Ticket.objects.create(
            cargo=1, seat=1, journey=self.journey, order=self.order
        )
        ticket_id = ticket.id
        self.journey.delete()
        self.assertFalse(Ticket.objects.filter(id=ticket_id).exists())