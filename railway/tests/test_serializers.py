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
        # Створюємо тестовий тип потяга для використання в тестах
        self.train_type = TrainType.objects.create(name="Express")

    def test_train_type_serializer_fields(self):
        """Тест перевіряє, що серіалізатор повертає правильні поля для типу потяга"""
        serializer = TrainTypeSerializer(instance=self.train_type)
        data = serializer.data

        self.assertEqual(set(data.keys()), {"id", "name"})
        self.assertEqual(data["name"], "Express")

    def test_train_type_serializer_create(self):
        """Тест перевіряє створення нового типу потяга через серіалізатор"""
        data = {"name": "Regional"}
        serializer = TrainTypeSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        train_type = serializer.save()
        self.assertEqual(train_type.name, "Regional")


class StationSerializerTest(TestCase):
    def setUp(self):
        # Створюємо тестову станцію з координатами
        self.station = Station.objects.create(
            name="Kyiv Central",
            latitude=50.4501,
            longitude=30.5234
        )

    def test_station_serializer_fields(self):
        """Тест перевіряє правильність полів та їх значень у серіалізаторі станції"""
        serializer = StationSerializer(instance=self.station)
        data = serializer.data

        self.assertEqual(set(data.keys()), {"id", "name", "latitude", "longitude"})
        self.assertEqual(data["name"], "Kyiv Central")
        self.assertEqual(float(data["latitude"]), 50.4501)
        self.assertEqual(float(data["longitude"]), 30.5234)

    def test_station_serializer_create(self):
        """Тест перевіряє створення нової станції через серіалізатор"""
        data = {
            "name": "Lviv",
            "latitude": 49.8397,
            "longitude": 24.0297
        }
        serializer = StationSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        station = serializer.save()
        self.assertEqual(station.name, "Lviv")


class TrainSerializerTest(TestCase):
    def setUp(self):
        # Створюємо тестовий тип потяга та сам потяг
        self.train_type = TrainType.objects.create(name="Express")
        self.train = Train.objects.create(
            name="Train 001",
            cargo_num=10,
            place_in_cargo=50,
            train_type=self.train_type
        )

    def test_train_serializer_fields(self):
        """Тест перевіряє наявність основних полів у базовому серіалізаторі потяга"""
        serializer = TrainSerializer(instance=self.train)
        data = serializer.data

        self.assertIn("id", data)
        self.assertIn("name", data)
        self.assertIn("cargo_num", data)
        self.assertIn("place_in_cargo", data)

    def test_train_list_serializer(self):
        """Тест перевіряє серіалізатор для списку потягів зі SlugRelatedField для типу"""
        serializer = TrainListSerializer(instance=self.train)
        data = serializer.data

        self.assertEqual(data["train_type"], "Express")  # Перевіряємо, що тип виводиться як строка

    def test_train_update_create_serializer(self):
        """Тест перевіряє серіалізатор для оновлення та створення потяга"""
        data = {
            "name": "Train 002",
            "cargo_num": 12,
            "place_in_cargo": 60,
            "train_type": "Express"  # Використовуємо назву типу замість ID
        }
        serializer = TrainUpdateCreateSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        train = serializer.save()
        self.assertEqual(train.name, "Train 002")
        self.assertEqual(train.train_type, self.train_type)  # Перевіряємо, що тип правильно зв'язаний

    def test_train_retrieve_serializer(self):
        """Тест перевіряє серіалізатор для детального перегляду потяга з вкладеним об'єктом типу"""
        serializer = TrainRetrieveSerializer(instance=self.train)
        data = serializer.data

        self.assertIsInstance(data["train_type"], dict)  # Перевіряємо, що тип - це об'єкт
        self.assertEqual(data["train_type"]["name"], "Express")


