from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from air_service.models import (
    Ticket,
    Flight,
    Airplane,
    Route,
    Airport,
    City,
    Country,
    AirplaneType,
    Order,
    Crew,
)
from django.test import TestCase


class TicketTestCase(TestCase):

    def setUp(self):
        user = get_user_model().objects.create_user(
            username="testuser", password="password123"
        )

        country = Country.objects.create(country_name="Testland")
        city = City.objects.create(city_name="Test City", country=country)
        airport = Airport.objects.create(
            airport_name="Test Airport",
            city=city
        )
        destination_airport = Airport.objects.create(
            airport_name="Destination Airport", city=city
        )

        airplane_type = AirplaneType.objects.create(type_name="Boeing 747")
        airplane = Airplane.objects.create(
            airplane_name="Airplane 1",
            rows=20,
            seats_in_row=6,
            airplane_type=airplane_type,
        )

        route = Route.objects.create(
            source=airport, destination=destination_airport, distance=1000
        )

        crew = Crew.objects.create(first_name="John", last_name="Doe")

        flight = Flight.objects.create(
            route=route,
            airplane=airplane,
            departure_datetime="2025-02-05 10:00:00",
            arrival_datetime="2025-02-05 12:00:00",
        )
        flight.crew.add(crew)

        order = Order.objects.create(user=user)

        self.flight = flight
        self.order = order
        self.airplane = airplane

    def test_valid_seat_and_row(self):
        ticket = Ticket(
            seat_row=1,
            seat_number=1,
            flight=self.flight,
            order=self.order
        )
        try:
            ticket.clean()
        except ValidationError:
            self.fail("ValidationError raised unexpectedly!")

    def test_valid_ticket_save(self):
        ticket = Ticket(
            seat_row=3,
            seat_number=4,
            flight=self.flight,
            order=self.order
        )
        try:
            ticket.save()
        except ValidationError:
            self.fail("ValidationError raised unexpectedly during save!")

        self.assertEqual(Ticket.objects.count(), 1)
