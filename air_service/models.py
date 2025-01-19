from django.db import models

from config.settings.base import AUTH_USER_MODEL


class Country(models.Model):
    country_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.country_name


class City(models.Model):
    city_name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.city_name


class Airport(models.Model):
    airport_name = models.CharField(max_length=100, unique=True)
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="airports"
    )

    def __str__(self):
        return self.airport_name


class AirplaneType(models.Model):
    type_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.type_name


class Airplane(models.Model):
    airplane_name = models.CharField(max_length=100, unique=True)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes"
    )

    def __str__(self):
        return (f"{self.airplane_name}:"
                f"(rows:{self.rows} "
                f"seats_in_row:{self.seats_in_row})")


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="routes_from"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="routes_to"
    )
    distance = models.IntegerField()

    def __str__(self):
        return f"from {self.source.airport_name} to {self.destination.airport_name}"

    def full_route(self):
        return f"{self.source.airport_name} - {self.destination.airport_name}"


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ["last_name", "first_name"]


class Flight(models.Model):
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE,
        related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    crew = models.ManyToManyField(
        Crew,
        related_name="flights"
    )
    departure_datetime = models.DateTimeField()
    arrival_datetime = models.DateTimeField()

    def __str__(self):
        return f"{self.route.__str__()}({self.departure_datetime}-{self.arrival_datetime})"


class Order(models.Model):
    order_created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    def __str__(self):
        return f"{self.user}(self.created_at)"


class Ticket(models.Model):
    seat_row = models.IntegerField()
    seat_number = models.IntegerField()
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    def __str__(self):
        return (
            f"row:{self.seat_row})"
            f"seat:{self.seat_number}:"
            f"{self.flight.__str__()}")