class RouteSerializerTest(TestCase):
    def setUp(self):
        # Створюємо тестові станції та маршрут
        self.source = Station.objects.create(
            name="Kyiv",
            latitude=50.4501,
            longitude=30.5234
        )
        self.destination = Station.objects.create(
            name="Lviv",
            latitude=49.8397,
            longitude=24.0297
        )
        self.route = Route.objects.create(
            source=self.source,
            destination=self.destination,
            distance=540
        )

    def test_route_update_create_serializer(self):
        """Тест перевіряє серіалізатор для створення/оновлення маршруту з назвами станцій"""
        data = {
            "source": "Kyiv",  # Використовуємо назву станції замість ID
            "destination": "Lviv",
            "distance": 540
        }
        serializer = RouteUpdateCreateSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        route = serializer.save()
        self.assertEqual(route.source, self.source)
        self.assertEqual(route.destination, self.destination)

    def test_route_string_serializer(self):
        """Тест перевіряє серіалізатор для відображення маршруту з стрічковими представленнями станцій"""
        serializer = RouteStringSerializer(instance=self.route)
        data = serializer.data

        self.assertEqual(data["source"], str(self.source))  # Перевіряємо string representation
        self.assertEqual(data["destination"], str(self.destination))


class JourneySerializerTest(TestCase):
    def setUp(self):
        # Створюємо всі необхідні об'єкти для тестування маршруту подорожі
        self.user = User.objects.create_user(
            email="test@test.com",
            password="testpass123",
            username="testuser"
        )
        self.crew_member = Crew.objects.create(
            first_name="John",
            last_name="Doe"
        )
        self.train_type = TrainType.objects.create(name="Express")
        self.train = Train.objects.create(
            name="Train 001",
            cargo_num=10,
            place_in_cargo=50,
            train_type=self.train_type
        )
        self.source = Station.objects.create(
            name="Kyiv",
            latitude=50.4501,
            longitude=30.5234
        )
        self.destination = Station.objects.create(
            name="Lviv",
            latitude=49.8397,
            longitude=24.0297
        )
        self.route = Route.objects.create(
            source=self.source,
            destination=self.destination,
            distance=540
        )
        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time="2024-12-01T10:00:00Z",
            arrival_time="2024-12-01T16:00:00Z"
        )
        self.journey.users.add(self.crew_member)  # Додаємо члена екіпажу до подорожі

    def test_journey_list_serializer(self):
        """Тест перевіряє серіалізатор для списку подорожей з кількістю вільних квитків"""
        from django.db.models import Count, F

        # Анотуємо подорож з розрахунком доступних квитків
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
        self.assertEqual(data["tickets_available"], 500)  # 10 вагонів * 50 місць - 0 проданих квитків

    def test_journey_retrieve_serializer(self):
        """Тест перевіряє серіалізатор для детального перегляду подорожі з проданими квитками"""
        serializer = JourneyRetrieveSerializer(instance=self.journey)
        data = serializer.data

        self.assertIn("users", data)
        self.assertIn("route", data)
        self.assertIn("train", data)
        self.assertIn("sold_tickets", data)  # Додаткове поле з проданими квитками

    def test_journey_serializer_create(self):
        """Тест перевіряє створення нової подорожі через серіалізатор"""
        data = {
            "route": self.route.id,
            "train": self.train.id,
            "users": [self.crew_member.id],  # Список ID членів екіпажу
            "departure_time": "2024-12-02T10:00:00Z",
            "arrival_time": "2024-12-02T16:00:00Z"
        }
        serializer = JourneySerializer(data=data)

        self.assertTrue(serializer.is_valid())
        journey = serializer.save()
        self.assertEqual(journey.route, self.route)
        self.assertEqual(journey.train, self.train)


