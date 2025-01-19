from django.db.models import Prefetch
from rest_framework import viewsets

from air_service.models import (
    Country,
    City,
    Airport,
    Airplane,
    Route,
    Crew,
    Flight,
    Order, Ticket,
)
from air_service.serializers import (
    CountrySerializer,
    CitySerializer,
    AirportSerializer,
    AirplaneListSerializer,
    AirplaneRetrieveSerializer,
    RouteSerializer,
    # CrewListSerializer,
    FlightSerializer,
    FlightListSerializer,
    CrewRetrieveSerializer,
    OrderSerializer,
)


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            return queryset.select_related("country")
        return queryset


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            return queryset.select_related("city__country")
        return queryset


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        return AirplaneRetrieveSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            return queryset.select_related("source", "destination")
        return queryset


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewRetrieveSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ("list", "retrieve"):
            return queryset.select_related(
                "route__source",
                "route__destination",
                "airplane",
            ).prefetch_related("crew")
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        return FlightSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user)
        if self.action in ("list", "retrieve"):
            tickets_prefetch = Prefetch(
                "tickets",
                queryset=Ticket.objects.select_related(
                    "flight__route__source",
                    "flight__route__destination"
                ),
            )
            return queryset.prefetch_related(tickets_prefetch)
        return queryset

