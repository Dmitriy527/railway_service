from django.db import models
from django.db.models import UniqueConstraint
from django.conf import settings

from user.models import Crew


class Station(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='source_routes')
    destination = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='destination_routes')
    distance = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['source', 'destination']),
        ]
        verbose_name_plural = 'Routes'

    def __str__(self):
        return f'{self.source} - {self.destination}: {self.distance}km.'



class TrainType(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Train Types'

    def __str__(self):
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=100)
    cargo_num = models.IntegerField()
    place_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(TrainType, on_delete=models.CASCADE, related_name='trains')

    class Meta:
        verbose_name_plural = 'Trains'

    def __str__(self):
        return f'{self.name}: cargo: {self.cargo_num}, place: {self.place_in_cargo}, train_type: {self.train_type}'


class Journey(models.Model):
    users = models.ManyToManyField(Crew, related_name='journeies')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='journeies')
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name='journeies')
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['departure_time', 'arrival_time']),
        ]
        verbose_name_plural = 'Journeies'

    def __str__(self):
        return f'{self.route} - {self.train}: {self.departure_time} - {self.arrival_time}'


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
    )

    def __str__(self):
        return f'{self.created_at}: {self.user}'


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, related_name='tickets')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tickets')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['cargo', 'seat', 'journey'],
                name='unique_ticket_cargo_seat_journey'),
        ]
        ordering = ['cargo', 'seat']
        verbose_name_plural = 'Tickets'

    def __str__(self):
        return f'{self.order.user} {self.cargo} - {self.seat}: {self.journey}'

    @staticmethod
    def validate_seat(cargo: int, seat: int, cargo_num: int, place_in_cargo: int, error_to_raise) -> None:
        if cargo < 1 or cargo > cargo_num:
            raise error_to_raise(
                {
                    'cargo': f'cargo must be between 1 and {cargo_num}, not {cargo}',
                }
            )
        if seat < 1 or seat > place_in_cargo:
            raise error_to_raise(
                {
                    'seat': f'seat must be between 1 and {place_in_cargo}, not {seat}',
                }
            )

    def clean(self) -> None:
        train = self.journey.train
        Ticket.validate_seat(self.cargo, self.seat, train.cargo_num, train.place_in_cargo, ValueError)