class TicketSerializerTest(TestCase):
    def setUp(self):
        # Створюємо всі об'єкти для тестування квитків
        self.user = User.objects.create_user(
            email="test@test.com",
            password="testpass123",
            username="testuser"
        )
        self.train_type = TrainType.objects.create(name="Express")
        self.train = Train.objects.create(
            name="Train 001",
            cargo_num=10,
            place_in_cargo=50,
            train_type=self.train_type
        )
        self.source = Station.objects.create(name="Kyiv", latitude=50.4501, longitude=30.5234)
        self.destination = Station.objects.create(name="Lviv", latitude=49.8397, longitude=24.0297)
        self.route = Route.objects.create(source=self.source, destination=self.destination, distance=540)
        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time="2024-12-01T10:00:00Z",
            arrival_time="2024-12-01T16:00:00Z"
        )
        self.order = Order.objects.create(user=self.user)
        self.ticket = Ticket.objects.create(
            cargo=1,
            seat=10,
            journey=self.journey,
            order=self.order
        )

    def test_ticket_serializer_fields(self):
        """Тест перевіряє базовий серіалізатор квитка з основними полями"""
        serializer = TicketSerializer(instance=self.ticket)
        data = serializer.data

        self.assertEqual(set(data.keys()), {"id", "cargo", "seat", "journey"})
        self.assertEqual(data["cargo"], 1)
        self.assertEqual(data["seat"], 10)

    def test_ticket_list_serializer(self):
        """Тест перевіряє серіалізатор для списку квитків з детальною інформацією про подорож"""
        serializer = TicketListSerializer(instance=self.ticket)
        data = serializer.data

        self.assertIn("journey", data)
        self.assertIsInstance(data["journey"], dict)  # Перевіряємо, що подорож - це об'єкт


class OrderSerializerTest(TestCase):
    def setUp(self):
        # Створюємо всі об'єкти для тестування замовлень
        self.user = User.objects.create_user(
            email="test@test.com",
            password="testpass123",
            username="testuser"
        )
        self.train_type = TrainType.objects.create(name="Express")
        self.train = Train.objects.create(
            name="Train 001",
            cargo_num=10,
            place_in_cargo=50,
            train_type=self.train_type
        )
        self.source = Station.objects.create(name="Kyiv", latitude=50.4501, longitude=30.5234)
        self.destination = Station.objects.create(name="Lviv", latitude=49.8397, longitude=24.0297)
        self.route = Route.objects.create(source=self.source, destination=self.destination, distance=540)
        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time="2024-12-01T10:00:00Z",
            arrival_time="2024-12-01T16:00:00Z"
        )

    def test_order_serializer_create_with_tickets(self):
        """Тест перевіряє створення замовлення з квитками через транзакцію"""
        data = {
            "user": self.user.id,
            "tickets": [
                {
                    "cargo": 1,
                    "seat": 10,
                    "journey": self.journey.id
                },
                {
                    "cargo": 1,
                    "seat": 11,
                    "journey": self.journey.id
                }
            ]
        }
        serializer = OrderSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        # У нашому OrderSerializer немає поля 'user' у Meta.fields,
        # тому передаємо його окремо
        order = serializer.save(user=self.user)

        self.assertEqual(order.tickets.count(), 2)
        self.assertEqual(order.user, self.user)

    def test_order_serializer_empty_tickets_invalid(self):
        """Тест перевіряє, що замовлення без квитків є невалідним"""
        data = {
            "user": self.user.id,
            "tickets": []  # Порожній список квитків
        }
        serializer = OrderSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("tickets", serializer.errors)

    def test_order_list_serializer(self):
        """Тест перевіряє серіалізатор для списку замовлень з детальною інформацією про квитки"""
        order = Order.objects.create(user=self.user)
        Ticket.objects.create(
            cargo=1,
            seat=10,
            journey=self.journey,
            order=order
        )

        serializer = OrderListSerializer(instance=order)
        data = serializer.data

        self.assertIn("tickets", data)
        self.assertIsInstance(data["tickets"], list)
        self.assertEqual(len(data["tickets"]), 1)  # Перевіряємо кількість квитків у замовленні