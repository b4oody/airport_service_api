from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from air_service.models import (
    City,
    Country,
    Airport,
    Airplane,
    AirplaneType,
    Route,
    Crew,
    Flight,
    Order,
    Ticket,
)

CITY_LIST_URL = reverse("air_service:city-list")
AIRPORT_LIST_URL = reverse("air_service:airport-list")
AIRPLANE_LIST_URL = reverse("air_service:airplane-list")
ROUTE_LIST_URL = reverse("air_service:route-list")
CREW_LIST_URL = reverse("air_service:crew-list")
FLIGHT_LIST_URL = reverse("air_service:flight-list")
ORDER_LIST_URL = reverse("air_service:order-list")


class FilteringTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password123"
        )

        self.country_ukraine = Country.objects.create(country_name="Ukraine")
        self.country_poland = Country.objects.create(country_name="Poland")

        self.city_kyiv = City.objects.create(
            city_name="Kyiv", country=self.country_ukraine
        )
        self.city_warsaw = City.objects.create(
            city_name="Warsaw", country=self.country_poland
        )

        self.airport_kyiv = Airport.objects.create(
            airport_name="Kyiv",
            city=self.city_kyiv,
        )
        self.airport_warsaw = Airport.objects.create(
            airport_name="Warsaw",
            city=self.city_warsaw,
        )

        self.airplane_type1 = AirplaneType.objects.create(
            type_name="Type1",
        )
        self.airplane_type2 = AirplaneType.objects.create(
            type_name="Type2",
        )
        self.airplane1 = Airplane.objects.create(
            airplane_name="Airplane1",
            rows=15,
            seats_in_row=5,
            airplane_type=self.airplane_type1,
        )
        self.airplane2 = Airplane.objects.create(
            airplane_name="Airplane2",
            rows=15,
            seats_in_row=5,
            airplane_type=self.airplane_type2,
        )

        self.route1 = Route.objects.create(
            source=self.airport_kyiv,
            destination=self.airport_warsaw,
            distance=700,
        )
        self.route2 = Route.objects.create(
            source=self.airport_warsaw,
            destination=self.airport_kyiv,
            distance=400,
        )

        self.crew1 = Crew.objects.create(
            first_name="Name1",
            last_name="LastName1"
        )
        self.crew2 = Crew.objects.create(
            first_name="Name2",
            last_name="LastName2"
        )
        self.crew3 = Crew.objects.create(
            first_name="Name1",
            last_name="LastName3"
        )

        self.flight1 = Flight.objects.create(
            route=self.route1,
            airplane=self.airplane1,
            departure_datetime=datetime(
                2025, 12, 10, 21, 45,
                tzinfo=timezone.utc
            ),
            arrival_datetime=datetime(
                2025, 12, 10, 23, 45,
                tzinfo=timezone.utc
            ),
        )
        self.flight1.crew.add(self.crew1, self.crew2, self.crew3)

        self.flight2 = Flight.objects.create(
            route=self.route2,
            airplane=self.airplane2,
            departure_datetime=datetime(
                2025, 12, 11, 22, 45,
                tzinfo=timezone.utc
            ),
            arrival_datetime=datetime(
                2025, 12, 11, 23, 45,
                tzinfo=timezone.utc
            ),
        )
        self.flight1.crew.add(self.crew1, self.crew2, self.crew3)

        self.order1 = Order.objects.create(
            order_created_at=datetime(
                2025, 12, 10, 22, 45, 3, 3,
                tzinfo=timezone.utc
            ),
            user=self.user,
        )
        self.order2 = Order.objects.create(
            order_created_at=datetime(
                2025, 12, 11, 22, 45,
                tzinfo=timezone.utc
            ),
            user=self.user,
        )
        self.ticket1 = Ticket.objects.create(
            seat_row=5, seat_number=3, flight=self.flight1, order=self.order1
        )
        self.ticket2 = Ticket.objects.create(
            seat_row=5, seat_number=4, flight=self.flight1, order=self.order2
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_city_filter_without_country_pagination(self):
        url = CITY_LIST_URL
        response = self.client.get(url, {"page": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_city_filter_by_country(self):
        url = CITY_LIST_URL
        response = self.client.get(url, {"country": "Ukraine"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["city_name"], "Kyiv")
        self.assertEqual(response.data["results"][0]["country"], "Ukraine")

    def test_city_filter_with_non_existing_country(self):
        url = CITY_LIST_URL
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_airport_filter_without_filtering(self):
        url = AIRPORT_LIST_URL
        response = self.client.get(url, {"page": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_airport_filter_by_city(self):
        url = AIRPORT_LIST_URL
        response = self.client.get(url, {"city": "kyiv"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["city"], "Kyiv")
        self.assertEqual(response.data["results"][0]["country"], "Ukraine")

    def test_airport_filter_by_country(self):
        url = AIRPORT_LIST_URL
        response = self.client.get(url, {"country": "poland"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["city"], "Warsaw")
        self.assertEqual(response.data["results"][0]["country"], "Poland")

    def test_airport_filter_by_city_and_country(self):
        url = AIRPORT_LIST_URL
        response = self.client.get(
            url,
            {"country": "ukraine"},
            {"city": "kyiv"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["city"], "Kyiv")
        self.assertEqual(response.data["results"][0]["country"], "Ukraine")

    def test_airplane_filter_without_filtering(self):
        url = AIRPLANE_LIST_URL
        response = self.client.get(url, {"page": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_airplane_filter_by_airplane_name(self):
        url = AIRPLANE_LIST_URL
        response = self.client.get(url, {"airplane_type": "type1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["airplane_type"],
            "Type1"
        )
        self.assertEqual(
            response.data["results"][0]["airplane_name"],
            "Airplane1"
        )

    def test_airplane_filtering_by_type(self):
        url = AIRPLANE_LIST_URL
        response = self.client.get(url, {"airplane_name": "airplane2"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["airplane_type"],
            "Type2"
        )
        self.assertEqual(
            response.data["results"][0]["airplane_name"],
            "Airplane2"
        )

    def test_airplane_filtering_by_type_and_name(self):
        url = AIRPLANE_LIST_URL
        response = self.client.get(
            url,
            {"airplane_name": "airplane2"},
            {"airplane_type": "type1"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["airplane_type"],
            "Type2"
        )
        self.assertEqual(
            response.data["results"][0]["airplane_name"],
            "Airplane2"
        )

    def test_route_filtering_without_filtering(self):
        url = ROUTE_LIST_URL
        response = self.client.get(url, {"page": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_route_filtering_by_source(self):
        url = ROUTE_LIST_URL
        response = self.client.get(url, {"source": "kyiv"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["source"]["airport_name"],
            "Kyiv"
        )
        self.assertEqual(
            response.data["results"][0]["destination"]["airport_name"],
            "Warsaw"
        )

    def test_route_filtering_by_destination(self):
        url = ROUTE_LIST_URL
        response = self.client.get(url, {"source": "warsaw"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["source"]["airport_name"], "Warsaw"
        )
        self.assertEqual(
            response.data["results"][0]["destination"]["airport_name"], "Kyiv"
        )

    def test_airplane_filtering_by_distance_min(self):
        url = ROUTE_LIST_URL
        response = self.client.get(url, {"distance_min": "500"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["source"]["airport_name"],
            "Kyiv"
        )
        self.assertEqual(
            response.data["results"][0]["destination"]["airport_name"],
            "Warsaw"
        )

    def test_airplane_filtering_by_distance_max(self):
        url = ROUTE_LIST_URL
        response = self.client.get(url, {"distance_max": "500"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["source"]["airport_name"],
            "Warsaw"
        )
        self.assertEqual(
            response.data["results"][0]["destination"]["airport_name"],
            "Kyiv"
        )

    def test_crew_filtering_without_filtering(self):
        url = CREW_LIST_URL
        response = self.client.get(url, {"page": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)

    def test_crew_filtering_by_first_name(self):
        url = CREW_LIST_URL
        response = self.client.get(url, {"first_name": "name1"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["first_name"], "Name1")
        self.assertEqual(response.data["results"][0]["last_name"], "LastName1")
        self.assertEqual(response.data["results"][1]["first_name"], "Name1")
        self.assertEqual(response.data["results"][1]["last_name"], "LastName3")

    def test_crew_filtering_by_last_name(self):
        url = CREW_LIST_URL
        response = self.client.get(url, {"last_name": "lastname2"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["first_name"], "Name2")
        self.assertEqual(response.data["results"][0]["last_name"], "LastName2")

    def test_flight_filtering_without_filtering(self):
        url = FLIGHT_LIST_URL
        response = self.client.get(url, {"page": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_flight_filtering_by_source(self):
        url = FLIGHT_LIST_URL
        response = self.client.get(url, {"source": "warsaw"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["route"], "Warsaw - Kyiv")

    def test_flight_filtering_by_destination(self):
        url = FLIGHT_LIST_URL
        response = self.client.get(url, {"destination": "warsaw"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["route"], "Kyiv - Warsaw")

    def test_flight_filtering_by_departure_datetime(self):
        url = FLIGHT_LIST_URL
        response = self.client.get(url, {"departure_datetime": "2025-12-10"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["departure_datetime"],
            "2025-12-10T21:45:00Z"
        )
        self.assertEqual(
            response.data["results"][0]["arrival_datetime"],
            "2025-12-10T23:45:00Z"
        )

    def test_flight_filtering_by_arrival_datetime(self):
        url = FLIGHT_LIST_URL
        response = self.client.get(url, {"departure_datetime": "2025-12-11"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["departure_datetime"],
            "2025-12-11T22:45:00Z"
        )
        self.assertEqual(
            response.data["results"][0]["arrival_datetime"],
            "2025-12-11T23:45:00Z"
        )

    def test_order_filtering_without_filtering(self):
        url = ORDER_LIST_URL
        response = self.client.get(url, {"page": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_order_filtering_by_order_created_at(self):
        url = ORDER_LIST_URL
        response = self.client.get(
            url,
            {"order_created_at__date": "2025-12-10"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_order_filtering_by_source(self):
        url = ORDER_LIST_URL
        response = self.client.get(url, {"source": "kyiv"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_order_filtering_by_destination(self):
        url = ORDER_LIST_URL
        response = self.client.get(url, {"destination": "kyiv"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)
